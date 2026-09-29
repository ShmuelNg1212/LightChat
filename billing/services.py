"""The only code allowed to change wallets.

Each operation is one short transaction built on a conditional UPDATE, so
concurrent requests (double clicks, several tabs) cannot overspend or
double-apply. Every change writes an append-only LedgerEntry.
"""

from django.db import transaction
from django.db.models import F, Q

from .models import LedgerEntry, Wallet


class InsufficientCredit(Exception):
    def __init__(self, needed: int, available: int):
        super().__init__(f"needed {needed} µcr, available {available} µcr")
        self.needed = needed
        self.available = available


def get_wallet(user) -> Wallet:
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


def _apply(user, kind, *, amount=0, held_delta=0, memo="", condition=None) -> LedgerEntry | None:
    """Apply a balance/held change atomically. Returns None if ``condition`` fails."""
    wallet = get_wallet(user)
    with transaction.atomic():
        qs = Wallet.objects.filter(pk=wallet.pk)
        if condition is not None:
            qs = qs.filter(condition)
        updated = qs.update(balance=F("balance") + amount, held=F("held") + held_delta)
        if not updated:
            return None
        wallet.refresh_from_db()
        return LedgerEntry.objects.create(
            wallet=wallet,
            kind=kind,
            amount=amount,
            held_delta=held_delta,
            balance_after=wallet.balance,
            held_after=wallet.held,
            memo=memo[:200],
        )


def grant(user, amount: int, *, kind=LedgerEntry.Kind.GRANT, memo="") -> LedgerEntry:
    if amount <= 0:
        raise ValueError("grant amount must be positive")
    return _apply(user, kind, amount=amount, memo=memo)


def topup(user, amount: int, *, max_available: int, memo="Demo top-up") -> LedgerEntry | None:
    """Add demo credit only if the result stays within ``max_available``."""
    if amount <= 0:
        raise ValueError("top-up amount must be positive")
    condition = Q(balance__lte=F("held") + (max_available - amount))
    return _apply(user, LedgerEntry.Kind.TOPUP, amount=amount, memo=memo, condition=condition)


def hold(user, amount: int, *, memo="") -> LedgerEntry:
    """Reserve ``amount`` of spendable credit, or raise InsufficientCredit."""
    if amount <= 0:
        raise ValueError("hold amount must be positive")
    entry = _apply(
        user,
        LedgerEntry.Kind.HOLD,
        held_delta=amount,
        memo=memo,
        condition=Q(balance__gte=F("held") + amount),
    )
    if entry is None:
        raise InsufficientCredit(amount, get_wallet(user).available)
    return entry


def settle(user, *, held: int, charge: int, memo="") -> LedgerEntry:
    """Release a hold of ``held`` and charge ``charge`` (which may exceed the hold)."""
    if held < 0 or charge < 0:
        raise ValueError("amounts must be non-negative")
    return _apply(user, LedgerEntry.Kind.CHARGE, amount=-charge, held_delta=-held, memo=memo)


def release(user, *, held: int, memo="") -> LedgerEntry:
    if held <= 0:
        raise ValueError("release amount must be positive")
    return _apply(user, LedgerEntry.Kind.RELEASE, held_delta=-held, memo=memo)


def adjust(user, amount: int, *, memo) -> LedgerEntry:
    """Admin correction to the settled balance (positive or negative)."""
    return _apply(user, LedgerEntry.Kind.ADJUST, amount=amount, memo=memo)
