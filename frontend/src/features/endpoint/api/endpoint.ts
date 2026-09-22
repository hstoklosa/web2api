import * as z from "zod";

export const endpointSchema = z.object({
  id: z.uuid(),
  name: z.string(),
  url: z.string(),
  description: z.string(),
  schema: z.record(z.string(), z.unknown()),
});

export type Endpoint = z.infer<typeof endpointSchema>;
