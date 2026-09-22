import {
  Accordion,
  Alert,
  Code,
  EmptyState,
  ScrollArea,
  Skeleton,
  Stack,
  Text,
} from "@mantine/core";

import { useEndpoints } from "@/features/endpoint/api/get-endpoints";
import { getApiErrorMessage } from "@/lib/axios";

export const EndpointList = () => {
  const endpoints = useEndpoints();

  if (endpoints.isPending) {
    return (
      <Stack gap="xs">
        <Skeleton
          height={48}
          radius="md"
        />
        <Skeleton
          height={48}
          radius="md"
        />
        <Skeleton
          height={48}
          radius="md"
        />
      </Stack>
    );
  }

  if (endpoints.isError) {
    return (
      <Alert
        color="red"
        variant="light"
      >
        {getApiErrorMessage(endpoints.error, "Could not load your endpoints.")}
      </Alert>
    );
  }

  if (endpoints.data.length === 0) {
    return (
      <EmptyState
        title="No endpoints yet"
        description="Create one above to turn a page into an API."
      />
    );
  }

  return (
    <Accordion
      multiple
      variant="separated"
      radius="md"
      // Collapsing an item should discard its panel state rather than keep it
      // alive off-screen.
      keepMounted={false}
    >
      {endpoints.data.map((endpoint) => (
        <Accordion.Item
          key={endpoint.id}
          value={endpoint.id}
        >
          <Accordion.Control>
            {/* `Accordion.Control` renders a button, so the label has to stay
                phrasing content: `span` keeps `Text` off its default `p`. */}
            <Text
              span
              display="block"
              fz="sm"
              fw={500}
            >
              {endpoint.name}
            </Text>
            <Text
              span
              display="block"
              fz="xs"
              c="dimmed"
              truncate
            >
              {endpoint.url}
            </Text>
          </Accordion.Control>
          <Accordion.Panel>
            <Stack gap="xs">
              <Text fz="sm">{endpoint.description}</Text>
              <ScrollArea.Autosize mah={240}>
                <Code block>{JSON.stringify(endpoint.schema, null, 2)}</Code>
              </ScrollArea.Autosize>
            </Stack>
          </Accordion.Panel>
        </Accordion.Item>
      ))}
    </Accordion>
  );
};
