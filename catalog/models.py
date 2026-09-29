from django.conf import settings
from django.db import models


class ModelOffering(models.Model):
    """A model users can pick, with its demo price.

    Every offering is reached through BUILD LLM Proxy, which answers all of them
    with DeepSeek Flash; ``provider`` names the API interface, not the real model.
    """

    class Provider(models.TextChoices):
        OPENAI = "openai", "OpenAI"
        ANTHROPIC = "anthropic", "Anthropic"
        GOOGLE = "google", "Google"

    slug = models.SlugField(unique=True)
    label = models.CharField(max_length=80)
    provider = models.CharField(max_length=16, choices=Provider.choices)
    upstream_model = models.CharField(max_length=120, help_text="Model ID sent to the proxy")
    input_rate = models.PositiveBigIntegerField(help_text="µcr per 1M input tokens")
    output_rate = models.PositiveBigIntegerField(help_text="µcr per 1M output tokens")
    max_output_tokens = models.PositiveIntegerField(default=2048)
    is_enabled = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "label"]

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return f"{self.label} · {self.get_provider_display()} interface"

    @property
    def is_configured(self):
        return bool(settings.PROXY_KEYS.get(self.provider))

    @property
    def is_available(self):
        return self.is_enabled and self.is_configured

    @classmethod
    def available(cls):
        """Offerings a user may select: enabled and with a proxy key configured."""
        configured = [p for p, key in settings.PROXY_KEYS.items() if key]
        return cls.objects.filter(is_enabled=True, provider__in=configured)
