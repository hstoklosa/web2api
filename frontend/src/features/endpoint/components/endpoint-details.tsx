import { Alert, Badge, Group, Paper, Stack, Text } from "@mantine/core";
import { Send } from "lucide-react";

import { Button } from "@/components/ui/button";
import { JsonViewer } from "@/components/ui/json-viewer";
import type { Endpoint } from "@/features/endpoint/api/endpoint";
import {
  getEndpointDataPath,
  useEndpointData,
} from "@/features/endpoint/api/get-endpoint-data";
import { apiClient, getApiErrorMessage } from "@/lib/axios";

import { ResponseFormat } from "./response-format";

const SectionLabel = ({ children }: { children: React.ReactNode }) => {
  return (
    <Text
      fz={11}
      fw={500}
      tt="uppercase"
      lts="0.05em"
      c="dimmed"
    >
      {children}
    </Text>
  );
};

type EndpointDetailsProps = {
  endpoint: Endpoint;
};

export const EndpointDetails = ({ endpoint }: EndpointDetailsProps) => {
  // Each request scrapes the live page, so wait for the user to send one.
  const endpointData = useEndpointData(endpoint.id, { enabled: false });

  const requestPath = `${apiClient.defaults.baseURL}${getEndpointDataPath(endpoint.id)}`;

  return (
    <Stack gap="md">
      <Text
        fz="sm"
        c="dimmed"
      >
        {endpoint.description}
      </Text>

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
          <Badge
            variant="light"
            color="teal"
            radius="sm"
          >
            GET
          </Badge>
          <Text
            flex={1}
            miw={0}
            ff="monospace"
            fz="xs"
            truncate
            title={requestPath}
          >
            {requestPath}
          </Text>
          <Button
            size="xs"
            fz={11}
            leftSection={<Send size={12} />}
            loading={endpointData.isFetching}
            onClick={() => endpointData.refetch()}
          >
            Send Request
          </Button>
        </Group>
      </Paper>

      <Stack gap={6}>
        <SectionLabel>Response format</SectionLabel>
        <ResponseFormat schema={endpoint.schema} />
      </Stack>

      <Stack gap={6}>
        <SectionLabel>Response</SectionLabel>
        {endpointData.isError ? (
          <Alert
            color="red"
            variant="light"
          >
            {getApiErrorMessage(
              endpointData.error,
              "Could not fetch this endpoint's data.",
            )}
          </Alert>
        ) : endpointData.data !== undefined ? (
          <JsonViewer data={endpointData.data} />
        ) : (
          <Text
            fz="xs"
            c="dimmed"
          >
            {endpointData.isFetching
              ? "Scraping the page..."
              : "Send the request to see what this endpoint returns."}
          </Text>
        )}
      </Stack>
    </Stack>
  );
};
