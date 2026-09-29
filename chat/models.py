from django.conf import settings
from django.db import models

TITLE_LENGTH = 60


class Conversation(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations")
    title = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]
        indexes = [models.Index(fields=["owner", "-updated_at"])]

    def __str__(self):
        return self.display_title

    @property
    def display_title(self):
        return self.title or "New chat"

    @staticmethod
    def title_from(prompt: str) -> str:
        """A default title from the first prompt, without a paid model call."""
        text = " ".join(prompt.split())
        return text if len(text) <= TITLE_LENGTH else text[: TITLE_LENGTH - 1].rstrip() + "…"


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=16, choices=Role.choices)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"


class Generation(models.Model):
    """One metered request for an assistant reply.

    Holds the price snapshot and the credit reservation, so historical charges
    never change when rates do. Status moves:
    pending → streaming → completed | failed | needs_reconciliation → (reconciled)
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        STREAMING = "streaming", "Streaming"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed (not charged)"
        NEEDS_RECONCILIATION = "needs_reconciliation", "Needs reconciliation"
        RECONCILED = "reconciled", "Reconciled"

    ACTIVE = (Status.PENDING, Status.STREAMING)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="generations")
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, related_name="generations")
    client_request_id = models.UUIDField()
    user_message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, related_name="generations")
    assistant_message = models.OneToOneField(
        Message, on_delete=models.SET_NULL, null=True, blank=True, related_name="generation"
    )

    # Snapshot of the model and price at request time
    offering = models.ForeignKey("catalog.ModelOffering", on_delete=models.SET_NULL, null=True)
    model_label = models.CharField(max_length=120)
    provider = models.CharField(max_length=16)
    upstream_model = models.CharField(max_length=120)
    input_rate = models.PositiveBigIntegerField()
    output_rate = models.PositiveBigIntegerField()
    max_output_tokens = models.PositiveIntegerField()

    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING)
    finish_reason = models.CharField(max_length=16, blank=True)
    error_kind = models.CharField(max_length=32, blank=True)
    error_message = models.CharField(max_length=300, blank=True)
    upstream_status = models.PositiveSmallIntegerField(null=True, blank=True)
    cancel_requested = models.BooleanField(default=False)

    reserved = models.BigIntegerField(help_text="µcr held at start")
    charged = models.BigIntegerField(null=True, blank=True, help_text="µcr charged at settlement")
    input_tokens = models.PositiveIntegerField(null=True, blank=True)
    output_tokens = models.PositiveIntegerField(null=True, blank=True)
    overage = models.BooleanField(default=False, help_text="Charge exceeded the reservation")
    resolution = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["user", "client_request_id"], name="generation_unique_request"),
        ]
        indexes = [models.Index(fields=["status", "created_at"])]

    def __str__(self):
        return f"Generation {self.pk} ({self.status})"

    @property
    def is_active(self):
        return self.status in self.ACTIVE
