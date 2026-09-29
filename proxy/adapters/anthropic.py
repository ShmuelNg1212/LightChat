from ..types import Done, Finish, TextDelta, Usage
from .base import Adapter, PreparedRequest, merge_consecutive

FINISH = {
    "end_turn": Finish.COMPLETE,
    "stop_sequence": Finish.COMPLETE,
    "max_tokens": Finish.LENGTH,
    "refusal": Finish.FILTERED,
}


class AnthropicMessages(Adapter):
    """POST /anthropic/v1/messages, streamed. Terminal event: message_stop."""

    def build(self, *, model, messages, max_output_tokens, key, system=""):
        body = {
            "model": model,
            "max_tokens": max_output_tokens,
            "messages": [{"role": m.role, "content": m.content} for m in merge_consecutive(messages)],
            "thinking": {"type": "disabled"},
            "stream": True,
        }
        if system:
            body["system"] = system
        return PreparedRequest(
            path="/anthropic/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
            body=body,
        )

    def parse(self, events):
        input_tokens = output_tokens = None
        reason = None
        for event in events:
            payload = self.load(event)
            kind = payload.get("type") or event.event
            if kind == "message_start":
                usage = (payload.get("message") or {}).get("usage") or {}
                input_tokens = usage.get("input_tokens", input_tokens)
                output_tokens = usage.get("output_tokens", output_tokens)
            elif kind == "content_block_delta":
                delta = payload.get("delta") or {}
                if delta.get("type") == "text_delta" and delta.get("text"):
                    yield TextDelta(delta["text"])
            elif kind == "message_delta":
                reason = (payload.get("delta") or {}).get("stop_reason") or reason
                usage = payload.get("usage") or {}
                # message_delta usage is cumulative
                input_tokens = usage.get("input_tokens", input_tokens)
                output_tokens = usage.get("output_tokens", output_tokens)
            elif kind == "message_stop":
                usage = Usage(input_tokens, output_tokens) if input_tokens is not None and output_tokens is not None else None
                if reason is None:
                    raise self.ended_early(usage)
                yield Done(FINISH.get(reason, Finish.OTHER), usage, reason)
                return
        raise self.ended_early()
