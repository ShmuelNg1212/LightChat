"""Fixtures follow the documented shapes (proxy docs revision 2026-09-19)."""

from django.test import SimpleTestCase, override_settings

from proxy.client import stream_reply
from proxy.types import Done, Finish, Message, ProxyError, TextDelta, Usage

from .helpers import FakeProxy, sse
from .test_openai import KEYS


def part(text, finish=None, usage=None):
    candidate = {"index": 0, "content": {"role": "model", "parts": [{"text": text}]}}
    if finish:
        candidate["finishReason"] = finish
    payload = {"candidates": [candidate], "modelVersion": "gemini-3.8-flash"}
    if usage:
        payload["usageMetadata"] = usage
    return payload


USAGE = {"promptTokenCount": 12, "candidatesTokenCount": 8, "totalTokenCount": 20}


def run(system=""):
    return list(
        stream_reply(
            provider="google",
            model="gemini-3.8-flash",
            messages=[Message("user", "Hi"), Message("assistant", "Hello"), Message("user", "Again")],
            max_output_tokens=64,
            system=system,
        )
    )


@override_settings(PROXY_KEYS=KEYS, PROXY_BASE_URL="https://proxy.test")
class GeminiAdapterTests(SimpleTestCase):
    def test_request_shape(self):
        with FakeProxy(sse(part("x", "STOP", USAGE))) as fake:
            run(system="Be brief.")
        request = fake.requests[0]
        self.assertEqual(
            str(request.url),
            "https://proxy.test/google/v1beta/models/gemini-3.8-flash:streamGenerateContent?alt=sse",
        )
        self.assertEqual(request.headers["x-goog-api-key"], "test-google-key")
        self.assertEqual(
            fake.last_json,
            {
                "contents": [
                    {"role": "user", "parts": [{"text": "Hi"}]},
                    {"role": "model", "parts": [{"text": "Hello"}]},
                    {"role": "user", "parts": [{"text": "Again"}]},
                ],
                "generationConfig": {"maxOutputTokens": 64, "thinkingConfig": {"thinkingBudget": 0}},
                "systemInstruction": {"parts": [{"text": "Be brief."}]},
            },
        )

    def test_streams_text_and_usage_event_without_candidates(self):
        with FakeProxy(sse(part("Hel"), part("lo", "STOP"), {"usageMetadata": USAGE})):
            events = run()
        self.assertEqual(events[:2], [TextDelta("Hel"), TextDelta("lo")])
        self.assertEqual(events[-1], Done(Finish.COMPLETE, Usage(12, 8), "STOP"))

    def test_finish_reasons(self):
        for reason, finish in [("MAX_TOKENS", Finish.LENGTH), ("SAFETY", Finish.FILTERED)]:
            with self.subTest(reason=reason), FakeProxy(sse(part("x", reason, USAGE))):
                self.assertEqual(run()[-1].finish, finish)

    def test_stream_ending_without_finish_is_interrupted(self):
        with FakeProxy(sse(part("Hel"))):
            with self.assertRaises(ProxyError) as ctx:
                run()
        self.assertEqual(ctx.exception.kind, "interrupted")

    def test_error_after_finish_is_not_success(self):
        with FakeProxy(sse(part("x", "STOP", USAGE), {"error": {"code": 500, "message": "late"}})):
            with self.assertRaises(ProxyError) as ctx:
                run()
        self.assertEqual(ctx.exception.kind, "stream_error")
