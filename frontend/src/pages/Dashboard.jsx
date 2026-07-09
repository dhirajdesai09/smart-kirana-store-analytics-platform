import { AlertTriangle, Boxes, IndianRupee, PackageCheck, Percent, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import api from "../api/client.js";
import EmptyState from "../components/EmptyState.jsx";
import MetricCard from "../components/MetricCard.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatusPill from "../components/StatusPill.jsx";
import { money, percent } from "../utils/format.js";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      api.get("/analytics/summary/"),
      api.get("/analytics/sales-trend/?period=day")
    ])
      .then(([summaryResponse, trendResponse]) => {
        setSummary(summaryResponse.data);
        setTrend(trendResponse.data.slice(-14));
      })
      .catch((err) => setError(err.response?.data?.detail || "Dashboard data is unavailable."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="content-loader">Loading dashboard...</div>;
  }

  if (error) {
    return <EmptyState title="Dashboard unavailable" detail={error} />;
  }

  const kpis = summary?.kpis || {};

  return (
    <section className="page-stack">
      <PageHeader eyebrow="Business overview" title="Dashboard" />
      <div className="metric-grid">
        <MetricCard icon={IndianRupee} tone="green" label="Total Revenue" value={money(kpis.total_revenue)} helper="All completed sales" />
        <MetricCard icon={TrendingUp} tone="blue" label="Daily Revenue" value={money(kpis.daily_revenue)} helper="Today" />
        <MetricCard icon={Percent} tone="amber" label="Gross Margin" value={percent(kpis.profit_margin_percent)} helper={money(kpis.gross_profit)} />
        <MetricCard icon={Boxes} tone="teal" label="Inventory Value" value={money(kpis.inventory_value)} helper={`${kpis.active_products || 0} active products`} />
      </div>

      <div className="dashboard-grid">
        <article className="panel wide">
          <div className="panel-title">
            <h2>Sales Trend</h2>
            <StatusPill tone="blue">14 days</StatusPill>
          </div>
          {trend.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={trend}>
                <defs>
                  <linearGradient id="revenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="period" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(value) => money(value)} />
                <Area type="monotone" dataKey="revenue" stroke="#0284c7" fill="url(#revenue)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState title="No sales yet" detail="Sales trend will appear after invoices are recorded." />
          )}
        </article>

        <article className="panel">
          <div className="panel-title">
            <h2>Alerts</h2>
            <AlertTriangle size={18} />
          </div>
          <div className="alert-list">
            {(summary.alerts || []).length ? summary.alerts.map((alert, index) => (
              <div className="alert-item" key={`${alert.type}-${index}`}>
                <StatusPill tone={alert.severity === "high" ? "red" : "amber"}>{alert.severity}</StatusPill>
                <div>
                  <strong>{alert.title}</strong>
                  <span>{alert.message}</span>
                </div>
              </div>
            )) : <EmptyState title="No alerts" detail="Critical stock and demand alerts will appear here." />}
          </div>
        </article>

        <article className="panel">
          <div className="panel-title">
            <h2>Top Products</h2>
            <PackageCheck size={18} />
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={summary.top_selling_products || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" hide />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => money(value)} />
              <Bar dataKey="revenue" fill="#16a34a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel wide">
          <div className="panel-title">
            <h2>Low Stock Products</h2>
            <StatusPill tone="red">{kpis.low_stock_count || 0} items</StatusPill>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>SKU</th>
                  <th>Category</th>
                  <th>Stock</th>
                  <th>Reorder</th>
                </tr>
              </thead>
              <tbody>
                {(summary.low_stock_products || []).map((product) => (
                  <tr key={product.product_id}>
                    <td>{product.name}</td>
                    <td>{product.sku}</td>
                    <td>{product.category}</td>
                    <td>{product.quantity}</td>
                    <td>{product.reorder_quantity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </div>
    </section>
  );
}
