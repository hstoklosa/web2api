import { createTheme } from "@mantine/core";

const fontFamily =
  '"SF Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace';

export const theme = createTheme({
  fontFamily,
  fontFamilyMonospace: fontFamily,
  primaryColor: "dark",
});
