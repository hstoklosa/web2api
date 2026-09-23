import {
  queryOptions,
  useMutation,
  useQuery,
  type UseMutationOptions,
} from "@tanstack/react-query";
import * as z from "zod";

import { clearToken, getToken, tokenSchema } from "./auth-token";
import { apiClient } from "./axios";

// The session is app-wide state that route guards, layouts, and features all
// read, so it lives here rather than in a feature.

export const userSchema = z.object({
  id: z.number(),
  email: z.email(),
});

export type User = z.infer<typeof userSchema>;

export type Token = z.infer<typeof tokenSchema>;

export const getUser = async (): Promise<User> => {
  const response = await apiClient.get("/auth/me");
  return userSchema.parse(response.data);
};

export const userQueryKey = ["auth", "user"] as const;

export const getUserQueryOptions = () => {
  return queryOptions({
    queryKey: userQueryKey,
    queryFn: getUser,
    // Without a token the request is a guaranteed 401, so don't make it.
    enabled: getToken() !== null,
    // The response interceptor has already tried to refresh the token, so a
    // 401 that reaches here is final and retrying would only repeat it.
    retry: false,
  });
};

export const useUser = () => {
  return useQuery(getUserQueryOptions());
};

export const loginInputSchema = z.object({
  email: z.email("Enter a valid email address"),
  password: z.string().min(1, "Enter your password"),
});

export type LoginInput = z.infer<typeof loginInputSchema>;

export const loginUser = async (input: LoginInput): Promise<Token> => {
  // The backend authenticates through OAuth2PasswordRequestForm, which expects
  // form-encoded `username` and `password` fields rather than JSON.
  const body = new URLSearchParams({
    username: input.email,
    password: input.password,
  });

  const response = await apiClient.post("/auth/login", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return tokenSchema.parse(response.data);
};

type UseLoginOptions = Pick<
  UseMutationOptions<Token, Error, LoginInput>,
  "onSuccess" | "onError"
>;

export const useLogin = (options?: UseLoginOptions) => {
  return useMutation({
    mutationFn: loginUser,
    ...options,
  });
};

export const registerInputSchema = z.object({
  email: z.email("Enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters long"),
});

export type RegisterInput = z.infer<typeof registerInputSchema>;

export const registerUser = async (input: RegisterInput): Promise<User> => {
  const response = await apiClient.post("/auth/register", input);
  return userSchema.parse(response.data);
};

type UseRegisterOptions = Pick<
  UseMutationOptions<User, Error, RegisterInput>,
  "onSuccess" | "onError"
>;

export const useRegister = (options?: UseRegisterOptions) => {
  return useMutation({
    mutationFn: registerUser,
    ...options,
  });
};

export const logoutUser = async (): Promise<void> => {
  // The backend clears the httpOnly refresh cookie, which only it can do. The
  // access token is dropped even if that request fails, so the user is always
  // signed out locally.
  try {
    await apiClient.post("/auth/logout");
  } finally {
    clearToken();
  }
};

type UseLogoutOptions = Pick<
  UseMutationOptions<void, Error, void>,
  "onSuccess" | "onError"
>;

export const useLogout = (options?: UseLogoutOptions) => {
  return useMutation({
    mutationFn: logoutUser,
    ...options,
  });
};
