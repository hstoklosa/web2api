import {
  Alert,
  EmptyState,
  Group,
  Paper,
  Skeleton,
  Stack,
  Text,
} from "@mantine/core";

import type { ApiKey } from "@/features/api-keys/api/api-key";
import { useApiKeys } from "@/features/api-keys/api/get-api-keys";
import { getApiErrorMessage } from "@/lib/axios";

import { RevokeApiKey } from "./revoke-api-key";

const dateFormat = new Intl.DateTimeFormat(undefined, {
  dateStyle: "medium",
  timeStyle: "short",
});

const formatDate = (value: string) => dateFormat.format(new Date(value));

const ApiKeyRow = ({ apiKey }: { apiKey: ApiKey }) => {
  return (
    <Paper
      withBorder
      radius="sm"
      py="xs"
      pl="md"
      pr="xs"
    >
      <Group
        gap="sm"
        wrap="nowrap"
      >
        <Stack
          gap={2}
          flex={1}
          miw={0}
        >
          <Group
            gap="xs"
            wrap="nowrap"
          >
            <Text
              fz="sm"
              fw={500}
              truncate
            >
              {apiKey.name}
            </Text>
            <Text
              ff="monospace"
              fz="xs"
              c="dimmed"
              style={{ flexShrink: 0 }}
            >
              {apiKey.prefix}...
            </Text>
          </Group>
          <Text
            fz="xs"
            c="dimmed"
          >
            Created {formatDate(apiKey.created_at)} ·{" "}
            {apiKey.last_used_at === null
              ? "Never used"
              : `Last used ${formatDate(apiKey.last_used_at)}`}
          </Text>
        </Stack>
        <RevokeApiKey apiKey={apiKey} />
      </Group>
    </Paper>
  );
};

export const ApiKeyList = () => {
  const apiKeys = useApiKeys();

  if (apiKeys.isPending) {
    return (
      <Stack gap="xs">
        <Skeleton
          height={58}
          radius="sm"
        />
        <Skeleton
          height={58}
          radius="sm"
        />
      </Stack>
    );
  }

  if (apiKeys.isError) {
    return (
      <Alert
        color="red"
        variant="light"
      >
        {getApiErrorMessage(apiKeys.error, "Could not load your API keys.")}
      </Alert>
    );
  }

  if (apiKeys.data.length === 0) {
    return (
      <EmptyState
        mt={64}
        title="No API keys yet"
        description="Create one to call your endpoints from scripts and servers."
      />
    );
  }

  return (
    <Stack gap="xs">
      {apiKeys.data.map((apiKey) => (
        <ApiKeyRow
          key={apiKey.id}
          apiKey={apiKey}
        />
      ))}
    </Stack>
  );
};
