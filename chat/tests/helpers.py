import uuid

from django.contrib.auth import get_user_model
from django.test import override_settings

from billing import services as billing
from proxy.tests.helpers import FakeProxy, sse

KEYS = {"openai": "test-openai-key", "anthropic": "test-anthropic-key", "google": "test-google-key"}
keys = override_settings(PROXY_KEYS=KEYS, PROXY_BASE_URL="https://proxy.test")


def openai_reply(*texts, finish="stop", prompt_tokens=12, completion_tokens=8, done=True):
    events = [{"choices": [{"index": 0, "delta": {"content": t}, "finish_reason": None}]} for t in texts]
    if finish:
        events.append({"choices": [{"index": 0, "delta": {}, "finish_reason": finish}]})
        events.append({"choices": [], "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens}})
    if done:
        events.append("[DONE]")
    return sse(*events)


def anthropic_reply(text, input_tokens=30, output_tokens=5):
    events = [
        {"type": "message_start", "message": {"usage": {"input_tokens": input_tokens, "output_tokens": 0}}},
        {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": text}},
        {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": output_tokens}},
        {"type": "message_stop"},
    ]
    return sse(*events, event_names=[e["type"] for e in events])


def make_user(name="ana", credit=1_000_000):
    user = get_user_model().objects.create_user(name, password="correct-horse-9")
    if credit:
        billing.grant(user, credit)
    return user


def rid():
    return str(uuid.uuid4())


__all__ = ["FakeProxy", "keys", "openai_reply", "anthropic_reply", "make_user", "rid", "sse"]
