"""Replay real, redacted proxy captures (doc/fixtures/proxy, made by `manage.py probe_proxy`)."""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from proxy.client import stream_reply
from proxy.types import Done, Finish, Message, ProxyError, TextDelta, Usage

from .helpers import FakeProxy
from .test_openai import KEYS

FIXTURES = Path(settings.BASE_DIR) / "doc" / "fixtures" / "proxy"
MODELS = {"openai": "gpt-5.6-luna", "anthropic": "claude-haiku-4-5-20251001", "google": "gemini-3.8-flash"}


def load(name):
    """Return (status, body) from a capture: '# ' header lines, '# ---', then the raw body."""
    header, _, body = (FIXTURES / name).read_text(encoding="utf-8").partition("# ---\n")
    status = int(next(line for line in header.splitlines() if line.startswith("# status:")).split(":")[1])
    return status, body


def run(provider):
    return list(
        stream_reply(
            provider=provider,
            model=MODELS[provider],
            messages=[Message("user", "Say hello in one sentence.")],
            max_output_tokens=32,
        )
    )


@override_settings(PROXY_KEYS=KEYS, PROXY_BASE_URL="https://proxy.test")
class CapturedStreamTests(SimpleTestCase):
    def test_each_interface_parses_its_real_stream(self):
        for provider in MODELS:
            with self.subTest(provider=provider):
                status, body = load(f"{provider}-stream.txt")
                with FakeProxy(body, status=status):
                    events = run(provider)
                text = "".join(e.text for e in events if isinstance(e, TextDelta))
                self.assertEqual(text, "Hello! How can I help you today?")
                self.assertEqual(events[-1].finish, Finish.COMPLETE)
                self.assertIsInstance(events[-1], Done)
                self.assertEqual(events[-1].usage, Usage(183, 9))

    def test_real_bad_key_response(self):
        status, body = load("openai-bad-key.txt")
        with FakeProxy(body, status=status):
            with self.assertRaises(ProxyError) as ctx:
                run("openai")
        self.assertEqual((ctx.exception.kind, ctx.exception.status, ctx.exception.nothing_generated), ("auth", 401, True))

    def test_truncated_real_stream_is_interrupted(self):
        for provider in MODELS:
            with self.subTest(provider=provider):
                _, body = load(f"{provider}-stream.txt")
                cut = body[: len(body) // 2].rsplit("\n\n", 1)[0] + "\n\n"
                with FakeProxy(cut):
                    with self.assertRaises(ProxyError) as ctx:
                        run(provider)
                self.assertEqual(ctx.exception.kind, "interrupted")
