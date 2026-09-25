import type { ResponseSchema } from "@/features/endpoint/api/endpoint";

import classes from "./response-format.module.css";

type ResponseFormatProps = {
  schema: ResponseSchema;
};

// Renders the response schema as a TypeScript-like signature, which reads far
// quicker than the JSON Schema it comes from.
export const ResponseFormat = ({ schema }: ResponseFormatProps) => {
  const isList = schema.type === "array";
  const fields = Object.entries(
    isList ? schema.items.properties : schema.properties,
  );

  return (
    <pre className={classes.root}>
      <span className={classes.punctuation}>
        {isList && <span className={classes.type}>Array</span>}
        {isList ? "<{" : "{"}
      </span>
      {fields.map(([name, { type }]) => (
        <div
          key={name}
          className={classes.field}
        >
          <span className={classes.name}>{name}</span>
          <span className={classes.punctuation}>: </span>
          <span className={classes.type}>{type}</span>
        </div>
      ))}
      <span className={classes.punctuation}>{isList ? "}>" : "}"}</span>
    </pre>
  );
};
