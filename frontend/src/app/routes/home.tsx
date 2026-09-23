import {
  Flex,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";
import { Link } from "react-router";

import { Button } from "@/components/ui/button";

const requestSnippet = `curl -X GET \\
  /v1/endpoints/dba9303c-fd9d-4982-bafd-05e7d872a722/data \\
  -H "Authorization: Bearer <token>"`;

const responseSnippet = `[
  {
    "rank": 1,
    "title": "Samsung is expected to more…",
    "score": 142,
    "comments_count": 102
  }
]`;

const Nav = () => {
  return (
    <Group
      justify="space-between"
      py="md"
    >
      <Text
        fw={700}
        size="lg"
      >
        web2api
      </Text>
    </Group>
  );
};

const Hero = () => {
  return (
    <Stack
      align="center"
      ta="center"
      gap="md"
    >
      <Title order={1}>Turn any webpage into a REST API</Title>
      <Text
        c="dimmed"
        size="lg"
        maw={560}
      >
        Describe the data you want in plain English. Get back a stable JSON API
        you can poll anytime - no scraping code, no maintenance.
      </Text>
      <Group>
        <Button
          size="md"
          component={Link}
          to="/register"
        >
          Get started free
        </Button>
        <Button
          variant="default"
          size="md"
          component={Link}
          to="/login"
        >
          Log in
        </Button>
      </Group>
    </Stack>
  );
};

const HowItWorks = () => {
  return (
    <SimpleGrid
      cols={{ base: 1, sm: 3 }}
      spacing="lg"
      maw={1320}
      mx="auto"
      w="100%"
    >
      <Paper
        withBorder
        radius="md"
        p="sm"
      >
        <Text
          fw={700}
          c="black"
          size="sm"
        >
          01
        </Text>
        <Text
          fw={600}
          mb={6}
        >
          Describe
        </Text>
        <Text
          size="xs"
          c="dimmed"
          mb={8}
        >
          Paste a URL and describe the data you want, in plain English.
        </Text>
        <Stack gap={2}>
          <Text
            ff="monospace"
            fz={11}
            c="dimmed"
          >
            POST /v1/endpoints
          </Text>
          <Text
            ff="monospace"
            fz={11}
          >
            url: news.ycombinator.com
          </Text>
          <Text
            ff="monospace"
            fz={11}
          >
            description: "List of all articles"
          </Text>
        </Stack>
      </Paper>

      <Paper
        withBorder
        radius="md"
        p="sm"
      >
        <Text
          fw={700}
          c="black"
          size="sm"
        >
          02
        </Text>
        <Text
          fw={600}
          mb={6}
        >
          Send a request
        </Text>
        <Text
          size="xs"
          c="dimmed"
          mb={8}
        >
          Call your endpoint like any REST API - no scraping code, just an HTTP
          request.
        </Text>
        <Text
          ff="monospace"
          fz={11}
          style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}
        >
          {requestSnippet}
        </Text>
      </Paper>

      <Paper
        withBorder
        radius="md"
        p="sm"
      >
        <Text
          fw={700}
          c="black"
          size="sm"
        >
          03
        </Text>
        <Text
          fw={600}
          mb={6}
        >
          Poll forever
        </Text>
        <Text
          size="xs"
          c="dimmed"
          mb={8}
        >
          We re-run the saved extraction and return fresh JSON - fast, no more
          LLM calls.
        </Text>
        <Text
          ff="monospace"
          fz={11}
          style={{ whiteSpace: "pre" }}
        >
          {responseSnippet}
        </Text>
      </Paper>
    </SimpleGrid>
  );
};

const HomeRoute = () => {
  // The concrete demo content doesn't fit a phone viewport without
  // scrolling, so the fixed-height, no-scroll layout only applies from the
  // `sm` breakpoint up - narrower screens fall back to normal page flow.
  const isDesktop = useMediaQuery("(min-width: 48em)");

  return (
    <Flex
      direction="column"
      h={isDesktop ? "100dvh" : "auto"}
      px="md"
      style={{ overflow: isDesktop ? "hidden" : "visible" }}
    >
      <Nav />
      <Flex
        flex={1}
        direction="column"
        justify="center"
        gap="xl"
        py={isDesktop ? undefined : "xl"}
        style={{
          minHeight: 0,
          overflow: isDesktop ? "hidden" : "visible",
        }}
      >
        <Hero />
        <HowItWorks />
      </Flex>
    </Flex>
  );
};

export default HomeRoute;
