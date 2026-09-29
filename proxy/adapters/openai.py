from ..types import Done, Finish, TextDelta, Usage
from .base import Adapter, PreparedRequest, merge_consecutive

FINISH = {"stop": Finish.COMPLETE, "length": Finish.LENGTH, "content_filter": Finish.FILTERED}


class OpenAIChatCompletions(Adapter):
    """POST /openai/v1/chat/completions, streamed. Terminal marker: data: [DONE]."""

    def build(self, *, model, messages, max_output_tokens, key, system=""):
        wire = [{"role": "system", "content": system}] if system else []
        wire += [{"role": m.role, "content": m.content} for m in merge_consecutive(messages)]
        return PreparedRequest(
            path="/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            body={
                "model": model,
                "messages": wire,
                "max_tokens": max_output_tokens,
                "reasoning_effort": "none",
                "stream": True,
                "stream_options": {"include_usage": True},
            },
        )

    def parse(self, events):
        usage, reason = None, None
        for event in events:
            if event.data.strip() == "[DONE]":
                if reason is None:
                    raise self.ended_early(usage)
                yield Done(FINISH.get(reason, Finish.OTHER), usage, reason)
                return
            chunk = self.load(event)
            if chunk.get("usage"):
                u = chunk["usage"]
                usage = Usage(u.get("prompt_tokens", 0), u.get("completion_tokens", 0))
            for choice in chunk.get("choices") or []:
                text = (choice.get("delta") or {}).get("content")
                if text:
                    yield TextDelta(text)
                if choice.get("finish_reason"):
                    reason = choice["finish_reason"]
        raise self.ended_early(usage)

