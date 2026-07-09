from django.conf import settings
from django.db import models

from apps.accounts.models import Store
from apps.inventory.models import Product


class Sale(models.Model):
    CASH = "cash"
    UPI = "upi"
    CARD = "card"
    CREDIT = "credit"
    MIXED = "mixed"
    PAYMENT_CHOICES = [
        (CASH, "Cash"),
        (UPI, "UPI"),
        (CARD, "Card"),
        (CREDIT, "Credit"),
        (MIXED, "Mixed"),
    ]

    DRAFT = "draft"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (COMPLETED, "Completed"),
        (REFUNDED, "Refunded"),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="sales")
    invoice_number = models.CharField(max_length=40)
    customer_name = models.CharField(max_length=160, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_gstin = models.CharField(max_length=20, blank=True)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=CASH)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=COMPLETED)
    sale_time = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sales",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["store", "invoice_number"], name="unique_invoice_per_store")]
        ordering = ["-sale_time"]
        indexes = [
            models.Index(fields=["store", "-sale_time"]),
            models.Index(fields=["store", "payment_mode"]),
            models.Index(fields=["store", "status"]),
        ]

    @property
    def profit_total(self):
        return sum(item.profit_amount for item in self.items.all())

    def __str__(self):
        return self.invoice_number


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sale_items")
    product_name_snapshot = models.CharField(max_length=180)
    sku_snapshot = models.CharField(max_length=64)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_price_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)
    profit_amount = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["sale"]),
        ]

    def __str__(self):
        return f"{self.product_name_snapshot} x {self.quantity}"
