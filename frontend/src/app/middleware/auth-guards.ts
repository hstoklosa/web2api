import { redirect, type MiddlewareFunction } from "react-router";

import { getUserQueryOptions } from "@/lib/auth";
import { getToken } from "@/lib/auth-token";
import { refreshAccessToken } from "@/lib/axios";
import { queryClient } from "@/lib/react-query";

/**
 * Whether the user has a live session. Without a stored token, the refresh
 * cookie may still restore one. The user is served from the cache while fresh
 * and revalidated against /auth/me once stale, where the response interceptor
 * refreshes an expired token before this gives up.
 */
const hasSession = async (): Promise<boolean> => {
  if (getToken() === null && !(await refreshAccessToken())) {
    return false;
  }

  try {
    await queryClient.query(getUserQueryOptions());
    return true;
  } catch {
    return false;
  }
};

/**
 * Blocks navigation into the authenticated app unless a valid session exists.
 * The current location is passed along so login can return the user to it.
 */
export const requireAuth: MiddlewareFunction = async ({ url }, next) => {
  if (!(await hasSession())) {
    const params = new URLSearchParams({ redirect: url.pathname + url.search });
    throw redirect(`/login?${params}`);
  }

  return next();
};

/**
 * Keeps logged-in users out of guest-only pages such as login and register.
 */
export const requireGuest: MiddlewareFunction = async (_, next) => {
  if (await hasSession()) {
    throw redirect("/dashboard");
  }

  return next();
};
