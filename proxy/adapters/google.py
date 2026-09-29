from ..types import Done, Finish, TextDelta, Usage
from .base import Adapter, PreparedRequest, merge_consecutive

FINISH = {"STOP": Finish.COMPLETE, "MAX_TOKENS": Finish.LENGTH, "SAFETY": Finish.FILTERED}
ROLES = {"user": "user", "assistant": "model"}


class GeminiGenerateContent(Adapter):
    """POST /google/v1beta/models/<model>:streamGenerateContent?alt=sse.

    No terminal sentinel: the reply is complete only when the stream ends
    cleanly after a finish reason.
    """

    def build(self, *, model, messages, max_output_tokens, key, system=""):
        body = {
            "contents": [
                {"role": ROLES[m.role], "parts": [{"text": m.content}]} for m in merge_consecutive(messages)
            ],
            "generationConfig": {
                "maxOutputTokens": max_output_tokens,
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        return PreparedRequest(
            path=f"/google/v1beta/models/{model}:streamGenerateContent?alt=sse",
            headers={"x-goog-api-key": key},
            body=body,
        )

    def parse(self, events):
        usage, reason = None, None
        for event in events:
            payload = self.load(event)
            for candidate in payload.get("candidates") or []:
                for part in (candidate.get("content") or {}).get("parts") or []:
                    if part.get("text") and not part.get("thought"):
                        yield TextDelta(part["text"])
                if candidate.get("finishReason"):
                    reason = candidate["finishReason"]
            meta = payload.get("usageMetadata")
            if meta:
                output = meta.get("candidatesTokenCount", 0) + meta.get("thoughtsTokenCount", 0)
                usage = Usage(meta.get("promptTokenCount", 0), output)
        if reason is None:
            raise self.ended_early(usage)
        yield Done(FINISH.get(reason, Finish.OTHER), usage, reason)
