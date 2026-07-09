import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

const api = axios.create({
  baseURL: API_URL,
  timeout: 20000,
  headers: {
    "Content-Type": "application/json"
  }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("storepulse_access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original?._retry) {
      original._retry = true;
      const refresh = localStorage.getItem("storepulse_refresh");
      if (refresh) {
        try {
          const { data } = await axios.post(`${API_URL}/auth/refresh/`, { refresh });
          localStorage.setItem("storepulse_access", data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch {
          localStorage.removeItem("storepulse_access");
          localStorage.removeItem("storepulse_refresh");
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
