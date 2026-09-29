"""Allow replies up to 25,000 output tokens (0.50 credits at 20.00 per 1M).

All three proxy interfaces accepted this limit when probed on 2026-09-29
(doc/wiki/external-dependencies.md).
"""

from django.db import migrations

SLUGS = ["gpt-5-6-luna", "claude-haiku-4-5", "gemini-3-8-flash"]


def raise_limit(apps, schema_editor):
    apps.get_model("catalog", "ModelOffering").objects.filter(slug__in=SLUGS).update(max_output_tokens=25_000)


def restore_limit(apps, schema_editor):
    apps.get_model("catalog", "ModelOffering").objects.filter(slug__in=SLUGS).update(max_output_tokens=2_048)


class Migration(migrations.Migration):
    dependencies = [("catalog", "0002_seed_proxy_models")]
    operations = [migrations.RunPython(raise_limit, restore_limit)]
