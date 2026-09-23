import { MutationCache, QueryCache, QueryClient } from "@tanstack/react-query";
import { isAxiosError } from "axios";

import { userQueryKey } from "./auth";

// The response interceptor refreshes the session before a 401 gets this far,
// so any 401 that does means the session is over. Marking the user as signed
// out lets the app layout send them to the login page.
const endSessionOnUnauthorized = (error: Error): void => {
  if (isAxiosError(error) && error.response?.status === 401) {
    queryClient.setQueryData(userQueryKey, null);
  }
};

export const queryClient = new QueryClient({
  queryCache: new QueryCache({ onError: endSessionOnUnauthorized }),
  mutationCache: new MutationCache({ onError: endSessionOnUnauthorized }),
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      retry: (failureCount, error) => {
        // Client errors will not resolve themselves, so fail fast on them.
        if (isAxiosError(error) && error.response !== undefined) {
          if (error.response.status < 500) {
            return false;
          }
        }

        return failureCount < 2;
      },
    },
  },
});
