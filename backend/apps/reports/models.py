from django.conf import settings
from django.db import models

from apps.accounts.models import Store


class AnalyticsReport(models.Model):
    SALES = "sales"
    PROFIT = "profit"
    INVENTORY = "inventory"
    SUPPLIER = "supplier"
    MONTHLY = "monthly"
    REPORT_TYPES = [
        (SALES, "Sales"),
        (PROFIT, "Profit"),
        (INVENTORY, "Inventory"),
        (SUPPLIER, "Supplier"),
        (MONTHLY, "Monthly Analytics"),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="analytics_reports")
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    title = models.CharField(max_length=180)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to="reports/", blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generated_reports",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["store", "report_type", "-created_at"])]

    def __str__(self):
        return self.title
