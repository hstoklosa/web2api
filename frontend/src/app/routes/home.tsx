import { Container, Stack, Text, Title } from "@mantine/core";

const HomeRoute = () => {
  return (
    <Container size="sm" py="xl">
      <Stack gap="xs">
        <Title order={1}>web2api</Title>
        <Text c="dimmed">Turn any URL into a REST API.</Text>
      </Stack>
    </Container>
  );
};

export default HomeRoute;
