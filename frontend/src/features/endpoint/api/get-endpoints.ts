import { queryOptions, useQuery } from "@tanstack/react-query";
import * as z from "zod";

import { apiClient } from "@/lib/axios";

import { endpointSchema, type Endpoint } from "./endpoint";

export const getEndpoints = async (): Promise<Endpoint[]> => {
  const response = await apiClient.get("/endpoints");
  return z.array(endpointSchema).parse(response.data);
};

export const endpointsQueryKey = ["endpoints"] as const;

export const getEndpointsQueryOptions = () => {
  return queryOptions({
    queryKey: endpointsQueryKey,
    queryFn: getEndpoints,
  });
};

export const useEndpoints = () => {
  return useQuery(getEndpointsQueryOptions());
};
