import json
from collections.abc import Iterator
from dataclasses import dataclass

from ..sse import SSEEvent
from ..types import Done, Message, ProxyError, TextDelta


@dataclass
class PreparedRequest:
    path: str
    headers: dict
    body: dict


def merge_consecutive(messages: list[Message]) -> list[Message]:
    """Join same-role neighbours (e.g. after a failed reply) so roles alternate."""
    merged: list[Message] = []
    for m in messages:
        if merged and merged[-1].role == m.role:
            merged[-1] = Message(m.role, f"{merged[-1].content}\n\n{m.content}")
        else:
            merged.append(m)
    return merged


class Adapter:
    """Translate between our conversation and one proxy interface's wire format."""

    def build(self, *, model: str, messages: list[Message], max_output_tokens: int, key: str, system: str = "") -> PreparedRequest:
        raise NotImplementedError

    def parse(self, events: Iterator[SSEEvent]) -> Iterator[TextDelta | Done]:
        """Yield text deltas, then exactly one Done. Raise ProxyError if the stream fails or ends early."""
        raise NotImplementedError

    @staticmethod
    def load(event: SSEEvent) -> dict:
        try:
            payload = json.loads(event.data)
        except json.JSONDecodeError as exc:
            raise ProxyError("bad_stream", "The model service sent an unreadable stream.") from exc
        if isinstance(payload, dict) and "error" in payload:
            error = payload["error"] if isinstance(payload["error"], dict) else {"message": str(payload["error"])}
            raise ProxyError("stream_error", error.get("message") or "The model service reported an error.", detail=error)
        return payload

    @staticmethod
    def ended_early(usage=None) -> ProxyError:
        return ProxyError("interrupted", "The reply stopped before it finished.", usage=usage)
