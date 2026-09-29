from .anthropic import AnthropicMessages
from .base import Adapter
from .google import GeminiGenerateContent
from .openai import OpenAIChatCompletions

ADAPTERS: dict[str, type[Adapter]] = {
    "openai": OpenAIChatCompletions,
    "anthropic": AnthropicMessages,
    "google": GeminiGenerateContent,
}


def adapter_for(provider: str) -> Adapter:
    return ADAPTERS[provider]()
