import { ActionIcon, Alert, Group, Modal, Text, Tooltip } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { ApiKey } from "@/features/api-keys/api/api-key";
import { useDeleteApiKey } from "@/features/api-keys/api/delete-api-key";
import { getApiErrorMessage } from "@/lib/axios";

type RevokeApiKeyProps = {
  apiKey: ApiKey;
};

export const RevokeApiKey = ({ apiKey }: RevokeApiKeyProps) => {
  const [confirmOpened, confirm] = useDisclosure(false);
  // The revoked key leaves the list on success, unmounting this component,
  // so there is nothing to close afterwards.
  const deleteApiKey = useDeleteApiKey();

  const closeConfirm = () => {
    // A failed attempt should not greet the next one with a stale error.
    deleteApiKey.reset();
    confirm.close();
  };

  return (
    <>
      <Tooltip
        label="Revoke"
        withArrow
      >
        <ActionIcon
          variant="subtle"
          color="gray"
          aria-label={`Revoke ${apiKey.name}`}
          onClick={confirm.open}
        >
          <Trash2 size={16} />
        </ActionIcon>
      </Tooltip>

      <Modal
        opened={confirmOpened}
        onClose={closeConfirm}
        title="Revoke API key"
        size={420}
        padding={24}
        radius="md"
        centered
        withCloseButton={false}
        overlayProps={{ backgroundOpacity: 0.35 }}
        styles={{
          header: {
            minHeight: "auto",
            paddingBottom: 6,
          },
          title: {
            fontSize: "var(--mantine-font-size-lg)",
            fontWeight: 600,
          },
        }}
      >
        <Text
          c="dimmed"
          fz="xs"
          mb="md"
        >
          Anything using{" "}
          <Text
            span
            inherit
            fw={500}
            c="var(--mantine-color-text)"
          >
            {apiKey.name}
          </Text>{" "}
          will be refused straight away. This cannot be undone.
        </Text>

        {deleteApiKey.isError && (
          <Alert
            color="red"
            variant="light"
            mb="md"
          >
            {getApiErrorMessage(
              deleteApiKey.error,
              "Could not revoke the API key.",
            )}
          </Alert>
        )}

        <Group
          justify="flex-end"
          gap="sm"
        >
          <Button
            variant="default"
            fz={11}
            onClick={closeConfirm}
            disabled={deleteApiKey.isPending}
          >
            Cancel
          </Button>
          <Button
            color="red"
            fz={11}
            leftSection={<Trash2 size={12} />}
            loading={deleteApiKey.isPending}
            onClick={() => deleteApiKey.mutate(apiKey.id)}
          >
            Revoke
          </Button>
        </Group>
      </Modal>
    </>
  );
};
