import axios, { isAxiosError } from "axios";

declare module "axios" {
  interface InternalAxiosRequestConfig {
    _retried?: boolean;
  }
}

// The session lives in httpOnly cookies that the browser attaches to every
// same-origin request, so no token ever passes through this client.
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

let refreshPromise: Promise<boolean> | null = null;

/**
 * Exchanges the refresh cookie for a new access cookie. Concurrent callers
 * share one request, and the result says whether the session is still alive.
 */
const refreshSession = (): Promise<boolean> => {
  refreshPromise ??= apiClient
    .post("/auth/refresh")
    .then(() => true)
    .catch(() => false)
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
};

// A 401 from these means bad credentials or an ended session, so refreshing
// would be wrong or loop.
const NO_REFRESH_URLS = ["/auth/login", "/auth/refresh"];

apiClient.interceptors.response.use(undefined, async (error: unknown) => {
  // The access cookie was rejected or has expired, so refresh it once and
  // replay the request, which the browser sends with the new cookie.
  if (
    isAxiosError(error) &&
    error.response?.status === 401 &&
    error.config &&
    !error.config._retried &&
    !NO_REFRESH_URLS.includes(error.config.url ?? "")
  ) {
    error.config._retried = true;
    if (await refreshSession()) {
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
