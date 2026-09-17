import axios, { isAxiosError } from "axios";

import { clearToken, getToken } from "./auth-token";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(undefined, (error: unknown) => {
  // The token was rejected (expired, invalid, or the user no longer exists),
  // so stop sending it. The error still propagates to the caller.
  if (isAxiosError(error) && error.response?.status === 401) {
    clearToken();
  }
  return Promise.reject(error);
});

export const getApiErrorMessage = (
  error: unknown,
  fallback = "Something went wrong, please try again.",
): string => {
  // Domain errors from the API respond with a string `detail`, while FastAPI's
  // own request validation responds with a list of issues.
  if (isAxiosError(error) && typeof error.response?.data?.detail === "string") {
    return error.response.data.detail;
  }

  return fallback;
};
