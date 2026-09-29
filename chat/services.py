"""Metered reply lifecycle: validate → deduplicate → hold → stream → settle.

Money rules (see doc/study and doc/plan for litechat-core):
- Credit is held *before* calling the proxy, sized so the real cost cannot exceed it.
- Holds, charges and releases are short transactions; none spans the stream.
- Nothing is retried. A failure that may have been billed upstream keeps its
  hold and waits for reconciliation instead of being treated as free.
"""

import logging
import time
import uuid
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone

from billing import services as billing
from billing.money import cost_for_tokens
from catalog.models import ModelOffering
from proxy.client import stream_reply
from proxy.types import Cancelled, Done, Finish, Message as ProxyMessage, ProxyError, TextDelta

from .models import Conversation, Generation, Message

log = logging.getLogger("litechat.chat")

MAX_PROMPT_CHARS = 16_000
MAX_ACTIVE_PER_USER = 3
# The proxy adds a hidden prompt (~175 tokens observed); allow generously for it.
REQUEST_OVERHEAD_TOKENS = 1_024
PER_MESSAGE_OVERHEAD_TOKENS = 16
CANCEL_POLL_SECONDS = 0.5


class SendRejected(Exception):
    """The request was refused before any credit was held or any call made."""

    def __init__(self, code: str, message: str, **extra):
        super().__init__(message)
        self.code = code
        self.message = message
        self.extra = extra


@dataclass
class Started:
    generation: Generation
    created_conversation: bool


def input_token_bound(history: list[ProxyMessage]) -> int:
    """An upper bound on input tokens: a token is never shorter than one UTF-8 byte."""
    return REQUEST_OVERHEAD_TOKENS + sum(
        len(m.content.encode("utf-8")) + PER_MESSAGE_OVERHEAD_TOKENS for m in history
    )


def reservation_for(offering: ModelOffering, history: list[ProxyMessage]) -> int:
    return cost_for_tokens(input_token_bound(history), offering.input_rate) + cost_for_tokens(
        offering.max_output_tokens, offering.output_rate
    )


def charge_for(generation: Generation, input_tokens: int, output_tokens: int) -> int:
    return cost_for_tokens(input_tokens, generation.input_rate) + cost_for_tokens(
        output_tokens, generation.output_rate
    )


def history_for(conversation: Conversation, upto: Message) -> list[ProxyMessage]:
    """Earlier exchanges that completed, then the new user message.

    Failed or interrupted replies (and the prompts that got them) are left out,
    so the model only sees answers the user actually received in full.
    """
    history: list[ProxyMessage] = []
    completed = {
        g.user_message_id: g.assistant_message
        for g in conversation.generations.filter(status=Generation.Status.COMPLETED)
        .exclude(assistant_message=None)
        .select_related("assistant_message")
    }
    for message in conversation.messages.filter(role=Message.Role.USER, id__lt=upto.id):
        reply = completed.get(message.id)
        if reply is not None:
            history += [ProxyMessage("user", message.content), ProxyMessage("assistant", reply.content)]
    history.append(ProxyMessage("user", upto.content))
    return history


def start(
    user,
    *,
    prompt: str,
    offering_slug: str,
    client_request_id: str,
    conversation_id: int | None = None,
    retry_message_id: int | None = None,
) -> Started:
    """Validate the request and hold credit. Raises SendRejected; never calls the proxy."""
    try:
        request_id = uuid.UUID(str(client_request_id))
    except ValueError:
        raise SendRejected("bad_request", "The request was malformed. Reload the page and try again.")

    existing = Generation.objects.filter(user=user, client_request_id=request_id).first()
    if existing:
        raise SendRejected("duplicate", "This message was already sent.", generation=existing)

    offering = ModelOffering.available().filter(slug=offering_slug).first()
    if offering is None:
        raise SendRejected("model_unavailable", "That model isn't available. Choose another one.")

    try:
        with transaction.atomic():
            conversation = None
            if conversation_id is not None:
                conversation = Conversation.objects.filter(pk=conversation_id, owner=user).first()
                if conversation is None:
                    raise SendRejected("not_found", "That chat doesn't exist.")

            if retry_message_id is not None:
                if conversation is None:
                    raise SendRejected("bad_request", "Nothing to retry.")
                user_message = _retryable_message(conversation, retry_message_id)
            else:
                prompt = prompt.strip()
                if not prompt:
                    raise SendRejected("empty", "Type a message first.")
                if len(prompt) > MAX_PROMPT_CHARS:
                    raise SendRejected("too_long", f"Messages are limited to {MAX_PROMPT_CHARS:,} characters.")
                user_message = None

            active = Generation.objects.filter(user=user, status__in=Generation.ACTIVE)
            if conversation is not None and active.filter(conversation=conversation).exists():
                raise SendRejected("busy", "Wait for the current reply to finish, or stop it.")
            if active.count() >= MAX_ACTIVE_PER_USER:
                raise SendRejected("busy", "Too many replies in progress. Wait for one to finish.")

            created = conversation is None
            if created:
                conversation = Conversation.objects.create(owner=user, title=Conversation.title_from(prompt))
            if user_message is None:
                user_message = Message.objects.create(conversation=conversation, role=Message.Role.USER, content=prompt)

            history = history_for(conversation, user_message)
            reserved = reservation_for(offering, history)
            try:
                billing.hold(user, reserved, memo=f"Reply with {offering.label}")
            except billing.InsufficientCredit as exc:
                raise SendRejected(
                    "insufficient_credit",
                    "Not enough credit for this reply. Add demo credits to continue.",
                    needed=exc.needed,
                    available=exc.available,
                )

            assistant = Message.objects.create(conversation=conversation, role=Message.Role.ASSISTANT)
            generation = Generation.objects.create(
                user=user,
                conversation=conversation,
                client_request_id=request_id,
                user_message=user_message,
                assistant_message=assistant,
                offering=offering,
                model_label=offering.display_name,
                provider=offering.provider,
                upstream_model=offering.upstream_model,
                input_rate=offering.input_rate,
                output_rate=offering.output_rate,
                max_output_tokens=offering.max_output_tokens,
                reserved=reserved,
            )
            conversation.save(update_fields=["updated_at"])
    except IntegrityError:
        # Lost a race with an identical request (double click, two tabs).
        existing = Generation.objects.filter(user=user, client_request_id=request_id).first()
        raise SendRejected("duplicate", "This message was already sent.", generation=existing)

    log.info("generation %s held %s µcr", generation.pk, reserved)
    return Started(generation, created)


def _retryable_message(conversation: Conversation, message_id: int) -> Message:
    """Only the latest prompt can be retried, and only if its last reply failed."""
    message = conversation.messages.filter(pk=message_id, role=Message.Role.USER).first()
    latest = conversation.messages.filter(role=Message.Role.USER).last()
    if message is None or message != latest:
        raise SendRejected("bad_request", "Only the latest message can be retried.")
    last = message.generations.order_by("-created_at").first()
    if last is not None and last.status in (*Generation.ACTIVE, Generation.Status.COMPLETED):
        raise SendRejected("bad_request", "This message already has a reply.")
    # Replace the failed reply on screen; its Generation stays for the ledger.
    if last is not None and last.assistant_message_id:
        failed = last.assistant_message
        last.assistant_message = None
        last.save(update_fields=["assistant_message"])
        failed.delete()
    return message


def run(generation: Generation):
    """Stream the reply. Yields ("delta", text) items, then one ("end", generation).

    Always finalizes: if the caller stops iterating (browser disconnected),
    the generation is marked for reconciliation.
    """
    history = history_for(generation.conversation, generation.user_message)
    Generation.objects.filter(pk=generation.pk).update(status=Generation.Status.STREAMING)
    generation.status = Generation.Status.STREAMING
    parts: list[str] = []
    last_poll = 0.0

    def should_cancel() -> bool:
        nonlocal last_poll
        now = time.monotonic()
        if now - last_poll < CANCEL_POLL_SECONDS:
            return False
        last_poll = now
        return Generation.objects.filter(pk=generation.pk, cancel_requested=True).exists()

    finished = False
    try:
        for event in stream_reply(
            provider=generation.provider,
            model=generation.upstream_model,
            messages=history,
            max_output_tokens=generation.max_output_tokens,
            should_cancel=should_cancel,
        ):
            if isinstance(event, TextDelta):
                parts.append(event.text)
                yield ("delta", event.text)
            elif isinstance(event, Done):
                _complete(generation, "".join(parts), event)
                finished = True
    except ProxyError as exc:
        _fail(generation, "".join(parts), exc)
        finished = True
    except Cancelled:
        _unsettled(generation, "".join(parts), "cancelled", "You stopped this reply.")
        finished = True
    except GeneratorExit:
        _unsettled(generation, "".join(parts), "disconnected", "The page closed before the reply finished.")
        raise
    except Exception:
        log.exception("generation %s crashed", generation.pk)
        _unsettled(generation, "".join(parts), "server_error", "Something went wrong on our side.")
        finished = True
    finally:
        if not finished and generation.is_active:
            _unsettled(generation, "".join(parts), "interrupted", "The reply stopped before it finished.")
    yield ("end", generation)


def _save_text(generation: Generation, text: str):
    if generation.assistant_message_id:
        Message.objects.filter(pk=generation.assistant_message_id).update(content=text)
        generation.assistant_message.content = text


def _finalize(generation: Generation, **fields):
    fields.setdefault("finished_at", timezone.now())
    for name, value in fields.items():
        setattr(generation, name, value)
    generation.save(update_fields=list(fields))


def _complete(generation: Generation, text: str, done: Done):
    with transaction.atomic():
        _save_text(generation, text)
        if done.usage is None:
            _finalize(
                generation,
                status=Generation.Status.NEEDS_RECONCILIATION,
                finish_reason=done.finish,
                error_kind="no_usage",
                error_message="The reply finished but its usage wasn't reported, so its cost is under review.",
            )
            return
        charge = charge_for(generation, done.usage.input_tokens, done.usage.output_tokens)
        billing.settle(generation.user, held=generation.reserved, charge=charge, memo=f"Reply with {generation.model_label}")
        _finalize(
            generation,
            status=Generation.Status.COMPLETED,
            finish_reason=done.finish,
            input_tokens=done.usage.input_tokens,
            output_tokens=done.usage.output_tokens,
            charged=charge,
            overage=charge > generation.reserved,
        )
    if generation.overage:
        log.warning("generation %s charge %s exceeded hold %s", generation.pk, charge, generation.reserved)


def _fail(generation: Generation, text: str, exc: ProxyError):
    log.info("generation %s failed: %s status=%s", generation.pk, exc.kind, exc.status)
    if exc.nothing_generated:
        with transaction.atomic():
            _save_text(generation, text)
            billing.release(generation.user, held=generation.reserved, memo="Reply failed: not charged")
            _finalize(
                generation,
                status=Generation.Status.FAILED,
                error_kind=exc.kind,
                error_message=exc.message,
                upstream_status=exc.status,
                charged=0,
            )
    else:
        _unsettled(generation, text, exc.kind, exc.message, status=exc.status)


def _unsettled(generation: Generation, text: str, kind: str, message: str, status: int | None = None):
    """Usage is unknown: keep the hold until someone reconciles it."""
    with transaction.atomic():
        _save_text(generation, text)
        _finalize(
            generation,
            status=Generation.Status.NEEDS_RECONCILIATION,
            error_kind=kind,
            error_message=message,
            upstream_status=status,
        )


def request_cancel(user, generation_id: int) -> bool:
    return bool(
        Generation.objects.filter(pk=generation_id, user=user, status__in=Generation.ACTIVE).update(
            cancel_requested=True
        )
    )
