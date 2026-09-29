"""Seed the three models documented by BUILD LLM Proxy (docs revision 2026-09-19).

Demo rates, identical because all three run DeepSeek Flash:
5.00 credits per 1M input tokens, 20.00 credits per 1M output tokens.
"""

from django.db import migrations

MODELS = [
    ("gpt-5-6-luna", "GPT-5.6 Luna", "openai", "gpt-5.6-luna", 10),
    ("claude-haiku-4-5", "Claude Haiku 4.5", "anthropic", "claude-haiku-4-5-20251001", 20),
    ("gemini-3-8-flash", "Gemini 3.8 Flash", "google", "gemini-3.8-flash", 30),
]


def seed(apps, schema_editor):
    ModelOffering = apps.get_model("catalog", "ModelOffering")
    for slug, label, provider, upstream, order in MODELS:
        ModelOffering.objects.update_or_create(
            slug=slug,
            defaults={
                "label": label,
                "provider": provider,
                "upstream_model": upstream,
                "input_rate": 5_000_000,
                "output_rate": 20_000_000,
                "max_output_tokens": 2048,
                "sort_order": order,
            },
        )


def unseed(apps, schema_editor):
    apps.get_model("catalog", "ModelOffering").objects.filter(slug__in=[m[0] for m in MODELS]).delete()


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
