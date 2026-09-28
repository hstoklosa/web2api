import {
  useMutation,
  useQueryClient,
  type UseMutationOptions,
} from "@tanstack/react-query";
import * as z from "zod";

import { apiClient } from "@/lib/axios";

import { createdApiKeySchema, type CreatedApiKey } from "./api-key";
import { apiKeysQueryKey } from "./get-api-keys";

export const createApiKeyInputSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "Name the key so you can tell it apart later")
    .max(100, "Keep the name under 100 characters"),
});

export type CreateApiKeyInput = z.infer<typeof createApiKeyInputSchema>;

export const createApiKey = async (
  input: CreateApiKeyInput,
): Promise<CreatedApiKey> => {
  const response = await apiClient.post("/api-keys", input);
  return createdApiKeySchema.parse(response.data);
};

type UseCreateApiKeyOptions = Pick<
  UseMutationOptions<CreatedApiKey, Error, CreateApiKeyInput>,
  "onSuccess" | "onError"
>;

export const useCreateApiKey = ({
  onSuccess,
  ...options
}: UseCreateApiKeyOptions = {}) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createApiKey,
    onSuccess: async (...args) => {
      // Awaiting the refetch keeps the mutation pending until the list shows
      // the new key.
      await queryClient.invalidateQueries({ queryKey: apiKeysQueryKey });
      await onSuccess?.(...args);
    },
    ...options,
  });
};
