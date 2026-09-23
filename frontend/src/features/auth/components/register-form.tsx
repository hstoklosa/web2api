import { Alert, Paper, PasswordInput, Stack, TextInput } from "@mantine/core";
import { schemaResolver, useForm } from "@mantine/form";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import {
  registerInputSchema,
  useLogin,
  useRegister,
  userQueryKey,
  type RegisterInput,
} from "@/lib/auth";
import { setToken } from "@/lib/auth-token";
import { getApiErrorMessage } from "@/lib/axios";

// Confirm password is a UI-only check, so it lives here rather than in the
// API payload schema that `registerInputSchema` defines.
const registerFormSchema = registerInputSchema
  .extend({
    confirmPassword: z.string(),
  })
  .refine((values) => values.password === values.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

type RegisterFormValues = z.infer<typeof registerFormSchema>;

export const RegisterForm = () => {
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

  const form = useForm<RegisterFormValues>({
    mode: "uncontrolled",
    initialValues: {
      email: "",
      password: "",
      confirmPassword: "",
    },
    validate: schemaResolver(registerFormSchema, { sync: true }),
  });

  const handleSubmit = ({ email, password }: RegisterFormValues) => {
    const input: RegisterInput = { email, password };
    register.mutate(input);
  };

  return (
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
          <PasswordInput
            label="Confirm password"
            placeholder="Confirm your password"
            key={form.key("confirmPassword")}
            {...form.getInputProps("confirmPassword")}
          />
          <Button
            type="submit"
            fullWidth
            mt="sm"
            loading={isPending}
          >
            Register
          </Button>
        </Stack>
      </form>
    </Paper>
  );
};
