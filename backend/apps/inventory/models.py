from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.accounts.models import Store


class Category(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default="#2563eb")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["store", "name"], name="unique_category_per_store")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="suppliers")
    name = models.CharField(max_length=160)
    contact_person = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    lead_time_days = models.PositiveIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["store", "name"], name="unique_supplier_per_store")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    PIECE = "piece"
    KG = "kg"
    LITRE = "litre"
    PACKET = "packet"
    UNIT_CHOICES = [
        (PIECE, "Piece"),
        (KG, "Kg"),
        (LITRE, "Litre"),
        (PACKET, "Packet"),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    supplier = models.ForeignKey(Supplier, null=True, blank=True, on_delete=models.SET_NULL, related_name="products")
    name = models.CharField(max_length=180)
    sku = models.CharField(max_length=64)
    barcode = models.CharField(max_length=80, blank=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default=PIECE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=10)
    reorder_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=25)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_sold_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["store", "sku"], name="unique_sku_per_store"),
            models.CheckConstraint(condition=models.Q(selling_price__gte=0), name="product_selling_price_positive"),
            models.CheckConstraint(condition=models.Q(purchase_price__gte=0), name="product_purchase_price_positive"),
        ]
        ordering = ["name"]
        indexes = [
            models.Index(fields=["store", "sku"]),
            models.Index(fields=["store", "is_active"]),
            models.Index(fields=["store", "expiry_date"]),
        ]

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    @property
    def profit_margin_percent(self):
        if not self.selling_price:
            return Decimal("0.00")
        return ((self.selling_price - self.purchase_price) / self.selling_price) * Decimal("100")

    @property
    def stock_value(self):
        return self.quantity * self.purchase_price

    @property
    def days_until_expiry(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.localdate()).days

    def __str__(self):
        return f"{self.name} ({self.sku})"


class InventoryLog(models.Model):
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    EXPIRY = "expiry"
    OPENING = "opening"
    ACTION_CHOICES = [
        (PURCHASE, "Purchase"),
        (SALE, "Sale"),
        (ADJUSTMENT, "Adjustment"),
        (RETURN, "Return"),
        (EXPIRY, "Expiry"),
        (OPENING, "Opening"),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="inventory_logs")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory_logs")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity_change = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_after = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=120, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="inventory_logs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["store", "-created_at"]),
            models.Index(fields=["product", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.product} {self.action} {self.quantity_change}"
