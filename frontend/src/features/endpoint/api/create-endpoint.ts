import {
  useMutation,
  useQueryClient,
  type UseMutationOptions,
} from "@tanstack/react-query";
import * as z from "zod";

import { apiClient } from "@/lib/axios";

import { endpointSchema, type Endpoint } from "./endpoint";
import { endpointsQueryKey } from "./get-endpoints";

export const createEndpointInputSchema = z.object({
  url: z.url("Enter a valid URL"),
  description: z.string().min(1, "Describe the data you want to extract"),
});

export type CreateEndpointInput = z.infer<typeof createEndpointInputSchema>;

export const createEndpoint = async (
  input: CreateEndpointInput,
): Promise<Endpoint> => {
  const response = await apiClient.post("/endpoints", input);
  return endpointSchema.parse(response.data);
};

type UseCreateEndpointOptions = Pick<
  UseMutationOptions<Endpoint, Error, CreateEndpointInput>,
  "onSuccess" | "onError"
>;

export const useCreateEndpoint = ({
  onSuccess,
  ...options
}: UseCreateEndpointOptions = {}) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createEndpoint,
    onSuccess: async (...args) => {
      // Awaiting the refetch keeps the mutation pending until the list shows
      // the new endpoint. `exact` spares the data queries nested under the
      // same key, since the new endpoint changes none of them.
      await queryClient.invalidateQueries({
        queryKey: endpointsQueryKey,
        exact: true,
      });
      await onSuccess?.(...args);
    },
    ...options,
  });
};
