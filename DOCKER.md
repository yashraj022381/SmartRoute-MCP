# Phase 6 — Running SmartRoute-MCP with Docker

This lets you start the whole system (API + UI + metrics dashboard) with
**one command**, without manually creating a venv or running several
separate terminals by hand.

## Before you start

You still need:
- **Docker Desktop** installed and running (download from https://www.docker.com/products/docker-desktop/)
- **Ollama** installed and running directly on your Windows computer, with
  `llama3.2:1b` pulled (Docker does NOT replace this - your local AI still
  lives outside the sealed box, same as before)
- Your `.env` file with your real `GROQ_API_KEY`, sitting in the project
  folder (same as every previous phase)

## Running it

From the project folder (the one with `Dockerfile` and `docker-compose.yml`
in it), run:

```
docker-compose up --build
```

The first run will take a few minutes (Docker is downloading base images
and installing all our packages inside the sealed box). Every run after
that will be much faster, since Docker reuses what it already built.

You should see logs from all four containers interleaved together
(`smartroute-api`, `smartroute-ui`, `smartroute-prometheus`,
`smartroute-grafana`), ending with something like:

```
smartroute-api | INFO:     Application startup complete.
smartroute-ui  | You can now view your Streamlit app in your browser.
```

Then open your browser to:

- **UI (the actual app):** http://localhost:8501
- **API docs (optional, for exploring):** http://localhost:8000/docs
- **Prometheus (optional, for exploring raw metrics):** http://localhost:9090
- **Grafana (the dashboard with history graphs):** http://localhost:3000
  - Log in with `admin` / `admin` (it'll ask you to change the password,
    or you can skip that for local use)
  - Add a data source: Prometheus, URL `http://prometheus:9090` (that's
    the compose service name again, not localhost - Grafana is asking
    from *inside* Docker's network)
  - From there you can build panels/graphs from any of the metrics in
    `metrics/prometheus_metrics.py` (requests, cost, latency, fallbacks),
    each broken down by tier

## Stopping it

Press `Ctrl+C` in the terminal, then run:

```
docker-compose down
```

This shuts down and removes all four containers. Your code and `.env` are
untouched - only the running containers go away.

## If something goes wrong

**"Can't reach the API server" in the UI:**
Give it a few extra seconds - the API container sometimes takes a moment
longer to finish starting than the UI container. Refresh the page.

**Ollama-related errors:**
Docker containers reach your local Ollama through a special address called
`host.docker.internal` (already configured in `docker-compose.yml`). If you
still get connection errors, double check Ollama is actually running on
your Windows computer (try `ollama list` in a normal terminal, outside
Docker, to confirm).

**Grafana shows "No data":**
Make sure you've actually routed a few queries through the API first (via
the UI, or `test_router.py`/`test_agents.py` run *inside* the container -
running them on your host machine instead won't show up here, since
that's a separate, non-Dockerized process hitting your local `smartroute.db`,
not this container's metrics).

**Note on persistence (database AND vector cache):**
For simplicity, both the SQLite database (`smartroute.db`) *and* the Chroma
vector store (`chroma_data/`) currently live *inside* the container, meaning
your routing history AND your RAG research cache both reset each time you
rebuild. That's a fine trade-off for a learning project - if you want either
(or both) to persist permanently across rebuilds, mounting them as Docker
*volumes* (the same technique used for Grafana's own dashboard settings
above) is a good next improvement to explore.