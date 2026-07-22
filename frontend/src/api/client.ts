import axios from "axios";

export const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8080/api";

const client = axios.create({ baseURL: API_BASE });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("learnsphere_access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default client;
