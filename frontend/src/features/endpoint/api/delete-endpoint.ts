import {
  useMutation,
  useQueryClient,
  type UseMutationOptions,
} from "@tanstack/react-query";

import { apiClient } from "@/lib/axios";

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
    onSuccess: async (...args) => {
      const [, id] = args;
      // The endpoint's data can never be fetched again, so drop it outright.
      queryClient.removeQueries({ queryKey: [...endpointsQueryKey, id] });
      // Awaiting the refetch keeps the mutation pending until the endpoint
      // has left the list.
      await queryClient.invalidateQueries({
        queryKey: endpointsQueryKey,
        exact: true,
      });
      await onSuccess?.(...args);
    },
    ...options,
  });
};
