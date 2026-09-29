from django.test import TestCase, override_settings

from catalog.models import ModelOffering


class CatalogTests(TestCase):
    def test_seeded_models_match_proxy_docs(self):
        ids = dict(ModelOffering.objects.values_list("provider", "upstream_model"))
        self.assertEqual(
            ids,
            {
                "openai": "gpt-5.6-luna",
                "anthropic": "claude-haiku-4-5-20251001",
                "google": "gemini-3.8-flash",
            },
        )

    @override_settings(PROXY_KEYS={"openai": "k", "anthropic": "", "google": "k"})
    def test_only_configured_and_enabled_models_are_available(self):
        ModelOffering.objects.filter(provider="google").update(is_enabled=False)
        self.assertEqual(list(ModelOffering.available().values_list("provider", flat=True)), ["openai"])

    def test_display_name_names_the_interface(self):
        offering = ModelOffering.objects.get(provider="anthropic")
        self.assertEqual(offering.display_name, "Claude Haiku 4.5 · Anthropic interface")
