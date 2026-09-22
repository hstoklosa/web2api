import { useMutation, type UseMutationOptions } from "@tanstack/react-query";
import * as z from "zod";

import { apiClient } from "@/lib/axios";

import { endpointSchema, type Endpoint } from "./endpoint";

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

export const useCreateEndpoint = (options?: UseCreateEndpointOptions) => {
  return useMutation({
    mutationFn: createEndpoint,
    ...options,
  });
};
