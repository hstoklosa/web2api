import { redirect, type MiddlewareFunction } from "react-router";

import { getUserQueryOptions } from "@/lib/auth";
import { queryClient } from "@/lib/react-query";

/**
 * Whether the user has a live session. The user is served from the cache while
 * fresh and revalidated against /auth/me once stale, where the response
 * interceptor refreshes an expired access cookie before this gives up.
 */
const hasSession = async (): Promise<boolean> => {
  try {
    return (await queryClient.query(getUserQueryOptions())) !== null;
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
