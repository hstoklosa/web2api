import {
  ActionIcon,
  Alert,
  CopyButton,
  Group,
  Paper,
  Stack,
  Text,
  Tooltip,
} from "@mantine/core";
import { Check, Copy } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { CreatedApiKey } from "@/features/api-keys/api/api-key";

type NewApiKeyProps = {
  apiKey: CreatedApiKey;
  onDone: () => void;
};

export const NewApiKey = ({ apiKey, onDone }: NewApiKeyProps) => {
  return (
    <Stack>
      <Alert
        color="yellow"
        variant="light"
      >
        Copy this key now. It is only stored as a hash, so you won&apos;t be
        able to see it again.
      </Alert>

      <Paper
        withBorder
        radius="sm"
        py={6}
        pl="xs"
        pr={6}
      >
        <Group
          gap="sm"
          wrap="nowrap"
        >
          <Text
            flex={1}
            miw={0}
            ff="monospace"
            fz="xs"
            style={{ overflowWrap: "anywhere" }}
          >
            {apiKey.key}
          </Text>
          <CopyButton value={apiKey.key}>
            {({ copied, copy }) => (
              <Tooltip
                label={copied ? "Copied" : "Copy"}
                withArrow
              >
                <ActionIcon
                  variant="subtle"
                  color={copied ? "teal" : "gray"}
                  aria-label="Copy API key"
                  onClick={copy}
                >
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                </ActionIcon>
              </Tooltip>
            )}
          </CopyButton>
        </Group>
      </Paper>

      <Text
        c="dimmed"
        fz="xs"
      >
        Send it as{" "}
        <Text
          span
          inherit
          ff="monospace"
          c="var(--mantine-color-text)"
        >
          Authorization: Bearer {apiKey.prefix}...
        </Text>{" "}
        with every request.
      </Text>

      <Group justify="flex-end">
        <Button
          fz={11}
          onClick={onDone}
        >
          Done
        </Button>
      </Group>
    </Stack>
  );
};
