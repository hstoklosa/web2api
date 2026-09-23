import { Container, Group, Modal, Stack, Text, Title } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { endpointsQueryKey } from "@/features/endpoint/api/get-endpoints";
import { CreateEndpointForm } from "@/features/endpoint/components/create-endpoint-form";
import { EndpointList } from "@/features/endpoint/components/endpoint-list";

const DashboardRoute = () => {
  const queryClient = useQueryClient();
  const [modalOpened, modal] = useDisclosure(false);

  return (
    <Container
      size={840}
      py="xl"
    >
      <Stack>
        <Group justify="space-between">
          <Title order={2}>Your Endpoints</Title>
          <Button
            fz={11}
            leftSection={<Plus size={12} />}
            onClick={modal.open}
          >
            New endpoint
          </Button>
        </Group>
        <EndpointList />
      </Stack>

      <Modal
        opened={modalOpened}
        onClose={modal.close}
        title="New endpoint"
        size={520}
        padding={24}
        radius="md"
        centered
        withCloseButton={false}
        overlayProps={{ backgroundOpacity: 0.35 }}
        styles={{
          // Pull the description up under the title instead of leaving the
          // header's default 60px minimum height between them.
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
          Paste a URL and describe what you want from it. We&apos;ll either
          match an existing API or build a new one.
        </Text>
        <CreateEndpointForm
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: endpointsQueryKey });
            modal.close();
          }}
          onCancel={modal.close}
        />
      </Modal>
    </Container>
  );
};

export default DashboardRoute;
