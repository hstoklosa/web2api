import * as z from "zod";

export const userSchema = z.object({
  id: z.number(),
  email: z.email(),
});

export type User = z.infer<typeof userSchema>;
