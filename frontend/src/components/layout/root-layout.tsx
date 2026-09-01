import { Box, Flex } from "@mantine/core";
import { Outlet } from "react-router";

const RootLayout = () => {
  return (
    <Flex direction="column" mih="100vh">
      <Box component="main" flex={1}>
        <Outlet />
      </Box>
    </Flex>
  );
};

export default RootLayout;
