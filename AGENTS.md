# Project Overview

web2api is a web app that turns a URL plus a plain-English description of the desired data into a REST API.

## MVP Core

1. User submits a URL (e.g., https://news.ycombinator.com/) + a plain-English description of the data they want (e.g., titles and urls of the top stories)
2. Fetch and clean the HTML, then have the LLM look at the page content + the user's description, infer a JSON schema, and generate extraction logic (css selectors).
3. Persist that "recipe" (selectors or request template + output schema) in Postgres.

## Backend Conventions

- Version API routes at the parent router, with resource routes such as `POST /v1/endpoints`.
- Keep route handlers focused on HTTP concerns and place request and response models in `app/schemas`.
- Put business logic and infrastructure error translation in `app/services`.
- Persist endpoints with a UUID, URL, description, and PostgreSQL JSONB extraction schema.
- The API registers no CORS middleware, since the Vite dev proxy keeps browser requests same-origin, so a split-origin deployment has to add `CORSMiddleware`.

## Frontend Conventions

- The frontend lives in `frontend/` and runs on React 19, Vite, Mantine, React Router data mode, TanStack Query, axios, and zod.
- Follow bulletproof-react layout: app setup in `src/app`, feature code in `src/features/<feature>/{api,components}`, shared UI in `src/components`, shared clients in `src/lib`.
- Import across those directories with the `@/*` alias, and keep relative paths for siblings within one directory.
- Keep imports unidirectional: features may import from `src/lib` and `src/components`, but never from `src/app` or another feature.
- Declare routes in `src/app/router.tsx`, keeping route components in `src/app/routes` nested under `RootLayout` from `src/components/layout`.
- Import route components statically, and reach for `lazy` only when a route pulls in a heavy dependency, since code splitting costs a round trip before that route renders.
- Register providers in `src/app/provider.tsx`.
- Call the API through `apiClient` in `src/lib/axios.ts`, whose `/v1` base URL `vite.config.ts` proxies to the backend in development.
- Pair each endpoint with its zod schemas and TanStack Query hook in one feature module, parsing the response rather than casting it.
- Share one zod schema per payload between form validation, via `schemaResolver` from `@mantine/form`, and the request it feeds.

## Commands

- Backend, from `backend/`: `docker compose up -d postgres` once, then `uv run fastapi dev`.
- Frontend, from `frontend/`: `npm run dev`, `npm run build`, `npm run lint`.
