import * as z from "zod";

export const tokenSchema = z.object({
  access_token: z.string(),
  token_type: z.literal("bearer"),
});

const TOKEN_KEY = "web2api.access_token";

// localStorage can throw when storage is disabled or unavailable, in which
// case the app behaves as though the user is logged out.

export const getToken = (): string | null => {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
};

export const setToken = (token: string): void => {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // Ignore: the session simply won't persist.
  }
};

export const clearToken = (): void => {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    // Ignore: nothing was stored to begin with.
  }
};
