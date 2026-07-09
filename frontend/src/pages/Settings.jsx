import { Save, UserPlus } from "lucide-react";
import { useEffect, useState } from "react";

import api from "../api/client.js";
import EmptyState from "../components/EmptyState.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatusPill from "../components/StatusPill.jsx";
import { useAuth } from "../context/AuthContext.jsx";

export default function Settings() {
  const { user, stores, reload } = useAuth();
  const store = stores[0];
  const [profile, setProfile] = useState({ phone: user?.phone || "", timezone: user?.timezone || "Asia/Kolkata" });
  const [staff, setStaff] = useState([]);
  const [staffForm, setStaffForm] = useState({ email: "", first_name: "", last_name: "", role: "cashier", password: "" });
  const [message, setMessage] = useState("");

  const loadStaff = () => {
    api.get("/staff/?page_size=50").then(({ data }) => setStaff(data.results || data));
  };

  useEffect(loadStaff, []);

  const saveProfile = async (event) => {
    event.preventDefault();
    await api.patch("/auth/me/", profile);
    await reload();
    setMessage("Profile updated.");
  };

  const addStaff = async (event) => {
    event.preventDefault();
    await api.post("/staff/", { ...staffForm, store: store?.id });
    setStaffForm({ email: "", first_name: "", last_name: "", role: "cashier", password: "" });
    setMessage("Staff member added.");
    loadStaff();
  };

  return (
    <section className="page-stack">
      <PageHeader eyebrow="Workspace" title="Settings" />
      {message ? <div className="success-banner">{message}</div> : null}
      <div className="settings-grid">
        <article className="panel">
          <div className="panel-title">
            <h2>Owner Profile</h2>
            <StatusPill tone="green">Active</StatusPill>
          </div>
          <form onSubmit={saveProfile} className="form-grid">
            <label className="span-2">
              Email
              <input value={user?.user?.email || ""} disabled />
            </label>
            <label>
              Phone
              <input value={profile.phone} onChange={(event) => setProfile({ ...profile, phone: event.target.value })} />
            </label>
            <label>
              Timezone
              <input value={profile.timezone} onChange={(event) => setProfile({ ...profile, timezone: event.target.value })} />
            </label>
            <button className="primary-button span-2">
              <Save size={17} />
              Save profile
            </button>
          </form>
        </article>

        <article className="panel">
          <div className="panel-title">
            <h2>Store</h2>
            <StatusPill tone="blue">{store?.city || "Primary"}</StatusPill>
          </div>
          {store ? (
            <div className="store-card">
              <strong>{store.name}</strong>
              <span>{store.business_type}</span>
              <span>{store.address || "Address not set"}</span>
              <span>{store.gstin || "GSTIN not set"}</span>
            </div>
          ) : <EmptyState title="No store" detail="Create a store from registration or API." />}
        </article>

        <article className="panel wide">
          <div className="panel-title">
            <h2>Staff Roles</h2>
            <UserPlus size={18} />
          </div>
          <form className="staff-form" onSubmit={addStaff}>
            <input placeholder="Email" type="email" value={staffForm.email} onChange={(event) => setStaffForm({ ...staffForm, email: event.target.value })} required />
            <input placeholder="First name" value={staffForm.first_name} onChange={(event) => setStaffForm({ ...staffForm, first_name: event.target.value })} />
            <input placeholder="Last name" value={staffForm.last_name} onChange={(event) => setStaffForm({ ...staffForm, last_name: event.target.value })} />
            <select value={staffForm.role} onChange={(event) => setStaffForm({ ...staffForm, role: event.target.value })}>
              <option value="cashier">Cashier</option>
              <option value="manager">Manager</option>
              <option value="analyst">Analyst</option>
            </select>
            <input placeholder="Initial password" type="password" value={staffForm.password} onChange={(event) => setStaffForm({ ...staffForm, password: event.target.value })} />
            <button className="primary-button">Add</button>
          </form>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {staff.map((member) => (
                  <tr key={member.id}>
                    <td>{member.user?.name}</td>
                    <td>{member.user?.email}</td>
                    <td>{member.role}</td>
                    <td><StatusPill tone={member.is_active ? "green" : "red"}>{member.is_active ? "Active" : "Inactive"}</StatusPill></td>
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
