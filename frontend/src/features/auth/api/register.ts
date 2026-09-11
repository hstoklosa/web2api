import { useMutation, type UseMutationOptions } from "@tanstack/react-query";
import * as z from "zod";

import { apiClient } from "@/lib/axios";

export const registerInputSchema = z.object({
  email: z.email("Enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters long"),
});

export type RegisterInput = z.infer<typeof registerInputSchema>;

export const userSchema = z.object({
  id: z.number(),
  email: z.email(),
});

export type User = z.infer<typeof userSchema>;

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
