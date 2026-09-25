import { ActionIcon, Alert, Group, Menu, Modal, Text } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { EllipsisVertical, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useDeleteEndpoint } from "@/features/endpoint/api/delete-endpoint";
import type { Endpoint } from "@/features/endpoint/api/endpoint";
import { getApiErrorMessage } from "@/lib/axios";

type EndpointActionsProps = {
  endpoint: Endpoint;
};

export const EndpointActions = ({ endpoint }: EndpointActionsProps) => {
  const [confirmOpened, confirm] = useDisclosure(false);
  // The deleted endpoint leaves the list on success, unmounting this
  // component, so there is nothing to close afterwards.
  const deleteEndpoint = useDeleteEndpoint();

  const closeConfirm = () => {
    // A failed attempt should not greet the next one with a stale error.
    deleteEndpoint.reset();
    confirm.close();
  };

  return (
    <>
      <Menu
        position="bottom-start"
        radius="sm"
        shadow="sm"
        width={160}
      >
        <Menu.Target>
          <ActionIcon
            variant="subtle"
            color="gray"
            aria-label={`Actions for ${endpoint.name}`}
          >
            <EllipsisVertical size={16} />
          </ActionIcon>
        </Menu.Target>
        <Menu.Dropdown>
          <Menu.Item
            color="red"
            fz="xs"
            leftSection={<Trash2 size={14} />}
            onClick={confirm.open}
          >
            Delete
          </Menu.Item>
        </Menu.Dropdown>
      </Menu>

      <Modal
        opened={confirmOpened}
        onClose={closeConfirm}
        title="Delete endpoint"
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
          <Text
            span
            inherit
            fw={500}
            c="var(--mantine-color-text)"
          >
            {endpoint.name}
          </Text>{" "}
          will stop serving data. This cannot be undone.
        </Text>

        {deleteEndpoint.isError && (
          <Alert
            color="red"
            variant="light"
            mb="md"
          >
            {getApiErrorMessage(
              deleteEndpoint.error,
              "Could not delete the endpoint.",
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
            disabled={deleteEndpoint.isPending}
          >
            Cancel
          </Button>
          <Button
            color="red"
            fz={11}
            leftSection={<Trash2 size={12} />}
            loading={deleteEndpoint.isPending}
            onClick={() => deleteEndpoint.mutate(endpoint.id)}
          >
            Delete
          </Button>
        </Group>
      </Modal>
    </>
  );
};
