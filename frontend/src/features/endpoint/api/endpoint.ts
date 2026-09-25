import * as z from "zod";

const fieldTypeSchema = z.enum(["string", "integer", "number", "boolean"]);

export type FieldType = z.infer<typeof fieldTypeSchema>;

const objectResponseSchema = z.object({
  type: z.literal("object"),
  properties: z.record(z.string(), z.object({ type: fieldTypeSchema })),
});

// The backend derives this JSON Schema from the extraction recipe, which
// yields either one flat object or a list of them.
export const responseSchemaSchema = z.discriminatedUnion("type", [
  objectResponseSchema,
  z.object({
    type: z.literal("array"),
    items: objectResponseSchema,
  }),
]);

export type ResponseSchema = z.infer<typeof responseSchemaSchema>;

export const endpointSchema = z.object({
  id: z.uuid(),
  name: z.string(),
  url: z.string(),
  description: z.string(),
  schema: responseSchemaSchema,
});

export type Endpoint = z.infer<typeof endpointSchema>;
