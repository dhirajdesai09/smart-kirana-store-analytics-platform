from django.contrib import admin

from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ("product_name_snapshot", "sku_snapshot", "line_total", "profit_amount")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "store", "grand_total", "payment_mode", "status", "sale_time")
    list_filter = ("payment_mode", "status")
    search_fields = ("invoice_number", "customer_name", "customer_phone", "store__name")
    inlines = [SaleItemInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("sale", "product_name_snapshot", "quantity", "unit_price", "line_total")
    search_fields = ("sale__invoice_number", "product_name_snapshot", "sku_snapshot")
