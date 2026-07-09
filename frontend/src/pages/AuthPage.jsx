import { BarChart3, Store } from "lucide-react";
import { useState } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext.jsx";

const emptyForm = {
  email: "",
  password: "",
  first_name: "",
  last_name: "",
  store_name: "",
  phone: "",
  city: "",
  state: ""
};

export default function AuthPage() {
  const { user, login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (user) {
    return <Navigate to="/" replace />;
  }

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      if (mode === "login") {
        await login(form.email, form.password);
      } else {
        await register(form);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Could not complete authentication.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <section className="auth-brand">
        <div className="brand-mark large">
          <Store size={28} />
        </div>
        <h1>StorePulse</h1>
        <p>Inventory, sales, forecasting, and daily business intelligence for neighborhood kirana stores.</p>
        <div className="auth-metrics">
          <div>
            <strong>Live POS</strong>
            <span>Invoices, GST fields, stock movement</span>
          </div>
          <div>
            <strong>Pandas BI</strong>
            <span>Trends, baskets, festivals, forecasts</span>
          </div>
        </div>
      </section>
      <section className="auth-panel">
        <div className="auth-tabs">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Register</button>
        </div>
        <div className="panel-heading">
          <BarChart3 size={22} />
          <div>
            <strong>{mode === "login" ? "Welcome back" : "Create your store"}</strong>
            <span>{mode === "login" ? "Use your owner or staff account" : "Owner account and store profile"}</span>
          </div>
        </div>
        {error ? <div className="error-banner">{error}</div> : null}
        <form onSubmit={submit} className="form-grid">
          <label>
            Email
            <input name="email" type="email" value={form.email} onChange={update} required />
          </label>
          <label>
            Password
            <input name="password" type="password" value={form.password} onChange={update} required minLength={8} />
          </label>
          {mode === "register" ? (
            <>
              <label>
                First name
                <input name="first_name" value={form.first_name} onChange={update} />
              </label>
              <label>
                Last name
                <input name="last_name" value={form.last_name} onChange={update} />
              </label>
              <label className="span-2">
                Store name
                <input name="store_name" value={form.store_name} onChange={update} required />
              </label>
              <label>
                Phone
                <input name="phone" value={form.phone} onChange={update} />
              </label>
              <label>
                City
                <input name="city" value={form.city} onChange={update} />
              </label>
              <label className="span-2">
                State
                <input name="state" value={form.state} onChange={update} />
              </label>
            </>
          ) : null}
          <button className="primary-button span-2" disabled={loading}>
            {loading ? "Please wait..." : mode === "login" ? "Login" : "Create account"}
          </button>
        </form>
        <small className="demo-note">Demo seed: owner@storepulse.local / Demo@12345</small>
      </section>
    </div>
  );
}
