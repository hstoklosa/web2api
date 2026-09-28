import * as z from "zod";

export const apiKeySchema = z.object({
  id: z.uuid(),
  name: z.string(),
  // The start of the key, since the full key is only shown once.
  prefix: z.string(),
  created_at: z.iso.datetime({ offset: true }),
  last_used_at: z.iso.datetime({ offset: true }).nullable(),
});

export type ApiKey = z.infer<typeof apiKeySchema>;

// Only the create response carries the key itself.
export const createdApiKeySchema = apiKeySchema.extend({
  key: z.string(),
});

export type CreatedApiKey = z.infer<typeof createdApiKeySchema>;
