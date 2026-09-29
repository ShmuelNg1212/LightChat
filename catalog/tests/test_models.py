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


class ReplyLimitTests(TestCase):
    def test_all_models_allow_25000_output_tokens(self):
        self.assertEqual(set(ModelOffering.objects.values_list("max_output_tokens", flat=True)), {25_000})

    def test_reply_writing_is_capped_at_half_a_credit(self):
        from billing.money import cost_for_tokens

        for offering in ModelOffering.objects.all():
            self.assertEqual(cost_for_tokens(offering.max_output_tokens, offering.output_rate), 500_000)


class ExampleCostTests(TestCase):
    def test_example_uses_real_rates(self):
        offering = ModelOffering.objects.get(provider="openai")
        # 1,000 x 5 µcr + 500 x 20 µcr at the seeded demo rates
        self.assertEqual(offering.example_cost, 15_000)
        offering.output_rate = 40_000_000
        self.assertEqual(offering.example_cost, 25_000)
