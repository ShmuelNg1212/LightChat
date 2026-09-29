from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from billing import services as billing
from chat import services
from chat.models import Generation

from .helpers import FakeProxy, keys, make_user, rid


@keys
class ReconciliationTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def unsettled(self):
        g = services.start(self.user, prompt="Hi", offering_slug="gpt-5-6-luna", client_request_id=rid()).generation
        with FakeProxy("bad gateway", status=502):
            list(services.run(g))
        g.refresh_from_db()
        self.assertEqual(g.status, Generation.Status.NEEDS_RECONCILIATION)
        return g

    def test_charge_held(self):
        g = self.unsettled()
        self.assertTrue(services.resolve(g.pk, charge_held=True))
        g.refresh_from_db()
        wallet = billing.get_wallet(self.user)
        self.assertEqual((g.status, g.charged), (Generation.Status.RECONCILED, g.reserved))
        self.assertEqual((wallet.balance, wallet.held), (1_000_000 - g.reserved, 0))

    def test_release(self):
        g = self.unsettled()
        self.assertTrue(services.resolve(g.pk, charge_held=False))
        wallet = billing.get_wallet(self.user)
        self.assertEqual((wallet.balance, wallet.held), (1_000_000, 0))

    def test_cannot_resolve_twice(self):
        g = self.unsettled()
        self.assertTrue(services.resolve(g.pk, charge_held=False))
        self.assertFalse(services.resolve(g.pk, charge_held=True))
        self.assertEqual(billing.get_wallet(self.user).balance, 1_000_000)

    def test_stale_active_generations_are_flagged(self):
        g = services.start(self.user, prompt="Hi", offering_slug="gpt-5-6-luna", client_request_id=rid()).generation
        Generation.objects.filter(pk=g.pk).update(created_at=timezone.now() - timedelta(minutes=30))
        out = StringIO()
        call_command("reconcile_stale_generations", stdout=out)
        self.assertIn("Flagged 1", out.getvalue())
        g.refresh_from_db()
        self.assertEqual((g.status, g.error_kind), (Generation.Status.NEEDS_RECONCILIATION, "stale"))
        self.assertEqual(billing.get_wallet(self.user).held, g.reserved)

    def test_admin_actions(self):
        g = self.unsettled()
        admin = get_user_model().objects.create_superuser("root", password="x")
        self.client.force_login(admin)
        changelist = reverse("admin:chat_generation_changelist")
        self.assertEqual(self.client.get(changelist).status_code, 200)
        self.client.post(changelist, {"action": "release_hold", "_selected_action": [g.pk]})
        g.refresh_from_db()
        self.assertEqual(g.status, Generation.Status.RECONCILED)

    def test_user_sees_review_outcome(self):
        g = self.unsettled()
        services.resolve(g.pk, charge_held=False)
        self.client.force_login(self.user)
        page = self.client.get(reverse("conversation", args=[g.conversation_id]))
        self.assertContains(page, "Not charged; the held credit was returned.")
