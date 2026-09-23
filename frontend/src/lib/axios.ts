import axios, { isAxiosError } from "axios";

import { clearToken, getToken, setToken, tokenSchema } from "./auth-token";

declare module "axios" {
  interface InternalAxiosRequestConfig {
    _retried?: boolean;
  }
}

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

let refreshPromise: Promise<boolean> | null = null;

/**
 * Exchanges the httpOnly refresh cookie for a new access token. Concurrent
 * callers share one request, and a failed refresh clears the stored token.
 */
export const refreshAccessToken = (): Promise<boolean> => {
  refreshPromise ??= apiClient
    .post("/auth/refresh")
    .then((response) => {
      setToken(tokenSchema.parse(response.data).access_token);
      return true;
    })
    .catch(() => {
      clearToken();
      return false;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
};

// A 401 from these means bad credentials or an ended session, so refreshing
// would be wrong or loop.
const NO_REFRESH_URLS = ["/auth/login", "/auth/refresh"];

apiClient.interceptors.response.use(undefined, async (error: unknown) => {
  // The access token was rejected, so refresh it once and replay the request.
  // The request interceptor attaches the new token to the replay.
  if (
    isAxiosError(error) &&
    error.response?.status === 401 &&
    error.config &&
    !error.config._retried &&
    !NO_REFRESH_URLS.includes(error.config.url ?? "")
  ) {
    error.config._retried = true;
    if (await refreshAccessToken()) {
      return apiClient(error.config);
    }
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
