"""
Automata Theory Visualizer — Web App
=====================================

Flask backend exposing the AutomataEngine via a JSON API and serving the
single-page frontend. The engine in `core/automata_engine.py` is reused
verbatim from the desktop application, so DFA / CFG / PDA logic stays
identical across both deployments.
"""

from __future__ import annotations

import os

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from core.automata_engine import AutomataEngine


app = Flask(__name__, static_folder="static", template_folder="templates")

# Allow the frontend to call the API from Cloudflare Pages or local dev.
cors_raw = os.environ.get("CORS_ORIGINS", "*")
cors_origins = [origin.strip() for origin in cors_raw.split(",") if origin.strip()]
if not cors_origins:
    cors_origins = "*"
CORS(app, resources={r"/api/*": {"origins": cors_origins}, r"/healthz": {"origins": cors_origins}})


def _engine_for(expression_name: str) -> AutomataEngine:
    """Build a fresh engine configured for the given expression."""
    engine = AutomataEngine()
    if not engine.set_expression(expression_name):
        raise ValueError(f"Unknown expression: {expression_name}")
    return engine


def _serialize_step(step) -> dict:
    return {
        "from_state": step.from_state,
        "symbol": step.symbol,
        "to_state": step.to_state,
        "step_number": step.step_number,
        "stack_before": list(step.stack_before),
        "stack_after": list(step.stack_after),
        "pda_action": step.pda_action,
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/expressions")
def list_expressions():
    """Return the catalog of predefined expressions."""
    engine = AutomataEngine()
    names = engine.get_expression_names()
    out = []
    for name in names:
        engine.set_expression(name)
        out.append({
            "name": name,
            "regex": engine.current_expression,
            "alphabet": sorted(engine.alphabet),
            "state_count": engine.state_count,
        })
    return jsonify(out)


@app.get("/api/automaton")
def get_automaton():
    """Return DFA (DOT + structured), CFG, and PDA data for one expression."""
    expression_name = request.args.get("expression", "")
    try:
        engine = _engine_for(expression_name)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    dfa_data = engine.get_dfa_graph_data() or {}
    cfg_rules = [
        {"left": r.left, "right": list(r.right)} for r in engine.get_cfg_rules()
    ]
    pda_states = [
        {"name": s.name, "state_type": s.state_type,
         "description": s.description, "label": s.label or s.name}
        for s in engine.get_pda_states()
    ]
    pda_transitions = [
        {
            "from_state": t.from_state,
            "to_state": t.to_state,
            "input_symbol": t.input_symbol,
            "stack_pop": t.stack_pop,
            "stack_push": t.stack_push,
        }
        for t in engine.get_pda_transitions()
    ]

    return jsonify({
        "expression": engine.current_expression,
        "expression_name": engine.current_expression_name,
        "alphabet": sorted(engine.alphabet),
        "state_count": engine.state_count,
        "states_warning": engine.states_warning,
        "dfa": {
            "dot": engine.get_dfa_dot(),
            **dfa_data,
        },
        "cfg": {
            "rules": cfg_rules,
            "text": engine.get_cfg_text(),
        },
        "pda": {
            "states": pda_states,
            "transitions": pda_transitions,
        },
    })


@app.post("/api/process")
def process_string():
    """Process an input string against the DFA and PDA representations."""
    body = request.get_json(silent=True) or {}
    expression_name = body.get("expression", "")
    input_string = body.get("input", "")
    mode = body.get("mode", "dfa").lower()

    try:
        engine = _engine_for(expression_name)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    # Validate alphabet first so we can return a friendly message.
    bad = [c for c in input_string if c not in engine.alphabet]
    if bad:
        return jsonify({
            "error": f"Invalid symbol '{bad[0]}'. Expected symbols from "
                      f"{{{', '.join(sorted(engine.alphabet))}}}",
            "accepted": False,
            "steps": [],
            "final_state": "",
        }), 200

    if mode == "pda":
        result = engine.process_string_pda(input_string)
    else:
        result = engine.process_string_dfa(input_string)

    return jsonify({
        "accepted": result.accepted,
        "final_state": result.final_state,
        "error_message": result.error_message,
        "steps": [_serialize_step(s) for s in result.steps],
        "input": input_string,
        "mode": mode,
    })


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
