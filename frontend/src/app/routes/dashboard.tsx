import { Container, Stack, Title } from "@mantine/core";

import { CreateEndpointForm } from "@/features/endpoint/components/create-endpoint-form";

const DashboardRoute = () => {
  return (
    <Container
      size={480}
      py="xl"
    >
      <Stack>
        <Title order={2}>New endpoint</Title>
        <CreateEndpointForm />
      </Stack>
    </Container>
  );
};

export default DashboardRoute;
