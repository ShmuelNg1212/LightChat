from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.test import TestCase

from billing import services
from billing.models import LedgerEntry
from billing.money import cost_for_tokens, credits, format_credits


class MoneyTests(TestCase):
    def test_credits_conversion(self):
        self.assertEqual(credits("1"), 1_000_000)
        self.assertEqual(credits("0.015"), 15_000)

    def test_cost_rounds_up(self):
        self.assertEqual(cost_for_tokens(1, 5_000_000), 5)
        self.assertEqual(cost_for_tokens(1, 1), 1)  # 1e-6 µcr rounds up, never free
        self.assertEqual(cost_for_tokens(0, 5_000_000), 0)

    def test_format(self):
        self.assertEqual(format_credits(1_234_500), "1.2345")
        self.assertEqual(format_credits(0), "0.0000")
        self.assertEqual(format_credits(12), "<0.0001")
        self.assertEqual(format_credits(12_000_000, 2), "12.00")


class ServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("ana", password="x")

    def assert_ledger_matches_wallet(self):
        wallet = services.get_wallet(self.user)
        totals = wallet.entries.aggregate(b=Sum("amount"), h=Sum("held_delta"))
        self.assertEqual(wallet.balance, totals["b"] or 0)
        self.assertEqual(wallet.held, totals["h"] or 0)

    def test_grant_hold_settle(self):
        services.grant(self.user, credits(1))
        services.hold(self.user, 300_000)
        wallet = services.get_wallet(self.user)
        self.assertEqual((wallet.balance, wallet.held, wallet.available), (1_000_000, 300_000, 700_000))

        entry = services.settle(self.user, held=300_000, charge=120_000)
        self.assertEqual(entry.kind, LedgerEntry.Kind.CHARGE)
        wallet.refresh_from_db()
        self.assertEqual((wallet.balance, wallet.held), (880_000, 0))
        self.assert_ledger_matches_wallet()

    def test_hold_cannot_exceed_available(self):
        services.grant(self.user, 500_000)
        services.hold(self.user, 400_000)
        with self.assertRaises(services.InsufficientCredit) as ctx:
            services.hold(self.user, 200_000)
        self.assertEqual(ctx.exception.available, 100_000)
        self.assertEqual(services.get_wallet(self.user).held, 400_000)
        self.assert_ledger_matches_wallet()

    def test_release(self):
        services.grant(self.user, 500_000)
        services.hold(self.user, 400_000)
        services.release(self.user, held=400_000)
        wallet = services.get_wallet(self.user)
        self.assertEqual((wallet.balance, wallet.held), (500_000, 0))
        self.assert_ledger_matches_wallet()

    def test_topup_respects_cap(self):
        services.grant(self.user, credits(4))
        self.assertIsNotNone(services.topup(self.user, credits(1), max_available=credits(5)))
        self.assertIsNone(services.topup(self.user, credits(1), max_available=credits(5)))
        self.assertEqual(services.get_wallet(self.user).balance, credits(5))

    def test_ledger_records_snapshots(self):
        services.grant(self.user, 1_000)
        entry = services.hold(self.user, 400)
        self.assertEqual((entry.balance_after, entry.held_after, entry.available_after), (1_000, 400, 600))
