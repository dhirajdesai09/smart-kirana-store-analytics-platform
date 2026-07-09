import {
  BarChart3,
  Boxes,
  FileSpreadsheet,
  LayoutDashboard,
  LogOut,
  ReceiptText,
  Settings,
  Store
} from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../context/AuthContext.jsx";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/inventory", label: "Inventory", icon: Boxes },
  { to: "/sales", label: "Sales", icon: ReceiptText },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/reports", label: "Reports", icon: FileSpreadsheet },
  { to: "/settings", label: "Settings", icon: Settings }
];

export default function AppLayout() {
  const { user, stores, logout } = useAuth();
  const store = stores[0];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Store size={20} />
          </div>
          <div>
            <strong>StorePulse</strong>
            <span>{store?.name || "Kirana Analytics"}</span>
          </div>
        </div>
        <nav>
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === "/"}>
              <item.icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <button className="logout-button" onClick={logout}>
          <LogOut size={18} />
          <span>Sign out</span>
        </button>
      </aside>
      <main className="main">
        <header className="topbar">
          <div>
            <span className="muted">Today</span>
            <strong>{new Date().toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "short" })}</strong>
          </div>
          <div className="user-chip">
            <span>{user?.user?.name?.slice(0, 1) || "S"}</span>
            <div>
              <strong>{user?.user?.name || "Store owner"}</strong>
              <small>{user?.user?.email}</small>
            </div>
          </div>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
