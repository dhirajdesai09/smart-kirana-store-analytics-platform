from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.views import MeView, PasswordResetRequestView, RegisterView, StaffViewSet, StoreViewSet
from apps.analytics_engine.views import AlertsView, BasketAnalysisView, DashboardSummaryView
from apps.analytics_engine.views import DemandForecastView, FestivalAnalyticsView, ProductPerformanceView
from apps.analytics_engine.views import SalesTrendView
from apps.inventory.views import CategoryViewSet, InventoryLogViewSet, ProductViewSet, SupplierViewSet
from apps.reports.views import AnalyticsReportViewSet, ExportReportView
from apps.sales.views import SaleViewSet


router = DefaultRouter()
router.register("stores", StoreViewSet, basename="store")
router.register("staff", StaffViewSet, basename="staff")
router.register("categories", CategoryViewSet, basename="category")
router.register("suppliers", SupplierViewSet, basename="supplier")
router.register("products", ProductViewSet, basename="product")
router.register("inventory-logs", InventoryLogViewSet, basename="inventory-log")
router.register("sales", SaleViewSet, basename="sale")
router.register("analytics-reports", AnalyticsReportViewSet, basename="analytics-report")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/me/", MeView.as_view(), name="me"),
    path("api/auth/password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("api/analytics/summary/", DashboardSummaryView.as_view(), name="analytics_summary"),
    path("api/analytics/sales-trend/", SalesTrendView.as_view(), name="sales_trend"),
    path("api/analytics/product-performance/", ProductPerformanceView.as_view(), name="product_performance"),
    path("api/analytics/basket/", BasketAnalysisView.as_view(), name="basket_analysis"),
    path("api/analytics/demand-forecast/", DemandForecastView.as_view(), name="demand_forecast"),
    path("api/analytics/festivals/", FestivalAnalyticsView.as_view(), name="festival_analytics"),
    path("api/analytics/alerts/", AlertsView.as_view(), name="alerts"),
    path("api/reports/export/", ExportReportView.as_view(), name="export_report"),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
