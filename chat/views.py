import json

from django.contrib import messages
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST

from billing.money import format_credits
from billing.services import get_wallet
from catalog.models import ModelOffering

from . import services
from .forms import RenameForm
from .models import Conversation, Generation


def owned(request, pk) -> Conversation:
    """Every conversation lookup goes through here: other users' chats are a 404."""
    return get_object_or_404(Conversation, pk=pk, owner=request.user)


def sidebar_context(request, current=None):
    offerings = list(ModelOffering.available())
    for offering in offerings:
        # The smallest hold a reply can take with this model (a one-line prompt in a new chat).
        offering.min_hold = services.reservation_for(offering, [services.ProxyMessage("user", "")])
    selected = None
    if current is not None:
        last = current.generations.exclude(offering=None).order_by("-created_at").first()
        selected = last.offering_id if last else None
    if selected not in {o.pk for o in offerings}:
        selected = offerings[0].pk if offerings else None
    return {
        "conversations": Conversation.objects.filter(owner=request.user).only("id", "title", "updated_at")[:200],
        "current": current,
        "offerings": offerings,
        "selected_offering": selected,
    }


def home(request):
    return render(request, "chat/chat.html", sidebar_context(request))


def conversation(request, pk):
    convo = owned(request, pk)
    context = sidebar_context(request, convo)
    context["chat_messages"] = convo.messages.select_related("generation")
    latest = convo.messages.filter(role="user").last()
    context["latest_user_id"] = latest.pk if latest else None
    context["rename_form"] = RenameForm(instance=convo)
    return render(request, "chat/chat.html", context)


@require_POST
def rename(request, pk):
    convo = owned(request, pk)
    form = RenameForm(request.POST, instance=convo)
    if form.is_valid():
        form.save()
    else:
        messages.error(request, "Chat names can't be empty.")
    return redirect("conversation", pk=convo.pk)


def delete(request, pk):
    convo = owned(request, pk)
    if request.method == "POST":
        convo.delete()
        messages.success(request, "Chat deleted.")
        return redirect("home")
    return render(request, "chat/confirm_delete.html", {"convo": convo})


REJECTION_STATUS = {
    "insufficient_credit": 402,
    "duplicate": 409,
    "busy": 409,
    "not_found": 404,
    "model_unavailable": 400,
}


def _balance(user) -> dict:
    wallet = get_wallet(user)
    return {"available": format_credits(wallet.available), "held": format_credits(wallet.held) if wallet.held else ""}


def _ndjson(event: dict) -> bytes:
    return (json.dumps(event, separators=(",", ":")) + "\n").encode()


@require_POST
def send(request):
    """Start a reply and stream it as newline-delimited JSON events."""
    try:
        data = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        data = {}

    def int_or_none(value):
        try:
            return int(value) if value not in (None, "") else None
        except (TypeError, ValueError):
            return None

    try:
        started = services.start(
            request.user,
            prompt=str(data.get("prompt", "")),
            offering_slug=str(data.get("model", "")),
            client_request_id=str(data.get("request_id", "")),
            conversation_id=int_or_none(data.get("conversation")),
            retry_message_id=int_or_none(data.get("retry")),
        )
    except services.SendRejected as exc:
        body = {"error": {"code": exc.code, "message": exc.message}}
        if exc.code == "insufficient_credit":
            body["error"]["needed"] = format_credits(exc.extra["needed"])
            body["error"]["available"] = format_credits(max(exc.extra["available"], 0))
        if exc.code == "duplicate" and exc.extra.get("generation") and exc.extra["generation"].conversation_id:
            body["error"]["url"] = reverse("conversation", args=[exc.extra["generation"].conversation_id])
        return JsonResponse(body, status=REJECTION_STATUS.get(exc.code, 400))

    generation = started.generation
    convo = generation.conversation

    def events():
        yield _ndjson(
            {
                "type": "start",
                "generation": generation.pk,
                "cancel_url": reverse("cancel", args=[generation.pk]),
                "conversation": convo.pk,
                "url": reverse("conversation", args=[convo.pk]),
                "title": convo.display_title,
                "created": started.created_conversation,
                "user_message": generation.user_message_id,
                "reserved": format_credits(generation.reserved),
                **_balance(request.user),
                "header_html": render_to_string("chat/_header.html", {"current": convo}, request=request)
                if started.created_conversation
                else "",
            }
        )
        for kind, value in services.run(generation):
            if kind == "delta":
                yield _ndjson({"type": "delta", "text": value})
            else:
                yield _ndjson(
                    {
                        "type": "end",
                        "status": value.status,
                        "html": render_to_string(
                            "chat/_message.html",
                            {"m": value.assistant_message, "g": value, "latest_user_id": value.user_message_id},
                            request=request,
                        ),
                        **_balance(request.user),
                        "charged": format_credits(value.charged) if value.status == Generation.Status.COMPLETED else "",
                    }
                )

    response = StreamingHttpResponse(events(), content_type="application/x-ndjson")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@require_POST
def cancel(request, pk):
    services.request_cancel(request.user, pk)
    return HttpResponse(status=204)
