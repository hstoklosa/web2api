import { Alert, Button, Paper, Stack, Textarea, TextInput } from "@mantine/core";
import { schemaResolver, useForm } from "@mantine/form";

import {
  createEndpointInputSchema,
  useCreateEndpoint,
  type CreateEndpointInput,
  type Endpoint,
} from "@/features/endpoint/api/create-endpoint";
import { getApiErrorMessage } from "@/lib/axios";

type CreateEndpointFormProps = {
  onSuccess?: (endpoint: Endpoint) => void;
};

export const CreateEndpointForm = ({ onSuccess }: CreateEndpointFormProps) => {
  const createEndpoint = useCreateEndpoint({
    onSuccess: (endpoint) => {
      form.reset();
      onSuccess?.(endpoint);
    },
  });

  const form = useForm<CreateEndpointInput>({
    mode: "uncontrolled",
    initialValues: {
      url: "",
      description: "",
    },
    validate: schemaResolver(createEndpointInputSchema, { sync: true }),
  });

  const handleSubmit = (values: CreateEndpointInput) => {
    createEndpoint.mutate(values);
  };

  return (
    <Paper
      withBorder
      radius="md"
      p="lg"
    >
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack>
          {createEndpoint.error && (
            <Alert
              color="red"
              variant="light"
            >
              {getApiErrorMessage(createEndpoint.error)}
            </Alert>
          )}

          <TextInput
            label="URL"
            placeholder="https://news.ycombinator.com"
            type="url"
            key={form.key("url")}
            {...form.getInputProps("url")}
          />
          <Textarea
            label="Description"
            placeholder="Titles and URLs of the top stories"
            autosize
            minRows={3}
            key={form.key("description")}
            {...form.getInputProps("description")}
          />
          <Button
            type="submit"
            color="dark"
            radius="sm"
            tt="uppercase"
            fz="xs"
            lts="0.05em"
            fullWidth
            mt="sm"
            loading={createEndpoint.isPending}
          >
            Create endpoint
          </Button>
        </Stack>
      </form>
    </Paper>
  );
};
