import importlib

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.test import TestCase

from billing import services

migration = importlib.import_module("billing.migrations.0002_raise_existing_to_five")


class RaiseExistingToFiveTests(TestCase):
    def test_tops_up_low_wallets_and_leaves_others(self):
        User = get_user_model()
        low = User.objects.create_user("low", password="x")
        services.grant(low, 919_795)
        services.hold(low, 100_000)  # held credit doesn't count as available
        rich = User.objects.create_user("rich", password="x")
        services.grant(rich, 7_000_000)

        migration.raise_to_five(apps, None)

        wallet = services.get_wallet(low)
        self.assertEqual(wallet.available, 5_000_000)
        entry = wallet.entries.first()
        self.assertEqual((entry.kind, entry.memo, entry.amount), ("grant", migration.MEMO, 5_000_000 - 819_795))
        totals = wallet.entries.aggregate(b=Sum("amount"), h=Sum("held_delta"))
        self.assertEqual((wallet.balance, wallet.held), (totals["b"], totals["h"]))
        self.assertEqual(services.get_wallet(rich).balance, 7_000_000)
        self.assertEqual(services.get_wallet(rich).entries.count(), 1)

    def test_running_twice_grants_once(self):
        user = get_user_model().objects.create_user("ana", password="x")
        services.grant(user, 1_000_000)
        migration.raise_to_five(apps, None)
        migration.raise_to_five(apps, None)
        self.assertEqual(services.get_wallet(user).balance, 5_000_000)
