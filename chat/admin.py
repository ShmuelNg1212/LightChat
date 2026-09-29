from django.contrib import admin

from .models import Conversation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Metadata only: message contents are private and not shown in the admin."""

    list_display = ("id", "owner", "created_at", "updated_at")
    search_fields = ("owner__username",)
    readonly_fields = ("owner", "created_at", "updated_at")
    exclude = ("title",)
