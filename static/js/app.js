// Automata Visualizer — frontend logic.
// Talks to the Flask API and renders DFA/PDA via Viz.js (Graphviz WASM).

const state = {
  expressions: [],
  current: null,        // { name, regex, alphabet, state_count }
  automaton: null,      // /api/automaton payload
  steps: [],            // current run's steps
  mode: 'dfa',          // 'dfa' | 'pda'
  stepIndex: -1,        // currently highlighted step
  playing: false,
  timer: null,
};

function getApiBase() {
  const meta = document.querySelector('meta[name="automata-api-base"]');
  const raw = (window.__AUTOMATA_API_BASE__ || (meta && meta.content) || '').trim();
  if (!raw || raw === '__AUTOMATA_API_BASE__') {
    return window.location.origin;
  }
  return raw.replace(/\/$/, '');
}

const API_BASE = getApiBase();

let vizPromise = null;
function getViz() {
  if (!vizPromise) {
    vizPromise = Viz.instance();
  }
  return vizPromise;
}

// ---------- API ----------
async function fetchExpressions() {
  const r = await fetch(`${API_BASE}/api/expressions`);
  return r.json();
}
async function fetchAutomaton(name) {
  const r = await fetch(`${API_BASE}/api/automaton?expression=` + encodeURIComponent(name));
  if (!r.ok) throw new Error((await r.json()).error || 'Failed to load');
  return r.json();
}
async function processString(name, input, mode) {
  const r = await fetch(`${API_BASE}/api/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ expression: name, input, mode }),
  });
  return r.json();
}

// ---------- DOM helpers ----------
const $ = (id) => document.getElementById(id);

function setResult(text, kind) {
  const el = $('result');
  el.textContent = text || '';
  el.className = 'result' + (kind ? ' ' + kind : '');
}

function clearHighlights(rootSelector) {
  document.querySelectorAll(rootSelector + ' .node.active, ' + rootSelector + ' .edge.active')
    .forEach(n => n.classList.remove('active'));
}

// ---------- DOT / SVG theming helpers ----------

/**
 * Injects dark-theme graph attributes directly into a DOT string so
 * Graphviz itself renders the correct colours (no post-hoc CSS hacks needed
 * for most things, but we still call applyDarkThemeSVG for the background).
 */
function injectDarkThemeDOT(dot) {
  const globalAttrs = [
    'bgcolor="transparent";',
    'node [style=filled, fillcolor="#313244", color="#89b4fa", fontcolor="#cdd6f4", fontname="Helvetica", fontsize=12, margin=0.25];',
    'edge [color="#6c7086", fontcolor="#a6adc8", fontname="Helvetica", fontsize=11];',
  ].join('\n  ');
  // Insert after the first opening brace of any digraph/graph block.
  return dot.replace(/^((?:di)?graph\s+\w+\s*\{)/m, `$1\n  ${globalAttrs}`);
}

/** Remove the white background polygon Graphviz adds by default. */
function applyDarkThemeSVG(svg) {
  // The very first <polygon> inside the top-level <g> is the background fill.
  const bg = svg.querySelector('g > polygon:first-of-type');
  if (bg) bg.setAttribute('fill', 'transparent');
  // Belt-and-braces: clear any explicit white fills on root polygons.
  svg.querySelectorAll('polygon[fill="white"], polygon[fill="#ffffff"], polygon[fill="#FFFFFF"]')
     .forEach(p => p.setAttribute('fill', 'transparent'));
  // Ensure the SVG itself has no background.
  svg.style.background = 'transparent';
}

// ---------- Rendering ----------
async function renderDFA(dot) {
  const container = $('dfa-graph');
  container.innerHTML = '<span style="color:#6c7086">Rendering…</span>';
  const viz = await getViz();
  const svg = viz.renderSVGElement(injectDarkThemeDOT(dot));
  applyDarkThemeSVG(svg);
  container.innerHTML = '';
  container.appendChild(svg);
}

function buildPdaDot(pda) {
  const borderColor = {
    start:    '#89b4fa',
    accept:   '#a6e3a1',
    reject:   '#f38ba8',
    decision: '#f9e2af',
    read:     '#cba6f7',
  };
  const fillColor = {
    start:    '#1e2a3a',
    accept:   '#1e3a2f',
    reject:   '#3a1e2f',
    decision: '#3a3020',
    read:     '#2a1e3a',
  };
  const shapeFor = (t) => {
    if (t === 'start' || t === 'accept' || t === 'reject') return 'ellipse';
    // Both 'decision' and 'read' render as diamonds to match the
    // reference flowcharts (image 3 / image 5).
    return 'diamond';
  };

  // PDA edge labels show only the input symbol (△ for null/ε).
  const NULL = '△';
  const pdaLabel = (t) => {
    return (t.input_symbol || 'ε').replaceAll('ε', NULL);
  };

  const lines = [
    'digraph PDA {',
    '  bgcolor="transparent";',
    '  rankdir=TB;',
    '  node [style=filled, fontname="Helvetica", fontcolor="#cdd6f4", fontsize=12,',
    '        color="#89b4fa", fillcolor="#313244", margin=0.3, penwidth=2];',
    '  edge [color="#6c7086", fontcolor="#a6adc8", fontname="Helvetica", fontsize=11];',
  ];

  for (const s of pda.states) {
    const c = borderColor[s.state_type] || '#89b4fa';
    const f = fillColor[s.state_type]   || '#313244';
    const shape = shapeFor(s.state_type);
    const label = (s.label && s.label.length) ? s.label : s.name;
    // Make diamonds a bit wider so the "Read" text fits nicely.
    const sizing = shape === 'diamond' ? ', width=1.2, height=0.7, fixedsize=true' : '';
    lines.push(`  "${s.name}" [shape=${shape}, label="${label}", color="${c}", fillcolor="${f}"${sizing}];`);
  }
  for (const t of pda.transitions) {
    const lbl = pdaLabel(t);
    lines.push(`  "${t.from_state}" -> "${t.to_state}" [label="${lbl}"];`);
  }
  lines.push('}');
  return lines.join('\n');
}

async function renderPDA(pda) {
  const container = $('pda-graph');
  container.innerHTML = '<span style="color:#6c7086">Rendering…</span>';
  const viz = await getViz();
  const svg = viz.renderSVGElement(buildPdaDot(pda));
  applyDarkThemeSVG(svg);
  container.innerHTML = '';
  container.appendChild(svg);
  // Always start at the top of tall PDA diagrams
  container.scrollTop = 0;
}

function renderCFG(text) {
  const el = $('cfg-text');
  el.innerHTML = colorizeCFG(text);
}

/**
 * Safe, tokenizer-based CFG colorizer.
 * Processes text line-by-line and character-by-character so later passes
 * never corrupt HTML inserted by earlier passes.
 */
function colorizeCFG(text) {
  const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // Colorize the right-hand side of a production rule token-by-token.
  function colorizeRHS(rhs) {
    let out = '';
    let i = 0;
    while (i < rhs.length) {
      const ch = rhs[i];
      if (ch === '|') {
        out += `<span style="color:#6c7086">|</span>`;
        i++;
      } else if (ch === 'ε') {
        out += `<i style="color:#cba6f7">ε</i>`;
        i++;
      } else if (ch >= 'A' && ch <= 'Z') {
        // Non-terminal variable (uppercase letter optionally followed by digits)
        let token = ch;
        i++;
        while (i < rhs.length && rhs[i] >= '0' && rhs[i] <= '9') {
          token += rhs[i++];
        }
        out += `<b style="color:#89b4fa">${esc(token)}</b>`;
      } else if ((ch >= 'a' && ch <= 'z') || (ch >= '0' && ch <= '9')) {
        out += `<span style="color:#a6e3a1">${esc(ch)}</span>`;
        i++;
      } else {
        out += esc(ch);
        i++;
      }
    }
    return out;
  }

  return text.split('\n').map(line => {
    // Section headers / separators
    if (line.startsWith('===')) {
      return `<span style="color:#f9e2af">${esc(line)}</span>`;
    }
    if (line.startsWith('Context-Free Grammar')) {
      return `<b style="color:#f9e2af">${esc(line)}</b>`;
    }
    if (line.startsWith('Start Symbol:') || line.startsWith('Terminals:')) {
      const colon = line.indexOf(':');
      return `<span style="color:#cba6f7">${esc(line.slice(0, colon + 1))}</span>${esc(line.slice(colon + 1))}`;
    }

    // Production rule line (contains →)
    const arrowIdx = line.indexOf('→');
    if (arrowIdx !== -1) {
      const lhs = line.slice(0, arrowIdx).trim();
      const rhs = line.slice(arrowIdx + 1);
      return `<b style="color:#89b4fa">${esc(lhs)}</b> <b style="color:#f9e2af">→</b>${colorizeRHS(rhs)}`;
    }

    return esc(line);
  }).join('\n');
}

// ---------- Highlighting (DFA & PDA) ----------
function findNode(svgRoot, label) {
  // Graphviz emits each node as <g class="node"> with a <title>name</title>.
  const titles = svgRoot.querySelectorAll('g.node > title');
  for (const t of titles) {
    if (t.textContent === label) return t.parentNode;
  }
  return null;
}

function findEdge(svgRoot, from, to) {
  const titles = svgRoot.querySelectorAll('g.edge > title');
  const key = `${from}->${to}`;
  for (const t of titles) {
    if (t.textContent === key) return t.parentNode;
  }
  return null;
}

function highlightStep(panelId, step, prevStep) {
  const svg = document.querySelector(`#${panelId} svg`);
  if (!svg) return;
  // Clear previous highlights
  svg.querySelectorAll('.node.active, .edge.active').forEach(n => n.classList.remove('active'));
  if (!step) return;
  const fromNode = findNode(svg, step.from_state);
  const toNode = findNode(svg, step.to_state);
  const edge = findEdge(svg, step.from_state, step.to_state);
  if (fromNode) fromNode.classList.add('active');
  if (toNode) toNode.classList.add('active');
  if (edge) edge.classList.add('active');
}

function renderStack(symbols, highlightKind) {
  const el = $('pda-stack');
  el.innerHTML = '';
  symbols.forEach((sym, i) => {
    const d = document.createElement('div');
    d.className = 'symbol';
    if (i === symbols.length - 1 && highlightKind) d.classList.add(highlightKind);
    d.textContent = sym;
    el.appendChild(d);
  });
}

function renderTrace(panelId, steps, currentIdx) {
  const el = $(panelId === 'view-dfa' ? 'dfa-trace' : 'pda-trace');
  el.innerHTML = '';
  steps.forEach((s, i) => {
    const div = document.createElement('div');
    div.className = 'step' + (i === currentIdx ? ' current' : '');
    let line = `${String(s.step_number).padStart(2, ' ')}.  ${s.from_state}  --${s.symbol}-->  ${s.to_state}`;
    if (s.pda_action) line += `   [${s.pda_action}]`;
    div.textContent = line;
    el.appendChild(div);
  });
}

// ---------- Animation control ----------
function resetRun() {
  state.steps = [];
  state.stepIndex = -1;
  stopPlaying();
  clearHighlights('#dfa-graph');
  clearHighlights('#pda-graph');
  renderTrace('view-dfa', [], -1);
  renderTrace('view-pda', [], -1);
  renderStack(['Z'], null);
  setResult('', '');
}

function stopPlaying() {
  state.playing = false;
  if (state.timer) { clearInterval(state.timer); state.timer = null; }
}

function applyStep(idx) {
  state.stepIndex = idx;
  const step = state.steps[idx];
  const prev = state.steps[idx - 1];
  if (state.mode === 'pda') {
    highlightStep('pda-graph', step, prev);
    if (step) {
      const kind = step.stack_after.length > step.stack_before.length ? 'pushed'
                 : step.stack_after.length < step.stack_before.length ? 'popped'
                 : null;
      renderStack(step.stack_after, kind);
    }
    renderTrace('view-pda', state.steps, idx);
  } else {
    highlightStep('dfa-graph', step, prev);
    renderTrace('view-dfa', state.steps, idx);
  }
}

function play(panel) {
  if (!state.steps.length) return;
  stopPlaying();
  state.playing = true;
  let i = Math.max(0, state.stepIndex);
  applyStep(i);
  state.timer = setInterval(() => {
    i++;
    if (i >= state.steps.length) {
      stopPlaying();
      announceResult();
      return;
    }
    applyStep(i);
  }, 700);
}

function stepOnce() {
  if (!state.steps.length) return;
  const next = state.stepIndex + 1;
  if (next >= state.steps.length) {
    announceResult();
    return;
  }
  applyStep(next);
  if (next === state.steps.length - 1) announceResult();
}

function announceResult() {
  if (!state.lastResult) return;
  setResult(
    state.lastResult.accepted ? 'ACCEPTED' : 'REJECTED',
    state.lastResult.accepted ? 'accepted' : 'rejected'
  );
}

// ---------- Event wiring ----------
async function loadExpression(name) {
  state.current = state.expressions.find(e => e.name === name);
  $('regex-display').textContent = state.current.regex;
  $('alphabet-hint').textContent = 'Alphabet: { ' + state.current.alphabet.join(', ') + ' }';
  $('state-count').textContent = 'States: ' + state.current.state_count;

  const auto = await fetchAutomaton(name);
  state.automaton = auto;
  await renderDFA(auto.dfa.dot);
  renderCFG(auto.cfg.text);
  await renderPDA(auto.pda);
  resetRun();
}

function switchView(view) {
  state.mode = view === 'pda' ? 'pda' : (view === 'dfa' ? 'dfa' : state.mode);
  document.querySelectorAll('.view-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.view === view));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  $(`view-${view}`).classList.add('active');
}

async function onTest() {
  const input = $('input').value.trim();
  if (!input) { setResult('Enter a string', 'rejected'); return; }
  // Determine which mode is active based on currently visible panel.
  const activePanel = document.querySelector('.panel.active').id;
  const mode = activePanel === 'view-pda' ? 'pda' : 'dfa';
  state.mode = mode;
  resetRun();
  const res = await processString(state.current.name, input, mode);
  state.lastResult = res;
  if (res.error_message || res.error) {
    setResult(res.error || res.error_message, 'rejected');
    state.steps = res.steps || [];
    return;
  }
  state.steps = res.steps;
  if (mode === 'cfg' || !state.steps.length) {
    announceResult();
  } else {
    play(activePanel);
  }
}

async function init() {
  state.expressions = await fetchExpressions();
  const sel = $('expression');
  state.expressions.forEach(e => {
    const o = document.createElement('option');
    o.value = e.name;
    o.textContent = e.name;
    sel.appendChild(o);
  });
  sel.addEventListener('change', () => loadExpression(sel.value));
  $('test-btn').addEventListener('click', onTest);
  $('input').addEventListener('keydown', (e) => { if (e.key === 'Enter') onTest(); });

  document.querySelectorAll('.view-btn').forEach(btn => {
    btn.addEventListener('click', () => switchView(btn.dataset.view));
  });

  $('dfa-play').addEventListener('click', () => { state.mode = 'dfa'; play('view-dfa'); });
  $('dfa-step').addEventListener('click', () => { state.mode = 'dfa'; stepOnce(); });
  $('dfa-reset').addEventListener('click', resetRun);
  $('pda-play').addEventListener('click', () => { state.mode = 'pda'; play('view-pda'); });
  $('pda-step').addEventListener('click', () => { state.mode = 'pda'; stepOnce(); });
  $('pda-reset').addEventListener('click', resetRun);

  if (state.expressions.length) await loadExpression(state.expressions[0].name);
}

init().catch(err => {
  console.error(err);
  setResult('Init failed: ' + err.message, 'rejected');
});
