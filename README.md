# web2api

Turn any URL plus a plain-English description into a REST endpoint that returns structured JSON.

Give web2api a page such as `https://news.ycombinator.com/` and ask for "titles and urls of the top stories".
An LLM reads the page once, infers a JSON schema and writes CSS selectors for it, and web2api saves that as a recipe.
From then on, every call to the endpoint fetches the live page and runs the selectors, with no further model calls, so responses are fast, cheap and deterministic.

## Features

- **Endpoints from a sentence.** Describe the data you want, and get back a named endpoint with a JSON schema, either a single object or a list of records.
- **Typed output.** Fields are typed as strings, integers, numbers or booleans, and values such as `$1,299.00` or `In Stock` are coerced to match.
- **Verified before saving.** Every generated selector is checked against the real page, so an endpoint is only created if it actually finds the data.
- **API keys.** Call your endpoints from scripts and servers with revocable, hashed API keys, while the browser app uses httpOnly cookie sessions.
- **Safe by default.** Server-side fetches are locked to the public internet on every connection and redirect, with size, time and per-user rate limits.

## Example

Create an endpoint:

```sh
curl http://localhost:8000/v1/endpoints \
  -H "Authorization: Bearer w2a_..." \
  -H "Content-Type: application/json" \
  -d '{"url": "https://news.ycombinator.com/", "description": "titles and urls of the top stories"}'
```

web2api names and describes the endpoint and returns the schema it inferred:

```json
{
  "id": "3f0c7b9e-...",
  "name": "hn_top_stories",
  "url": "https://news.ycombinator.com/",
  "description": "Returns a list of the top stories on the Hacker News front page, each with a title and url.",
  "schema": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "title": { "type": "string" },
        "url": { "type": "string" }
      }
    }
  },
  "created_at": "...",
  "updated_at": "..."
}
```

Then call it whenever you need fresh data:

```sh
curl http://localhost:8000/v1/endpoints/3f0c7b9e-.../data \
  -H "Authorization: Bearer w2a_..."
```

```json
[
  { "title": "Show HN: ...", "url": "https://example.com/..." },
  { "title": "...", "url": "https://..." }
]
```

## Tech stack

| Layer | Tools |
| --- | --- |
| Backend | Python 3.14, FastAPI, SQLAlchemy 2 (async) with asyncpg, Alembic, Pydantic, httpx, BeautifulSoup |
| AI | OpenAI SDK with structured outputs, pointed at OpenRouter by default, so any compatible model works |
| Data | PostgreSQL 17 with JSONB for recipes, Redis 8 for rate limit counters |
| Auth | JWT access and refresh tokens in httpOnly cookies, Argon2 password hashing, SHA-256 hashed API keys |
| Frontend | React 19, TypeScript, Vite, Mantine, React Router, TanStack Query, axios, zod |
| Tooling | uv, Ruff, pytest, ESLint, Prettier, Docker Compose |

## Running locally

You need Docker, [uv](https://docs.astral.sh/uv/) and Node.js.
Postgres and Redis run in Docker, while the backend and frontend run on your machine.

### Configuration

Copy the example environment file and fill it in:

```sh
cp backend/.env.example backend/.env
```

| Variable | Value |
| --- | --- |
| `OPENAI_API_KEY` | An API key for the provider at `OPENAI_BASE_URL`, which defaults to OpenRouter. |
| `DATABASE_URL` | `postgresql+asyncpg://web2api:web2api@localhost:5432/web2api` for the Postgres in `docker-compose.yaml`. |
| `SECRET_KEY` | A random string for signing session tokens, such as the output of `openssl rand -hex 32`. |

`REDIS_URL` already points at the Redis in `docker-compose.yaml`, and the other variables have working defaults in the example file.

### Backend

From `backend/`:

```sh
docker compose up -d postgres redis
uv run alembic upgrade head
uv run fastapi dev
```

The API runs at http://localhost:8000, with interactive docs at http://localhost:8000/docs.
If port 5432 is taken, start Postgres with `POSTGRES_PORT=5433 docker compose up -d postgres` and change the port in `DATABASE_URL` to match.
The same goes for Redis with `REDIS_PORT` and `REDIS_URL`.

The app does not create tables itself, so run `uv run alembic upgrade head` again whenever you pull changes that add migrations.
It only applies the migrations the database has not seen yet, so running it when nothing changed does nothing.

### Frontend

From `frontend/`:

```sh
npm install
npm run dev
```

The app runs at http://localhost:5173.
The dev server proxies `/v1` to the backend on port 8000, so start the backend first.

### Changing the database schema

The schema is managed with [Alembic](https://alembic.sqlalchemy.org/) migrations in `backend/migrations/versions`.
After changing a model in `backend/app/models`, generate a migration from `backend/`:

```sh
uv run alembic revision --autogenerate -m "add foo to endpoints"
```

Read the generated file before applying it.
Autogenerate turns a renamed column into a dropped column and a new one, which loses its data, and a new non-null column on a table with rows needs a `server_default` or a backfill.
Then apply it with `uv run alembic upgrade head`, and commit it together with the model change.

`uv run alembic check` fails if the models have changes that no migration covers, and needs the database to be up to date first.
`uv run alembic current` shows which migration the database is at, and `uv run alembic downgrade -1` undoes the last one.

### Tests and lint

- Backend tests, from `backend/`: `uv run pytest`.
- Backend lint and formatting, from `backend/`: `uv run ruff check --fix` and `uv run ruff format`, configured in `backend/pyproject.toml`.
- Frontend lint and formatting, from `frontend/`: `npm run lint`, with `npm run format` to fix formatting.

## Calling the API

The app signs you in with cookies, which only a browser sends.
To call the API from a script or a server, create an API key on the API keys page and send it as a Bearer token:

```sh
curl http://localhost:8000/v1/endpoints/<endpoint id>/data \
  -H "Authorization: Bearer w2a_..."
```

A key acts as the user who created it, on every route except managing API keys, which only a signed-in browser can do.
That way a leaked key can't create more keys or revoke the others, so you can always revoke it from the app.
The key is shown once when you create it, and the server only keeps its SHA-256 hash.
Each user can have up to 25 keys, and the API keys page shows when each one was last used, to the minute.
A request that sends a key is judged on the key alone, so a wrong or revoked key returns a 401 even alongside a valid session cookie.

### Routes

All routes live under `/v1`, and interactive docs are at `/docs`.

| Route | Purpose |
| --- | --- |
| `POST /v1/auth/register`, `POST /v1/auth/login` | Create an account or sign in, setting the session cookies. |
| `POST /v1/auth/refresh`, `POST /v1/auth/logout` | Issue a new access token from the refresh cookie, or end the session. |
| `GET /v1/auth/me` | The signed-in user. |
| `POST /v1/endpoints` | Build an endpoint from `url` and `description`. |
| `GET /v1/endpoints`, `GET /v1/endpoints/{id}` | List your endpoints, or get one with its schema. |
| `GET /v1/endpoints/{id}/data` | Fetch the page now and return the extracted data. |
| `DELETE /v1/endpoints/{id}` | Delete an endpoint. |
| `GET /v1/api-keys`, `POST /v1/api-keys`, `DELETE /v1/api-keys/{id}` | Manage API keys, from a browser session only. |

## Architecture

```mermaid
flowchart LR
    subgraph create["POST /v1/endpoints"]
        A[Fetch page] --> B[Clean HTML] --> C[LLM writes plan] --> D[Validate selectors] --> E[(Save recipe)]
    end
    subgraph call["GET /v1/endpoints/{id}/data"]
        F[(Load recipe)] --> G[Fetch page] --> H[Clean HTML] --> I[Run selectors] --> J[Typed JSON]
    end
```

### Building an endpoint

1. **Fetch.** The page is downloaded through an httpx transport that checks every connection against private and reserved addresses, described under [Limits and safety](#limits-and-safety).
2. **Clean.** Scripts, styles, SVGs, iframes, comments, inline styles and event handlers are stripped, leaving the content markup, which is then capped at 80,000 characters for the model.
3. **Plan.** The model gets the cleaned HTML and the user's description, and returns a plan through structured output, parsed straight into a Pydantic model.
   The plan holds the extraction schema, plus a snake_case name and a description for the endpoint.
4. **Validate.** Field names must be unique, every selector must be valid CSS, and every field must match at least one element on the fetched page.
   A plan that fails is rejected with a plain-language error rather than saved broken.
5. **Save.** The extraction schema is stored in a PostgreSQL JSONB column on the user's endpoint.

A saved recipe looks like this:

```json
{
  "item_selector": "tr.athing",
  "fields": [
    { "name": "title", "selector": ".titleline > a", "type": "string", "source": { "kind": "text" } },
    { "name": "url", "selector": ".titleline > a", "type": "string", "source": { "kind": "attribute", "name": "href" } },
    { "name": "points", "selector": ".score", "relative_to": "next_sibling", "type": "integer", "source": { "kind": "text" } }
  ]
}
```

With an `item_selector`, the endpoint returns a list with one record per matching element, and field selectors run inside each one.
Without it, the endpoint returns a single object and field selectors run against the whole page.
`relative_to: "next_sibling"` covers layouts like Hacker News, where one record is spread over two sibling rows.

### Calling an endpoint

The data route loads the recipe, fetches and cleans the live page, and runs the selectors with BeautifulSoup.
Each value is read from the element's text or an attribute, then coerced to the field's type, so `"1,204 points"` becomes `1204`.
The model is never called here, which keeps each call to a single page fetch plus parsing.

### Design decisions

- **The LLM runs once per endpoint, not once per request.** Selectors are generated up front and reused, which makes calls fast, cheap and repeatable, and keeps the model's output reviewable as plain data.
- **HTML parsing runs in worker processes.** Parsing a large page takes seconds of pure-Python CPU work, which would stall every other request on the event loop, and threads do not help while the parser holds the GIL.
  Argon2 hashing is kept off the event loop too.
- **Database connections are released before slow work.** Requests commit before fetching a page or calling the model, so a slow site cannot drain the connection pool.
- **Every failure has a status and a message.** Services translate fetch, model and validation failures into typed application errors with their own HTTP status, and log the technical cause separately.
- **Ownership is enforced in queries.** Every read, update and delete is scoped by user, and another user's endpoint returns 404 rather than 403, so ids cannot be probed.

### Project layout

```
backend/
  app/
    api/routes/   HTTP handlers for auth, endpoints and API keys
    schemas/      Pydantic request, response and extraction models
    services/     Fetching, cleaning, planning, validation and extraction
    core/         Config, SSRF-safe HTTP, rate limiting, security, errors
    models/       SQLAlchemy models
  migrations/     Alembic migrations
  tests/          pytest suite
frontend/
  src/
    app/          Router, providers, theme and route components
    features/     auth, endpoint and api-keys, each with its api hooks and components
    components/   Shared UI
    lib/          axios client, session handling and query client
```

The frontend follows the [bulletproof-react](https://github.com/alan2207/bulletproof-react) layout.
Each API call is paired with a zod schema that parses its response and a TanStack Query hook, and form validation reuses the same schemas.
A 401 triggers one token refresh and a replay of the request, and a 401 after that ends the session.

## Limits and safety

web2api fetches the page behind every URL you submit, both when it builds an endpoint and on every call to that endpoint's data.
Those fetches run from the server, so they are restricted to the public internet.

### Private addresses are blocked

URLs that resolve to a private or reserved address are rejected with a 422.
That covers loopback (`localhost`, `127.0.0.1`, `::1`), private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `fc00::/7`), link-local addresses including cloud metadata at `169.254.169.254`, carrier-grade NAT (`100.64.0.0/10`), and other reserved ranges.
Numeric spellings such as `http://2130706433/` or `http://0x7f.1/` are caught too, because the check runs on the addresses the hostname actually resolves to.
A hostname is rejected if any of its addresses is private, even when others are public.

The check runs when each connection is opened, and the connection goes to the exact address that was checked.
So redirects to a private address are blocked at that hop, and a DNS answer that changes between the check and the connection cannot slip past it.
TLS certificates are still verified against the hostname.
Proxy settings from the environment are ignored, so they cannot route requests around the check.

This means you cannot point web2api at a service on your own machine or network, such as `http://localhost:3000`.
Any port on a public host is allowed.

### Fetch limits

| Limit | Value |
| --- | --- |
| Redirects followed | 5 |
| Connect timeout | 5 seconds |
| Read timeout, per chunk | 10 seconds |
| Total time per fetch | 20 seconds |
| Response size, after decompression | 5 MB |
| Content types | `text/html`, `application/xhtml+xml`, or none |

Requests send a desktop Chrome `User-Agent`, since many sites turn away clients that don't look like a browser.
Pages are decoded with the charset from the `Content-Type` header, falling back to UTF-8.

Only the HTML the server returns is read, and no JavaScript runs, so data that a page renders in the browser is out of reach.

### Generation limits

Building an endpoint asks the AI model for an extraction plan once.
Each attempt may take up to 2 minutes, and timeouts, rate limits and provider errors are retried up to twice, but the whole step is cut off after 3 minutes.
The plan's selectors are then checked against the fetched page, and the endpoint is only saved if every field matches something.

### Rate limits

Each user gets their own budget per group of routes, counted over a moving window.
Requests made with an API key count against the budget of the user who owns it, the same as requests from the app.

| Routes | Limit |
| --- | --- |
| `POST /v1/endpoints` | 10 per hour |
| `GET /v1/endpoints/{id}/data` | 60 per minute |
| `GET /v1/endpoints`, `GET /v1/endpoints/{id}`, `DELETE /v1/endpoints/{id}` | 120 per minute, shared |
| `POST /v1/api-keys` | 20 per hour |

Going over a limit returns a 429 with a `Retry-After` header in seconds.
The counters live in Redis, so they hold across workers and API restarts.
If Redis refuses connections or takes over half a second to answer, requests are allowed through and the error is logged, so an outage never takes the API down.

### Errors

| Status | Meaning |
| --- | --- |
| 401 | You are not signed in, or the API key is wrong or revoked. |
| 422 | The URL points to a private or reserved address. |
| 429 | You went over a rate limit. The `Retry-After` header says how many seconds to wait. |
| 502 | The page could not be fetched: an error status, a connection, DNS or TLS failure, too many redirects, a redirect to a non-HTTP URL, a non-HTML response, or a response over 5 MB. |
| 502 | The AI model could not be reached, failed, or returned an unusable plan, or its selectors found none of the requested data on the page. |
| 503 | The AI model is rate limited. |
| 504 | The page took longer than 20 seconds, or the AI model took longer than 3 minutes. |

Each error's `detail` says what went wrong in plain language, and the app shows it as is.
The technical cause, such as a provider error or the selectors that missed, goes to the server log instead.

## License

[MIT](LICENSE)
