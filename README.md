# web2api

Turn any URL + plain description into a REST endpoint that returns structured JSON data.

## Running locally

You need Docker, [uv](https://docs.astral.sh/uv/) and Node.js.
Postgres runs in Docker, while the backend and frontend run on your machine.

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

The other variables have working defaults in the example file.

### Backend

From `backend/`:

```sh
docker compose up -d postgres
uv run alembic upgrade head
uv run fastapi dev
```

The API runs at http://localhost:8000, with interactive docs at http://localhost:8000/docs.
If port 5432 is taken, start Postgres with `POSTGRES_PORT=5433 docker compose up -d postgres` and change the port in `DATABASE_URL` to match.

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
- Frontend lint and formatting, from `frontend/`: `npm run lint`, with `npm run format` to fix formatting.

## Architecture

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

### Errors

| Status | Meaning |
| --- | --- |
| 422 | The URL points to a private or reserved address. |
| 502 | The page could not be fetched: an error status, a connection, DNS or TLS failure, too many redirects, a redirect to a non-HTTP URL, a non-HTML response, or a response over 5 MB. |
| 502 | The AI model could not be reached, failed, or returned an unusable plan, or its selectors found none of the requested data on the page. |
| 503 | The AI model is rate limited. |
| 504 | The page took longer than 20 seconds, or the AI model took longer than 3 minutes. |

Each error's `detail` says what went wrong in plain language, and the app shows it as is.
The technical cause, such as a provider error or the selectors that missed, goes to the server log instead.
