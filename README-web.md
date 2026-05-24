# Automata Visualizer — Web App

The desktop PyQt6 app has been converted into a deployable Flask web app
that reuses the same `core/automata_engine.py` logic. Visualization is
rendered in the browser using Graphviz compiled to WebAssembly via
[`@viz-js/viz`](https://github.com/mdaines/viz-js), so **no Graphviz
binary is required on the server**.

## Local development

```bash
python -m venv .venv
. .venv/Scripts/activate          # Windows
# . .venv/bin/activate            # macOS/Linux

pip install -r requirements-web.txt
python app.py
```

Then open http://localhost:5000.

## Production (gunicorn)

```bash
pip install -r requirements-web.txt
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

## Docker

```bash
docker build -t automata-web .
docker run --rm -p 8000:8000 automata-web
```

## Deploy

* **Heroku / Render / Railway / Fly.io** — `Procfile` and `runtime.txt`
  are provided. Point the platform at this repository; the build will
  use `requirements-web.txt`.
* **Any container host** — use the included `Dockerfile`.

The `PORT` environment variable is honored by both `app.py` (Flask dev
server) and the `Procfile` / `Dockerfile` (gunicorn).

## Cloudflare Pages + Azure Container Apps

This repository is prepared for a split deploy:

* Frontend: Cloudflare Pages
* Backend: Azure Container Apps
* Trigger: GitHub Actions on push to `main`

Set these repository secrets before enabling the workflow:

* `AZURE_CREDENTIALS` - Azure service principal JSON used by `azure/login`
* `AZURE_RESOURCE_GROUP` - Resource group containing the Container App and ACR
* `AZURE_ACR_NAME` - Azure Container Registry name, for example `automataacr`
* `AZURE_CONTAINERAPP_NAME` - Container App name, for example `automata-web`
* `CLOUDFLARE_API_TOKEN` - Cloudflare API token with Pages write access
* `CLOUDFLARE_ACCOUNT_ID` - Cloudflare account ID
* `CLOUDFLARE_PAGES_PROJECT` - Cloudflare Pages project name
* `AUTOMATA_API_BASE` - Public backend URL, for example `https://api.example.com`

If you use a custom domain in Cloudflare, set `AUTOMATA_API_BASE` to that
domain so the browser and API CORS line up cleanly.

## HTTP API

| Method | Path                       | Description                              |
|--------|----------------------------|------------------------------------------|
| GET    | `/`                        | Single-page UI                           |
| GET    | `/api/expressions`         | List predefined regex expressions        |
| GET    | `/api/automaton?expression=NAME` | DFA (DOT + structured), CFG, PDA  |
| POST   | `/api/process`             | `{expression, input, mode: dfa\|pda}` → steps + accepted |
| GET    | `/healthz`                 | Liveness probe                           |

## GitHub Actions workflow

The workflow in `.github/workflows/deploy.yml` builds the static frontend
into `dist/`, injects the backend API URL, deploys it to Cloudflare Pages,
then builds and updates the Azure backend container.

## Desktop app

The original PyQt6 desktop app remains intact in `ui/` and `main.py`. The
desktop dependencies in `requirements.txt` are **not** required to run
the web app — only `requirements-web.txt` is.
