"""Fixtures follow the documented shapes (proxy docs revision 2026-09-19)."""

from django.test import SimpleTestCase, override_settings

from proxy.client import stream_reply
from proxy.types import Done, Finish, Message, ProxyError, TextDelta, Usage

from .helpers import FakeProxy, sse
from .test_openai import KEYS

START = {"type": "message_start", "message": {"id": "msg_x", "type": "message", "role": "assistant", "content": [], "usage": {"input_tokens": 12, "output_tokens": 1}}}
BLOCK_START = {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}
PING = {"type": "ping"}


def delta(text):
    return {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": text}}


BLOCK_STOP = {"type": "content_block_stop", "index": 0}


def message_delta(reason):
    return {"type": "message_delta", "delta": {"stop_reason": reason, "stop_sequence": None}, "usage": {"output_tokens": 8}}


STOP = {"type": "message_stop"}


def body(*events):
    return sse(*events, event_names=[e["type"] for e in events])


def run(system=""):
    return list(
        stream_reply(
            provider="anthropic",
            model="claude-haiku-4-5-20251001",
            messages=[Message("user", "Hi"), Message("assistant", "Hello"), Message("user", "Again")],
            max_output_tokens=64,
            system=system,
        )
    )


@override_settings(PROXY_KEYS=KEYS, PROXY_BASE_URL="https://proxy.test")
class AnthropicAdapterTests(SimpleTestCase):
    def test_request_shape(self):
        with FakeProxy(body(START, delta("x"), message_delta("end_turn"), STOP)) as fake:
            run(system="Be brief.")
        request = fake.requests[0]
        self.assertEqual(str(request.url), "https://proxy.test/anthropic/v1/messages")
        self.assertEqual(request.headers["x-api-key"], "test-anthropic-key")
        self.assertEqual(request.headers["anthropic-version"], "2023-06-01")
        self.assertEqual(
            fake.last_json,
            {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 64,
                "messages": [
                    {"role": "user", "content": "Hi"},
                    {"role": "assistant", "content": "Hello"},
                    {"role": "user", "content": "Again"},
                ],
                "thinking": {"type": "disabled"},
                "stream": True,
                "system": "Be brief.",
            },
        )

    def test_streams_text_and_usage(self):
        with FakeProxy(body(START, BLOCK_START, PING, delta("Hel"), delta("lo"), BLOCK_STOP, message_delta("end_turn"), STOP)):
            events = run()
        self.assertEqual(events[:2], [TextDelta("Hel"), TextDelta("lo")])
        self.assertEqual(events[-1], Done(Finish.COMPLETE, Usage(12, 8), "end_turn"))

    def test_max_tokens_is_truncation(self):
        with FakeProxy(body(START, delta("x"), message_delta("max_tokens"), STOP)):
            self.assertEqual(run()[-1].finish, Finish.LENGTH)

    def test_block_stop_is_not_message_end(self):
        with FakeProxy(body(START, delta("x"), BLOCK_STOP)):
            with self.assertRaises(ProxyError) as ctx:
                run()
        self.assertEqual(ctx.exception.kind, "interrupted")

    def test_error_event(self):
        error = {"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}}
        with FakeProxy(body(START, delta("x"), error)):
            with self.assertRaises(ProxyError) as ctx:
                run()
        self.assertEqual((ctx.exception.kind, ctx.exception.nothing_generated), ("stream_error", False))
