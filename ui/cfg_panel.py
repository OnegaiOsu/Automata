"""
CFG Panel - Context-Free Grammar visualization.
Displays production rules in a formatted, readable view with a graphical
derivation tree diagram.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QGroupBox, QScrollArea, QFrame,
    QSizePolicy, QSplitter, QGraphicsView, QGraphicsScene,
    QGraphicsTextItem, QGraphicsEllipseItem, QToolBar, QPushButton
)
from PyQt6.QtCore import Qt, QPointF, QRectF, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QFont, QColor, QTextCharFormat, QSyntaxHighlighter,
    QTextDocument, QPen, QBrush, QPainter, QPainterPath
)
import math

from core.automata_engine import AutomataEngine


class CFGHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for CFG production rules."""
    
    def __init__(self, document: QTextDocument):
        super().__init__(document)
        
        # Formats
        self.variable_format = QTextCharFormat()
        self.variable_format.setForeground(QColor("#89b4fa"))
        self.variable_format.setFontWeight(QFont.Weight.Bold)
        
        self.terminal_format = QTextCharFormat()
        self.terminal_format.setForeground(QColor("#a6e3a1"))
        
        self.arrow_format = QTextCharFormat()
        self.arrow_format.setForeground(QColor("#f9e2af"))
        self.arrow_format.setFontWeight(QFont.Weight.Bold)
        
        self.epsilon_format = QTextCharFormat()
        self.epsilon_format.setForeground(QColor("#cba6f7"))
        self.epsilon_format.setFontItalic(True)
        
        self.separator_format = QTextCharFormat()
        self.separator_format.setForeground(QColor("#6c7086"))
    
    def highlightBlock(self, text: str):
        """Apply syntax highlighting to a block of text."""
        # Highlight arrow
        arrow_pos = text.find('→')
        if arrow_pos != -1:
            self.setFormat(arrow_pos, 1, self.arrow_format)
            
            # Left side is variable
            left_side = text[:arrow_pos].strip()
            start = text.find(left_side)
            if start != -1:
                self.setFormat(start, len(left_side), self.variable_format)
            
            # Right side parsing
            right_side = text[arrow_pos + 1:]
            offset = arrow_pos + 1
            
            i = 0
            while i < len(right_side):
                char = right_side[i]
                
                if char == '|':
                    self.setFormat(offset + i, 1, self.separator_format)
                elif char == 'ε':
                    self.setFormat(offset + i, 1, self.epsilon_format)
                elif char.isupper() or (char == 'A' and i + 1 < len(right_side) and right_side[i+1].isdigit()):
                    # Variable (uppercase or A followed by number)
                    var_end = i + 1
                    while var_end < len(right_side) and right_side[var_end].isdigit():
                        var_end += 1
                    self.setFormat(offset + i, var_end - i, self.variable_format)
                    i = var_end - 1
                elif char.islower() or char.isdigit():
                    # Terminal
                    self.setFormat(offset + i, 1, self.terminal_format)
                
                i += 1
        
        # Highlight section headers
        if text.startswith('=') or text.startswith('Context-Free Grammar'):
            header_format = QTextCharFormat()
            header_format.setForeground(QColor("#f9e2af"))
            header_format.setFontWeight(QFont.Weight.Bold)
            self.setFormat(0, len(text), header_format)
        
        # Highlight metadata
        if text.startswith('Start Symbol:') or text.startswith('Terminals:'):
            label_format = QTextCharFormat()
            label_format.setForeground(QColor("#cba6f7"))
            colon_pos = text.find(':')
            if colon_pos != -1:
                self.setFormat(0, colon_pos + 1, label_format)


class CFGPanel(QWidget):
    """Panel for displaying Context-Free Grammar production rules with derivation tree."""
    
    animation_finished = pyqtSignal(bool)
    
    def __init__(self, engine: AutomataEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.steps = []
        self.current_idx = -1
        self.last_result = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Context-Free Grammar")
        title.setObjectName("title")
        title.setStyleSheet("font-size: 20px; color: #89b4fa;")
        header_layout.addWidget(title)
        
        # Add Toolbar
        toolbar = QToolBar()
        toolbar.setIconSize(toolbar.iconSize())
        toolbar.setStyleSheet("background: transparent; border: none;")
        
        self.btn_play = QPushButton("Play")
        self.btn_play.clicked.connect(self.play_simulation)
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_simulation)
        self.btn_step = QPushButton("Step")
        self.btn_step.clicked.connect(self.step_simulation)
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset_simulation)
        
        for btn in [self.btn_play, self.btn_stop, self.btn_step, self.btn_reset]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            toolbar.addWidget(btn)
            
        header_layout.addStretch()
        header_layout.addWidget(toolbar)
        
        layout.addLayout(header_layout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._timer_tick)
        
        # Main content: derivation tree (top) + rules (bottom)
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # ===== TOP: Derivation tree diagram =====
        tree_group = QGroupBox("Derivation Tree")
        tree_layout = QVBoxLayout(tree_group)
        
        self.tree_scene = QGraphicsScene()
        self.tree_scene.setBackgroundBrush(QBrush(QColor("#11111b")))
        
        self.tree_view = QGraphicsView(self.tree_scene)
        self.tree_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.tree_view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.tree_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.tree_view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.tree_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tree_view.setMinimumHeight(280)
        self.tree_view.wheelEvent = self._wheel_zoom
        
        tree_layout.addWidget(self.tree_view)
        splitter.addWidget(tree_group)
        
        # ===== BOTTOM: Production rules text and Trace =====
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        rules_group = QGroupBox("Production Rules")
        rules_layout = QVBoxLayout(rules_group)
        
        self.rules_text = QTextEdit()
        self.rules_text.setReadOnly(True)
        self.rules_text.setFont(QFont("Cascadia Code", 16))
        self.rules_text.setStyleSheet("line-height: 200%;")
        self.rules_text.setMinimumHeight(120)
        
        self.highlighter = CFGHighlighter(self.rules_text.document())
        rules_layout.addWidget(self.rules_text)
        
        trace_group = QGroupBox("Derivation Trace")
        trace_layout = QVBoxLayout(trace_group)
        
        self.trace_text = QTextEdit()
        self.trace_text.setReadOnly(True)
        self.trace_text.setFont(QFont("Cascadia Code", 12))
        self.trace_text.setMinimumHeight(120)
        trace_layout.addWidget(self.trace_text)
        
        bottom_splitter.addWidget(rules_group)
        bottom_splitter.addWidget(trace_group)
        bottom_splitter.setSizes([300, 300])
        
        splitter.addWidget(bottom_splitter)
        
        splitter.setSizes([450, 250])
        layout.addWidget(splitter, 1)
        
        # Legend
        legend_group = QGroupBox("Legend")
        legend_layout = QHBoxLayout(legend_group)
        legend_layout.setSpacing(30)
        
        legends = [
            ("S, A, B...", "#89b4fa", "Variables"),
            ("a, b, 0, 1", "#a6e3a1", "Terminals"),
            ("→", "#f9e2af", "Production"),
            ("|", "#6c7086", "OR"),
            ("ε", "#cba6f7", "Empty string"),
        ]
        
        for symbol, color, description in legends:
            item_layout = QHBoxLayout()
            
            symbol_label = QLabel(symbol)
            symbol_label.setStyleSheet(f"color: {color}; font-family: 'Cascadia Code'; font-weight: bold;")
            
            desc_label = QLabel(f"= {description}")
            desc_label.setStyleSheet("color: #a6adc8; font-size: 11px;")
            
            item_layout.addWidget(symbol_label)
            item_layout.addWidget(desc_label)
            item_layout.addStretch()
            
            legend_layout.addLayout(item_layout)
        
        legend_layout.addStretch()
        layout.addWidget(legend_group)
    
    def _wheel_zoom(self, event):
        """Handle mouse wheel for zooming."""
        factor = 1.15
        if event.angleDelta().y() > 0:
            self.tree_view.scale(factor, factor)
        else:
            self.tree_view.scale(1 / factor, 1 / factor)
    
    def update_grammar(self):
        """Update the displayed grammar and derivation tree from the engine."""
        cfg_text = self.engine.get_cfg_text()
        
        # Remove the metadata headers if any to match reference exactly
        lines = cfg_text.split('\n')
        clean_lines = []
        for line in lines:
            if line.startswith('=') or line.startswith('Context') or line.startswith('Start') or line.startswith('Terminal'):
                continue
            
            # Format arrows to be like reference (space around arrow)
            if '→' in line:
                line = line.replace('→', '->')
            
            if line.strip():
                clean_lines.append(line)
        
        formatted_text = "\n\n".join(clean_lines)
        self.rules_text.setPlainText(formatted_text)
        self._build_derivation_tree()
    
    def _build_derivation_tree(self):
        """Build a visual derivation tree from the CFG rules."""
        self.tree_scene.clear()
        
        rules = self.engine.get_cfg_rules()
        if not rules:
            text = self.tree_scene.addText("No grammar loaded.")
            text.setDefaultTextColor(QColor("#6c7086"))
            text.setFont(QFont("Segoe UI", 14))
            return
        
        # Build rule lookup: variable -> list of productions
        rule_map = {}
        for rule in rules:
            rule_map[rule.left] = rule.right
        
        # Build tree structure from the start symbol S
        # Each node: (label, is_terminal, children)
        tree = self._expand_tree('S', rule_map, depth=0, max_depth=3)
        
        # Layout and render the tree
        self._render_tree(tree)
    
    def _expand_tree(self, symbol, rule_map, depth, max_depth):
        """
        Expand a symbol into a tree structure.
        Returns: (label, is_terminal, children_list)
        Use the first production for visualization.
        """
        if depth > max_depth or symbol not in rule_map:
            # Terminal or max depth reached
            is_terminal = symbol not in rule_map
            return (symbol, is_terminal, [])
        
        # Use the first production rule for the tree
        production = rule_map[symbol][0]
        
        # Parse the production into children
        children = []
        i = 0
        while i < len(production):
            char = production[i]
            if char == 'ε':
                children.append(('ε', True, []))
                i += 1
            elif char.isupper():
                # Non-terminal — could be multi-char like A1
                var = char
                j = i + 1
                while j < len(production) and production[j].isdigit():
                    var += production[j]
                    j += 1
                child = self._expand_tree(var, rule_map, depth + 1, max_depth)
                children.append(child)
                i = j
            else:
                # Terminal character(s)
                children.append((char, True, []))
                i += 1
        
        return (symbol, False, children)
    
    def _render_tree(self, tree):
        """Render the tree into the QGraphicsScene."""
        # First pass: compute subtree widths
        widths = {}
        self._compute_widths(tree, widths)
        
        # Layout parameters
        h_gap = 30   # Horizontal gap between siblings
        v_gap = 70   # Vertical gap between levels
        
        # Second pass: assign positions
        positions = {}
        self._assign_positions(tree, 0, 0, widths, positions, h_gap, v_gap)
        
        # Center positions
        if positions:
            all_x = [p[0] for p in positions.values()]
            all_y = [p[1] for p in positions.values()]
            cx = (min(all_x) + max(all_x)) / 2
            positions = {k: (v[0] - cx, v[1]) for k, v in positions.items()}
        
        # Draw edges first (behind nodes)
        self._draw_tree_edges(tree, positions)
        
        # Draw nodes
        self._draw_tree_nodes(tree, positions)
        
        # Fit view
        rect = self.tree_scene.itemsBoundingRect()
        rect.adjust(-40, -40, 40, 40)
        self.tree_scene.setSceneRect(rect)
        self.tree_view.resetTransform()
        self.tree_view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
    
    def _compute_widths(self, node, widths):
        """Compute the width of each subtree (number of leaves)."""
        label, is_terminal, children = node
        node_id = id(node)
        
        if not children:
            widths[node_id] = 1
            return 1
        
        total = 0
        for child in children:
            total += self._compute_widths(child, widths)
        widths[node_id] = total
        return total
    
    def _assign_positions(self, node, x, y, widths, positions, h_gap, v_gap):
        """Assign (x, y) positions to each node."""
        label, is_terminal, children = node
        node_id = id(node)
        
        if not children:
            positions[node_id] = (x, y)
            return
        
        # Position this node
        positions[node_id] = (x, y)
        
        # Position children centered beneath
        total_width = sum(widths[id(c)] for c in children)
        start_x = x - (total_width - 1) * h_gap / 2
        
        current_x = start_x
        for child in children:
            child_width = widths[id(child)]
            child_x = current_x + (child_width - 1) * h_gap / 2
            self._assign_positions(child, child_x, y + v_gap, widths, positions, h_gap, v_gap)
            current_x += child_width * h_gap
    
    def _draw_tree_edges(self, node, positions):
        """Draw edges from parent to children."""
        label, is_terminal, children = node
        node_id = id(node)
        
        if node_id not in positions:
            return
        
        px, py = positions[node_id]
        
        for child in children:
            child_id = id(child)
            if child_id in positions:
                cx, cy = positions[child_id]
                # Draw line from parent bottom to child top
                self.tree_scene.addLine(
                    px, py + 15, cx, cy - 15,
                    QPen(QColor("#585b70"), 2)
                )
                # Recurse
                self._draw_tree_edges(child, positions)
    
    def _draw_tree_nodes(self, node, positions):
        """Draw node labels (circles for variables, plain text for terminals)."""
        label, is_terminal, children = node
        node_id = id(node)
        
        if node_id not in positions:
            return
        
        x, y = positions[node_id]
        
        if is_terminal:
            # Terminal: green text, no circle
            color = "#cba6f7" if label == 'ε' else "#a6e3a1"
            font = QFont("Cascadia Code", 12, QFont.Weight.Bold)
            
            text_item = self.tree_scene.addText(label)
            text_item.setDefaultTextColor(QColor(color))
            text_item.setFont(font)
            rect = text_item.boundingRect()
            text_item.setPos(x - rect.width() / 2, y - rect.height() / 2)
        else:
            # Non-terminal: circle with label
            radius = 18
            self.tree_scene.addEllipse(
                x - radius, y - radius, radius * 2, radius * 2,
                QPen(QColor("#89b4fa"), 2),
                QBrush(QColor("#313244"))
            )
            
            text_item = self.tree_scene.addText(label)
            text_item.setDefaultTextColor(QColor("#89b4fa"))
            text_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            rect = text_item.boundingRect()
            text_item.setPos(x - rect.width() / 2, y - rect.height() / 2)
        
        # Recurse into children
        for child in children:
            self._draw_tree_nodes(child, positions)
    
    def resizeEvent(self, event):
        """Handle resize to fit tree."""
        super().resizeEvent(event)
        rect = self.tree_scene.sceneRect()
        if rect.isValid() and not rect.isEmpty():
            self.tree_view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
    
    def clear(self):
        """Clear the grammar display."""
        self.rules_text.clear()
        self.rules_text.setPlainText("No grammar loaded. Select an expression above.")
        self.tree_scene.clear()
        self.trace_text.clear()

    # --- Animation & Simulation ---
    
    def process_string(self, input_string: str):
        """Start simulating the string."""
        self.last_result = self.engine.process_string_cfg(input_string)
        self.steps = self.last_result.steps if self.last_result else []
        self.current_idx = -1
        self.reset_simulation()
        self.play_simulation()
        
    def play_simulation(self):
        if not self.steps: return
        self.stop_simulation()
        self.current_idx = max(0, self.current_idx)
        self._apply_step(self.current_idx)
        self.timer.start(700)
        
    def stop_simulation(self):
        self.timer.stop()
        
    def step_simulation(self):
        if not self.steps: return
        self.stop_simulation()
        if self.current_idx >= len(self.steps) - 1:
            self._announce_result()
            return
        self.current_idx += 1
        self._apply_step(self.current_idx)
        if self.current_idx >= len(self.steps) - 1:
            self._announce_result()
            
    def reset_simulation(self):
        self.stop_simulation()
        self.current_idx = -1
        self.trace_text.clear()
        # Reset to static tree
        self._build_derivation_tree()
        
    def _timer_tick(self):
        self.current_idx += 1
        if self.current_idx >= len(self.steps):
            self.stop_simulation()
            self._announce_result()
            return
        self._apply_step(self.current_idx)
        
    def _apply_step(self, idx: int):
        # Update derivation trace
        self.trace_text.clear()
        for i in range(idx + 1):
            step = self.steps[i]
            prefix = "→ " if i == idx else "  "
            if step.rule_left:
                line = f"{prefix}{i+1}. {step.rule_left} -> {step.rule_right}  (Current: {step.current_string})"
            else:
                line = f"{prefix}{i+1}. Matched!  (Current: {step.current_string})"
            self.trace_text.append(line)
        
        # We can dynamically build the exact derivation tree!
        # Because we're using QGraphicsScene, we can just rebuild the tree from scratch with the steps
        self.tree_scene.clear()
        rules = self.engine.get_cfg_rules()
        if not rules: return
        
        rule_map = {}
        for rule in rules: rule_map[rule.left] = rule.right
        
        tree = self._build_tree_from_steps(rule_map, idx)
        self._render_tree(tree)
        
    def _build_tree_from_steps(self, rule_map, max_idx):
        # Tree node format: (label, is_terminal, children)
        root = ['S', False, []]
        
        def get_leftmost_nt(node):
            if not node[1] and not node[2] and node[0] != 'ε':
                return node
            for child in node[2]:
                found = get_leftmost_nt(child)
                if found: return found
            return None
            
        for i in range(max_idx + 1):
            step = self.steps[i]
            if not step.rule_left: continue
            
            target = get_leftmost_nt(root)
            if not target: break
            
            right = step.rule_right
            idx = 0
            while idx < len(right):
                char = right[idx]
                if char == 'ε':
                    target[2].append(['ε', True, []])
                    idx += 1
                elif char.isupper():
                    var = char
                    j = idx + 1
                    while j < len(right) and right[j].isdigit():
                        var += right[j]
                        j += 1
                    target[2].append([var, False, []])
                    idx = j
                else:
                    target[2].append([char, True, []])
                    idx += 1
                    
        # Recursively freeze into tuples for the renderer
        def freeze(node):
            return (node[0], node[1], [freeze(c) for c in node[2]])
            
        return freeze(root)

    def _announce_result(self):
        if self.last_result:
            self.animation_finished.emit(self.last_result.accepted)
