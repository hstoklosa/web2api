import { ActionIcon, Box, Group, Text } from "@mantine/core";
import { LogOut } from "lucide-react";
import { Navigate, Outlet, useLocation } from "react-router";

import { useLogout, useUser } from "@/lib/auth";

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
        <Text
          fw={700}
          size="lg"
        >
          web2api
        </Text>
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
