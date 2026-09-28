import { ActionIcon, Anchor, Box, Group, Text } from "@mantine/core";
import { LogOut } from "lucide-react";
import { Link, Navigate, Outlet, useLocation, useMatch } from "react-router";

import { useLogout, useUser } from "@/lib/auth";

type HeaderLinkProps = {
  to: string;
  children: React.ReactNode;
};

const HeaderLink = ({ to, children }: HeaderLinkProps) => {
  const active = useMatch(to) !== null;

  return (
    <Anchor
      component={Link}
      to={to}
      fz="xs"
      fw={500}
      tt="uppercase"
      lts="0.05em"
      underline="never"
      c={active ? "var(--mantine-color-text)" : "dimmed"}
      aria-current={active ? "page" : undefined}
    >
      {children}
    </Anchor>
  );
};

const Header = () => {
  const logout = useLogout();

  return (
    <Box
      component="header"
      style={{ borderBottom: "1px solid var(--mantine-color-gray-3)" }}
    >
      <Group
        justify="space-between"
        px="md"
        py="sm"
      >
        <Group gap="xl">
          <Text
            fw={700}
            size="lg"
          >
            web2api
          </Text>
          <Group
            component="nav"
            gap="lg"
          >
            <HeaderLink to="/dashboard">Endpoints</HeaderLink>
            <HeaderLink to="/api-keys">API keys</HeaderLink>
          </Group>
        </Group>
        <ActionIcon
          variant="default"
          size="lg"
          radius="sm"
          c="dimmed"
          aria-label="Sign out"
          loading={logout.isPending}
          onClick={() => logout.mutate()}
        >
          <LogOut size={16} />
        </ActionIcon>
      </Group>
    </Box>
  );
};

const AppLayout = () => {
  const { data: user } = useUser();
  const location = useLocation();

  // The route guard only checks the session on navigation, so this catches it
  // ending while the user stays on a page: logout, a failed refresh, or a
  // logout in another tab that the focus refetch of /auth/me picks up.
  if (user === null) {
    const params = new URLSearchParams({
      redirect: location.pathname + location.search,
    });
    return (
      <Navigate
        to={`/login?${params}`}
        replace
      />
    );
  }

  return (
    <>
      <Header />
      <Outlet />
    </>
  );
};

export default AppLayout;
