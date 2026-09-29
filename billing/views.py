from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import services
from .money import format_credits


def credits_page(request):
    wallet = services.get_wallet(request.user)
    page = Paginator(wallet.entries.all(), 50).get_page(request.GET.get("page"))
    return render(
        request,
        "billing/credits.html",
        {
            "wallet": wallet,
            "page": page,
            "topup_amount": settings.TOPUP_AMOUNT_MICRO,
            "topup_max": settings.TOPUP_MAX_AVAILABLE_MICRO,
            "can_topup": wallet.available + settings.TOPUP_AMOUNT_MICRO <= settings.TOPUP_MAX_AVAILABLE_MICRO,
        },
    )


@require_POST
def topup(request):
    entry = services.topup(
        request.user,
        settings.TOPUP_AMOUNT_MICRO,
        max_available=settings.TOPUP_MAX_AVAILABLE_MICRO,
    )
    if entry:
        messages.success(request, f"Added {format_credits(settings.TOPUP_AMOUNT_MICRO, 2)} demo credits.")
    else:
        messages.warning(
            request,
            f"Demo top-ups stop at {format_credits(settings.TOPUP_MAX_AVAILABLE_MICRO, 2)} available credits.",
        )
    return redirect("credits")
