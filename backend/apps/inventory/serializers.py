from django.db import transaction
from rest_framework import serializers

from .models import Category, InventoryLog, Product, Supplier


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "store", "name", "description", "color", "created_at"]
        read_only_fields = ["id", "created_at"]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id",
            "store",
            "name",
            "contact_person",
            "phone",
            "email",
            "address",
            "gstin",
            "lead_time_days",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    profit_margin_percent = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    stock_value = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    restock_recommendation = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "store",
            "category",
            "category_name",
            "supplier",
            "supplier_name",
            "name",
            "sku",
            "barcode",
            "unit",
            "quantity",
            "reorder_level",
            "reorder_quantity",
            "purchase_price",
            "selling_price",
            "tax_rate",
            "expiry_date",
            "is_active",
            "last_sold_at",
            "is_low_stock",
            "profit_margin_percent",
            "stock_value",
            "days_until_expiry",
            "restock_recommendation",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "last_sold_at", "created_at", "updated_at"]

    def validate(self, attrs):
        store = attrs.get("store") or getattr(self.instance, "store", None)
        category = attrs.get("category") or getattr(self.instance, "category", None)
        supplier = attrs.get("supplier") or getattr(self.instance, "supplier", None)
        if category and store and category.store_id != store.id:
            raise serializers.ValidationError({"category": "Category must belong to the product store."})
        if supplier and store and supplier.store_id != store.id:
            raise serializers.ValidationError({"supplier": "Supplier must belong to the product store."})
        return attrs

    def get_restock_recommendation(self, obj):
        if not obj.is_low_stock:
            return None
        recommended = max(obj.reorder_quantity, obj.reorder_level * 2 - obj.quantity)
        return {
            "recommended_quantity": recommended,
            "estimated_purchase_value": recommended * obj.purchase_price,
        }

    @transaction.atomic
    def create(self, validated_data):
        product = super().create(validated_data)
        InventoryLog.objects.create(
            store=product.store,
            product=product,
            action=InventoryLog.OPENING,
            quantity_change=product.quantity,
            quantity_after=product.quantity,
            reference="opening-stock",
            created_by=self.context["request"].user if self.context.get("request") else None,
        )
        return product


class InventoryLogSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = InventoryLog
        fields = [
            "id",
            "store",
            "product",
            "product_name",
            "sku",
            "action",
            "quantity_change",
            "quantity_after",
            "reference",
            "note",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "quantity_after", "created_by", "created_at"]

    def validate(self, attrs):
        product = attrs["product"]
        store = attrs.get("store") or product.store
        if product.store_id != store.id:
            raise serializers.ValidationError({"product": "Product must belong to this store."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        product = validated_data["product"]
        quantity_change = validated_data["quantity_change"]
        product.quantity = product.quantity + quantity_change
        if product.quantity < 0:
            raise serializers.ValidationError({"quantity_change": "Stock quantity cannot become negative."})
        product.save(update_fields=["quantity", "updated_at"])
        validated_data["store"] = product.store
        validated_data["quantity_after"] = product.quantity
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
