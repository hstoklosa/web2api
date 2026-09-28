import { Alert, Group, Stack, TextInput } from "@mantine/core";
import { schemaResolver, useForm } from "@mantine/form";
import { KeyRound } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { CreatedApiKey } from "@/features/api-keys/api/api-key";
import {
  createApiKeyInputSchema,
  useCreateApiKey,
  type CreateApiKeyInput,
} from "@/features/api-keys/api/create-api-key";
import { getApiErrorMessage } from "@/lib/axios";

type CreateApiKeyFormProps = {
  onSuccess?: (apiKey: CreatedApiKey) => void;
  onCancel?: () => void;
};

export const CreateApiKeyForm = ({
  onSuccess,
  onCancel,
}: CreateApiKeyFormProps) => {
  const createApiKey = useCreateApiKey({
    onSuccess: (apiKey) => {
      form.reset();
      onSuccess?.(apiKey);
    },
  });

  const form = useForm<CreateApiKeyInput>({
    mode: "uncontrolled",
    initialValues: {
      name: "",
    },
    validate: schemaResolver(createApiKeyInputSchema, { sync: true }),
  });

  const handleSubmit = (values: CreateApiKeyInput) => {
    createApiKey.mutate(values);
  };

  return (
    <form onSubmit={form.onSubmit(handleSubmit)}>
      <Stack>
        {createApiKey.error && (
          <Alert
            color="red"
            variant="light"
          >
            {getApiErrorMessage(createApiKey.error)}
          </Alert>
        )}

        <TextInput
          label="Name"
          radius="sm"
          placeholder="Price tracker script"
          data-autofocus
          key={form.key("name")}
          {...form.getInputProps("name")}
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
            leftSection={<KeyRound size={12} />}
            loading={createApiKey.isPending}
          >
            Create key
          </Button>
        </Group>
      </Stack>
    </form>
  );
};
