from django.contrib import admin

from .models import LedgerEntry, Wallet


class LedgerEntryInline(admin.TabularInline):
    model = LedgerEntry
    fields = ("created_at", "kind", "amount", "held_delta", "balance_after", "held_after", "memo")
    readonly_fields = fields
    extra = 0
    can_delete = False
    ordering = ("-created_at", "-id")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "held", "updated_at")
    search_fields = ("user__username",)
    readonly_fields = ("user", "balance", "held", "updated_at")
    inlines = [LedgerEntryInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    """Read-only: the ledger is append-only. Corrections go through billing.services.adjust."""

    list_display = ("created_at", "wallet", "kind", "amount", "held_delta", "balance_after", "held_after", "memo")
    list_filter = ("kind",)
    search_fields = ("wallet__user__username", "memo")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
