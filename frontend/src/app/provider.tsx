import "@mantine/core/styles.css";

import { MantineProvider } from "@mantine/core";

const AppProvider = ({ children }: { children: React.ReactNode }) => {
  return <MantineProvider>{children}</MantineProvider>;
};

export default AppProvider;
