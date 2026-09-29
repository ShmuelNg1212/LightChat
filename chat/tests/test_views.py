import json

from django.test import Client, TestCase
from django.urls import reverse

from billing import services as billing
from chat.models import Conversation, Generation

from .helpers import FakeProxy, keys, make_user, openai_reply, rid


def read_events(response):
    body = b"".join(response.streaming_content).decode()
    return [json.loads(line) for line in body.splitlines() if line]


@keys
class SendViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)

    def post(self, **data):
        payload = {"prompt": "Hello", "model": "gpt-5-6-luna", "request_id": rid(), **data}
        return self.client.post(reverse("send"), json.dumps(payload), content_type="application/json")

    def test_streams_start_deltas_and_end(self):
        with FakeProxy(openai_reply("Hi", " there")):
            response = self.post()
            self.assertEqual(response["Content-Type"], "application/x-ndjson")
            events = read_events(response)
        self.assertEqual([e["type"] for e in events], ["start", "delta", "delta", "end"])
        start, end = events[0], events[-1]
        convo = Conversation.objects.get()
        self.assertEqual((start["conversation"], start["created"], start["title"]), (convo.pk, True, "Hello"))
        self.assertEqual(end["status"], "completed")
        self.assertIn("Hi there", end["html"])
        self.assertEqual(end["available"], "1.00")

    def test_chat_page_offers_models_and_composer(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'id="composer"')
        self.assertContains(response, "GPT-5.6 Luna · OpenAI interface")

    def test_insufficient_credit_is_402(self):
        billing.adjust(self.user, -billing.get_wallet(self.user).balance, memo="drain")
        response = self.post()
        self.assertEqual(response.status_code, 402)
        self.assertEqual(response.json()["error"]["code"], "insufficient_credit")

    def test_duplicate_is_409_and_links_the_chat(self):
        request_id = rid()
        with FakeProxy(openai_reply("Hi")):
            read_events(self.post(request_id=request_id))
            response = self.post(request_id=request_id)
        self.assertEqual(response.status_code, 409)
        convo = Conversation.objects.get()
        self.assertEqual(response.json()["error"]["url"], reverse("conversation", args=[convo.pk]))
        self.assertEqual(Generation.objects.count(), 1)

    def test_foreign_conversation_is_404(self):
        other = make_user("ben")
        convo = Conversation.objects.create(owner=other)
        response = self.post(conversation=convo.pk)
        self.assertEqual(response.status_code, 404)

    def test_cancel_endpoint_only_affects_own_generation(self):
        with FakeProxy(openai_reply("a", "b", "c")):
            response = self.post()
            generation = Generation.objects.get()
            other = Client()
            other.force_login(make_user("ben"))
            self.assertEqual(other.post(reverse("cancel", args=[generation.pk])).status_code, 204)
            generation.refresh_from_db()
            self.assertFalse(generation.cancel_requested)
            self.assertEqual(self.client.post(reverse("cancel", args=[generation.pk])).status_code, 204)
            events = read_events(response)
        self.assertEqual(events[-1]["status"], "needs_reconciliation")
        generation.refresh_from_db()
        self.assertEqual(generation.error_kind, "cancelled")

    def test_csrf_is_enforced(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.post(reverse("send"), "{}", content_type="application/json")
        self.assertEqual(response.status_code, 403)

    def test_send_requires_login(self):
        self.client.logout()
        self.assertEqual(self.post().status_code, 302)


@keys
class MessageDisplayTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)

    def send(self, body, **data):
        payload = {"prompt": "Hello", "model": "gpt-5-6-luna", "request_id": rid(), **data}
        with FakeProxy(body):
            return read_events(self.client.post(reverse("send"), json.dumps(payload), content_type="application/json"))

    def test_completed_reply_shows_model_tokens_and_charge(self):
        events = self.send(openai_reply("**Hi**", prompt_tokens=100, completion_tokens=50))
        self.assertIn("<strong>Hi</strong>", events[-1]["html"])
        page = self.client.get(reverse("conversation", args=[Conversation.objects.get().pk]))
        self.assertContains(page, "GPT-5.6 Luna · OpenAI interface")
        self.assertContains(page, "100 in · 50 out tokens")
        self.assertContains(page, "0.0015 credits")  # 100*5 + 50*20 = 1500 µcr
        self.assertContains(page, "Charged")

    def test_start_event_reports_hold_estimate(self):
        events = self.send(openai_reply("Hi"))
        self.assertRegex(events[0]["reserved"], r"^0\.\d{4}$")

    def test_under_review_reply_shows_held_amount(self):
        payload = {"prompt": "Hello", "model": "gpt-5-6-luna", "request_id": rid()}
        with FakeProxy("bad gateway", status=502):
            read_events(self.client.post(reverse("send"), json.dumps(payload), content_type="application/json"))
        page = self.client.get(reverse("conversation", args=[Conversation.objects.get().pk]))
        self.assertContains(page, "Under review")
        self.assertContains(page, "credits held")

    def test_disclosure_and_prices_visible(self):
        page = self.client.get(reverse("home"))
        self.assertContains(page, "answered by DeepSeek Flash")
        self.assertContains(page, "In 5.00 · Out 20.00 credits per 1M tokens")
        credits = self.client.get(reverse("credits"))
        self.assertContains(credits, "Models and prices")
        self.assertContains(credits, "Claude Haiku 4.5 · Anthropic interface")
