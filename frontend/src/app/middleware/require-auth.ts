import { redirect, type MiddlewareFunction } from "react-router";

import { getUserQueryOptions } from "@/features/auth/api/get-user";
import { getToken } from "@/lib/auth-token";
import { queryClient } from "@/lib/react-query";

const loginRedirect = (url: URL) => {
  const params = new URLSearchParams({ redirect: url.pathname + url.search });
  return redirect(`/login?${params}`);
};

/**
 * Blocks navigation into the authenticated app unless a valid session exists.
 * The current location is passed along so login can return the user to it.
 */
export const requireAuth: MiddlewareFunction = async ({ url }, next) => {
  if (getToken() === null) {
    throw loginRedirect(url);
  }

  try {
    // Served from the cache while fresh and revalidated against /auth/me once
    // stale, so an expired or revoked token is caught within one staleTime.
    await queryClient.query(getUserQueryOptions());
  } catch {
    // The token was rejected and the response interceptor has cleared it.
    throw loginRedirect(url);
  }

  return next();
};
