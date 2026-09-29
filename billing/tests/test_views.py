from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from billing import services
from billing.models import LedgerEntry


class SignupGrantTests(TestCase):
    def test_signup_grants_welcome_credits(self):
        self.client.post(
            reverse("signup"),
            {"username": "ana", "password1": "correct-horse-9", "password2": "correct-horse-9"},
        )
        user = get_user_model().objects.get(username="ana")
        wallet = services.get_wallet(user)
        self.assertEqual(wallet.balance, 1_000_000)
        self.assertEqual(wallet.entries.get().kind, LedgerEntry.Kind.GRANT)


@override_settings(TOPUP_AMOUNT_MICRO=1_000_000, TOPUP_MAX_AVAILABLE_MICRO=2_000_000)
class CreditsPageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("ana", password="x")
        services.grant(self.user, 500_000, memo="Welcome credits")
        self.client.force_login(self.user)

    def test_page_shows_balance_history_and_demo_label(self):
        response = self.client.get(reverse("credits"))
        self.assertContains(response, "Demo credits, not real money")
        self.assertContains(response, "0.5000")
        self.assertContains(response, "Welcome credits")

    def test_topup_adds_credit_until_cap(self):
        self.client.post(reverse("topup"))
        self.assertEqual(services.get_wallet(self.user).balance, 1_500_000)
        response = self.client.post(reverse("topup"), follow=True)
        self.assertContains(response, "Demo top-ups stop at")
        self.assertEqual(services.get_wallet(self.user).balance, 1_500_000)

    def test_topup_requires_post(self):
        self.assertEqual(self.client.get(reverse("topup")).status_code, 405)

    def test_balance_pill_in_header(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'id="balance-available">0.5000<')
