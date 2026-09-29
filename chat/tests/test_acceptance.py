"""Acceptance criteria from doc/study/2026-09-29-1243-litechat-core.md, checked end to end.

Scenarios already covered elsewhere are listed for traceability:
- private data / 404 for others: test_conversations, test_views, test_services
- context across turns and a model switch: test_services.test_context_and_model_switch
- errors, truncation, interruption, stop, retry: test_services, test_views
- pricing, per-reply cost, estimate vs charge: test_views.MessageDisplayTests
- reconciliation of unknown usage: test_reconciliation
"""

import importlib
import json
import threading

from django.apps import apps

from django.db import connection
from django.db.models import Sum
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from billing import services as billing
from catalog.models import ModelOffering
from chat import services
from chat.models import Conversation, Generation

from .helpers import KEYS, FakeProxy, keys, make_user, openai_reply, rid


def race(fn, n):
    results, barrier = [], threading.Barrier(n)

    def worker(i):
        barrier.wait()
        try:
            results.append(("ok", fn(i)))
        except services.SendRejected as exc:
            results.append((exc.code, None))
        finally:
            connection.close()

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


@keys
class ConcurrentTabsTests(TransactionTestCase):
    def setUp(self):
        # TransactionTestCase empties tables between tests; restore the seeded catalog.
        importlib.import_module("catalog.migrations.0002_seed_proxy_models").seed(apps, None)

    def test_same_message_from_two_tabs_is_charged_once(self):
        user = make_user()
        request_id = rid()
        results = race(
            lambda i: services.start(user, prompt="Hi", offering_slug="gpt-5-6-luna", client_request_id=request_id), 4
        )
        self.assertEqual(sorted(code for code, _ in results), ["duplicate"] * 3 + ["ok"])
        self.assertEqual(Generation.objects.count(), 1)
        self.assertEqual(billing.get_wallet(user).entries.filter(kind="hold").count(), 1)

    def test_parallel_messages_cannot_overspend(self):
        user = make_user(credit=0)
        one = services.reservation_for(
            ModelOffering.objects.get(slug="gpt-5-6-luna"), [services.ProxyMessage("user", "Hi")]
        )
        billing.grant(user, one * 2 + 1)  # room for exactly two replies
        results = race(
            lambda i: services.start(user, prompt="Hi", offering_slug="gpt-5-6-luna", client_request_id=rid()), 5
        )
        codes = sorted(code for code, _ in results)
        self.assertEqual(codes.count("ok"), 2)
        self.assertEqual(codes.count("insufficient_credit"), 3)
        wallet = billing.get_wallet(user)
        self.assertLessEqual(wallet.held, wallet.balance)


@keys
class AcceptanceTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)

    def send(self, body, **data):
        payload = {"prompt": "Hello", "model": "gpt-5-6-luna", "request_id": rid(), **data}
        with FakeProxy(body):
            response = self.client.post(reverse("send"), json.dumps(payload), content_type="application/json")
            return b"".join(response.streaming_content).decode()

    def test_proxy_keys_never_reach_the_browser(self):
        streamed = self.send(openai_reply("Hi"))
        convo = Conversation.objects.get()
        pages = [
            streamed,
            self.client.get(reverse("home")).content.decode(),
            self.client.get(reverse("conversation", args=[convo.pk])).content.decode(),
            self.client.get(reverse("credits")).content.decode(),
        ]
        for key in KEYS.values():
            for page in pages:
                self.assertNotIn(key, page)

    def test_conversations_survive_sign_out_and_in(self):
        self.send(openai_reply("Remember me"))
        convo = Conversation.objects.get()
        self.client.logout()
        self.assertTrue(self.client.login(username="ana", password="correct-horse-9"))
        page = self.client.get(reverse("conversation", args=[convo.pk]))
        self.assertContains(page, "Remember me")
        self.assertContains(self.client.get(reverse("home")), convo.display_title)

    def test_each_reply_records_its_model(self):
        first = json.loads(self.send(openai_reply("A")).splitlines()[0])
        with FakeProxy(
            'event: message_start\ndata: {"type":"message_start","message":{"usage":{"input_tokens":5,"output_tokens":0}}}\n\n'
            'event: content_block_delta\ndata: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"B"}}\n\n'
            'event: message_delta\ndata: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":1}}\n\n'
            'event: message_stop\ndata: {"type":"message_stop"}\n\n'
        ):
            payload = {"prompt": "Next", "model": "claude-haiku-4-5", "request_id": rid(), "conversation": first["conversation"]}
            response = self.client.post(reverse("send"), json.dumps(payload), content_type="application/json")
            b"".join(response.streaming_content)
        labels = list(Generation.objects.order_by("created_at").values_list("model_label", flat=True))
        self.assertEqual(labels, ["GPT-5.6 Luna · OpenAI interface", "Claude Haiku 4.5 · Anthropic interface"])

    def test_insufficient_credit_blocks_the_paid_request(self):
        billing.adjust(self.user, -billing.get_wallet(self.user).balance, memo="drain")
        payload = {"prompt": "Hello", "model": "gpt-5-6-luna", "request_id": rid()}
        with FakeProxy(openai_reply("never")) as fake:
            response = self.client.post(reverse("send"), json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 402)
        self.assertEqual(fake.requests, [])  # the proxy was never called

    def test_ledger_always_balances(self):
        self.send(openai_reply("A"))
        with FakeProxy('{"error": {}}', status=429):
            payload = {"prompt": "B", "model": "gpt-5-6-luna", "request_id": rid()}
            b"".join(self.client.post(reverse("send"), json.dumps(payload), content_type="application/json").streaming_content)
        wallet = billing.get_wallet(self.user)
        totals = wallet.entries.aggregate(b=Sum("amount"), h=Sum("held_delta"))
        self.assertEqual((wallet.balance, wallet.held), (totals["b"], totals["h"]))
        self.assertEqual(wallet.held, 0)
