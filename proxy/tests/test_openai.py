"""Fixtures follow the documented shapes (proxy docs revision 2026-09-19)."""

import httpx
from django.test import SimpleTestCase, override_settings

from proxy.client import stream_reply
from proxy.types import Cancelled, Done, Finish, Message, ProxyError, TextDelta, Usage

from .helpers import FakeProxy, sse

KEYS = {"openai": "test-openai-key", "anthropic": "test-anthropic-key", "google": "test-google-key"}


def chunk(content=None, finish=None):
    delta = {"content": content} if content is not None else {}
    return {"object": "chat.completion.chunk", "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}


USAGE = {"object": "chat.completion.chunk", "choices": [], "usage": {"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20}}


def run(**kw):
    return list(
        stream_reply(provider="openai", model="gpt-5.6-luna", messages=[Message("user", "Hi")], max_output_tokens=64, **kw)
    )


@override_settings(PROXY_KEYS=KEYS, PROXY_BASE_URL="https://proxy.test")
class OpenAIAdapterTests(SimpleTestCase):
    def test_request_shape(self):
        with FakeProxy(sse(chunk("x", "stop"), USAGE, "[DONE]")) as fake:
            list(
                stream_reply(
                    provider="openai",
                    model="gpt-5.6-luna",
                    messages=[Message("user", "a"), Message("user", "b"), Message("assistant", "c")],
                    max_output_tokens=64,
                    system="Be brief.",
                )
            )
        request = fake.requests[0]
        self.assertEqual(str(request.url), "https://proxy.test/openai/v1/chat/completions")
        self.assertEqual(request.headers["authorization"], "Bearer test-openai-key")
        self.assertEqual(
            fake.last_json,
            {
                "model": "gpt-5.6-luna",
                "messages": [
                    {"role": "system", "content": "Be brief."},
                    {"role": "user", "content": "a\n\nb"},
                    {"role": "assistant", "content": "c"},
                ],
                "max_tokens": 64,
                "reasoning_effort": "none",
                "stream": True,
                "stream_options": {"include_usage": True},
            },
        )

    def test_streams_text_then_done_with_usage(self):
        with FakeProxy(sse(chunk("Hello"), chunk("!"), chunk(None, "stop"), USAGE, "[DONE]")):
            events = run()
        self.assertEqual(events[:2], [TextDelta("Hello"), TextDelta("!")])
        self.assertEqual(events[-1], Done(Finish.COMPLETE, Usage(12, 8), "stop"))

    def test_length_finish(self):
        with FakeProxy(sse(chunk("x", "length"), USAGE, "[DONE]")):
            self.assertEqual(run()[-1].finish, Finish.LENGTH)

    def test_stream_without_done_is_interrupted(self):
        with FakeProxy(sse(chunk("Hel"))):
            with self.assertRaises(ProxyError) as ctx:
                run()
        self.assertEqual(ctx.exception.kind, "interrupted")
        self.assertFalse(ctx.exception.nothing_generated)

    def test_error_inside_stream(self):
        with FakeProxy(sse(chunk("x"), {"error": {"message": "boom"}})):
            with self.assertRaises(ProxyError) as ctx:
                run()
        self.assertEqual(ctx.exception.kind, "stream_error")
        self.assertFalse(ctx.exception.nothing_generated)

    def test_rejections_before_generation_are_not_billable(self):
        for status, kind in [(400, "bad_request"), (401, "auth"), (403, "auth"), (429, "rate_limited")]:
            with self.subTest(status=status), FakeProxy('{"error": "x"}', status=status):
                with self.assertRaises(ProxyError) as ctx:
                    run()
                self.assertEqual((ctx.exception.kind, ctx.exception.nothing_generated), (kind, True))

    def test_upstream_failures_need_reconciliation(self):
        for status in (502, 503, 504):
            with self.subTest(status=status), FakeProxy("bad gateway", status=status):
                with self.assertRaises(ProxyError) as ctx:
                    run()
                self.assertEqual((ctx.exception.kind, ctx.exception.nothing_generated), ("upstream", False))

    def test_connect_error_is_not_billable(self):
        with FakeProxy(exc=httpx.ConnectError("dns")):
            with self.assertRaises(ProxyError) as ctx:
                run()
        self.assertEqual((ctx.exception.kind, ctx.exception.nothing_generated), ("unreachable", True))

    def test_read_timeout_needs_reconciliation(self):
        with FakeProxy(exc=httpx.ReadTimeout("slow")):
            with self.assertRaises(ProxyError) as ctx:
                run()
        self.assertEqual((ctx.exception.kind, ctx.exception.nothing_generated), ("timeout", False))

    def test_cancel(self):
        with FakeProxy(sse(chunk("a"), chunk("b"), chunk(None, "stop"), USAGE, "[DONE]")):
            with self.assertRaises(Cancelled):
                run(should_cancel=lambda: True)

    @override_settings(PROXY_KEYS={"openai": ""})
    def test_missing_key(self):
        with self.assertRaises(ProxyError) as ctx:
            run()
        self.assertEqual((ctx.exception.kind, ctx.exception.nothing_generated), ("not_configured", True))


@override_settings(PROXY_KEYS=KEYS, PROXY_BASE_URL="https://proxy.test")
class DurationLimitTests(SimpleTestCase):
    def run_with_clock(self, *elapsed):
        from unittest import mock

        ticks = iter([0.0, *elapsed])
        with mock.patch("proxy.client.time.monotonic", side_effect=lambda: next(ticks)):
            with FakeProxy(sse(chunk("a"), chunk("b"), chunk(None, "stop"), USAGE, "[DONE]")):
                return run()

    def test_long_reply_under_twenty_minutes_completes(self):
        events = self.run_with_clock(19 * 60, 19 * 60 + 30, 19 * 60 + 40)
        self.assertEqual(events[-1].finish, Finish.COMPLETE)

    def test_reply_over_twenty_minutes_is_stopped(self):
        with self.assertRaises(ProxyError) as ctx:
            self.run_with_clock(20 * 60 + 1)
        self.assertEqual((ctx.exception.kind, ctx.exception.nothing_generated), ("timeout", False))

    @override_settings(REPLY_MAX_SECONDS=260.0)
    def test_configured_limit_stops_the_reply_before_the_platform_does(self):
        with self.assertRaises(ProxyError) as ctx:
            self.run_with_clock(261)
        self.assertEqual(ctx.exception.kind, "timeout")

    @override_settings(REPLY_CHUNK_TIMEOUT_SECONDS=25.0)
    def test_gap_between_chunks_is_configurable(self):
        from proxy.client import make_http_client

        with make_http_client() as http:
            self.assertEqual((http.timeout.read, http.timeout.connect), (25.0, 5.0))
