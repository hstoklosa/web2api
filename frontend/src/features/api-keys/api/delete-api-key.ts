import {
  useMutation,
  useQueryClient,
  type UseMutationOptions,
} from "@tanstack/react-query";

import { apiClient } from "@/lib/axios";

import { apiKeysQueryKey } from "./get-api-keys";

export const deleteApiKey = async (id: string): Promise<void> => {
  await apiClient.delete(`/api-keys/${id}`);
};

type UseDeleteApiKeyOptions = Pick<
  UseMutationOptions<void, Error, string>,
  "onSuccess" | "onError"
>;

export const useDeleteApiKey = ({
  onSuccess,
  ...options
}: UseDeleteApiKeyOptions = {}) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteApiKey,
    onSuccess: async (...args) => {
      // Awaiting the refetch keeps the mutation pending until the key has
      // left the list.
      await queryClient.invalidateQueries({ queryKey: apiKeysQueryKey });
      await onSuccess?.(...args);
    },
    ...options,
  });
};
