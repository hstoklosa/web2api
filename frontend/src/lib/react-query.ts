import { QueryClient } from "@tanstack/react-query";
import { isAxiosError } from "axios";

export const queryClient = new QueryClient({
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
