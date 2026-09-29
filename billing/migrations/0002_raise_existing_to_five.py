"""One-time: bring every existing wallet up to 5.00 available credits.

Approved in doc/study/2026-09-29-1347-reply-limit-and-starting-credit.md.
Written as a normal ledger grant so balances still equal the ledger total.
Not reversed: credit already granted (and possibly spent) is not taken back.
"""

from django.db import migrations
from django.db.models import F

TARGET = 5_000_000  # µcr
MEMO = "Starting credit raised to 5.00"


def raise_to_five(apps, schema_editor):
    Wallet = apps.get_model("billing", "Wallet")
    LedgerEntry = apps.get_model("billing", "LedgerEntry")
    for wallet in Wallet.objects.all():
        missing = TARGET - (wallet.balance - wallet.held)
        if missing <= 0:
            continue
        Wallet.objects.filter(pk=wallet.pk).update(balance=F("balance") + missing)
        wallet.refresh_from_db()
        LedgerEntry.objects.create(
            wallet=wallet,
            kind="grant",
            amount=missing,
            held_delta=0,
            balance_after=wallet.balance,
            held_after=wallet.held,
            memo=MEMO,
        )


class Migration(migrations.Migration):
    dependencies = [("billing", "0001_initial")]
    operations = [migrations.RunPython(raise_to_five, migrations.RunPython.noop)]
