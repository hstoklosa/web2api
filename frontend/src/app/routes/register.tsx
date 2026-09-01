import {
  Button,
  Container,
  Paper,
  PasswordInput,
  Stack,
  TextInput,
  Title,
} from "@mantine/core";
import { schemaResolver, useForm } from "@mantine/form";
import * as z from "zod";

const registerSchema = z.object({
  email: z.email("Enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters long"),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

const RegisterRoute = () => {
  const form = useForm<RegisterFormValues>({
    mode: "uncontrolled",
    initialValues: {
      email: "",
      password: "",
    },
    validate: schemaResolver(registerSchema, { sync: true }),
  });

  const handleSubmit = (values: RegisterFormValues) => {
    console.log(values);
  };

  return (
    <Container size={420} py="xl">
      <Title order={2} ta="center">
        Create an account
      </Title>

      <Paper withBorder radius="md" p="lg" mt="lg">
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack>
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
            <Button type="submit" fullWidth mt="sm">
              Register
            </Button>
          </Stack>
        </form>
      </Paper>
    </Container>
  );
};

export default RegisterRoute;
