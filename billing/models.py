from django.conf import settings
from django.db import models
from django.db.models import Q


class Wallet(models.Model):
    """A user's demo-credit balance, in integer micro-credits (1 credit = 1,000,000).

    ``balance`` is settled credit. ``held`` is reserved for generations in flight.
    Spendable credit is ``balance - held``. Change these only through billing.services.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.BigIntegerField(default=0)
    held = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(held__gte=0), name="wallet_held_non_negative"),
        ]

    def __str__(self):
        return f"Wallet of {self.user}"

    @property
    def available(self):
        return self.balance - self.held


class LedgerEntry(models.Model):
    """Append-only record of every wallet change. Never updated or deleted."""

    class Kind(models.TextChoices):
        GRANT = "grant", "Sign-up grant"
        TOPUP = "topup", "Demo top-up"
        HOLD = "hold", "Hold"
        RELEASE = "release", "Hold released"
        CHARGE = "charge", "Charge"
        ADJUST = "adjust", "Adjustment"

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="entries")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    amount = models.BigIntegerField(default=0, help_text="Change to balance, µcr")
    held_delta = models.BigIntegerField(default=0, help_text="Change to held, µcr")
    balance_after = models.BigIntegerField()
    held_after = models.BigIntegerField()
    memo = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name_plural = "ledger entries"

    def __str__(self):
        return f"{self.get_kind_display()} {self.amount} µcr"

    @property
    def available_after(self):
        return self.balance_after - self.held_after
