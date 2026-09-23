import { ActionIcon, Box, Group, Text } from "@mantine/core";
import { useQueryClient } from "@tanstack/react-query";
import { LogOut } from "lucide-react";
import { Outlet, useNavigate } from "react-router";

import { useLogout } from "@/lib/auth";

const Header = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const logout = useLogout({
    onSuccess: async () => {
      // Leave the app before dropping the cache, so mounted queries don't
      // refetch without a token. The next user then starts from a clean cache.
      await navigate("/login");
      queryClient.clear();
    },
  });

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
  return (
    <>
      <Header />
      <Outlet />
    </>
  );
};

export default AppLayout;
