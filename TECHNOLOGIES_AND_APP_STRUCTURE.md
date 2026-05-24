# Automata App: Technologies and How It Is Built

## Overview
This project provides two versions of the same automata visualizer:
- **Web app** (Flask backend + browser frontend)
- **Desktop app** (PyQt6)

Both versions share the same core automata logic in `core/automata_engine.py`.

## Technologies Used

### Language
- **Python 3.12** (runtime defined in `runtime.txt`)
- **JavaScript (vanilla)** for frontend behavior in `static/js/app.js`
- **HTML/CSS** for the web UI (`templates/index.html`, `static/css/styles.css`)

### Backend (Web)
- **Flask**: HTTP server and API routes (`app.py`)
- **Flask-Cors**: CORS configuration for `/api/*` and `/healthz`
- **Gunicorn**: production WSGI server (`Procfile`, `Dockerfile`)

### Frontend (Web)
- **Vanilla JS SPA-style UI**: no framework dependency
- **Viz.js (`@viz-js/viz`)** loaded from CDN: renders Graphviz DOT to SVG in-browser via WebAssembly

### Core Automata Logic
- Custom Python data models and state machines in `core/automata_engine.py`:
  - DFA
  - CFG
  - PDA
- Predefined expressions are compiled into handcrafted automata structures for visualization and step playback.

### Desktop Application
- **PyQt6** (`main.py`, `ui/`)
- Uses the same shared engine as the web app for consistent automata behavior.

### Packaging, Build, and Deployment
- **Docker** (`Dockerfile`) for containerized backend deployment
- **Cloudflare Pages + Azure Container Apps** deployment flow via GitHub Actions (`.github/workflows/deploy.yml`)
- **Static frontend build script** (`scripts/build_frontend.py`) that:
  - copies web assets to `dist/`
  - injects `AUTOMATA_API_BASE` into HTML for environment-specific API routing

## How the App Is Made

## 1) Shared Engine Layer
`core/automata_engine.py` is the foundation.
It defines automata data structures, predefined expressions, transition logic, and step-by-step processing output.

Both web and desktop applications call this same engine, so acceptance/rejection behavior stays aligned across platforms.

## 2) Web Backend Layer
`app.py` wraps the engine with JSON APIs:
- `GET /api/expressions` → list of available expressions and metadata
- `GET /api/automaton?expression=...` → DFA/CFG/PDA representation data
- `POST /api/process` → processes an input string and returns step trace + result
- `GET /healthz` → liveness endpoint

The backend also serves the web shell from `templates/index.html` and static assets from `static/`.

## 3) Web Frontend Layer
The frontend (`static/js/app.js`) performs:
- expression loading from API
- rendering DFA and PDA graphs via Viz.js
- CFG text rendering and coloring
- step-by-step playback controls (play/step/reset)
- result display (accepted/rejected)

All graph visuals are rendered as SVG in the browser.

## 4) Deployment/Build Pipeline
- Local/dev web run: `python app.py`
- Production web run: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
- Container run: `Dockerfile`
- CI/CD workflow:
  - builds static frontend (`scripts/build_frontend.py`)
  - deploys frontend to Cloudflare Pages
  - builds/pushes backend image to Azure Container Registry
  - updates Azure Container App

## 5) Desktop Variant
`main.py` starts the PyQt6 UI in `ui/`.
The UI visualizes DFA/CFG/PDA using the same engine APIs as the web version.

## Key Architectural Characteristic
The project is designed around **single-source automata logic + multiple presentation layers**:
- One core engine
- Two user interfaces (web and desktop)

This keeps behavior consistent while allowing different deployment targets.
