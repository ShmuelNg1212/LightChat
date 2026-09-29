from .base import Adapter
from .openai import OpenAIChatCompletions

ADAPTERS: dict[str, type[Adapter]] = {
    "openai": OpenAIChatCompletions,
}


def adapter_for(provider: str) -> Adapter:
    return ADAPTERS[provider]()
