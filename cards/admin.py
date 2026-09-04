from django.contrib import admin

from cards.models import Card, StatusHistory


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("masked_number", "user", "network", "status", "created_at")
    list_filter = ("status", "network", "created_at")
    search_fields = ("user__username", "holder_name")
    readonly_fields = ("token", "last_four", "created_at", "updated_at")

    @admin.display(description="Número")
    def masked_number(self, obj):
        return obj.masked_number


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("card", "status", "created_at")
    list_filter = ("status", "created_at")
    readonly_fields = ("card", "status", "created_at")

    def has_add_permission(self, request):
        return False
