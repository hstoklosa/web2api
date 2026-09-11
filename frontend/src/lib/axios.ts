import axios, { isAxiosError } from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/v1",
  headers: {
    "Content-Type": "application/json",
  },
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
