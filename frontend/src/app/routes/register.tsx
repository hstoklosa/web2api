import {
  Alert,
  Button,
  Container,
  Paper,
  PasswordInput,
  Stack,
  TextInput,
  Title,
} from "@mantine/core";
import { schemaResolver, useForm } from "@mantine/form";

import {
  registerInputSchema,
  useRegister,
  type RegisterInput,
} from "@/features/auth/api/register";
import { getApiErrorMessage } from "@/lib/axios";

const RegisterRoute = () => {
  const register = useRegister();

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
    <Container
      size={420}
      py="xl"
    >
      <Title
        order={2}
        ta="center"
      >
        Create an account
      </Title>

      <Paper
        withBorder
        radius="md"
        p="lg"
        mt="lg"
      >
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack>
            {register.isError && (
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
            <Button
              type="submit"
              color="purple"
              fullWidth
              mt="sm"
              loading={register.isPending}
            >
              Register
            </Button>
          </Stack>
        </form>
      </Paper>
    </Container>
  );
};

export default RegisterRoute;
