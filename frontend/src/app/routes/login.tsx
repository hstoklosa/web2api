import { Anchor, Container, Flex, Stack, Text, Title } from "@mantine/core";
import { Link } from "react-router";

import { LoginForm } from "@/features/auth/components/login-form";

const LoginRoute = () => {
  return (
    <Flex
      mih="100dvh"
      direction="column"
      align="center"
      justify="center"
      px="md"
    >
      <Container
        size={420}
        w="100%"
        py="xl"
      >
        <Stack
          align="center"
          gap={2}
          mb="lg"
        >
          <Anchor
            component={Link}
            to="/"
            underline="never"
            c="black"
            fw={700}
            size="lg"
          >
            web2api
          </Anchor>
          <Title
            order={2}
            ta="center"
          >
            Welcome back
          </Title>
        </Stack>

        <LoginForm />

        <Text
          ta="center"
          size="sm"
          mt="md"
        >
          Don&apos;t have an account?{" "}
          <Anchor
            component={Link}
            to="/register"
            size="sm"
            c="black"
          >
            Register
          </Anchor>
        </Text>
      </Container>
    </Flex>
  );
};

export default LoginRoute;
