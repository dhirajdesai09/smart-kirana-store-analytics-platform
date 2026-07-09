from django.db import models
from rest_framework import viewsets

from apps.common.permissions import IsStoreMember
from apps.common.viewsets import StoreScopedQuerySetMixin

from .models import Category, InventoryLog, Product, Supplier
from .serializers import CategorySerializer, InventoryLogSerializer, ProductSerializer, SupplierSerializer


class CategoryViewSet(StoreScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsStoreMember]
    queryset = Category.objects.select_related("store").all()
    filterset_fields = ["store"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]

    def perform_create(self, serializer):
        serializer.save(store=self.get_active_store())


class SupplierViewSet(StoreScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [IsStoreMember]
    queryset = Supplier.objects.select_related("store").all()
    filterset_fields = ["store", "lead_time_days"]
    search_fields = ["name", "phone", "email", "gstin"]
    ordering_fields = ["name", "lead_time_days", "created_at"]

    def perform_create(self, serializer):
        serializer.save(store=self.get_active_store())


class ProductViewSet(StoreScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsStoreMember]
    queryset = Product.objects.select_related("store", "category", "supplier").all()
    filterset_fields = ["store", "category", "supplier", "is_active", "unit"]
    search_fields = ["name", "sku", "barcode", "supplier__name", "category__name"]
    ordering_fields = [
        "name",
        "quantity",
        "reorder_level",
        "selling_price",
        "purchase_price",
        "expiry_date",
        "updated_at",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        low_stock = self.request.query_params.get("low_stock")
        expiring = self.request.query_params.get("expiring_days")
        if low_stock in {"true", "1", "yes"}:
            queryset = queryset.filter(quantity__lte=models.F("reorder_level"))
        if expiring:
            from django.utils import timezone
            from datetime import timedelta

            try:
                days = int(expiring)
            except ValueError:
                days = 30
            queryset = queryset.filter(expiry_date__lte=timezone.localdate() + timedelta(days=days))
        return queryset

    def perform_create(self, serializer):
        serializer.save(store=self.get_active_store())


class InventoryLogViewSet(StoreScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = InventoryLogSerializer
    permission_classes = [IsStoreMember]
    queryset = InventoryLog.objects.select_related("store", "product", "created_by").all()
    filterset_fields = ["store", "product", "action"]
    search_fields = ["product__name", "product__sku", "reference", "note"]
    ordering_fields = ["created_at", "quantity_change"]
