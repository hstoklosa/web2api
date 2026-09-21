import "@mantine/core/styles.css";

import { MantineProvider } from "@mantine/core";
import { QueryClientProvider } from "@tanstack/react-query";

import { queryClient } from "@/lib/react-query";

import { theme } from "./theme";

const AppProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider theme={theme}>{children}</MantineProvider>
    </QueryClientProvider>
  );
};

export default AppProvider;
