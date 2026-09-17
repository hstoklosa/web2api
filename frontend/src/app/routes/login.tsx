import {
  Alert,
  Anchor,
  Button,
  Container,
  Paper,
  PasswordInput,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import { schemaResolver, useForm } from "@mantine/form";
import { useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useSearchParams } from "react-router";

import { userQueryKey } from "@/features/auth/api/get-user";
import {
  loginInputSchema,
  useLogin,
  type LoginInput,
} from "@/features/auth/api/login";
import { setToken } from "@/lib/auth-token";
import { getApiErrorMessage } from "@/lib/axios";

// Only follow same-origin paths, so the param cannot be used as an open
// redirect ("//evil.com" and "/\evil.com" both resolve to another host).
const getRedirectTarget = (value: string | null): string => {
  if (value !== null && /^\/(?![/\\])/.test(value)) {
    return value;
  }
  return "/dashboard";
};

const LoginRoute = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();

  const login = useLogin({
    onSuccess: (token) => {
      setToken(token.access_token);
      // Drop any previously cached user so the auth middleware loads the
      // account that just signed in instead of trusting stale data.
      queryClient.removeQueries({ queryKey: userQueryKey });
      navigate(getRedirectTarget(searchParams.get("redirect")));
    },
  });

  const form = useForm<LoginInput>({
    mode: "uncontrolled",
    initialValues: {
      email: "",
      password: "",
    },
    validate: schemaResolver(loginInputSchema, { sync: true }),
  });

  const handleSubmit = (values: LoginInput) => {
    login.mutate(values);
  };

  return (
    <Container
      size={420}
      py="xl"
    >
      <Title
        order={2}
        ta="center"
      >
        Welcome back
      </Title>

      <Paper
        withBorder
        radius="md"
        p="lg"
        mt="lg"
      >
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack>
            {login.error && (
              <Alert
                color="red"
                variant="light"
              >
                {getApiErrorMessage(login.error)}
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
              color="purple"
              fullWidth
              mt="sm"
              loading={login.isPending}
            >
              Log in
            </Button>
          </Stack>
        </form>
      </Paper>

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
        >
          Register
        </Anchor>
      </Text>
    </Container>
  );
};

export default LoginRoute;
