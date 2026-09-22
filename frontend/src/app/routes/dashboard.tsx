import { Container, Stack, Title } from "@mantine/core";
import { useQueryClient } from "@tanstack/react-query";

import { endpointsQueryKey } from "@/features/endpoint/api/get-endpoints";
import { CreateEndpointForm } from "@/features/endpoint/components/create-endpoint-form";
import { EndpointList } from "@/features/endpoint/components/endpoint-list";

const DashboardRoute = () => {
  const queryClient = useQueryClient();

  return (
    <Container
      size={480}
      py="xl"
    >
      <Stack>
        <Title order={2}>New endpoint</Title>
        <CreateEndpointForm
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: endpointsQueryKey });
          }}
        />

        <Title
          order={2}
          mt="lg"
        >
          Your endpoints
        </Title>
        <EndpointList />
      </Stack>
    </Container>
  );
};

export default DashboardRoute;
