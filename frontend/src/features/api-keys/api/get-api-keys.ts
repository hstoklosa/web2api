import { queryOptions, useQuery } from "@tanstack/react-query";
import * as z from "zod";

import { apiClient } from "@/lib/axios";

import { apiKeySchema, type ApiKey } from "./api-key";

export const getApiKeys = async (): Promise<ApiKey[]> => {
  const response = await apiClient.get("/api-keys");
  return z.array(apiKeySchema).parse(response.data);
};

export const apiKeysQueryKey = ["api-keys"] as const;

export const getApiKeysQueryOptions = () => {
  return queryOptions({
    queryKey: apiKeysQueryKey,
    queryFn: getApiKeys,
  });
};

export const useApiKeys = () => {
  return useQuery(getApiKeysQueryOptions());
};
