from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Store

from .services import StoreAnalyticsEngine


class AnalyticsBaseView(APIView):
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
        if not value:
            return None
        return datetime.strptime(value, "%Y-%m-%d").date()

    def engine(self, request):
        store = self.get_store(request)
        start = self.parse_date(request.query_params.get("start"))
        end = self.parse_date(request.query_params.get("end"))
        return StoreAnalyticsEngine(store=store, start=start, end=end)


class DashboardSummaryView(AnalyticsBaseView):
    def get(self, request):
        return Response(self.engine(request).dashboard_summary())


class SalesTrendView(AnalyticsBaseView):
    def get(self, request):
        period = request.query_params.get("period", "day")
        return Response(self.engine(request).sales_trend(period=period))


class ProductPerformanceView(AnalyticsBaseView):
    def get(self, request):
        limit = int(request.query_params.get("limit", 20))
        engine = self.engine(request)
        return Response(
            {
                "products": engine.product_performance(limit=limit),
                "categories": engine.category_analysis(),
                "slow_moving": engine.slow_moving_products(limit=limit),
            }
        )


class BasketAnalysisView(AnalyticsBaseView):
    def get(self, request):
        return Response(self.engine(request).basket_analysis(limit=int(request.query_params.get("limit", 10))))


class DemandForecastView(AnalyticsBaseView):
    def get(self, request):
        return Response(self.engine(request).demand_forecast(days=int(request.query_params.get("days", 7))))


class FestivalAnalyticsView(AnalyticsBaseView):
    def get(self, request):
        return Response(self.engine(request).festival_analytics())


class AlertsView(AnalyticsBaseView):
    def get(self, request):
        return Response(self.engine(request).alerts())
