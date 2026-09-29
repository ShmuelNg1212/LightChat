from django.contrib import admin, messages

from billing.money import format_credits

from . import services
from .models import Conversation, Generation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Metadata only: message contents are private and not shown in the admin."""

    list_display = ("id", "owner", "created_at", "updated_at")
    search_fields = ("owner__username",)
    readonly_fields = ("owner", "created_at", "updated_at")
    exclude = ("title",)


@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):
    """Metering records. Reconcile replies whose usage is unknown with the actions."""

    list_display = ("id", "created_at", "user", "model_label", "status", "error_kind", "held", "charged_credits", "input_tokens", "output_tokens")
    list_filter = ("status", "provider", "error_kind")
    search_fields = ("user__username", "=id")
    actions = ["charge_held", "release_hold"]
    exclude = ("user_message", "assistant_message", "conversation")

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields if f.name not in self.exclude]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Held / reserved")
    def held(self, obj):
        return format_credits(obj.reserved)

    @admin.display(description="Charged")
    def charged_credits(self, obj):
        return format_credits(obj.charged)

    def _resolve(self, request, queryset, charge_held):
        done = sum(services.resolve(g.pk, charge_held=charge_held) for g in queryset)
        skipped = queryset.count() - done
        messages.info(request, f"Resolved {done} reply(ies); skipped {skipped} not awaiting review.")

    @admin.action(description="Reconcile: charge the held amount")
    def charge_held(self, request, queryset):
        self._resolve(request, queryset, True)

    @admin.action(description="Reconcile: release the hold (not charged)")
    def release_hold(self, request, queryset):
        self._resolve(request, queryset, False)
