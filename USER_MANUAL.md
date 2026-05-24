# Automata Theory Visualizer — User Instruction Manual

## Table of Contents

1. [Overview](#1-overview)
2. [Getting Started](#2-getting-started)
   - [Web App](#21-web-app)
   - [Desktop App](#22-desktop-app)
3. [Interface Layout](#3-interface-layout)
4. [Selecting an Expression](#4-selecting-an-expression)
5. [Testing a String](#5-testing-a-string)
6. [DFA View](#6-dfa-view)
7. [CFG View](#7-cfg-view)
8. [PDA View](#8-pda-view)
9. [Playback Controls](#9-playback-controls)
10. [Understanding the Output](#10-understanding-the-output)
11. [Predefined Expressions Reference](#11-predefined-expressions-reference)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Overview

**Automata Theory Visualizer** is an educational tool for exploring how regular expressions are represented as three equivalent formal models:

| Model | Full Name | What It Shows |
|-------|-----------|---------------|
| **DFA** | Deterministic Finite Automaton | State diagram with animated transitions |
| **CFG** | Context-Free Grammar | Production rules and derivation tree |
| **PDA** | Pushdown Automaton | Flowchart diagram with live stack visualization |

The app comes with two predefined regular expressions. You can select either expression, enter a test string from its alphabet, and watch the automaton process it step by step.

---

## 2. Getting Started

### 2.1 Web App

The web app runs in any modern browser. No installation beyond Python is required.

**Start the server:**

```bash
# Create and activate a virtual environment (first time only)
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# Install dependencies (first time only)
pip install -r requirements-web.txt

# Run the server
python app.py
```

Open **http://localhost:5000** in your browser.

> **Production mode:** Run `gunicorn -w 2 -b 0.0.0.0:8000 app:app` for a multi-worker server.
> **Docker:** `docker build -t automata-web . && docker run --rm -p 8000:8000 automata-web`

### 2.2 Desktop App

The desktop app uses PyQt6 for a native window experience.

**Requirements:** PyQt6 and Graphviz must be installed.

```bash
# Install desktop dependencies (first time only)
pip install -r requirements.txt

# Launch the desktop app
python main.py
```

The window opens at 1400 × 900 pixels and is resizable down to 1200 × 800.

---

## 3. Interface Layout

The application is divided into two regions:

```
┌─────────────────┬──────────────────────────────────────────┐
│                 │                                          │
│   SIDEBAR       │   VISUALIZATION PANEL                    │
│   (left)        │   (right, tabbed)                        │
│                 │                                          │
│ • Expression    │  [ DFA | CFG | PDA ]                     │
│ • Regex display │                                          │
│ • Test String   │  Graph / diagram for the selected view   │
│ • Alphabet hint │                                          │
│ • Test button   │  Playback controls (DFA / PDA only)      │
│ • Result label  │  Transition trace log                    │
│ • View buttons  │                                          │
│   DFA / CFG / PDA                                         │
│                 │                                          │
│ • State count   │                                          │
└─────────────────┴──────────────────────────────────────────┘
```

---

## 4. Selecting an Expression

1. Locate the **Expression** dropdown in the sidebar.
2. Choose one of the two predefined entries:
   - **Expression 1 (a,b)** — uses the alphabet `{a, b}`
   - **Expression 2 (0,1)** — uses the alphabet `{0, 1}`
3. The full regular expression string is displayed below the dropdown for reference.
4. The **Alphabet** hint and **States** counter at the bottom of the sidebar update automatically.
5. All three views (DFA, CFG, PDA) refresh to reflect the new expression.

---

## 5. Testing a String

1. Click inside the **Test String** input field.
2. Type a string using only the symbols shown in the **Alphabet** hint (e.g. `ababab` for Expression 1).
3. Press **Enter** or click the **Test** button.
4. The result appears in the sidebar:
   - **ACCEPTED** (green) — the string belongs to the language.
   - **REJECTED** (red) — the string does not belong to the language.
   - **Error message** — if the string contains a symbol not in the alphabet, a descriptive error is shown and no animation runs.
5. The active view (DFA or PDA) immediately starts the playback animation.

> **Tip:** The input field also validates symbols against the current alphabet. Any character outside the alphabet produces an error before the automaton is run.

---

## 6. DFA View

The DFA (Deterministic Finite Automaton) view shows a directed graph where:

| Visual Element | Meaning |
|----------------|---------|
| Circle node | A state |
| Double circle | An accepting (final) state |
| Arrow into a state with no source node | The initial (start) state |
| Directed arrow between states | A transition labeled with the input symbol |
| Self-loop arrow on a state | The state loops back to itself on that symbol |
| **Yellow** highlighted node / edge | Currently visited state or transition (step mode) |
| **Green** highlighted node / edge | Active transition during playback |
| **T** state | Dead / trap state — strings that reach here are rejected |

### Navigating the DFA graph

- **Web app:** The graph is rendered as an SVG. You can scroll inside the graph area to see all states.
- **Desktop app:** The graph is rendered in a zoomable QGraphicsView. Use the mouse wheel to zoom; click-and-drag to pan.

---

## 7. CFG View

The CFG (Context-Free Grammar) view is split into two areas:

### Derivation Tree (top section)

A visual tree diagram showing how the start symbol `S` expands through production rules down to terminal symbols. Each node represents a grammar variable or terminal:

- **Blue** nodes — non-terminal variables (S, A, B, …)
- **Green** leaf nodes — terminal symbols (a, b, 0, 1)

You can scroll and zoom (mouse wheel) inside the tree area.

### Production Rules (bottom section)

A syntax-highlighted listing of all grammar productions. The color scheme is:

| Color | Meaning |
|-------|---------|
| **Blue** (`#89b4fa`) | Non-terminal variable (e.g. `S`, `A1`) |
| **Green** (`#a6e3a1`) | Terminal symbol (e.g. `a`, `b`, `0`, `1`) |
| **Yellow** (`#f9e2af`) | Production arrow `→` |
| **Gray** (`#6c7086`) | Alternation separator `\|` |
| **Purple** (`#cba6f7`) | Empty string `ε` |

> **Note:** The CFG view is display-only. String testing does not animate the CFG; use the DFA or PDA views to trace individual steps.

---

## 8. PDA View

The PDA (Pushdown Automaton) view is split into two columns:

### Left — Flowchart Diagram

States are rendered using different shapes to indicate their role:

| Shape | Color | State Type |
|-------|-------|-----------|
| Ellipse | Blue | Start state |
| Ellipse | Green | Accept state |
| Ellipse | Red | Reject state |
| Diamond | Yellow | Decision / Read state |
| Diamond | Purple | Read / process state |

Arrows between states are labeled with the input symbol read at that transition (`△` represents a null / ε transition).

### Right — Stack Panel

Displays the contents of the pushdown stack in real time during animation:

- **Stack Bottom** is shown at the bottom of the panel; the top of the stack grows upward.
- **Green border** on the top symbol — a push operation just occurred.
- **Red border** on the top symbol — a pop operation just occurred.
- The initial stack contains the bottom-of-stack marker `Z`.

### Right — Trace Log

Below the stack is a scrollable log of all transitions taken, formatted as:

```
 1.  START  --a-->  q1   [push a]
 2.  q1     --b-->  q2   [pop a, push b]
```

The **current step** is highlighted in the trace during step-by-step mode.

---

## 9. Playback Controls

Both the DFA view and the PDA view have three playback buttons:

| Button | Action |
|--------|--------|
| **Play** | Runs through all steps automatically, one transition every ~700 ms, then shows the final Accept / Reject result. |
| **Step** | Advances one transition at a time. Click repeatedly to walk through the computation manually. |
| **Reset** | Clears the current run, removes all highlights, and resets the stack to its initial state. |

**Workflow:**
1. Enter a string and press **Test** (auto-play starts immediately).
2. Click **Reset** to clear the animation.
3. Click **Step** to walk through transitions one at a time.
4. Click **Play** at any point to resume automatic playback from the current step.

---

## 10. Understanding the Output

### Accept / Reject

After a run completes the sidebar shows one of:

- **ACCEPTED** — the input string is a member of the regular language defined by the chosen expression.
- **REJECTED** — the input string is not a member of the language. The trace log shows exactly where the computation failed.

### Step trace format

Each line in the trace log follows:

```
<step#>.  <from_state>  --<symbol>-->  <to_state>  [<pda_action>]
```

- `<step#>` — sequential step number starting at 1.
- `<from_state>` — the state the automaton was in before reading the symbol.
- `<symbol>` — the input symbol consumed.
- `<to_state>` — the state the automaton moved to.
- `[<pda_action>]` — (PDA only) describes the stack operation, e.g. `push a` or `pop b`.

### Trap state (DFA)

The DFA contains a special **T** (trap) state. Any transition that would be undefined in a strict DFA leads to T, which self-loops on all symbols. Once the computation reaches T, the string will be rejected regardless of remaining input.

---

## 11. Predefined Expressions Reference

### Expression 1 (a,b)

| Property | Value |
|----------|-------|
| **Regex** | `(aba+bab)(a+b)*(bab)(a+b)*(a+b+ab+ba)(a+b+aa)*` |
| **Alphabet** | `{a, b}` |
| **DFA States** | 11 (including initial `-`, final `+`, and trap `T`) |

**What the expression matches:**
Strings that begin with either `aba` or `bab`, followed by any sequence of `a` and `b`, then contain the sub-sequence `bab`, followed by any sequence, then at least one symbol from `{a, b, ab, ba}`, and finally any sequence from `{a, b, aa}`.

**Example accepted strings:** `abababbaba`, `babbabba`
**Example rejected strings:** `aaa`, `babba` (missing required inner `bab`)

### Expression 2 (0,1)

| Property | Value |
|----------|-------|
| **Regex** | `((101+111+101)+(1+0+11))(1+0+01)*(111+000+101)(1+0)*` |
| **Alphabet** | `{0, 1}` |

**What the expression matches:**
Strings that open with one of `{101, 111, 1, 0, 11}`, continue with any sequence from `{1, 0, 01}`, then contain one of `{111, 000, 101}` as a landmark, followed by any sequence of `1` and `0`.

---

## 12. Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Page loads but graph area is blank | Viz.js WASM is still loading | Wait a moment or refresh the page |
| "Invalid symbol" error on test | String contains characters not in the alphabet | Use only the symbols shown in the **Alphabet** hint |
| Desktop app fails to launch | PyQt6 or Graphviz not installed | Run `pip install -r requirements.txt` and ensure Graphviz is on `PATH` |
| Web server returns 500 | Python dependencies missing | Run `pip install -r requirements-web.txt` |
| Animation plays but shows no highlights | String was processed by a view that doesn't animate (CFG) | Switch to the DFA or PDA view, reset, then test again |
| DFA trace ends at state T | Input string is not in the language | The trap state T means no valid transition existed; check your string against the regex |
| PDA stack is empty unexpectedly | String triggered a pop from an empty stack | The string is rejected; the trace log will show the last valid step |
