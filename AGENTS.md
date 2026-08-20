# Project Overview

web2api is a web app that turns a URL plus a plain-English description of the desired data into a REST API.

## MVP Core

1. User submits a URL (e.g., https://news.ycombinator.com/) + a plain-English description of the data they want (e.g., titles and urls of the top stories)
2. Fetch and clean the HTML, then have the LLM look at the page content + the user's description, infer a JSON schema, and generate extraction logic (css selectors).
3. Persist that "recipe" (selectors or request template + output schema) in Postgres.
