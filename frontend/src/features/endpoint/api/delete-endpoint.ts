import {
  useMutation,
  useQueryClient,
  type UseMutationOptions,
} from "@tanstack/react-query";

import { apiClient } from "@/lib/axios";

import type { Endpoint } from "./endpoint";
import { endpointsQueryKey } from "./get-endpoints";

export const deleteEndpoint = async (id: string): Promise<void> => {
  await apiClient.delete(`/endpoints/${id}`);
};

type UseDeleteEndpointOptions = Pick<
  UseMutationOptions<void, Error, string>,
  "onSuccess" | "onError"
>;

export const useDeleteEndpoint = ({
  onSuccess,
  ...options
}: UseDeleteEndpointOptions = {}) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteEndpoint,
    onSuccess: (...args) => {
      const [, id] = args;
      // Drop the endpoint from the cached list rather than refetching it, and
      // forget any data fetched from it, since neither can come back.
      queryClient.setQueryData<Endpoint[]>(endpointsQueryKey, (endpoints) =>
        endpoints?.filter((endpoint) => endpoint.id !== id),
      );
      queryClient.removeQueries({ queryKey: [...endpointsQueryKey, id] });
      return onSuccess?.(...args);
    },
    ...options,
  });
};
