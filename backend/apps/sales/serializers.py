from decimal import Decimal

from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from rest_framework import serializers

from apps.inventory.models import InventoryLog, Product

from .models import Sale, SaleItem


class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = SaleItem
        fields = [
            "id",
            "product",
            "product_name",
            "sku",
            "product_name_snapshot",
            "sku_snapshot",
            "quantity",
            "unit_price",
            "purchase_price_snapshot",
            "discount",
            "tax_rate",
            "tax_amount",
            "line_total",
            "profit_amount",
        ]
        read_only_fields = [
            "id",
            "product_name_snapshot",
            "sku_snapshot",
            "purchase_price_snapshot",
            "tax_amount",
            "line_total",
            "profit_amount",
        ]


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    item_count = serializers.IntegerField(read_only=True)
    profit_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id",
            "store",
            "invoice_number",
            "customer_name",
            "customer_phone",
            "customer_gstin",
            "payment_mode",
            "subtotal",
            "discount_total",
            "tax_total",
            "grand_total",
            "paid_amount",
            "balance_amount",
            "status",
            "sale_time",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "items",
            "item_count",
            "profit_total",
        ]
        read_only_fields = [
            "id",
            "invoice_number",
            "subtotal",
            "discount_total",
            "tax_total",
            "grand_total",
            "balance_amount",
            "created_by",
            "created_at",
            "updated_at",
            "item_count",
            "profit_total",
        ]
        extra_kwargs = {"sale_time": {"required": False}}

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("At least one product is required.")
        return items

    def validate(self, attrs):
        store = attrs.get("store") or getattr(self.instance, "store", None)
        if not store:
            request = self.context.get("request")
            profile = getattr(request.user, "profile", None) if request else None
            store = profile.default_store if profile and profile.default_store_id else None
        if not store:
            raise serializers.ValidationError({"store": "Select a store before creating a sale."})
        for item in attrs.get("items", []):
            product = item["product"]
            if product.store_id != store.id:
                raise serializers.ValidationError({"items": f"{product.name} does not belong to this store."})
            if attrs.get("status", Sale.COMPLETED) == Sale.COMPLETED and product.quantity < item["quantity"]:
                raise serializers.ValidationError({"items": f"Insufficient stock for {product.name}."})
        return attrs

    def _generate_invoice_number(self, store):
        today = timezone.localdate()
        prefix = f"SP-{today:%Y%m%d}"
        count = Sale.objects.filter(store=store, invoice_number__startswith=prefix).aggregate(count=Count("id"))[
            "count"
        ]
        return f"{prefix}-{count + 1:04d}"

    def _calculate_line(self, product, item):
        quantity = item["quantity"]
        unit_price = item.get("unit_price") or product.selling_price
        discount = item.get("discount") or Decimal("0")
        tax_rate = item.get("tax_rate")
        if tax_rate is None:
            tax_rate = product.tax_rate
        gross = quantity * unit_price
        taxable = max(gross - discount, Decimal("0"))
        tax_amount = taxable * tax_rate / Decimal("100")
        line_total = taxable + tax_amount
        profit_amount = (unit_price - product.purchase_price) * quantity - discount
        return {
            "unit_price": unit_price,
            "discount": discount,
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "line_total": line_total,
            "profit_amount": profit_amount,
        }

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        store = validated_data["store"]
        sale = Sale.objects.create(
            **validated_data,
            invoice_number=self._generate_invoice_number(store),
            created_by=self.context["request"].user,
        )
        subtotal = Decimal("0")
        discount_total = Decimal("0")
        tax_total = Decimal("0")
        grand_total = Decimal("0")
        for item_data in items_data:
            product = Product.objects.select_for_update().get(id=item_data["product"].id)
            calculated = self._calculate_line(product, item_data)
            subtotal += item_data["quantity"] * calculated["unit_price"]
            discount_total += calculated["discount"]
            tax_total += calculated["tax_amount"]
            grand_total += calculated["line_total"]
            SaleItem.objects.create(
                sale=sale,
                product=product,
                product_name_snapshot=product.name,
                sku_snapshot=product.sku,
                quantity=item_data["quantity"],
                unit_price=calculated["unit_price"],
                purchase_price_snapshot=product.purchase_price,
                discount=calculated["discount"],
                tax_rate=calculated["tax_rate"],
                tax_amount=calculated["tax_amount"],
                line_total=calculated["line_total"],
                profit_amount=calculated["profit_amount"],
            )
            if sale.status == Sale.COMPLETED:
                product.quantity = product.quantity - item_data["quantity"]
                product.last_sold_at = sale.sale_time
                product.save(update_fields=["quantity", "last_sold_at", "updated_at"])
                InventoryLog.objects.create(
                    store=store,
                    product=product,
                    action=InventoryLog.SALE,
                    quantity_change=-item_data["quantity"],
                    quantity_after=product.quantity,
                    reference=sale.invoice_number,
                    note="Sale checkout",
                    created_by=sale.created_by,
                )
        sale.subtotal = subtotal
        sale.discount_total = discount_total
        sale.tax_total = tax_total
        sale.grand_total = grand_total
        sale.balance_amount = sale.grand_total - sale.paid_amount
        sale.save(
            update_fields=[
                "subtotal",
                "discount_total",
                "tax_total",
                "grand_total",
                "balance_amount",
                "updated_at",
            ]
        )
        return sale

    @transaction.atomic
    def update(self, instance, validated_data):
        if "items" in validated_data:
            raise serializers.ValidationError({"items": "Editing sale line items is not supported. Refund and re-enter."})
        return super().update(instance, validated_data)
