# Automata Theory Visualizer

A comprehensive, interactive visualizer for Automata Theory, built with Python. This project features both a native **Desktop application** (PyQt6) and a dynamic **Web application** (Flask + Vanilla JS), sharing the exact same Python simulation engine.

---

## Features

- **Deterministic Finite Automata (DFA)**: Test strings against formal DFA definitions. Visualizes state transitions on a graph.
- **Context-Free Grammar (CFG)**: Parse strings using a custom backtracking recursive descent parser. Animates the leftmost derivation tree dynamically as the string is matched.
- **Pushdown Automata (PDA)**: Trace stack transitions step-by-step. Includes a native SVG interactive trace visualizer on the web application.

---

## Quick Start

### 1. Desktop Application
Run the desktop GUI via PyQt6:
```bash
python main.py
```

### 2. Web Application
Run the local Flask development server:
```bash
python app.py
```
Then navigate to `http://127.0.0.1:5000` in your web browser.

---

## Deployment

The frontend of this application is designed to be statically compiled and deployed to **Cloudflare Pages** via GitHub Actions, while the backend API (`app.py`) is deployed as a Docker container to Azure Container Apps. 

To deploy changes to the live site, simply commit your changes and push them to the `main` branch. The CI/CD pipelines in `.github/workflows` will handle the rest.

---

## Acknowledgments & Credits

This project relies on several incredible open-source packages and tools. We extend our deep gratitude to their creators and maintainers:

### Python Dependencies
* **[PyQt6](https://riverbankcomputing.com/software/pyqt/)**: Powers the native desktop graphical user interface.
* **[Flask](https://flask.palletsprojects.com/)**: The lightweight WSGI web application framework used to power the API backend.
* **[automata-lib](https://github.com/caleb531/automata)**: For robust theoretical definitions and evaluations of DFA state machines.
* **[graphviz (Python)](https://github.com/xflr6/graphviz)**: For interfacing with the Graphviz DOT engine in Python.

### Web & Rendering Engines
* **[Graphviz](https://graphviz.org/)**: The core layout engine used to calculate node positions and route edges for our DFA state machines.
* **[Viz.js (@viz-js/viz)](https://github.com/mdaines/viz-js)**: A magnificent WebAssembly port of Graphviz that allows our web application to render complex DOT graphs entirely in the user's browser, eliminating server-side rendering latency.
* **[Catppuccin](https://github.com/catppuccin/catppuccin)**: For the gorgeous, soothing pastel dark-theme color palette used throughout both the web and desktop UI.

---
*For a detailed guide on using the visualizer, see the `USER_MANUAL.md`.*
