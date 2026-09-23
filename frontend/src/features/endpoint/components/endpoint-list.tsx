import {
  Accordion,
  Alert,
  CloseButton,
  Code,
  EmptyState,
  ScrollArea,
  Skeleton,
  Stack,
  Text,
  TextInput,
} from "@mantine/core";
import { useMemo } from "react";
import { useSearchParams } from "react-router";

import { useEndpoints } from "@/features/endpoint/api/get-endpoints";
import { getApiErrorMessage } from "@/lib/axios";

const SEARCH_PARAM = "q";

export const EndpointList = () => {
  const endpoints = useEndpoints();
  const [searchParams, setSearchParams] = useSearchParams();

  const search = searchParams.get(SEARCH_PARAM) ?? "";

  const matches = useMemo(() => {
    const term = search.trim().toLowerCase();
    const data = endpoints.data ?? [];

    if (term === "") {
      return data;
    }

    return data.filter((endpoint) =>
      [endpoint.name, endpoint.url, endpoint.description].some((field) =>
        field.toLowerCase().includes(term),
      ),
    );
  }, [endpoints.data, search]);

  const handleSearchChange = (value: string) => {
    setSearchParams(
      (params) => {
        if (value === "") {
          params.delete(SEARCH_PARAM);
        } else {
          params.set(SEARCH_PARAM, value);
        }
        return params;
      },
      // Typing is not navigation, so keep it out of the history stack.
      { replace: true },
    );
  };

  if (endpoints.isPending) {
    return (
      <Stack gap="xs">
        <Skeleton
          height={48}
          radius="sm"
        />
        <Skeleton
          height={48}
          radius="sm"
        />
        <Skeleton
          height={48}
          radius="sm"
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

  // Nothing to search through, so the input would only be in the way.
  if (endpoints.data.length === 0) {
    return (
      <EmptyState
        title="No endpoints yet"
        description="Create one to turn a page into an API."
      />
    );
  }

  return (
    <Stack gap="xs">
      <TextInput
        aria-label="Search endpoints"
        placeholder="Search endpoints"
        radius="sm"
        value={search}
        onChange={(event) => handleSearchChange(event.currentTarget.value)}
        rightSectionPointerEvents="all"
        rightSection={
          search === "" ? null : (
            <CloseButton
              aria-label="Clear search"
              onClick={() => handleSearchChange("")}
            />
          )
        }
      />

      {matches.length === 0 ? (
        <EmptyState
          mt={64}
          title="No matching endpoints"
          description={`Nothing matches "${search.trim()}".`}
        />
      ) : (
        <Accordion
          multiple
          variant="separated"
          radius="sm"
          // Collapsing an item should discard its panel state rather than keep
          // it alive off-screen.
          keepMounted={false}
        >
          {matches.map((endpoint) => (
            <Accordion.Item
              key={endpoint.id}
              value={endpoint.id}
            >
              <Accordion.Control>
                {/* `Accordion.Control` renders a button, so the label has to
                    stay phrasing content: `span` keeps `Text` off its default
                    `p`. */}
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
                    <Code block>
                      {JSON.stringify(endpoint.schema, null, 2)}
                    </Code>
                  </ScrollArea.Autosize>
                </Stack>
              </Accordion.Panel>
            </Accordion.Item>
          ))}
        </Accordion>
      )}
    </Stack>
  );
};
