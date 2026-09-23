import { useMutation, type UseMutationOptions } from "@tanstack/react-query";
import * as z from "zod";

import { tokenSchema } from "@/lib/auth-token";
import { apiClient } from "@/lib/axios";

export const loginInputSchema = z.object({
  email: z.email("Enter a valid email address"),
  password: z.string().min(1, "Enter your password"),
});

export type LoginInput = z.infer<typeof loginInputSchema>;

export type Token = z.infer<typeof tokenSchema>;

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
