import { Alert, Paper, PasswordInput, Stack, TextInput } from "@mantine/core";
import { schemaResolver, useForm } from "@mantine/form";
import { useNavigate, useSearchParams } from "react-router";

import { Button } from "@/components/ui/button";
import { loginInputSchema, useLogin, type LoginInput } from "@/lib/auth";
import { getApiErrorMessage } from "@/lib/axios";

// Only follow same-origin paths, so the param cannot be used as an open
// redirect ("//evil.com" and "/\evil.com" both resolve to another host).
const getRedirectTarget = (value: string | null): string => {
  if (value !== null && /^\/(?![/\\])/.test(value)) {
    return value;
  }
  return "/dashboard";
};

export const LoginForm = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const login = useLogin({
    onSuccess: () => {
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
    <Paper
      withBorder
      radius="md"
      p="lg"
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
            fullWidth
            mt="sm"
            loading={login.isPending}
          >
            Log in
          </Button>
        </Stack>
      </form>
    </Paper>
  );
};
