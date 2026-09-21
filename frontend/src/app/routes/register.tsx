import {
  Alert,
  Anchor,
  Button,
  Container,
  Flex,
  Paper,
  PasswordInput,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import { schemaResolver, useForm } from "@mantine/form";
import { useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router";

import { userQueryKey } from "@/features/auth/api/get-user";
import { useLogin } from "@/features/auth/api/login";
import {
  registerInputSchema,
  useRegister,
  type RegisterInput,
} from "@/features/auth/api/register";
import { setToken } from "@/lib/auth-token";
import { getApiErrorMessage } from "@/lib/axios";

const RegisterRoute = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const login = useLogin();

  // Registration does not issue a token, so log in with the same credentials
  // once the account exists.
  const register = useRegister({
    onSuccess: (user, input) =>
      login.mutate(input, {
        onSuccess: (token) => {
          setToken(token.access_token);
          // Seed the current-user query with the user we already have so the
          // dashboard renders without waiting on /auth/me.
          queryClient.setQueryData(userQueryKey, user);
          navigate("/dashboard");
        },
      }),
  });

  const isPending = register.isPending || login.isPending;
  const error = register.error ?? login.error;

  const form = useForm<RegisterInput>({
    mode: "uncontrolled",
    initialValues: {
      email: "",
      password: "",
    },
    validate: schemaResolver(registerInputSchema, { sync: true }),
  });

  const handleSubmit = (values: RegisterInput) => {
    register.mutate(values);
  };

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

        <Paper
          withBorder
          radius="md"
          p="lg"
        >
          <form onSubmit={form.onSubmit(handleSubmit)}>
            <Stack>
              {error && (
                <Alert
                  color="red"
                  variant="light"
                >
                  {getApiErrorMessage(error)}
                </Alert>
              )}

              <TextInput
                label="Email"
                placeholder="you@example.com"
                type="email"
                key={form.key("email")}
                {...form.getInputProps("email")}
              />
              <PasswordInput
                label="Password"
                placeholder="Your password"
                key={form.key("password")}
                {...form.getInputProps("password")}
              />
              <Button
                type="submit"
                color="dark"
                radius="sm"
                tt="uppercase"
                fz="xs"
                lts="0.05em"
                fullWidth
                mt="sm"
                loading={isPending}
              >
                Register
              </Button>
            </Stack>
          </form>
        </Paper>

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
