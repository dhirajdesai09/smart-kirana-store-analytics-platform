from django.contrib import admin

from .models import Category, InventoryLog, Product, Supplier


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "color", "created_at")
    search_fields = ("name", "store__name")


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "phone", "lead_time_days")
    search_fields = ("name", "store__name", "phone")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "store", "category", "quantity", "reorder_level", "selling_price")
    list_filter = ("is_active", "unit", "category")
    search_fields = ("name", "sku", "barcode", "store__name")


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ("product", "action", "quantity_change", "quantity_after", "created_at")
    list_filter = ("action",)
    search_fields = ("product__name", "product__sku", "reference")
