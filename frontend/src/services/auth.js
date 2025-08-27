// src/services/auth.js
import API from "./api";

export const login = async (credentials) => {
  const res = await API.post("/auth/login", credentials);
  return res.data;
};

export const register = async (userData) => {
  const res = await API.post("/auth/register", userData);
  return res.data;
};

export const getProfile = async () => {
  const res = await API.get("/users/me");
  return res.data;
};
