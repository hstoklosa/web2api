import { Alert, Paper, PasswordInput, Stack, TextInput } from "@mantine/core";
import { schemaResolver, useForm } from "@mantine/form";
import { useNavigate } from "react-router";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import {
  registerInputSchema,
  useRegister,
  type RegisterInput,
} from "@/lib/auth";
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
  const register = useRegister({
    onSuccess: () => {
      navigate("/dashboard");
    },
  });

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
          {register.error && (
            <Alert
              color="red"
              variant="light"
            >
              {getApiErrorMessage(register.error)}
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
            loading={register.isPending}
          >
            Register
          </Button>
        </Stack>
      </form>
    </Paper>
  );
};
