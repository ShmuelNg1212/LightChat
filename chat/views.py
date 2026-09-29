from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RenameForm
from .models import Conversation


def owned(request, pk) -> Conversation:
    """Every conversation lookup goes through here: other users' chats are a 404."""
    return get_object_or_404(Conversation, pk=pk, owner=request.user)


def sidebar_context(request, current=None):
    return {
        "conversations": Conversation.objects.filter(owner=request.user).only("id", "title", "updated_at")[:200],
        "current": current,
    }


def home(request):
    return render(request, "chat/chat.html", sidebar_context(request))


def conversation(request, pk):
    convo = owned(request, pk)
    context = sidebar_context(request, convo)
    context["chat_messages"] = convo.messages.all()
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
