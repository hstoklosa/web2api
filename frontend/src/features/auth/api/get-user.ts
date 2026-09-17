import { queryOptions, useQuery } from "@tanstack/react-query";

import { getToken } from "@/lib/auth-token";
import { apiClient } from "@/lib/axios";

import { userSchema, type User } from "./user";

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
    // A rejected token is final; the response interceptor has already
    // cleared it, so retrying would only repeat the failure.
    retry: false,
  });
};

export const useUser = () => {
  return useQuery(getUserQueryOptions());
};
