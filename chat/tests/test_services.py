import httpx
from django.test import TestCase

from billing import services as billing
from chat import services
from chat.models import Conversation, Generation, Message
from chat.services import SendRejected

from .helpers import FakeProxy, anthropic_reply, keys, make_user, openai_reply, rid


def consume(generation):
    deltas, end = [], None
    for kind, value in services.run(generation):
        if kind == "delta":
            deltas.append(value)
        else:
            end = value
    return "".join(deltas), end


@keys
class GenerationLifecycleTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def send(self, prompt="Hello", model="gpt-5-6-luna", **kw):
        return services.start(self.user, prompt=prompt, offering_slug=model, client_request_id=kw.pop("request_id", rid()), **kw)

    def wallet(self):
        return billing.get_wallet(self.user)

    def test_happy_path_holds_then_charges_actual_usage(self):
        started = self.send("Plan a trip")
        g = started.generation
        self.assertTrue(started.created_conversation)
        self.assertEqual(g.conversation.title, "Plan a trip")
        self.assertEqual(self.wallet().held, g.reserved)

        with FakeProxy(openai_reply("Hi", " there")):
            text, end = consume(g)

        self.assertEqual(text, "Hi there")
        g.refresh_from_db()
        self.assertEqual(g.status, Generation.Status.COMPLETED)
        self.assertEqual((g.input_tokens, g.output_tokens), (12, 8))
        self.assertEqual(g.charged, 12 * 5 + 8 * 20)  # 5 and 20 µcr per token
        self.assertEqual(g.assistant_message.content, "Hi there")
        wallet = self.wallet()
        self.assertEqual((wallet.balance, wallet.held), (1_000_000 - g.charged, 0))
        self.assertFalse(g.overage)

    def test_reservation_covers_real_hidden_prompt(self):
        g = self.send("Say hello in one sentence.").generation
        # Real sample: 183 input tokens for this prompt; the bound must cover it.
        self.assertGreaterEqual(services.input_token_bound(services.history_for(g.conversation, g.user_message)), 183)

    def test_duplicate_request_id_is_refused_without_second_hold(self):
        request_id = rid()
        first = self.send(request_id=request_id).generation
        with self.assertRaises(SendRejected) as ctx:
            self.send(request_id=request_id)
        self.assertEqual(ctx.exception.code, "duplicate")
        self.assertEqual(ctx.exception.extra["generation"], first)
        self.assertEqual(self.wallet().entries.filter(kind="hold").count(), 1)
        self.assertEqual(Message.objects.filter(role="user").count(), 1)

    def test_insufficient_credit_creates_nothing(self):
        poor = make_user("poor", credit=10)
        with self.assertRaises(SendRejected) as ctx:
            services.start(poor, prompt="Hi", offering_slug="gpt-5-6-luna", client_request_id=rid())
        self.assertEqual(ctx.exception.code, "insufficient_credit")
        self.assertFalse(Conversation.objects.filter(owner=poor).exists())
        self.assertFalse(Generation.objects.filter(user=poor).exists())

    def test_rejection_before_generation_releases_hold(self):
        g = self.send().generation
        with FakeProxy('{"error": {}}', status=429):
            text, end = consume(g)
        g.refresh_from_db()
        self.assertEqual((g.status, g.error_kind, g.charged), (Generation.Status.FAILED, "rate_limited", 0))
        wallet = self.wallet()
        self.assertEqual((wallet.balance, wallet.held), (1_000_000, 0))

    def test_upstream_failure_keeps_hold_for_reconciliation(self):
        g = self.send().generation
        with FakeProxy("bad gateway", status=502):
            consume(g)
        g.refresh_from_db()
        self.assertEqual(g.status, Generation.Status.NEEDS_RECONCILIATION)
        self.assertEqual(self.wallet().held, g.reserved)

    def test_interrupted_stream_saves_partial_text_and_keeps_hold(self):
        g = self.send().generation
        with FakeProxy(openai_reply("Partial", finish=None, done=False)):
            text, _ = consume(g)
        g.refresh_from_db()
        self.assertEqual((g.status, g.error_kind), (Generation.Status.NEEDS_RECONCILIATION, "interrupted"))
        self.assertEqual(g.assistant_message.content, "Partial")
        self.assertEqual(self.wallet().held, g.reserved)

    def test_timeout_is_not_retried(self):
        g = self.send().generation
        with FakeProxy(exc=httpx.ReadTimeout("slow")) as fake:
            consume(g)
        self.assertEqual(len(fake.requests), 1)
        g.refresh_from_db()
        self.assertEqual(g.status, Generation.Status.NEEDS_RECONCILIATION)

    def test_cancel(self):
        g = self.send().generation
        self.assertTrue(services.request_cancel(self.user, g.pk))
        with FakeProxy(openai_reply("a", "b", "c")):
            consume(g)
        g.refresh_from_db()
        self.assertEqual((g.status, g.error_kind), (Generation.Status.NEEDS_RECONCILIATION, "cancelled"))

    def test_browser_disconnect_marks_for_reconciliation(self):
        g = self.send().generation
        with FakeProxy(openai_reply("a", "b", "c")):
            stream = services.run(g)
            next(stream)
            stream.close()
        g.refresh_from_db()
        self.assertEqual((g.status, g.error_kind), (Generation.Status.NEEDS_RECONCILIATION, "disconnected"))
        self.assertEqual(g.assistant_message.content, "a")

    def test_one_reply_at_a_time_per_conversation(self):
        g = self.send().generation
        with self.assertRaises(SendRejected) as ctx:
            self.send(conversation_id=g.conversation_id)
        self.assertEqual(ctx.exception.code, "busy")

    def test_context_and_model_switch(self):
        g1 = self.send("My name is Ana.").generation
        with FakeProxy(openai_reply("Nice to meet you, Ana.")):
            consume(g1)
        g2 = self.send("What is my name?", model="claude-haiku-4-5", conversation_id=g1.conversation_id).generation
        with FakeProxy(anthropic_reply("Ana.")) as fake:
            consume(g2)
        self.assertEqual(
            fake.last_json["messages"],
            [
                {"role": "user", "content": "My name is Ana."},
                {"role": "assistant", "content": "Nice to meet you, Ana."},
                {"role": "user", "content": "What is my name?"},
            ],
        )
        g2.refresh_from_db()
        self.assertEqual(g2.model_label, "Claude Haiku 4.5 · Anthropic interface")
        self.assertEqual(g2.status, Generation.Status.COMPLETED)

    def test_failed_exchange_is_left_out_of_context_and_can_be_retried(self):
        g1 = self.send("First").generation
        with FakeProxy("x", status=429):
            consume(g1)
        retry = self.send("", conversation_id=g1.conversation_id, retry_message_id=g1.user_message_id).generation
        self.assertEqual(retry.user_message_id, g1.user_message_id)
        g1.refresh_from_db()
        self.assertIsNone(g1.assistant_message)  # the failed bubble is replaced
        with FakeProxy(openai_reply("OK")) as fake:
            consume(retry)
        self.assertEqual(fake.last_json["messages"], [{"role": "user", "content": "First"}])
        self.assertEqual(Message.objects.filter(role="user").count(), 1)

    def test_completed_message_cannot_be_retried(self):
        g = self.send().generation
        with FakeProxy(openai_reply("OK")):
            consume(g)
        with self.assertRaises(SendRejected):
            self.send("", conversation_id=g.conversation_id, retry_message_id=g.user_message_id)

    def test_other_users_conversation_is_not_found(self):
        g = self.send().generation
        with FakeProxy(openai_reply("OK")):
            consume(g)
        other = make_user("ben")
        with self.assertRaises(SendRejected) as ctx:
            services.start(other, prompt="hi", offering_slug="gpt-5-6-luna", client_request_id=rid(), conversation_id=g.conversation_id)
        self.assertEqual(ctx.exception.code, "not_found")

    def test_unconfigured_model_is_refused(self):
        with self.settings(PROXY_KEYS={"openai": "", "anthropic": "k", "google": "k"}):
            with self.assertRaises(SendRejected) as ctx:
                self.send()
        self.assertEqual(ctx.exception.code, "model_unavailable")

    def test_empty_and_overlong_prompts(self):
        for prompt, code in [("   ", "empty"), ("x" * 16_001, "too_long")]:
            with self.subTest(code=code), self.assertRaises(SendRejected) as ctx:
                self.send(prompt)
            self.assertEqual(ctx.exception.code, code)
        self.assertFalse(Conversation.objects.exists())
