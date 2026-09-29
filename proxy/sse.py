"""Minimal Server-Sent Events parser (https://html.spec.whatwg.org/#event-stream-interpretation)."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class SSEEvent:
    event: str
    data: str


def iter_sse(lines: Iterable[str]) -> Iterator[SSEEvent]:
    """Group decoded lines into events. Comments and unknown fields are ignored."""
    event, data = "", []
    for line in lines:
        line = line.rstrip("\r")
        if not line:
            if data:
                yield SSEEvent(event or "message", "\n".join(data))
            event, data = "", []
            continue
        if line.startswith(":"):
            continue
        field, _, value = line.partition(":")
        if value.startswith(" "):
            value = value[1:]
        if field == "event":
            event = value
        elif field == "data":
            data.append(value)
    if data:  # stream ended without a trailing blank line
        yield SSEEvent(event or "message", "\n".join(data))
