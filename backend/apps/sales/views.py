from django.db import models
from django.utils import timezone
from rest_framework import viewsets

from apps.common.permissions import IsStoreMember
from apps.common.viewsets import StoreScopedQuerySetMixin

from .models import Sale
from .serializers import SaleSerializer


class SaleViewSet(StoreScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [IsStoreMember]
    queryset = Sale.objects.select_related("store", "created_by").prefetch_related("items__product").all()
    filterset_fields = ["store", "payment_mode", "status"]
    search_fields = ["invoice_number", "customer_name", "customer_phone", "items__product_name_snapshot"]
    ordering_fields = ["sale_time", "grand_total", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if start:
            queryset = queryset.filter(sale_time__date__gte=start)
        if end:
            queryset = queryset.filter(sale_time__date__lte=end)
        return queryset.annotate(item_count=models.Count("items"))

    def perform_create(self, serializer):
        serializer.save(
            store=self.get_active_store(),
            sale_time=serializer.validated_data.get("sale_time") or timezone.now(),
        )
