import { Container, Group, Modal, Stack, Text, Title } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { Plus } from "lucide-react";
import { useState } from "react";

import { Head } from "@/components/seo/head";
import { Button } from "@/components/ui/button";
import type { CreatedApiKey } from "@/features/api-keys/api/api-key";
import { ApiKeyList } from "@/features/api-keys/components/api-key-list";
import { CreateApiKeyForm } from "@/features/api-keys/components/create-api-key-form";
import { NewApiKey } from "@/features/api-keys/components/new-api-key";

const ApiKeysRoute = () => {
  const [modalOpened, modal] = useDisclosure(false);
  // Held only until the modal closes, since the key is never shown again.
  const [createdKey, setCreatedKey] = useState<CreatedApiKey | null>(null);

  const closeModal = () => {
    modal.close();
    setCreatedKey(null);
  };

  return (
    <Container
      size={840}
      py="xl"
    >
      <Head title="API keys" />
      <Stack>
        <Group justify="space-between">
          <Title order={2}>API Keys</Title>
          <Button
            fz={11}
            leftSection={<Plus size={12} />}
            onClick={modal.open}
          >
            New API key
          </Button>
        </Group>
        <Text
          c="dimmed"
          fz="xs"
        >
          Call your endpoints from scripts and servers by sending a key in the
          Authorization header. Keys can&apos;t manage other keys, so revoke a
          leaked one here.
        </Text>
        <ApiKeyList />
      </Stack>

      <Modal
        opened={modalOpened}
        onClose={closeModal}
        title={createdKey ? "Your new API key" : "New API key"}
        size={520}
        padding={24}
        radius="md"
        centered
        withCloseButton={false}
        // A stray click must not throw away a key that can't be shown again.
        closeOnClickOutside={createdKey === null}
        closeOnEscape={createdKey === null}
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
        {createdKey ? (
          <NewApiKey
            apiKey={createdKey}
            onDone={closeModal}
          />
        ) : (
          <>
            <Text
              c="dimmed"
              fz="xs"
              mb="md"
            >
              Name the key after whatever will use it, so you know what breaks
              if you revoke it.
            </Text>
            <CreateApiKeyForm
              onSuccess={setCreatedKey}
              onCancel={closeModal}
            />
          </>
        )}
      </Modal>
    </Container>
  );
};

export default ApiKeysRoute;
