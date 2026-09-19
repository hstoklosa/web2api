import { redirect, type MiddlewareFunction } from "react-router";

import { getUserQueryOptions } from "@/features/auth/api/get-user";
import { getToken } from "@/lib/auth-token";
import { queryClient } from "@/lib/react-query";

/**
 * Whether the stored token belongs to a live session. Served from the cache
 * while fresh and revalidated against /auth/me once stale, so an expired or
 * revoked token is caught within one staleTime. A rejected token has already
 * been cleared by the response interceptor by the time this returns false.
 */
const hasSession = async (): Promise<boolean> => {
  if (getToken() === null) {
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
