from django.contrib import admin

from .models import AnalyticsReport


@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(admin.ModelAdmin):
    list_display = ("title", "store", "report_type", "period_start", "period_end", "created_at")
    list_filter = ("report_type",)
    search_fields = ("title", "store__name")
