from collections import Counter
from datetime import date, datetime, timedelta
from decimal import Decimal
from itertools import combinations

import numpy as np
import pandas as pd
from django.db.models import F
from django.utils import timezone

from apps.inventory.models import Product
from apps.sales.models import Sale, SaleItem


def _money(value):
    if pd.isna(value):
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return round(float(value), 2)


def _number(value):
    if pd.isna(value):
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    return value


class StoreAnalyticsEngine:
    def __init__(self, store, start=None, end=None):
        self.store = store
        self.start = start
        self.end = end

    def _date_filter(self, queryset, field_name):
        if self.start:
            queryset = queryset.filter(**{f"{field_name}__date__gte": self.start})
        if self.end:
            queryset = queryset.filter(**{f"{field_name}__date__lte": self.end})
        return queryset

    def sales_frame(self):
        queryset = SaleItem.objects.filter(
            sale__store=self.store,
            sale__status=Sale.COMPLETED,
        ).select_related("sale", "product", "product__category")
        queryset = self._date_filter(queryset, "sale__sale_time")
        rows = queryset.annotate(category_name=F("product__category__name")).values(
            "sale_id",
            "sale__invoice_number",
            "sale__sale_time",
            "sale__payment_mode",
            "product_id",
            "product_name_snapshot",
            "sku_snapshot",
            "category_name",
            "quantity",
            "unit_price",
            "purchase_price_snapshot",
            "discount",
            "tax_amount",
            "line_total",
            "profit_amount",
        )
        frame = pd.DataFrame.from_records(rows)
        if frame.empty:
            return pd.DataFrame(
                columns=[
                    "sale_id",
                    "sale__invoice_number",
                    "sale__sale_time",
                    "sale__payment_mode",
                    "product_id",
                    "product_name_snapshot",
                    "sku_snapshot",
                    "category_name",
                    "quantity",
                    "unit_price",
                    "purchase_price_snapshot",
                    "discount",
                    "tax_amount",
                    "line_total",
                    "profit_amount",
                ]
            )
        decimal_columns = [
            "quantity",
            "unit_price",
            "purchase_price_snapshot",
            "discount",
            "tax_amount",
            "line_total",
            "profit_amount",
        ]
        for column in decimal_columns:
            frame[column] = frame[column].astype(float)
        frame = frame.rename(columns={"category_name": "category"})
        frame["sale_time"] = pd.to_datetime(frame["sale__sale_time"], utc=True).dt.tz_convert(
            str(timezone.get_current_timezone())
        )
        frame["sale_date"] = frame["sale_time"].dt.date
        frame["sale_hour"] = frame["sale_time"].dt.hour
        frame["weekday"] = frame["sale_time"].dt.day_name()
        frame["month"] = frame["sale_time"].dt.tz_localize(None).dt.to_period("M").astype(str)
        return frame

    def products_frame(self):
        rows = Product.objects.filter(store=self.store, is_active=True).select_related("category", "supplier").values(
            "id",
            "name",
            "sku",
            "category__name",
            "supplier__name",
            "quantity",
            "reorder_level",
            "reorder_quantity",
            "purchase_price",
            "selling_price",
            "expiry_date",
            "last_sold_at",
        )
        frame = pd.DataFrame.from_records(rows)
        if frame.empty:
            return pd.DataFrame(
                columns=[
                    "id",
                    "name",
                    "sku",
                    "category__name",
                    "supplier__name",
                    "quantity",
                    "reorder_level",
                    "reorder_quantity",
                    "purchase_price",
                    "selling_price",
                    "expiry_date",
                    "last_sold_at",
                ]
            )
        for column in ["quantity", "reorder_level", "reorder_quantity", "purchase_price", "selling_price"]:
            frame[column] = frame[column].astype(float)
        return frame

    def dashboard_summary(self):
        sales = self.sales_frame()
        products = self.products_frame()
        today = timezone.localdate()
        month = today.strftime("%Y-%m")

        total_revenue = sales["line_total"].sum() if not sales.empty else 0
        daily_revenue = sales.loc[sales["sale_date"] == today, "line_total"].sum() if not sales.empty else 0
        monthly_revenue = sales.loc[sales["month"] == month, "line_total"].sum() if not sales.empty else 0
        gross_profit = sales["profit_amount"].sum() if not sales.empty else 0
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue else 0

        top_selling = self.product_performance(limit=5)
        low_stock = products.loc[products["quantity"] <= products["reorder_level"]] if not products.empty else products
        inventory_value = (
            (products["quantity"] * products["purchase_price"]).sum()
            if not products.empty
            else 0
        )
        slow_moving = self.slow_moving_products(limit=5)

        low_stock_records = []
        for _, row in low_stock.head(10).iterrows():
            low_stock_records.append(
                {
                    "product_id": int(row["id"]),
                    "name": row["name"],
                    "sku": row["sku"],
                    "category": row["category__name"],
                    "supplier": row["supplier__name"],
                    "quantity": _number(row["quantity"]),
                    "reorder_level": _number(row["reorder_level"]),
                    "reorder_quantity": _number(row["reorder_quantity"]),
                    "purchase_price": _money(row["purchase_price"]),
                    "selling_price": _money(row["selling_price"]),
                }
            )

        return {
            "kpis": {
                "total_revenue": _money(total_revenue),
                "daily_revenue": _money(daily_revenue),
                "monthly_revenue": _money(monthly_revenue),
                "gross_profit": _money(gross_profit),
                "profit_margin_percent": round(float(profit_margin), 2),
                "inventory_value": _money(inventory_value),
                "low_stock_count": int(len(low_stock)),
                "active_products": int(len(products)),
            },
            "top_selling_products": top_selling,
            "slow_moving_products": slow_moving,
            "low_stock_products": low_stock_records,
            "alerts": self.alerts(limit=5),
        }

    def sales_trend(self, period="day"):
        sales = self.sales_frame()
        if sales.empty:
            return []
        if period == "month":
            sales["bucket"] = sales["sale_time"].dt.to_period("M").astype(str)
        elif period == "week":
            sales["bucket"] = sales["sale_time"].dt.to_period("W").astype(str)
        elif period == "hour":
            sales["bucket"] = sales["sale_hour"].astype(str).str.zfill(2) + ":00"
        else:
            sales["bucket"] = sales["sale_date"].astype(str)
        grouped = (
            sales.groupby("bucket")
            .agg(revenue=("line_total", "sum"), profit=("profit_amount", "sum"), units=("quantity", "sum"))
            .reset_index()
            .sort_values("bucket")
        )
        return [
            {
                "period": row["bucket"],
                "revenue": _money(row["revenue"]),
                "profit": _money(row["profit"]),
                "units": _number(row["units"]),
            }
            for _, row in grouped.iterrows()
        ]

    def product_performance(self, limit=20):
        sales = self.sales_frame()
        products = self.products_frame()
        if sales.empty:
            return []
        performance = (
            sales.groupby(["product_id", "product_name_snapshot", "sku_snapshot", "category"])
            .agg(
                quantity_sold=("quantity", "sum"),
                revenue=("line_total", "sum"),
                profit=("profit_amount", "sum"),
                invoices=("sale_id", "nunique"),
            )
            .reset_index()
        )
        merged = performance.merge(
            products[["id", "quantity", "reorder_level", "selling_price", "purchase_price"]],
            left_on="product_id",
            right_on="id",
            how="left",
        )
        merged["margin_percent"] = np.where(
            merged["revenue"] > 0,
            (merged["profit"] / merged["revenue"]) * 100,
            0,
        )
        merged = merged.sort_values(["revenue", "quantity_sold"], ascending=False).head(limit)
        return [
            {
                "product_id": int(row["product_id"]),
                "name": row["product_name_snapshot"],
                "sku": row["sku_snapshot"],
                "category": row["category"],
                "quantity_sold": _number(row["quantity_sold"]),
                "revenue": _money(row["revenue"]),
                "profit": _money(row["profit"]),
                "margin_percent": round(float(row["margin_percent"]), 2),
                "invoices": int(row["invoices"]),
                "stock_on_hand": _number(row.get("quantity", 0)),
                "low_stock": bool(row.get("quantity", 0) <= row.get("reorder_level", 0)),
            }
            for _, row in merged.iterrows()
        ]

    def slow_moving_products(self, limit=10):
        products = self.products_frame()
        sales = self.sales_frame()
        if products.empty:
            return []
        if sales.empty:
            products["quantity_sold"] = 0
        else:
            sold = sales.groupby("product_id").agg(quantity_sold=("quantity", "sum")).reset_index()
            products = products.merge(sold, left_on="id", right_on="product_id", how="left")
            products["quantity_sold"] = products["quantity_sold"].fillna(0)
        products["stock_value"] = products["quantity"] * products["purchase_price"]
        result = products.sort_values(["quantity_sold", "stock_value"], ascending=[True, False]).head(limit)
        return [
            {
                "product_id": int(row["id"]),
                "name": row["name"],
                "sku": row["sku"],
                "category": row["category__name"],
                "quantity_sold": _number(row["quantity_sold"]),
                "stock_on_hand": _number(row["quantity"]),
                "stock_value": _money(row["stock_value"]),
            }
            for _, row in result.iterrows()
        ]

    def category_analysis(self):
        sales = self.sales_frame()
        if sales.empty:
            return []
        pivot = pd.pivot_table(
            sales,
            values=["line_total", "quantity", "profit_amount"],
            index="category",
            aggfunc={"line_total": "sum", "quantity": "sum", "profit_amount": "sum"},
        ).reset_index()
        pivot = pivot.sort_values("line_total", ascending=False)
        return [
            {
                "category": row["category"],
                "revenue": _money(row["line_total"]),
                "units": _number(row["quantity"]),
                "profit": _money(row["profit_amount"]),
            }
            for _, row in pivot.iterrows()
        ]

    def basket_analysis(self, limit=10):
        sales = self.sales_frame()
        if sales.empty:
            return {"rules": [], "message": "Not enough sales data for basket analysis."}
        baskets = sales.groupby("sale_id")["product_name_snapshot"].apply(lambda values: sorted(set(values))).tolist()
        pair_counter = Counter()
        product_counter = Counter()
        for basket in baskets:
            product_counter.update(basket)
            for pair in combinations(basket, 2):
                pair_counter[pair] += 1
        rules = []
        for (left, right), support_count in pair_counter.most_common(limit):
            left_confidence = support_count / product_counter[left] if product_counter[left] else 0
            right_confidence = support_count / product_counter[right] if product_counter[right] else 0
            rules.append(
                {
                    "antecedent": left,
                    "consequent": right,
                    "support_count": support_count,
                    "support_percent": round(support_count / len(baskets) * 100, 2),
                    "confidence_percent": round(max(left_confidence, right_confidence) * 100, 2),
                    "insight": f"Customers buying {left} also buy {right}.",
                }
            )
        return {"rules": rules, "transaction_count": len(baskets)}

    def demand_forecast(self, days=7):
        sales = self.sales_frame()
        products = self.products_frame()
        if products.empty:
            return []
        today = timezone.localdate()
        date_index = pd.date_range(today - timedelta(days=29), today, freq="D").date
        results = []
        for _, product in products.iterrows():
            product_sales = sales.loc[sales["product_id"] == product["id"]] if not sales.empty else pd.DataFrame()
            if product_sales.empty:
                daily = pd.Series(0, index=date_index)
            else:
                grouped = product_sales.groupby("sale_date")["quantity"].sum()
                daily = grouped.reindex(date_index, fill_value=0)
            last_week = daily.tail(7)
            trailing_month = daily.tail(30)
            avg_daily = float(last_week.mean())
            volatility = float(trailing_month.std()) if len(trailing_month) > 1 else 0.0
            trend = 0.0
            if trailing_month.sum() > 0 and len(trailing_month) >= 2:
                x = np.arange(len(trailing_month))
                trend = float(np.polyfit(x, trailing_month.values.astype(float), 1)[0])
            forecast = max(0.0, (avg_daily + max(trend, 0)) * days)
            stock_on_hand = float(product["quantity"])
            shortage_quantity = max(0.0, forecast - stock_on_hand)
            results.append(
                {
                    "product_id": int(product["id"]),
                    "name": product["name"],
                    "sku": product["sku"],
                    "category": product["category__name"],
                    "current_stock": round(stock_on_hand, 2),
                    "avg_daily_sales": round(avg_daily, 2),
                    "next_week_demand": round(float(np.ceil(forecast)), 2),
                    "recommended_restock": round(float(np.ceil(shortage_quantity + product["reorder_quantity"])), 2)
                    if shortage_quantity
                    else 0,
                    "shortage_risk": shortage_quantity > 0 or stock_on_hand <= product["reorder_level"],
                    "volatility": round(volatility, 2),
                }
            )
        return sorted(results, key=lambda item: (item["shortage_risk"], item["next_week_demand"]), reverse=True)

    def festival_analytics(self):
        festivals = [
            {"name": "New Year", "date": date(2026, 1, 1)},
            {"name": "Makar Sankranti", "date": date(2026, 1, 14)},
            {"name": "Holi", "date": date(2026, 3, 4)},
            {"name": "Eid", "date": date(2026, 3, 20)},
            {"name": "Raksha Bandhan", "date": date(2026, 8, 28)},
            {"name": "Diwali", "date": date(2026, 11, 8)},
            {"name": "New Year", "date": date(2025, 1, 1)},
            {"name": "Holi", "date": date(2025, 3, 14)},
            {"name": "Eid", "date": date(2025, 3, 31)},
            {"name": "Diwali", "date": date(2025, 10, 20)},
        ]
        sales = self.sales_frame()
        if sales.empty:
            return []
        output = []
        for festival in festivals:
            start = festival["date"] - timedelta(days=3)
            end = festival["date"] + timedelta(days=3)
            window = sales[(sales["sale_date"] >= start) & (sales["sale_date"] <= end)]
            if window.empty:
                continue
            category_mix = (
                window.groupby("category")
                .agg(revenue=("line_total", "sum"), units=("quantity", "sum"))
                .reset_index()
                .sort_values("revenue", ascending=False)
                .head(5)
            )
            baseline_start = start - timedelta(days=14)
            baseline_end = start - timedelta(days=1)
            baseline = sales[(sales["sale_date"] >= baseline_start) & (sales["sale_date"] <= baseline_end)]
            festival_revenue = window["line_total"].sum()
            baseline_daily = baseline["line_total"].sum() / max((baseline_end - baseline_start).days + 1, 1)
            festival_daily = festival_revenue / 7
            spike_percent = ((festival_daily - baseline_daily) / baseline_daily * 100) if baseline_daily else 0
            output.append(
                {
                    "festival": festival["name"],
                    "date": festival["date"].isoformat(),
                    "revenue": _money(festival_revenue),
                    "daily_spike_percent": round(float(spike_percent), 2),
                    "top_categories": [
                        {
                            "category": row["category"],
                            "revenue": _money(row["revenue"]),
                            "units": _number(row["units"]),
                        }
                        for _, row in category_mix.iterrows()
                    ],
                }
            )
        return output

    def alerts(self, limit=None):
        products = self.products_frame()
        alerts = []
        if not products.empty:
            low_stock = products.loc[products["quantity"] <= products["reorder_level"]].copy()
            low_stock["severity"] = np.where(low_stock["quantity"] <= low_stock["reorder_level"] / 2, "high", "medium")
            for _, row in low_stock.iterrows():
                alerts.append(
                    {
                        "type": "low_stock",
                        "severity": row["severity"],
                        "title": f"{row['name']} is low on stock",
                        "message": f"Only {row['quantity']} left. Suggested reorder: {row['reorder_quantity']}.",
                        "product_id": int(row["id"]),
                    }
                )
            expiring = products.dropna(subset=["expiry_date"]).copy()
            if not expiring.empty:
                expiring["days_until_expiry"] = expiring["expiry_date"].apply(lambda value: (value - timezone.localdate()).days)
                expiring = expiring[(expiring["days_until_expiry"] >= 0) & (expiring["days_until_expiry"] <= 30)]
                for _, row in expiring.iterrows():
                    alerts.append(
                        {
                            "type": "expiry",
                            "severity": "high" if row["days_until_expiry"] <= 7 else "medium",
                            "title": f"{row['name']} expires soon",
                            "message": f"Expiry in {row['days_until_expiry']} days.",
                            "product_id": int(row["id"]),
                        }
                    )
        sales = self.sales_frame()
        if not sales.empty:
            today = timezone.localdate()
            current = sales[(sales["sale_date"] >= today - timedelta(days=6)) & (sales["sale_date"] <= today)][
                "line_total"
            ].sum()
            previous = sales[
                (sales["sale_date"] >= today - timedelta(days=13)) & (sales["sale_date"] <= today - timedelta(days=7))
            ]["line_total"].sum()
            if previous and current < previous * 0.8:
                alerts.append(
                    {
                        "type": "revenue_drop",
                        "severity": "medium",
                        "title": "Revenue dipped this week",
                        "message": f"Last 7 days are {round((1 - current / previous) * 100, 1)}% below the prior week.",
                    }
                )
        for forecast in self.demand_forecast(days=7)[:5]:
            if forecast["shortage_risk"] and forecast["next_week_demand"] > 0:
                alerts.append(
                    {
                        "type": "demand",
                        "severity": "medium",
                        "title": f"Demand risk for {forecast['name']}",
                        "message": f"Expected demand is {forecast['next_week_demand']} next week.",
                        "product_id": forecast["product_id"],
                    }
                )
        severity_order = {"high": 0, "medium": 1, "low": 2}
        alerts = sorted(alerts, key=lambda item: severity_order.get(item.get("severity"), 3))
        return alerts[:limit] if limit else alerts
