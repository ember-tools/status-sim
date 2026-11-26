# Status Sim

Radio and vehicle status exercises for fire brigades, at
[statussim.emberbox.app](https://statussim.emberbox.app). A dispatch centre, unit leaders and
vehicles play one exercise together, each role on its own device: vehicles set their status on a
status keypad, the dispatch centre sees every report and hands out incidents from prepared
scenarios, and unit leaders call vehicles to their own channel. The interface is German.

Status Sim is one of the tools of the [Emberbox](https://emberbox.app).

## Features

- **Vehicle:** status keypad (statuses 1 to 8, request to talk 5, flash 0) with the transitions of
  the real radio, short status messages, messages from dispatch and the unit leader, requests to
  switch channels.
- **Dispatch:** several dispatchers share one exercise and take over vehicles; requests to talk are
  sorted by waiting time, vehicles are grouped by urgency; status, messages and notes per vehicle.
- **Unit leader:** takes over vehicles, asks them to switch to its channel and works through their
  scenarios.
- **Scenarios:** the JSON files in `src/static/scenarios/` generate the radio messages of an
  incident as a checklist shared by dispatch and unit leader.

Every exercise has three codes, one per role. There are no accounts.

## Data and retention

An exercise lives in the server's memory and, with `REDIS_URL` set, in Redis under the key
`ls:<dispatch code>`: the names of the dispatch centre, dispatchers, unit leaders and vehicles,
statuses, messages, notes and scenario progress.

**An exercise is deleted seven days after its last access.** Every request that uses one of its
codes counts as an access (polling, actions, opening one of its pages) and renews the Redis
`EXPIRE` of its key to seven days. Once seven days pass without any, the key expires in Redis and
the server drops the exercise and its codes from memory within a minute. A vehicle that has not
polled for five minutes is removed from its exercise earlier.

With Redis persistence on (AOF), an expired key leaves the append-only file only when Redis
rewrites it. `compose.prod.yml` therefore sets `auto-aof-rewrite-min-size` to 1 MB, so even a small
instance rewrites the file regularly and expired exercises do not linger on disk; keep that setting
when running Redis elsewhere.

In the browser, Status Sim keeps per exercise the name and radio channel of dispatchers and unit
leaders and whether requests to talk are combined (`localStorage` keys `statussim.dispatch` and
`statussim.unit-leader`, entries dropped after seven days), and the colour mode
(`vueuse-color-scheme`). `frontend/browser-storage.json` lists the keys the code uses.

## Running it

The image is `ghcr.io/ember-tools/status-sim`, built by CI on every push to `main`. It serves API
and frontend on port 8000, runs as a non-root user and reports its health at `/api/health`.

`compose.prod.yml` is a template for running it with Redis behind Traefik (entrypoint
`websecure`, certificate resolver `letsencrypt`, host `statussim.emberbox.app`); adapt the labels
to your proxy. The `redis-data` volume holds the exercises; the app container keeps no state.
The proxy must pass `X-Forwarded-*` headers; uvicorn runs with `--proxy-headers`.

| Variable | Default | Meaning |
|---|---|---|
| `REDIS_URL` | none | Redis for persistence, such as `redis://redis:6379`. Without it, exercises live only in memory and are lost on restart. |
| `CORS_ORIGINS` | `https://statussim.emberbox.app` | Comma-separated origins allowed to call the API from another site. |
| `LOG_FORMAT` | `json` in the image | `json` for structured logs, otherwise plain text. |
| `LOG_LEVEL` | `INFO` | Log level. |
| `DEMO_MODE` | `false` | Starts a demo exercise with simulated vehicles. |
| `FRONTEND_DIR` | `src/frontend_dist`, else `frontend/dist` | Where the built frontend is read from. |

## Development

Everything runs through `./toolchain.sh`, inside the nix shell of `shell.nix` via direnv
(`direnv allow` once). `./toolchain.sh help` lists all commands.

```sh
./toolchain.sh be-install && ./toolchain.sh fe-install
./toolchain.sh be-dev      # backend on port 8000
./toolchain.sh fe-dev      # Vite dev server, proxies /api to the backend
./toolchain.sh verify      # everything CI runs
./toolchain.sh fe-lint     # ESLint, duplication, comments, em dashes, browser storage
./toolchain.sh docker-app  # local stack with Redis from compose.yml
```

The backend is FastAPI (`src/`), the frontend Vue 3 with [`@emberbox/ui`](https://github.com/ember-tools/emberbox)
and Nuxt UI (`frontend/`). The frontend has no vue-router; `src/navigation.ts` maps the address to
a view. The landing page, the help overview (`/hilfe`) and one page per help topic (`/hilfe/<topic>`,
listed in `frontend/src/helpTopics.ts`) are prerendered at build time; the backend serves
them from `pages/`, every other path gets the single-page shell with `X-Robots-Tag: noindex`.

## License

[GPL-3.0](LICENSE).
