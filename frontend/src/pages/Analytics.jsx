import { Activity, CalendarDays, GitMerge, PackageSearch, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import api from "../api/client.js";
import EmptyState from "../components/EmptyState.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatusPill from "../components/StatusPill.jsx";
import { money } from "../utils/format.js";

export default function Analytics() {
  const [data, setData] = useState({ products: [], categories: [], baskets: [], forecast: [], festivals: [], trend: [] });
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState("week");

  useEffect(() => {
    Promise.all([
      api.get("/analytics/product-performance/"),
      api.get("/analytics/basket/"),
      api.get("/analytics/demand-forecast/"),
      api.get("/analytics/festivals/"),
      api.get(`/analytics/sales-trend/?period=${period}`)
    ])
      .then(([performance, basket, forecast, festival, trend]) => {
        setData({
          products: performance.data.products || [],
          categories: performance.data.categories || [],
          baskets: basket.data.rules || [],
          forecast: forecast.data || [],
          festivals: festival.data || [],
          trend: trend.data || []
        });
      })
      .finally(() => setLoading(false));
  }, [period]);

  if (loading) {
    return <div className="content-loader">Loading analytics...</div>;
  }

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Business intelligence"
        title="Analytics"
        actions={
          <div className="segmented">
            {["day", "week", "month"].map((item) => (
              <button key={item} className={period === item ? "active" : ""} onClick={() => setPeriod(item)}>{item}</button>
            ))}
          </div>
        }
      />
      <div className="analytics-grid">
        <article className="panel wide">
          <div className="panel-title">
            <h2>Revenue & Profit</h2>
            <TrendingUp size={18} />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="period" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => money(value)} />
              <Line dataKey="revenue" stroke="#0284c7" strokeWidth={2} dot={false} />
              <Line dataKey="profit" stroke="#16a34a" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </article>

        <article className="panel">
          <div className="panel-title">
            <h2>Category Mix</h2>
            <Activity size={18} />
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.categories}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="category" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => money(value)} />
              <Bar dataKey="revenue" fill="#0f766e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="panel">
          <div className="panel-title">
            <h2>Demand Forecast</h2>
            <PackageSearch size={18} />
          </div>
          <div className="insight-list">
            {data.forecast.slice(0, 6).map((item) => (
              <div className="insight-row" key={item.product_id}>
                <div>
                  <strong>{item.name}</strong>
                  <span>{item.current_stock} in stock</span>
                </div>
                <div>
                  <StatusPill tone={item.shortage_risk ? "red" : "green"}>
                    {item.next_week_demand}
                  </StatusPill>
                  <small>next week</small>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-title">
            <h2>Basket Analysis</h2>
            <GitMerge size={18} />
          </div>
          <div className="insight-list">
            {data.baskets.length ? data.baskets.map((rule) => (
              <div className="basket-rule" key={`${rule.antecedent}-${rule.consequent}`}>
                <strong>{rule.antecedent} + {rule.consequent}</strong>
                <span>{rule.confidence_percent}% confidence</span>
                <small>{rule.insight}</small>
              </div>
            )) : <EmptyState title="More invoices needed" detail="Product-pair rules appear after repeated baskets." />}
          </div>
        </article>

        <article className="panel wide">
          <div className="panel-title">
            <h2>Festival & Seasonal Spikes</h2>
            <CalendarDays size={18} />
          </div>
          <div className="festival-grid">
            {data.festivals.length ? data.festivals.map((festival) => (
              <div className="festival-card" key={`${festival.festival}-${festival.date}`}>
                <span>{festival.date}</span>
                <strong>{festival.festival}</strong>
                <b>{money(festival.revenue)}</b>
                <StatusPill tone={festival.daily_spike_percent > 0 ? "green" : "amber"}>
                  {festival.daily_spike_percent}% spike
                </StatusPill>
              </div>
            )) : <EmptyState title="No festival windows yet" detail="Festival comparison appears when sales overlap configured India festival periods." />}
          </div>
        </article>
      </div>
    </section>
  );
}
