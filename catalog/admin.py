from django.contrib import admin

from .models import ModelOffering


@admin.register(ModelOffering)
class ModelOfferingAdmin(admin.ModelAdmin):
    list_display = ("label", "provider", "upstream_model", "input_rate", "output_rate", "max_output_tokens", "is_enabled", "is_configured")
    list_editable = ("input_rate", "output_rate", "is_enabled")
    list_filter = ("provider", "is_enabled")

    @admin.display(boolean=True, description="Key configured")
    def is_configured(self, obj):
        return obj.is_configured
