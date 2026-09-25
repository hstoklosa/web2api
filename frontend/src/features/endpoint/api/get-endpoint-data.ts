import { queryOptions, useQuery } from "@tanstack/react-query";
import * as z from "zod";

import { apiClient } from "@/lib/axios";

import { endpointsQueryKey } from "./get-endpoints";

const recordSchema = z.record(z.string(), z.unknown());

// The backend returns a single object or a list of them, depending on
// the endpoint's extraction schema.
export const endpointDataSchema = z.union([
  recordSchema,
  z.array(recordSchema),
]);

export type EndpointData = z.infer<typeof endpointDataSchema>;

export const getEndpointDataPath = (id: string) => `/endpoints/${id}/data`;

export const getEndpointData = async (id: string): Promise<EndpointData> => {
  const response = await apiClient.get(getEndpointDataPath(id));
  return endpointDataSchema.parse(response.data);
};

export const getEndpointDataQueryKey = (id: string) =>
  [...endpointsQueryKey, id, "data"] as const;

export const getEndpointDataQueryOptions = (id: string) => {
  return queryOptions({
    queryKey: getEndpointDataQueryKey(id),
    queryFn: () => getEndpointData(id),
  });
};

type UseEndpointDataOptions = {
  // Each fetch scrapes the live page, so callers can hold it until the user
  // asks for it and trigger it with `refetch`.
  enabled?: boolean;
};

export const useEndpointData = (
  id: string,
  { enabled }: UseEndpointDataOptions = {},
) => {
  return useQuery({ ...getEndpointDataQueryOptions(id), enabled });
};
