from datetime import datetime
from io import BytesIO

import pandas as pd
from django.http import HttpResponse
from django.db.models import F
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Store
from apps.analytics_engine.services import StoreAnalyticsEngine
from apps.common.permissions import IsStoreMember
from apps.common.viewsets import StoreScopedQuerySetMixin
from apps.inventory.models import Product
from apps.sales.models import SaleItem

from .models import AnalyticsReport
from .serializers import AnalyticsReportSerializer


class AnalyticsReportViewSet(StoreScopedQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = AnalyticsReportSerializer
    permission_classes = [IsStoreMember]
    queryset = AnalyticsReport.objects.select_related("store", "generated_by").all()
    filterset_fields = ["store", "report_type"]
    search_fields = ["title"]
    ordering_fields = ["created_at", "period_start", "period_end"]

    def perform_create(self, serializer):
        serializer.save(
            store=self.get_active_store(),
            generated_by=self.request.user,
        )


class ExportReportView(APIView):
    def get_store(self, request):
        store_id = request.query_params.get("store")
        stores = Store.objects.filter(memberships__user=request.user, memberships__is_active=True)
        if request.user.is_staff:
            stores = Store.objects.all()
        if store_id:
            return stores.get(id=store_id)
        profile = getattr(request.user, "profile", None)
        if profile and profile.default_store_id:
            return profile.default_store
        return stores.first()

    def parse_date(self, value):
        return datetime.strptime(value, "%Y-%m-%d").date() if value else None

    def build_frame(self, store, report_type, start, end):
        engine = StoreAnalyticsEngine(store=store, start=start, end=end)
        if report_type == AnalyticsReport.INVENTORY:
            rows = Product.objects.filter(store=store).select_related("category", "supplier").annotate(
                category_name=F("category__name"),
                supplier_name=F("supplier__name"),
            ).values(
                "sku",
                "name",
                "category_name",
                "supplier_name",
                "quantity",
                "reorder_level",
                "purchase_price",
                "selling_price",
                "expiry_date",
            )
            return pd.DataFrame.from_records(rows).rename(
                columns={"category_name": "category", "supplier_name": "supplier"}
            )
        if report_type == AnalyticsReport.SUPPLIER:
            inventory = pd.DataFrame.from_records(
                Product.objects.filter(store=store).select_related("supplier").annotate(
                    supplier_name=F("supplier__name")
                ).values(
                    "supplier_name",
                    "quantity",
                    "purchase_price",
                    "selling_price",
                )
            )
            if inventory.empty:
                return inventory
            inventory["stock_value"] = inventory["quantity"].astype(float) * inventory["purchase_price"].astype(float)
            grouped = (
                inventory.groupby("supplier_name", dropna=False)
                .agg(product_count=("supplier_name", "count"), stock_value=("stock_value", "sum"))
                .reset_index()
            )
            return grouped.rename(columns={"supplier_name": "supplier"})
        if report_type == AnalyticsReport.PROFIT:
            return pd.DataFrame(engine.product_performance(limit=1000))
        rows = SaleItem.objects.filter(sale__store=store, sale__status="completed").select_related(
            "sale", "product", "product__category"
        )
        if start:
            rows = rows.filter(sale__sale_time__date__gte=start)
        if end:
            rows = rows.filter(sale__sale_time__date__lte=end)
        data = rows.annotate(
            invoice=F("sale__invoice_number"),
            sale_time_value=F("sale__sale_time"),
            payment_mode_value=F("sale__payment_mode"),
            product_value=F("product_name_snapshot"),
            category_name=F("product__category__name"),
        ).values(
            "invoice",
            "sale_time_value",
            "payment_mode_value",
            "sku_snapshot",
            "product_value",
            "category_name",
            "quantity",
            "unit_price",
            "discount",
            "tax_amount",
            "line_total",
            "profit_amount",
        )
        return pd.DataFrame.from_records(data).rename(
            columns={
                "sale_time_value": "sale_time",
                "payment_mode_value": "payment_mode",
                "sku_snapshot": "sku",
                "product_value": "product",
                "category_name": "category",
            }
        )

    def dataframe_response(self, frame, report_type, export_format):
        if frame.empty and not len(frame.columns):
            frame = pd.DataFrame([{"message": "No data available for the selected report."}])
        filename = f"storepulse-{report_type}-report"
        if export_format == "xlsx":
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                frame.to_excel(writer, sheet_name="Report", index=False)
            response = HttpResponse(
                output.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
            return response
        if export_format == "pdf":
            output = BytesIO()
            doc = SimpleDocTemplate(output, pagesize=A4)
            styles = getSampleStyleSheet()
            story = [Paragraph(f"StorePulse {report_type.title()} Report", styles["Title"]), Spacer(1, 12)]
            preview = frame.head(30).copy()
            table_data = [list(preview.columns)] + preview.astype(str).values.tolist()
            table = Table(table_data, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ]
                )
            )
            story.append(table)
            doc.build(story)
            response = HttpResponse(output.getvalue(), content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
            return response
        response = HttpResponse(frame.to_csv(index=False), content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
        return response

    def get(self, request):
        store = self.get_store(request)
        if not store:
            return Response({"detail": "No store found for this account."}, status=400)
        report_type = request.query_params.get("type", AnalyticsReport.SALES)
        export_format = request.query_params.get("format", "csv")
        start = self.parse_date(request.query_params.get("start"))
        end = self.parse_date(request.query_params.get("end"))
        frame = self.build_frame(store, report_type, start, end)
        AnalyticsReport.objects.create(
            store=store,
            report_type=report_type,
            title=f"{report_type.title()} report",
            period_start=start,
            period_end=end,
            metadata={"format": export_format, "rows": int(len(frame))},
            generated_by=request.user,
        )
        return self.dataframe_response(frame, report_type, export_format)
