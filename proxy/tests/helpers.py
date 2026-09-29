import json

import httpx

from proxy import client


def sse(*events: dict | str, event_names: list[str] | None = None) -> str:
    """Build an SSE body. Dicts become JSON data lines; strings are sent verbatim."""
    out = []
    for i, e in enumerate(events):
        name = event_names[i] if event_names else None
        prefix = f"event: {name}\n" if name else ""
        out.append(f"{prefix}data: {e if isinstance(e, str) else json.dumps(e)}\n\n")
    return "".join(out)


class FakeProxy:
    """Install an httpx MockTransport answering with a canned status and body."""

    def __init__(self, body: str = "", status: int = 200, exc: Exception | None = None):
        self.body, self.status, self.exc = body, status, exc
        self.requests: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.exc:
            raise self.exc
        return httpx.Response(self.status, text=self.body, headers={"content-type": "text/event-stream"})

    def __enter__(self):
        client.set_transport(httpx.MockTransport(self.handler))
        return self

    def __exit__(self, *exc):
        client.set_transport(None)

    @property
    def last_json(self) -> dict:
        return json.loads(self.requests[-1].content)
