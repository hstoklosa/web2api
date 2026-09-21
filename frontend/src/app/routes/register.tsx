import { Anchor, Container, Flex, Stack, Text, Title } from "@mantine/core";
import { Link } from "react-router";

import { RegisterForm } from "@/features/auth/components/register-form";

const RegisterRoute = () => {
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
            Create an account
          </Title>
        </Stack>

        <RegisterForm />

        <Text
          ta="center"
          size="sm"
          mt="md"
        >
          Already have an account?{" "}
          <Anchor
            component={Link}
            to="/login"
            size="sm"
            c="black"
          >
            Log in
          </Anchor>
        </Text>
      </Container>
    </Flex>
  );
};

export default RegisterRoute;
