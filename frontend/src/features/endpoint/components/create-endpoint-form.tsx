import { Alert, Group, Stack, Textarea, TextInput } from "@mantine/core";
import { schemaResolver, useForm } from "@mantine/form";
import { ClockFading } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  createEndpointInputSchema,
  useCreateEndpoint,
  type CreateEndpointInput,
} from "@/features/endpoint/api/create-endpoint";
import type { Endpoint } from "@/features/endpoint/api/endpoint";
import { getApiErrorMessage } from "@/lib/axios";

type CreateEndpointFormProps = {
  onSuccess?: (endpoint: Endpoint) => void;
  onCancel?: () => void;
};

export const CreateEndpointForm = ({
  onSuccess,
  onCancel,
}: CreateEndpointFormProps) => {
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
          radius="sm"
          placeholder="https://news.ycombinator.com"
          type="url"
          key={form.key("url")}
          {...form.getInputProps("url")}
        />
        <Textarea
          label="Description"
          radius="sm"
          placeholder="Titles and URLs of the top stories"
          autosize
          minRows={3}
          key={form.key("description")}
          {...form.getInputProps("description")}
        />
        <Group
          justify="flex-end"
          gap="sm"
          mt="sm"
        >
          {onCancel && (
            <Button
              type="button"
              variant="default"
              fz={11}
              onClick={onCancel}
            >
              Cancel
            </Button>
          )}
          <Button
            type="submit"
            fz={11}
            leftSection={<ClockFading size={12} />}
            loading={createEndpoint.isPending}
          >
            Build it
          </Button>
        </Group>
      </Stack>
    </form>
  );
};
