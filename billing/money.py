"""Credit amounts are integer micro-credits (µcr); these helpers convert for display."""

from decimal import ROUND_HALF_UP, Decimal

MICRO = 1_000_000


def credits(amount: int | float | str) -> int:
    """Whole or fractional credits → µcr, e.g. credits("1.5") == 1_500_000."""
    return int((Decimal(str(amount)) * MICRO).to_integral_value(ROUND_HALF_UP))


def format_credits(micro: int | None, places: int = 4) -> str:
    if micro is None:
        return "—"
    value = Decimal(micro) / MICRO
    quantum = Decimal(1).scaleb(-places)
    shown = value.quantize(quantum, ROUND_HALF_UP)
    if micro and shown == 0:
        smallest = f"{quantum:f}"
        return f"<{smallest}" if micro > 0 else f">-{smallest}"
    return f"{shown:,f}"


def cost_for_tokens(tokens: int, rate_per_million: int) -> int:
    """µcr cost of ``tokens`` at ``rate_per_million`` µcr per 1M tokens, rounded up."""
    return -(-tokens * rate_per_million // MICRO)
