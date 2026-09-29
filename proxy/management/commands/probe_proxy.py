"""Capture real, redacted proxy responses as fixtures.

Makes one small PAID streamed request per configured interface, plus (with
--bad-key) one request with an invalid key. Writes doc/fixtures/proxy/*.txt
and checks each capture parses with our adapter.
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from proxy.adapters import adapter_for
from proxy.client import make_http_client
from proxy.sse import iter_sse
from proxy.types import Done, Message, ProxyError, TextDelta

MODELS = {"openai": "gpt-5.6-luna", "anthropic": "claude-haiku-4-5-20251001", "google": "gemini-3.8-flash"}
OUT = Path(settings.BASE_DIR) / "doc" / "fixtures" / "proxy"
KEEP_HEADERS = {"content-type", "x-request-id"}


class Command(BaseCommand):
    help = "Make one tiny paid request per configured proxy interface and save redacted transcripts."

    def add_arguments(self, parser):
        parser.add_argument("--provider", choices=sorted(MODELS), action="append")
        parser.add_argument("--bad-key", action="store_true", help="Also send one request with an invalid key.")
        parser.add_argument("--max-tokens", type=int, default=32)
        parser.add_argument("--no-save", action="store_true", help="Report only; leave the committed fixtures untouched.")

    def handle(self, *args, **opts):
        self.save = not opts["no_save"]
        OUT.mkdir(parents=True, exist_ok=True)
        for provider in opts["provider"] or sorted(MODELS):
            key = settings.PROXY_KEYS.get(provider)
            if not key:
                self.stdout.write(f"{provider}: no key configured, skipped")
                continue
            self.capture(provider, key, opts["max_tokens"], f"{provider}-stream.txt")
        if opts["bad_key"]:
            self.capture("openai", "invalid-key-for-probe", opts["max_tokens"], "openai-bad-key.txt")

    def capture(self, provider, key, max_tokens, filename):
        adapter = adapter_for(provider)
        req = adapter.build(
            model=MODELS[provider],
            messages=[Message("user", "Say hello in one sentence.")],
            max_output_tokens=max_tokens,
            key=key,
        )
        with make_http_client() as http:
            with http.stream("POST", req.path, headers=req.headers, json=req.body) as response:
                lines = list(response.iter_lines())
                status = response.status_code
                headers = {k: v for k, v in response.headers.items() if k.lower() in KEEP_HEADERS}

        text = "\n".join(lines)
        for secret in filter(None, settings.PROXY_KEYS.values()):
            text = text.replace(secret, "[REDACTED]")
        header_lines = "".join(f"# {k}: {v}\n" for k, v in sorted(headers.items()))
        if self.save:
            (OUT / filename).write_text(
                f"# POST {req.path}\n# status: {status}\n{header_lines}# ---\n{text}\n", encoding="utf-8"
            )
        else:
            filename = "(not saved)"

        outcome = f"HTTP {status} with max_tokens={max_tokens}"
        if status != 200:
            outcome += f", body: {text[:300]}"
        if status == 200:
            try:
                events = list(adapter.parse(iter_sse(lines)))
                reply = "".join(e.text for e in events if isinstance(e, TextDelta))
                done = events[-1]
                outcome += f", parsed: finish={done.finish} ({done.raw_reason}), usage={done.usage}, text={reply!r}"
                assert isinstance(done, Done)
            except ProxyError as exc:
                outcome += f", PARSE FAILED: {exc}"
        self.stdout.write(f"{provider} → {filename}: {outcome}")
