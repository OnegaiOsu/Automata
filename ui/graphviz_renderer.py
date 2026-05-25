"""
Graphviz Renderer — shared utilities for rendering DOT graphs as QPixmaps.

Used by the DFA and PDA panels to produce Graphviz-native graph images with
Catppuccin Mocha dark-theme styling and optional animation highlighting.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

# ---------------------------------------------------------------------------
# Catppuccin Mocha palette (matches styles.qss / web CSS)
# ---------------------------------------------------------------------------
BG = "#11111b"
PANEL = "#1e1e2e"
SURFACE = "#313244"
SURFACE2 = "#45475a"
TEXT = "#cdd6f4"
MUTED = "#a6adc8"
DIM = "#6c7086"
BLUE = "#89b4fa"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"
MAUVE = "#cba6f7"

# PDA node colours keyed by state_type
PDA_BORDER = {
    "start": BLUE,
    "accept": GREEN,
    "reject": RED,
    "decision": YELLOW,
    "read": MAUVE,
}
PDA_FILL = {
    "start": "#1e2a3a",
    "accept": "#1e3a2f",
    "reject": "#3a1e2f",
    "decision": "#3a3020",
    "read": "#2a1e3a",
}


def setup_graphviz_path() -> None:
    """Ensure the bundled Graphviz binary directory is on PATH."""
    if getattr(sys, "frozen", False):
        bundle_dir = sys._MEIPASS
        gv_bin = os.path.join(bundle_dir, "graphviz")
    else:
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        gv_bin = os.path.join(app_dir, "Graphviz-14.1.2-win64", "bin")

    if os.path.isdir(gv_bin) and gv_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = gv_bin + os.pathsep + os.environ.get("PATH", "")


# Call once at import time so every consumer gets it for free.
setup_graphviz_path()


def render_dot_to_pixmap(
    dot_source: str,
    *,
    dpi: int = 150,
    engine: str = "dot",
) -> QPixmap:
    """
    Render a DOT string to a ``QPixmap`` via the ``graphviz`` Python library.

    Parameters
    ----------
    dot_source : str
        Complete DOT source text.
    dpi : int
        Render resolution (default 150 — crisp on HiDPI screens).
    engine : str
        Graphviz layout engine (``dot``, ``neato``, ``fdp`` …).

    Returns
    -------
    QPixmap
        The rendered graph as a Qt pixmap (transparent background).
    """
    import graphviz  # lazy import – heavy C library

    src = graphviz.Source(dot_source, engine=engine)
    png_bytes: bytes = src.pipe(format="png")

    img = QImage()
    img.loadFromData(png_bytes)
    return QPixmap.fromImage(img)


# ---------------------------------------------------------------------------
# DFA DOT builder
# ---------------------------------------------------------------------------

def build_dfa_dot(
    engine,
    *,
    highlight_nodes: set[str] | None = None,
    highlight_edges: set[tuple[str, str]] | None = None,
    active_node: str | None = None,
) -> str:
    """
    Build a Graphviz DOT string for the current DFA with dark-theme styling.

    Parameters
    ----------
    engine : AutomataEngine
        Engine instance with a loaded expression.
    highlight_nodes : set[str], optional
        State names to highlight (yellow border).
    highlight_edges : set[tuple[str,str]], optional
        (from, to) pairs whose edges should be highlighted green.
    active_node : str, optional
        A single "currently active" node drawn with green fill.
    """
    data = engine.get_dfa_graph_data()
    if not data:
        return 'digraph G { label="No DFA loaded"; }'

    states = data["states"]
    transitions = data["transitions"]
    initial_state = str(data["initial_state"])
    final_states = {str(s) for s in data["final_states"]}

    hl_nodes = highlight_nodes or set()
    hl_edges = highlight_edges or set()

    lines = [
        "digraph DFA {",
        "    dpi=300;",
        "    rankdir=LR;",
        f'    bgcolor="{BG}";',
        f'    node [style=filled, fillcolor="{SURFACE}", color="{BLUE}", '
        f'fontcolor="{TEXT}", fontname="Helvetica", fontsize=12, margin=0.25];',
        f'    edge [color="{DIM}", fontcolor="{MUTED}", '
        f'fontname="Helvetica", fontsize=11];',
    ]

    # Nodes
    for state in sorted(states, key=str):
        s = str(state)
        attrs: list[str] = []
        if s in final_states:
            attrs.append("shape=doublecircle")
        else:
            attrs.append("shape=circle")

        if s == active_node:
            attrs.extend([
                f'fillcolor="#1e3a2f"',
                f'color="{GREEN}"',
                "penwidth=5",
            ])
        elif s in hl_nodes:
            attrs.extend([
                f'fillcolor="{SURFACE2}"',
                f'color="{YELLOW}"',
                "penwidth=4",
            ])

        lines.append(f'    "{s}" [{", ".join(attrs)}];')

    # Invisible start arrow
    lines.append('    "" [shape=none, width=0, height=0, margin=0, label="", style="invis"];')
    lines.append(f'    "" -> "{initial_state}" [color="{BLUE}"];')

    # Edges — group by (from, to) to merge labels
    edge_map: dict[tuple[str, str], list[str]] = {}
    for from_state, trans in transitions.items():
        for symbol, to_state in trans.items():
            key = (str(from_state), str(to_state))
            edge_map.setdefault(key, []).append(symbol)

    for (f, t), symbols in edge_map.items():
        label = ",".join(sorted(symbols))
        eattrs = [f'label="{label}"']
        if (f, t) in hl_edges:
            eattrs.extend([f'color="{GREEN}"', "penwidth=4",
                           f'fontcolor="{GREEN}"'])
        lines.append(f'    "{f}" -> "{t}" [{", ".join(eattrs)}];')

    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# PDA DOT builder
# ---------------------------------------------------------------------------

def build_pda_dot(
    engine,
    *,
    highlight_state: str | None = None,
) -> str:
    """
    Build a Graphviz DOT string for the current PDA flowchart.

    Parameters
    ----------
    engine : AutomataEngine
        Engine instance with a loaded expression.
    highlight_state : str, optional
        PDA state *name* to highlight (yellow border).
    """
    pda_states = engine.get_pda_states()
    pda_transitions = engine.get_pda_transitions()

    if not pda_states:
        return 'digraph G { label="No PDA loaded"; }'

    NULL = "eps"

    lines = [
        "digraph PDA {",
        "    dpi=300;",
        f'    bgcolor="{BG}";',
        "    rankdir=TB;",
        f'    node [style=filled, fontname="Helvetica", fontcolor="{TEXT}", '
        f'fontsize=12, color="{BLUE}", fillcolor="{SURFACE}", margin=0.3, penwidth=2];',
        f'    edge [color="{DIM}", fontcolor="{MUTED}", '
        f'fontname="Helvetica", fontsize=11];',
    ]

    for s in pda_states:
        st = s.state_type
        shape = "ellipse" if st in ("start", "accept", "reject") else "diamond"
        bc = PDA_BORDER.get(st, BLUE)
        fc = PDA_FILL.get(st, SURFACE)
        label = s.label if s.label else s.name
        sizing = ', width=1.2, height=0.7, fixedsize=true' if shape == "diamond" else ""

        # Highlighting
        extra = ""
        if highlight_state and s.name == highlight_state:
            bc = YELLOW
            fc = SURFACE2
            extra = ", penwidth=4"

        lines.append(
            f'    "{s.name}" [shape={shape}, label="{label}", '
            f'color="{bc}", fillcolor="{fc}"{sizing}{extra}];'
        )

    for t in pda_transitions:
        lbl = (t.input_symbol or "ε").replace("ε", NULL)
        lines.append(f'    "{t.from_state}" -> "{t.to_state}" [label="{lbl}"];')

    lines.append("}")
    return "\n".join(lines)
