import {
  queryOptions,
  useMutation,
  useQuery,
  useQueryClient,
  type QueryClient,
  type UseMutationOptions,
} from "@tanstack/react-query";
import { isAxiosError } from "axios";
import * as z from "zod";

import { apiClient } from "./axios";

// The session is app-wide state that route guards, layouts, and features all
// read, so it lives here rather than in a feature. The tokens sit in httpOnly
// cookies that scripts cannot read, so the cached current user is the only
// client-side record of the session: a user when signed in, null when not.

export const userSchema = z.object({
  id: z.number(),
  email: z.email(),
});

export type User = z.infer<typeof userSchema>;

export const getUser = async (): Promise<User | null> => {
  try {
    const response = await apiClient.get("/auth/me");
    return userSchema.parse(response.data);
  } catch (error) {
    // The response interceptor has already tried to refresh the session, so a
    // 401 that reaches here means there is none.
    if (isAxiosError(error) && error.response?.status === 401) {
      return null;
    }
    throw error;
  }
};

export const userQueryKey = ["auth", "user"] as const;

export const getUserQueryOptions = () => {
  return queryOptions({
    queryKey: userQueryKey,
    queryFn: getUser,
  });
};

export const useUser = () => {
  return useQuery(getUserQueryOptions());
};

/**
 * Starts the client side of a new session. Anything cached for a previous
 * user is dropped, and the user the API returned is cached so the route guards
 * don't have to ask for it again.
 */
const startSession = (queryClient: QueryClient, user: User): void => {
  queryClient.removeQueries();
  queryClient.setQueryData(userQueryKey, user);
};

export const loginInputSchema = z.object({
  email: z.email("Enter a valid email address"),
  password: z.string().min(1, "Enter your password"),
});

export type LoginInput = z.infer<typeof loginInputSchema>;

export const loginUser = async (input: LoginInput): Promise<User> => {
  const response = await apiClient.post("/auth/login", input);
  return userSchema.parse(response.data);
};

type UseLoginOptions = Pick<
  UseMutationOptions<User, Error, LoginInput>,
  "onSuccess" | "onError"
>;

export const useLogin = (options?: UseLoginOptions) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: loginUser,
    ...options,
    onSuccess: (...args) => {
      startSession(queryClient, args[0]);
      return options?.onSuccess?.(...args);
    },
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
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: registerUser,
    ...options,
    onSuccess: (...args) => {
      startSession(queryClient, args[0]);
      return options?.onSuccess?.(...args);
    },
  });
};

export const logoutUser = async (): Promise<void> => {
  // Only the backend can clear the httpOnly session cookies.
  await apiClient.post("/auth/logout");
};

type UseLogoutOptions = Pick<
  UseMutationOptions<void, Error, void>,
  "onSuccess" | "onError"
>;

export const useLogout = (options?: UseLogoutOptions) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: logoutUser,
    ...options,
    onSuccess: (...args) => {
      // The app layout redirects to login once the user is null. The previous
      // user's data is dropped when the next session starts, since clearing
      // it now would refetch the pages still mounted into 401s.
      queryClient.setQueryData(userQueryKey, null);
      return options?.onSuccess?.(...args);
    },
  });
};
