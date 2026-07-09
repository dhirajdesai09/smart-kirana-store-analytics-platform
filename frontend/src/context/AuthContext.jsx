import { createContext, useContext, useEffect, useMemo, useState } from "react";

import api from "../api/client.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(Boolean(localStorage.getItem("storepulse_access")));

  const loadMe = async () => {
    const { data } = await api.get("/auth/me/");
    setUser(data.profile);
    setStores(data.stores || []);
    return data;
  };

  useEffect(() => {
    if (!localStorage.getItem("storepulse_access")) {
      setLoading(false);
      return;
    }
    loadMe().catch(() => {
      localStorage.removeItem("storepulse_access");
      localStorage.removeItem("storepulse_refresh");
    }).finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const { data } = await api.post("/auth/login/", { username: email, password });
    localStorage.setItem("storepulse_access", data.access);
    localStorage.setItem("storepulse_refresh", data.refresh);
    return loadMe();
  };

  const register = async (payload) => {
    await api.post("/auth/register/", payload);
    return login(payload.email, payload.password);
  };

  const logout = () => {
    localStorage.removeItem("storepulse_access");
    localStorage.removeItem("storepulse_refresh");
    setUser(null);
    setStores([]);
  };

  const value = useMemo(
    () => ({ user, stores, loading, login, register, logout, reload: loadMe }),
    [user, stores, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
