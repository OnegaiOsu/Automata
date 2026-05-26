"""
PDA Panel - Pushdown Automaton visualization with flowchart-style diagram.
Shows state diagram as flowchart alongside stack operations during string processing.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsPolygonItem,
    QGraphicsPathItem, QGraphicsLineItem,
    QLabel, QSizePolicy, QGroupBox, QFrame, QSplitter, QTextEdit
)
from PyQt6.QtCore import (
    Qt, QTimer, QPointF, QRectF, pyqtSignal
)
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QFont, QPainter, QPainterPath, QPolygonF
)
from typing import Optional
import math

from core.automata_engine import AutomataEngine, ProcessingResult, TransitionStep


class FlowchartNode:
    """Base class for flowchart nodes."""
    
    def __init__(self, x: float, y: float, text: str, node_type: str):
        self.x = x
        self.y = y
        self.text = text
        self.node_type = node_type  # 'start', 'accept', 'reject', 'read', 'decision'
        self.item = None
        self.label = None
    
    def create_item(self, scene: QGraphicsScene):
        """Create the graphics item for this node."""
        raise NotImplementedError


class EllipseNode(FlowchartNode):
    """Ellipse/oval node for Start, Accept, Reject states."""
    
    WIDTH = 80
    HEIGHT = 40
    
    def __init__(self, x: float, y: float, text: str, node_type: str):
        super().__init__(x, y, text, node_type)
        self._default_pen = None
        self._default_brush = None
    
    def create_item(self, scene: QGraphicsScene):
        # Choose color based on node type
        if self.node_type == 'start':
            pen_color = "#89b4fa"
            fill_color = "#313244"
        elif self.node_type == 'accept':
            pen_color = "#a6e3a1"
            fill_color = "#1e3a2f"
        elif self.node_type == 'reject':
            pen_color = "#f38ba8"
            fill_color = "#3a1e2f"
        else:
            pen_color = "#89b4fa"
            fill_color = "#313244"
        
        self._default_pen = QPen(QColor(pen_color), 2)
        self._default_brush = QBrush(QColor(fill_color))

        self.item = scene.addEllipse(
            self.x - self.WIDTH/2, self.y - self.HEIGHT/2,
            self.WIDTH, self.HEIGHT,
            self._default_pen,
            self._default_brush
        )
        
        # Add text label
        self.label = scene.addText(self.text)
        self.label.setDefaultTextColor(QColor("#cdd6f4"))
        self.label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        rect = self.label.boundingRect()
        self.label.setPos(self.x - rect.width()/2, self.y - rect.height()/2)
        
        return self.item

    def highlight(self):
        """Highlight this node as the active state."""
        if self.item is not None:
            self.item.setPen(QPen(QColor("#f9e2af"), 4))
            self.item.setBrush(QBrush(QColor("#45475a")))

    def reset_appearance(self):
        """Restore default colors."""
        if self.item is not None and self._default_pen is not None:
            self.item.setPen(self._default_pen)
            self.item.setBrush(self._default_brush)


class DiamondNode(FlowchartNode):
    """Diamond node for decision/Read states."""
    
    SIZE = 50
    
    def __init__(self, x: float, y: float, text: str, node_type: str = 'decision'):
        super().__init__(x, y, text, node_type)
        self._default_pen = QPen(QColor("#89b4fa"), 2)
        self._default_brush = QBrush(QColor("#313244"))
    
    def create_item(self, scene: QGraphicsScene):
        # Create diamond shape
        points = [
            QPointF(self.x, self.y - self.SIZE/2),      # Top
            QPointF(self.x + self.SIZE/2, self.y),      # Right
            QPointF(self.x, self.y + self.SIZE/2),      # Bottom
            QPointF(self.x - self.SIZE/2, self.y),      # Left
        ]
        polygon = QPolygonF(points)
        
        self.item = scene.addPolygon(
            polygon,
            self._default_pen,
            self._default_brush
        )
        
        # Add text label
        self.label = scene.addText(self.text)
        self.label.setDefaultTextColor(QColor("#cdd6f4"))
        self.label.setFont(QFont("Segoe UI", 9))
        rect = self.label.boundingRect()
        self.label.setPos(self.x - rect.width()/2, self.y - rect.height()/2)
        
        return self.item

    def highlight(self):
        """Highlight this node as the active state."""
        if self.item is not None:
            self.item.setPen(QPen(QColor("#f9e2af"), 4))
            self.item.setBrush(QBrush(QColor("#45475a")))

    def reset_appearance(self):
        """Restore default colors."""
        if self.item is not None:
            self.item.setPen(self._default_pen)
            self.item.setBrush(self._default_brush)


class StackSymbol(QGraphicsRectItem):
    """Visual representation of a stack symbol."""
    
    WIDTH = 60
    HEIGHT = 35
    
    def __init__(self, symbol: str, index: int):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.symbol = symbol
        self.index = index
        
        # Appearance
        self.setBrush(QBrush(QColor("#313244")))
        self.setPen(QPen(QColor("#89b4fa"), 2))
        
        # Symbol label
        self.label = QGraphicsTextItem(symbol, self)
        self.label.setDefaultTextColor(QColor("#cdd6f4"))
        font = QFont("Cascadia Code", 14, QFont.Weight.Bold)
        self.label.setFont(font)
        
        # Center label
        rect = self.label.boundingRect()
        self.label.setPos(
            (self.WIDTH - rect.width()) / 2,
            (self.HEIGHT - rect.height()) / 2
        )
    
    def highlight_push(self):
        """Highlight for push operation."""
        self.setBrush(QBrush(QColor("#1e3a2f")))
        self.setPen(QPen(QColor("#a6e3a1"), 3))
    
    def highlight_pop(self):
        """Highlight for pop operation."""
        self.setBrush(QBrush(QColor("#3a1e2f")))
        self.setPen(QPen(QColor("#f38ba8"), 3))
    
    def reset_appearance(self):
        """Reset to default appearance."""
        self.setBrush(QBrush(QColor("#313244")))
        self.setPen(QPen(QColor("#89b4fa"), 2))


class StackView(QGraphicsView):
    """View for animated stack visualization."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#11111b")))
        self.setScene(self.scene)
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMinimumWidth(120)
        self.setMaximumWidth(200)
        
        self._symbols: list[StackSymbol] = []
        self._base_y = 400  # Bottom of stack
        
        # Add stack base indicator
        self._draw_stack_base()
    
    def _draw_stack_base(self):
        """Draw the stack base indicator."""
        # Base line
        self.scene.addLine(
            10, self._base_y + 10,
            StackSymbol.WIDTH + 30, self._base_y + 10,
            QPen(QColor("#45475a"), 3)
        )
        
        # Label
        label = self.scene.addText("Stack Bottom")
        label.setDefaultTextColor(QColor("#6c7086"))
        label.setFont(QFont("Segoe UI", 9))
        label.setPos(5, self._base_y + 15)
    
    def set_stack(self, symbols: list[str]):
        """Set the entire stack state."""
        # Clear existing symbols
        for sym in self._symbols:
            self.scene.removeItem(sym)
        self._symbols.clear()
        
        # Add new symbols
        for i, symbol in enumerate(symbols):
            self._add_symbol(symbol, animate=False)
    
    def _add_symbol(self, symbol: str, animate: bool = True):
        """Add a symbol to the top of the stack."""
        index = len(self._symbols)
        y = self._base_y - (index + 1) * (StackSymbol.HEIGHT + 5)
        
        sym_item = StackSymbol(symbol, index)
        sym_item.setPos(20, y)
        
        if animate:
            sym_item.highlight_push()
            sym_item.highlight_push()
            # Simple jump (snap) instead of smooth interpolation
            sym_item.setPos(20, y)
        
        self._symbols.append(sym_item)
        self.scene.addItem(sym_item)
        
        # Adjust view
        self.fitInView(
            QRectF(0, min(y - 50, 0), StackSymbol.WIDTH + 50, self._base_y + 50),
            Qt.AspectRatioMode.KeepAspectRatio
        )
    
    def pop_symbol(self) -> Optional[str]:
        """Remove and return the top symbol."""
        if not self._symbols:
            return None
        
        sym = self._symbols.pop()
        sym.highlight_pop()
        
        # Remove after brief delay (would animate in full implementation)
        QTimer.singleShot(200, lambda: self.scene.removeItem(sym))
        
        return sym.symbol
    
    def clear_stack(self):
        """Clear all symbols from the stack."""
        for sym in self._symbols:
            self.scene.removeItem(sym)
        self._symbols.clear()
    
    def highlight_top(self, highlight: bool = True):
        """Highlight the top of stack."""
        if self._symbols:
            if highlight:
                self._symbols[-1].highlight_push()
            else:
                self._symbols[-1].reset_appearance()


class PDAPanel(QWidget):
    """Panel for PDA visualization with animated stack."""
    
    # Signals
    animation_finished = pyqtSignal(bool)
    step_changed = pyqtSignal(int, int)
    
    # Animation timing for 120fps
    FRAME_TIME_MS = 8
    TRANSITION_DURATION_MS = 400
    
    def __init__(self, engine: AutomataEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        
        # State
        self._current_result: Optional[ProcessingResult] = None
        self._current_step = 0
        self._input_string = ""
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._animation_tick)
        self._animation_frame = 0
        self._is_animating = False
        self._diagram_nodes: dict[str, FlowchartNode] = {}
        self._diagram_edges = {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header with description
        header = QLabel("Pushdown Automaton (PDA)")
        header.setStyleSheet("font-size: 20px; color: #89b4fa; font-weight: bold;")
        layout.addWidget(header)
        
        desc = QLabel(
            "A PDA extends a finite automaton with a stack memory. "
            "For regular languages (like these regex patterns), the stack operations "
            "are simplified but demonstrate the concept of stack-based processing."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #a6adc8; font-size: 12px; padding: 5px;")
        layout.addWidget(desc)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: State diagram (simplified view)
        state_group = QGroupBox("State Diagram")
        state_layout = QVBoxLayout(state_group)
        
        self.state_scene = QGraphicsScene()
        self.state_scene.setBackgroundBrush(QBrush(QColor("#11111b")))
        
        self.state_view = QGraphicsView(self.state_scene)
        self.state_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.state_view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.state_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.state_view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.state_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.state_view.wheelEvent = self._wheel_zoom_pda
        
        state_layout.addWidget(self.state_view)
        
        # Current state indicator
        self.current_state_label = QLabel("Current State: -")
        self.current_state_label.setStyleSheet(
            "background-color: #313244; padding: 8px; border-radius: 4px; font-weight: bold;"
        )
        state_layout.addWidget(self.current_state_label)
        
        splitter.addWidget(state_group)
        
        # Right side: Stack visualization
        stack_group = QGroupBox("Stack")
        stack_layout = QVBoxLayout(stack_group)
        
        self.stack_view = StackView()
        stack_layout.addWidget(self.stack_view)
        
        # Stack info
        self.stack_info = QLabel("Stack: [ Z ]")
        self.stack_info.setStyleSheet(
            "background-color: #313244; padding: 8px; border-radius: 4px;"
            "font-family: 'Cascadia Code';"
        )
        stack_layout.addWidget(self.stack_info)
        
        # ===== Input String Tracker =====
        input_group = QGroupBox("Input String")
        input_layout = QVBoxLayout(input_group)
        
        self.input_display = QLabel("")
        self.input_display.setStyleSheet(
            "font-family: 'Cascadia Code'; font-size: 16px; padding: 8px; "
            "background-color: #1e1e2e; border-radius: 4px; letter-spacing: 4px;"
        )
        self.input_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout.addWidget(self.input_display)
        
        stack_layout.addWidget(input_group)
        
        splitter.addWidget(stack_group)
        splitter.setSizes([500, 200])
        
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(splitter)
        
        bottom_panel = QWidget()
        bottom_layout = QVBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)
        
        # ===== Logs & Transition Layout =====
        logs_layout = QHBoxLayout()
        logs_layout.setSpacing(10)

        # ===== Step Log =====
        step_log_group = QGroupBox("Step Trace")
        step_log_layout = QVBoxLayout(step_log_group)
        
        self.step_log = QTextEdit()
        self.step_log.setReadOnly(True)
        self.step_log.setFont(QFont("Cascadia Code", 11))
        self.step_log.setMaximumHeight(120)
        self.step_log.setStyleSheet(
            "background-color: #1e1e2e; border: 1px solid #313244; border-radius: 4px;"
        )
        step_log_layout.addWidget(self.step_log)
        
        logs_layout.addWidget(step_log_group, stretch=2)
        
        # Transition display
        trans_group = QGroupBox("Current Transition")
        trans_layout = QHBoxLayout(trans_group)
        
        self.transition_label = QLabel("δ(state, input, stack_top) → (new_state, stack_operation)")
        self.transition_label.setStyleSheet(
            "font-family: 'Cascadia Code'; font-size: 13px; padding: 10px;"
        )
        self.transition_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.transition_label.setWordWrap(True)
        trans_layout.addWidget(self.transition_label)
        
        logs_layout.addWidget(trans_group, stretch=1)
        
        bottom_layout.addLayout(logs_layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        controls_layout.setContentsMargins(10, 10, 10, 10)
        
        self.play_btn = QPushButton("Play")
        self.play_btn.setObjectName("control")
        self.play_btn.clicked.connect(self._on_play)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setObjectName("control")
        self.pause_btn.clicked.connect(self._on_pause)
        self.pause_btn.setEnabled(False)
        
        self.step_btn = QPushButton("Step")
        self.step_btn.setObjectName("control")
        self.step_btn.clicked.connect(self._on_step)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setObjectName("stop")
        self.reset_btn.clicked.connect(self._on_reset)
        
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.pause_btn)
        controls_layout.addWidget(self.step_btn)
        controls_layout.addWidget(self.reset_btn)
        controls_layout.addStretch()
        
        self.step_label = QLabel("Step: 0 / 0")
        self.step_label.setObjectName("status")
        controls_layout.addWidget(self.step_label)
        
        bottom_layout.addLayout(controls_layout)
        
        main_splitter.addWidget(bottom_panel)
        main_splitter.setSizes([500, 200])
        layout.addWidget(main_splitter, 1)
    
    def build_diagram(self):
        """Build flowchart-style PDA diagram matching the user's design."""
        self.state_scene.clear()
        self._flowchart_nodes = {}
        self._diagram_nodes: dict[str, FlowchartNode] = {}
        self._diagram_edges = {}
        data = self.engine.get_dfa_graph_data()
        if not data:
            text = self.state_scene.addText("No PDA loaded. Select an expression above.")
            text.setDefaultTextColor(QColor("#6c7086"))
            text.setFont(QFont("Segoe UI", 14))
            return
        
        # Get PDA states and transitions from engine
        pda_states = self.engine.get_pda_states()
        pda_transitions = self.engine.get_pda_transitions()
        
        # Check which expression is active
        current_expr = self.engine._current_expression_key
        
        if current_expr and '0,1' in current_expr:
            self._build_expression2_flowchart()
        else:
            self._build_expression1_flowchart()
        
        # Fit view
        self.state_view.fitInView(
            self.state_scene.sceneRect().adjusted(-30, -30, 30, 30),
            Qt.AspectRatioMode.KeepAspectRatio
        )

    # DFA state -> flowchart node key, used to drive highlighting on
    # the PDA diagram during step-by-step processing.
    _EXPR1_STATE_TO_NODE = {
        '-':  'Read1',
        'q1': 'ReadA1',
        'q2': 'ReadB1',
        'q3': 'ReadA2',
        'q4': 'ReadB2',
        'T':  'Reject',
        'q5': 'ReadLoop',
        'q6': 'ReadBab1',
        'q7': 'ReadBab2',
        'q8': 'ReadBab3',
        '+':  'Accept',
    }

    _EXPR2_STATE_TO_NODE = {
        '-': 'D_Top',
        'q1': 'D_L1',
        'q3': 'D_R1',
        'q2': 'D_L2',
        'q8': 'D_R2',
        'q10': 'D_R2',
        'q5': 'D_M_Right',
        'q6': 'D_M_Left',
        'q4': ['D_L3', 'D_BR'],
        'q7': 'D_q7',
        'q9': 'D_R3',
        '+': 'Accept',
        'T': 'Reject'
    }

    def _state_to_node_key(self, state: str) -> Optional[str]:
        """Map a DFA state name to the flowchart node key for the active expression."""
        current_expr = getattr(self.engine, '_current_expression_key', '') or ''
        mapping = (self._EXPR2_STATE_TO_NODE if '0,1' in current_expr
                   else self._EXPR1_STATE_TO_NODE)
        return mapping.get(str(state))

    def _highlight_state(self, state: str, *, accept_final: bool = False):
        """Reset all flowchart nodes and highlight the one for `state`."""
        self._reset_diagram_highlights()
        key = self._state_to_node_key(state)
        if key:
            keys = key if isinstance(key, list) else [key]
            for k in keys:
                if k in self._diagram_nodes:
                    self._diagram_nodes[k].highlight()
        if accept_final and 'Accept' in self._diagram_nodes:
            self._diagram_nodes['Accept'].highlight()

    def _reset_diagram_highlights(self):
        """Clear all flowchart highlights."""
        for node in self._diagram_nodes.values():
            node.reset_appearance()
        if hasattr(self, '_diagram_edges'):
            for items in self._diagram_edges.values():
                for item in items:
                    if isinstance(item, QGraphicsPathItem):
                        item.setPen(QPen(QColor("#6c7086"), 2))
                    elif isinstance(item, QGraphicsPolygonItem):
                        item.setBrush(QBrush(QColor("#6c7086")))
                    elif isinstance(item, QGraphicsTextItem):
                        item.setDefaultTextColor(QColor("#a6adc8"))

    def _find_nearest_node(self, x: float, y: float) -> Optional[str]:
        best = None
        best_dist = float('inf')
        for key, node in self._diagram_nodes.items():
            dist = (node.x - x)**2 + (node.y - y)**2
            if dist < best_dist:
                best_dist = dist
                best = key
        return best

    def _register_edge(self, x1, y1, x2, y2, items):
        if not hasattr(self, '_diagram_edges'):
            self._diagram_edges = {}
        from_node = self._find_nearest_node(x1, y1)
        to_node = self._find_nearest_node(x2, y2)
        if from_node and to_node:
            edge_id = f"{from_node}->{to_node}"
            if edge_id not in self._diagram_edges:
                self._diagram_edges[edge_id] = []
            self._diagram_edges[edge_id].extend([it for it in items if it])

    def _highlight_edge(self, edge_id: str):
        if hasattr(self, '_diagram_edges') and edge_id in self._diagram_edges:
            for item in self._diagram_edges[edge_id]:
                if isinstance(item, QGraphicsPathItem):
                    item.setPen(QPen(QColor("#a6e3a1"), 3))
                elif isinstance(item, QGraphicsPolygonItem):
                    item.setBrush(QBrush(QColor("#a6e3a1")))
                elif isinstance(item, QGraphicsTextItem):
                    item.setDefaultTextColor(QColor("#a6e3a1"))
    def _build_expression1_flowchart(self):
        """Build flowchart for Expression 1 exactly matching the user's reference image."""
        self.state_scene.clear()
        
        cx = 250
        y_spacing = 80
        y = 30
        
        # Start node
        start_node = EllipseNode(cx, y, "Start", "start")
        start_node.create_item(self.state_scene)
        self._flowchart_nodes['Start'] = (cx, y)
        self._diagram_nodes['Start'] = start_node
        
        y += y_spacing
        
        # First decision
        read1 = DiamondNode(cx, y, "Read", "decision")
        read1.create_item(self.state_scene)
        self._flowchart_nodes['Read1'] = (cx, y)
        self._diagram_nodes['Read1'] = read1
        
        self._draw_ortho_arrow(cx, y - y_spacing + 20, cx, y - 25, "", bend="v")
        
        # Arrow from Read1 straight down to Reject
        y_branch_top = y + 120
        y_reject = y + 220
        y_branch_bottom = y + 320
        
        reject = EllipseNode(cx, y_reject, "Reject", "reject")
        reject.create_item(self.state_scene)
        self._diagram_nodes['Reject'] = reject
        
        self._draw_ortho_arrow(cx, y + 25, cx, y_reject - 35, "null", bend="v")
        
        left_x = cx - 140
        right_x = cx + 140
        
        # Left Branch top (ReadB1)
        read_b1 = DiamondNode(left_x, y_branch_top, "Read", "decision")
        read_b1.create_item(self.state_scene)
        self._diagram_nodes['ReadB1'] = read_b1
        
        self._draw_ortho_arrow(cx - 25, y, left_x, y_branch_top - 25, "b", bend="hv")
        
        # Right Branch top (ReadA1)
        read_a1 = DiamondNode(right_x, y_branch_top, "Read", "decision")
        read_a1.create_item(self.state_scene)
        self._diagram_nodes['ReadA1'] = read_a1
        
        self._draw_ortho_arrow(cx + 25, y, right_x, y_branch_top - 25, "a", bend="hv")
        
        # Arrow ReadB1 -> Reject
        self._draw_ortho_arrow(left_x + 15, y_branch_top + 15, cx - 20, y_reject - 20, "b", bend="v", bend_pos=y_branch_top + 45)
        # Arrow ReadA1 -> Reject
        self._draw_ortho_arrow(right_x - 15, y_branch_top + 15, cx + 20, y_reject - 20, "a", bend="v", bend_pos=y_branch_top + 45)
        
        # Left Branch bottom (ReadB2)
        read_b2 = DiamondNode(left_x, y_branch_bottom, "Read", "decision")
        read_b2.create_item(self.state_scene)
        self._diagram_nodes['ReadB2'] = read_b2
        
        self._draw_ortho_arrow(left_x, y_branch_top + 25, left_x, y_branch_bottom - 25, "a", bend="v")
        
        # Right Branch bottom (ReadA2)
        read_a2 = DiamondNode(right_x, y_branch_bottom, "Read", "decision")
        read_a2.create_item(self.state_scene)
        self._diagram_nodes['ReadA2'] = read_a2
        
        self._draw_ortho_arrow(right_x, y_branch_top + 25, right_x, y_branch_bottom - 25, "b", bend="v")
        
        # Arrow ReadB2 -> Reject
        self._draw_ortho_arrow(left_x + 25, y_branch_bottom, cx - 25, y_reject + 15, "a", bend="h", bend_pos=left_x + 60)
        # Arrow ReadA2 -> Reject
        self._draw_ortho_arrow(right_x - 25, y_branch_bottom, cx + 25, y_reject + 15, "b", bend="h", bend_pos=right_x - 60)
        
        # Converge to the vertical line
        y = y_branch_bottom + y_spacing
        
        # ReadLoop (q5)
        read_loop = DiamondNode(cx, y, "Read", "decision")
        read_loop.create_item(self.state_scene)
        self._diagram_nodes['ReadLoop'] = read_loop
        
        self._draw_ortho_arrow(left_x + 15, y_branch_bottom + 15, cx - 15, y - 15, "b", bend="v", bend_pos=y_branch_bottom + 40)
        self._draw_ortho_arrow(right_x - 15, y_branch_bottom + 15, cx + 15, y - 15, "a", bend="v", bend_pos=y_branch_bottom + 40)
        self._draw_loop(cx, y, "a")
        
        # ReadBab1 (q6)
        y += y_spacing
        read_bab1 = DiamondNode(cx, y, "Read", "decision")
        read_bab1.create_item(self.state_scene)
        self._diagram_nodes['ReadBab1'] = read_bab1
        
        self._draw_ortho_arrow(cx, y - y_spacing + 25, cx, y - 25, "b", bend="v")
        self._draw_ortho_arrow(cx + 25, y, cx + 15, y - y_spacing + 15, "b", bend="h", bend_pos=cx + 60)
        
        # ReadBab2 (q7)
        y += y_spacing
        read_bab2 = DiamondNode(cx, y, "Read", "decision")
        read_bab2.create_item(self.state_scene)
        self._diagram_nodes['ReadBab2'] = read_bab2
        
        self._draw_ortho_arrow(cx, y - y_spacing + 25, cx, y - 25, "a", bend="v")
        self._draw_ortho_arrow(cx + 25, y, cx + 20, y - y_spacing*2 + 15, "a", bend="h", bend_pos=cx + 100)
        
        # ReadBab3 (q8)
        y += y_spacing
        read_bab3 = DiamondNode(cx, y, "Read", "decision")
        read_bab3.create_item(self.state_scene)
        self._diagram_nodes['ReadBab3'] = read_bab3
        
        self._draw_ortho_arrow(cx, y - y_spacing + 25, cx, y - 25, "b", bend="v")
        self._draw_loop(cx, y, "a,b")
        
        # Accept node
        y += y_spacing
        accept = EllipseNode(cx, y, "Accept", "accept")
        accept.create_item(self.state_scene)
        self._diagram_nodes['Accept'] = accept
        self._draw_ortho_arrow(cx, y - y_spacing + 25, cx, y - 20, "null", bend="v")
        
    def _build_expression2_flowchart(self):
        """
        Build flowchart for Expression 2 (0,1).
        Expression: ((101+111+101)+(1+0+11))(1+0+01)*(111+000+101)(1+0)*
        """
        cx = 250
        y_top = 120
        y_reject = 200
        y_row1 = 240
        y_row2 = 340
        y_row3 = 400
        y_row4 = 600
        y_row5 = 700
        y_accept = 800
        
        col_L2 = cx - 200
        col_L1 = cx - 100
        col_C = cx
        col_R1 = cx + 100
        col_R2 = cx + 200
        
        # Nodes
        start = EllipseNode(col_C, 30, "Start", "start")
        start.create_item(self.state_scene)
        self._diagram_nodes['Start'] = start
        
        d_top = DiamondNode(col_C, y_top, "Read", "decision")
        d_top.create_item(self.state_scene)
        self._diagram_nodes['D_Top'] = d_top
        
        reject = EllipseNode(col_C, y_reject, "Reject", "reject")
        reject.create_item(self.state_scene)
        self._diagram_nodes['Reject'] = reject
        
        d_l1 = DiamondNode(col_L2, y_row1, "Read", "decision")
        d_l1.create_item(self.state_scene)
        self._diagram_nodes['D_L1'] = d_l1
        
        d_r1 = DiamondNode(col_R2, y_row1, "Read", "decision")
        d_r1.create_item(self.state_scene)
        self._diagram_nodes['D_R1'] = d_r1
        
        d_l2 = DiamondNode(col_L2, y_row2, "Read", "decision")
        d_l2.create_item(self.state_scene)
        self._diagram_nodes['D_L2'] = d_l2
        
        d_m_right = DiamondNode(col_R1, y_row2, "Read", "decision")
        d_m_right.create_item(self.state_scene)
        self._diagram_nodes['D_M_Right'] = d_m_right
        
        d_r2 = DiamondNode(col_R2, y_row2, "Read", "decision")
        d_r2.create_item(self.state_scene)
        self._diagram_nodes['D_R2'] = d_r2
        
        d_m_left = DiamondNode(col_L1, y_row3, "Read", "decision")
        d_m_left.create_item(self.state_scene)
        self._diagram_nodes['D_M_Left'] = d_m_left
        
        d_l3 = DiamondNode(col_L2, y_row4, "Read", "decision")
        d_l3.create_item(self.state_scene)
        self._diagram_nodes['D_L3'] = d_l3
        
        d_q7 = DiamondNode(col_C, y_row4, "Read", "decision")
        d_q7.create_item(self.state_scene)
        self._diagram_nodes['D_q7'] = d_q7
        
        d_r3 = DiamondNode(col_R2, y_row4, "Read", "decision")
        d_r3.create_item(self.state_scene)
        self._diagram_nodes['D_R3'] = d_r3
        
        d_br = DiamondNode(col_R1, y_row5, "Read", "decision")
        d_br.create_item(self.state_scene)
        self._diagram_nodes['D_BR'] = d_br
        
        accept = EllipseNode(col_C, y_accept, "Accept", "accept")
        accept.create_item(self.state_scene)
        self._diagram_nodes['Accept'] = accept
        
        # Top arrows
        self._draw_ortho_arrow(col_C, 30 + 25, col_C, y_top - 25, "", bend="v")
        self._draw_ortho_arrow(col_C, y_top + 25, col_C, y_reject - 25, "null", bend="v") # triangle label equivalent
        
        self._draw_ortho_arrow(col_C - 25, y_top, col_L2, y_row1 - 25, "1", bend="hv")
        self._draw_ortho_arrow(col_C + 25, y_top, col_R2, y_row1 - 25, "0", bend="hv")
        
        # Row 1 -> Row 2
        self._draw_ortho_arrow(col_L2, y_row1 + 25, col_L2, y_row2 - 25, "1", bend="v")
        self._draw_ortho_arrow(col_L2 + 15, y_row1 + 15, col_R2 - 10, y_row2 - 20, "0", bend="v", bend_pos=y_row1 + 45) # L1 to R2
        
        self._draw_ortho_arrow(col_R2, y_row1 + 25, col_R2, y_row2 - 25, "0", bend="v")
        self._draw_ortho_arrow(col_R2 - 15, y_row1 + 15, col_R1, y_row2 - 25, "1", bend="v", bend_pos=y_row1 + 60)
        
        # Row 2 -> Row 3/4
        self._draw_ortho_arrow(col_L2, y_row2 + 25, col_L2, y_row4 - 25, "1", bend="v") # L2 to L3
        self._draw_ortho_arrow(col_L2 + 15, y_row2 + 15, col_L1, y_row3 - 25, "0", bend="v", bend_pos=y_row3 - 40) # L2 to M_Left
        
        self._draw_ortho_arrow(col_R1, y_row2 + 25, col_R1, y_row5 - 25, "1", bend="v") # M_Right to BR
        self._draw_ortho_arrow(col_R1 - 15, y_row2 + 15, col_L1 + 10, y_row3 - 20, "0", bend="v", bend_pos=y_row3 - 40) # M_Right to M_Left
        
        self._draw_ortho_arrow(col_R2, y_row2 + 25, col_R2, y_row4 - 25, "1", bend="v") # R2 to R3
        self._draw_ortho_arrow(col_R2 - 15, y_row2 + 15, col_C + 15, y_row4 - 15, "0", bend="v", bend_pos=500) # R2 to q7
        
        # Row 3 (M_Left) -> Row 4 / Accept
        self._draw_ortho_arrow(col_L1 + 15, y_row3 + 15, col_C - 15, y_row4 - 15, "0", bend="v", bend_pos=y_row3 + 45) # M_Left to q7
        self._draw_ortho_arrow(col_L1, y_row3 + 25, col_C - 20, y_accept - 25, "1", bend="v", bend_pos=750) # M_Left to Accept avoids q7
        
        # Row 4 -> Accept / Backwards
        # L3
        self._draw_ortho_arrow(col_L2, y_row4 + 25, col_C - 30, y_accept - 20, "1", bend="v", bend_pos=730) # L3 to Accept avoids q7
        self._draw_ortho_arrow(col_L2 + 25, y_row4, col_L1 - 15, y_row3 + 15, "0", bend="v", bend_pos=470) # L3 to M_Left backwards UP
        
        # q7
        self._draw_ortho_arrow(col_C, y_row4 + 25, col_C, y_accept - 25, "0", bend="v") # q7 to Accept
        self._draw_ortho_arrow(col_C + 25, y_row4, col_R2 - 25, y_row4, "1", bend="vh") # q7 to R3
        
        # R3
        self._draw_ortho_arrow(col_R2 - 15, y_row4 + 15, col_R1 + 15, y_row5 - 15, "1", bend="v", bend_pos=y_row4 + 50) # R3 to BR
        self._draw_ortho_arrow(col_R2 - 25, y_row4, col_L1 + 15, y_row3 + 15, "0", bend="v", bend_pos=470) # R3 to M_Left backwards UP
        
        # Row 5 (BR) -> Accept / Backwards
        self._draw_ortho_arrow(col_R1, y_row5 + 25, col_C + 20, y_accept - 25, "1", bend="v", bend_pos=750) # BR to Accept avoids q7
        
        # BR to M_Left (orthogonal path avoiding q7)
        path = QPainterPath()
        path.moveTo(col_R1 - 25, y_row5)
        path.lineTo(col_C + 50, y_row5)
        path.lineTo(col_C + 50, 485)
        path.lineTo(col_L1 + 5, 485)
        path.lineTo(col_L1 + 5, y_row3 + 20)
        path_item = self.state_scene.addPath(path, QPen(QColor("#6c7086"), 2))
        
        # Arrowhead and label for BR -> M_Left
        x2, y2 = col_L1 + 5, y_row3 + 20
        arrow_angle = -math.pi/2 # UP
        arrow_size = 10
        p1 = QPointF(x2, y2)
        p2 = QPointF(x2 - arrow_size * math.cos(arrow_angle - math.pi/6), y2 - arrow_size * math.sin(arrow_angle - math.pi/6))
        p3 = QPointF(x2 - arrow_size * math.cos(arrow_angle + math.pi/6), y2 - arrow_size * math.sin(arrow_angle + math.pi/6))
        arrow_item = self.state_scene.addPolygon(QPolygonF([p1, p2, p3]), QPen(Qt.PenStyle.NoPen), QBrush(QColor("#6c7086")))
        
        text = self.state_scene.addText("0")
        text.setDefaultTextColor(QColor("#a6adc8"))
        text.setFont(QFont("Segoe UI", 9))
        text.setPos(col_C + 55, 470)
        self._register_edge(col_R1 - 25, y_row5, col_L1 + 5, y_row3 + 20, [path_item, arrow_item, text])
        
        # Accept loop
        self._draw_loop_bottom(col_C, y_accept, "0, 1")
    
    def _draw_loop_bottom(self, cx: float, cy: float, label: str):
        """Draw a self-loop on the bottom (for Accept nodes)."""
        path = QPainterPath()
        path.moveTo(cx - 15, cy + 30)
        path.cubicTo(cx - 40, cy + 80, cx + 40, cy + 80, cx + 15, cy + 30)
        path_item = self.state_scene.addPath(path, QPen(QColor("#6c7086"), 2))
        
        # Arrowhead at (cx + 15, cy + 30)
        x2, y2 = cx + 15, cy + 30
        angle = math.atan2(-50, 25)
        arrow_size = 10
        p1 = QPointF(x2, y2)
        p2 = QPointF(x2 - arrow_size * math.cos(angle - math.pi/6), y2 - arrow_size * math.sin(angle - math.pi/6))
        p3 = QPointF(x2 - arrow_size * math.cos(angle + math.pi/6), y2 - arrow_size * math.sin(angle + math.pi/6))
        arrow_item = self.state_scene.addPolygon(QPolygonF([p1, p2, p3]), QPen(Qt.PenStyle.NoPen), QBrush(QColor("#6c7086")))
        
        text_item = self._draw_text(cx - 10, cy + 85, label)
        self._register_edge(cx, cy, cx, cy, [path_item, arrow_item, text_item])

    def _draw_loop_left(self, cx: float, cy: float, label: str):
        """Draw a self-loop indicator on the left side."""
        path = QPainterPath()
        path.moveTo(cx - 15, cy - 10)
        path.cubicTo(cx - 50, cy - 40, cx - 50, cy + 40, cx - 15, cy + 10)
        path_item = self.state_scene.addPath(path, QPen(QColor("#6c7086"), 2))
        
        # Arrowhead at (cx - 15, cy + 10)
        x2, y2 = cx - 15, cy + 10
        angle = math.atan2(-30, 35)
        arrow_size = 10
        p1 = QPointF(x2, y2)
        p2 = QPointF(x2 - arrow_size * math.cos(angle - math.pi/6), y2 - arrow_size * math.sin(angle - math.pi/6))
        p3 = QPointF(x2 - arrow_size * math.cos(angle + math.pi/6), y2 - arrow_size * math.sin(angle + math.pi/6))
        arrow_item = self.state_scene.addPolygon(QPolygonF([p1, p2, p3]), QPen(Qt.PenStyle.NoPen), QBrush(QColor("#6c7086")))
        
        text = self.state_scene.addText(label)
        text.setDefaultTextColor(QColor("#a6adc8"))
        text.setFont(QFont("Segoe UI", 9))
        text.setPos(cx - 75, cy - 8)
        self._register_edge(cx, cy, cx, cy, [path_item, arrow_item, text])
    
    def _draw_ortho_arrow(self, x1: float, y1: float, x2: float, y2: float, label: str, bend="v", bend_pos=None):
        """Draw an orthogonal arrow with right angles."""
        path = QPainterPath()
        path.moveTo(x1, y1)
        
        arrow_angle = 0
        
        if bend == "v":
            # vertical -> horizontal -> vertical
            by = bend_pos if bend_pos is not None else (y1 + y2) / 2
            path.lineTo(x1, by)
            path.lineTo(x2, by)
            path.lineTo(x2, y2)
            arrow_angle = math.pi/2 if y2 > by else -math.pi/2
            text_x = (x1 + x2) / 2
            text_y = by - 15
            if x1 == x2: text_x += 10
            
        elif bend == "h":
            # horizontal -> vertical -> horizontal
            bx = bend_pos if bend_pos is not None else (x1 + x2) / 2
            path.lineTo(bx, y1)
            path.lineTo(bx, y2)
            path.lineTo(x2, y2)
            arrow_angle = 0 if x2 > bx else math.pi
            text_x = bx
            text_y = (y1 + y2) / 2 - 15
            if y1 == y2: text_y -= 10
            
        elif bend == "vh":
            # vertical -> horizontal
            path.lineTo(x1, y2)
            path.lineTo(x2, y2)
            arrow_angle = 0 if x2 > x1 else math.pi
            text_x = (x1 + x2) / 2
            text_y = y2 - 15
            if x1 == x2: text_x += 10
            if y1 == y2: text_y -= 10
            
        elif bend == "hv":
            # horizontal -> vertical
            path.lineTo(x2, y1)
            path.lineTo(x2, y2)
            arrow_angle = math.pi/2 if y2 > y1 else -math.pi/2
            text_x = x2
            text_y = (y1 + y2) / 2 - 15
            if x1 == x2: text_x += 10
            if y1 == y2: text_y -= 10
            
        path_item = self.state_scene.addPath(path, QPen(QColor("#6c7086"), 2))
        
        # Draw arrowhead
        arrow_size = 10
        p1 = QPointF(x2, y2)
        p2 = QPointF(x2 - arrow_size * math.cos(arrow_angle - math.pi/6), 
                     y2 - arrow_size * math.sin(arrow_angle - math.pi/6))
        p3 = QPointF(x2 - arrow_size * math.cos(arrow_angle + math.pi/6), 
                     y2 - arrow_size * math.sin(arrow_angle + math.pi/6))
        arrow_item = self.state_scene.addPolygon(QPolygonF([p1, p2, p3]), QPen(Qt.PenStyle.NoPen), QBrush(QColor("#6c7086")))
        
        text = None
        if label:
            text = self.state_scene.addText(label)
            text.setDefaultTextColor(QColor("#a6adc8"))
            text.setFont(QFont("Segoe UI", 9))
            rect = text.boundingRect()
            if bend in ("v", "vh"):
                text.setPos(text_x - rect.width()/2, text_y - rect.height()/2)
            else:
                text.setPos(text_x + 5, text_y - rect.height()/2)
        self._register_edge(x1, y1, x2, y2, [path_item, arrow_item, text])

    def _draw_arrow(self, x1: float, y1: float, x2: float, y2: float, label: str):
        """Draw an arrow between two points."""
        # Line
        path_item = self.state_scene.addLine(x1, y1, x2, y2, QPen(QColor("#6c7086"), 2))
        
        # Arrow head
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_size = 10
        
        p1 = QPointF(x2, y2)
        p2 = QPointF(
            x2 - arrow_size * math.cos(angle - math.pi/6),
            y2 - arrow_size * math.sin(angle - math.pi/6)
        )
        p3 = QPointF(
            x2 - arrow_size * math.cos(angle + math.pi/6),
            y2 - arrow_size * math.sin(angle + math.pi/6)
        )
        
        polygon = QPolygonF([p1, p2, p3])
        arrow_item = self.state_scene.addPolygon(
            polygon,
            QPen(Qt.PenStyle.NoPen),
            QBrush(QColor("#6c7086"))
        )
        
        # Label
        if label:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            text = self.state_scene.addText(label)
            text.setDefaultTextColor(QColor("#a6adc8"))
            text.setFont(QFont("Segoe UI", 9))
            text.setPos(mid_x + 5, mid_y - 10)
        self._register_edge(x1, y1, x2, y2, [path_item, arrow_item, text if label else None])

    def _draw_curved_arrow(self, x1: float, y1: float, x2: float, y2: float, label: str, offset: float = 40):
        """Draw a curved arrow between two vertical points, bulging out."""
        path = QPainterPath()
        path.moveTo(x1, y1)
        
        mid_y = (y1 + y2) / 2
        path.quadTo(x1 + offset, mid_y, x2, y2)
        
        path_item = self.state_scene.addPath(path, QPen(QColor("#6c7086"), 2))
        
        angle = math.atan2(y2 - mid_y, x2 - (x1 + offset*0.5)) 
        arrow_size = 10
        
        p1 = QPointF(x2, y2)
        p2 = QPointF(
            x2 - arrow_size * math.cos(angle - math.pi/6),
            y2 - arrow_size * math.sin(angle - math.pi/6)
        )
        p3 = QPointF(
            x2 - arrow_size * math.cos(angle + math.pi/6),
            y2 - arrow_size * math.sin(angle + math.pi/6)
        )
        
        polygon = QPolygonF([p1, p2, p3])
        arrow_item = self.state_scene.addPolygon(
            polygon,
            QPen(Qt.PenStyle.NoPen),
            QBrush(QColor("#6c7086"))
        )
        
        if label:
            text = self.state_scene.addText(label)
            text.setDefaultTextColor(QColor("#a6adc8"))
            text.setFont(QFont("Segoe UI", 9))
            max_x = x1 + offset * 0.5
            # Place label outside the furthest point of the curve
            padding = 5 if offset > 0 else -20
            text.setPos(max_x + padding, mid_y - 10)
        self._register_edge(x1, y1, x2, y2, [path_item, arrow_item, text if label else None])
    
    def _draw_text(self, x: float, y: float, text: str):
        """Draw text at a position."""
        item = self.state_scene.addText(text)
        item.setDefaultTextColor(QColor("#a6adc8"))
        item.setFont(QFont("Segoe UI", 9))
        item.setPos(x, y)
        return item
    
    def _draw_loop(self, cx: float, cy: float, label: str):
        """Draw a self-loop indicator."""
        path = QPainterPath()
        path.moveTo(cx + 15, cy - 10)
        path.cubicTo(cx + 50, cy - 40, cx + 50, cy + 40, cx + 15, cy + 10)
        path_item = self.state_scene.addPath(path, QPen(QColor("#6c7086"), 2))
        
        # Arrowhead at (cx + 15, cy + 10)
        x2, y2 = cx + 15, cy + 10
        angle = math.atan2(-30, -35)
        arrow_size = 10
        p1 = QPointF(x2, y2)
        p2 = QPointF(x2 - arrow_size * math.cos(angle - math.pi/6), y2 - arrow_size * math.sin(angle - math.pi/6))
        p3 = QPointF(x2 - arrow_size * math.cos(angle + math.pi/6), y2 - arrow_size * math.sin(angle + math.pi/6))
        arrow_item = self.state_scene.addPolygon(QPolygonF([p1, p2, p3]), QPen(Qt.PenStyle.NoPen), QBrush(QColor("#6c7086")))
        
        text = self.state_scene.addText(label)
        text.setDefaultTextColor(QColor("#a6adc8"))
        text.setFont(QFont("Segoe UI", 9))
        text.setPos(cx + 55, cy - 8)
        self._register_edge(cx, cy, cx, cy, [path_item, arrow_item, text])
    
    def _draw_state(self, x: float, y: float, state_id: str,
                    is_initial: bool = False, is_final: bool = False):
        """Draw a state circle (legacy method)."""
        radius = 35
        
        # Outer circle
        circle = self.state_scene.addEllipse(
            x - radius, y - radius, radius * 2, radius * 2,
            QPen(QColor("#89b4fa"), 3),
            QBrush(QColor("#313244"))
        )
        
        # Inner circle for final states
        if is_final:
            inner_radius = radius - 6
            self.state_scene.addEllipse(
                x - inner_radius, y - inner_radius,
                inner_radius * 2, inner_radius * 2,
                QPen(QColor("#89b4fa"), 2),
                QBrush()
            )
        
        # Initial arrow
        if is_initial:
            self.state_scene.addLine(
                x - radius - 40, y,
                x - radius - 5, y,
                QPen(QColor("#89b4fa"), 3)
            )
        
        # Label
        label = self.state_scene.addText(str(state_id))
        label.setDefaultTextColor(QColor("#cdd6f4"))
        label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        rect = label.boundingRect()
        label.setPos(x - rect.width() / 2, y - rect.height() / 2)
    
    def process_string(self, input_string: str):
        """Start processing a string through the PDA."""
        self._on_reset()
        self._input_string = input_string
        
        self._current_result = self.engine.process_string_pda(input_string)
        self._current_step = 0
        
        total_steps = len(self._current_result.steps)
        self.step_label.setText(f"Step: 0 / {total_steps}")
        
        # Initialize stack
        self.stack_view.set_stack(['Z'])
        self.stack_info.setText("Stack: [ Z ]")
        
        # Initialize input display with cursor at position 0
        self._update_input_display(0)
        
        # Clear step log and add header
        self.step_log.clear()
        self.step_log.append(
            '<span style="color: #f9e2af;">Step | State → State | Input | Stack Action</span>'
        )
        self.step_log.append('<span style="color: #585b70;">─────────────────────────────────────────</span>')
        
        # Set initial state
        if self.engine.get_dfa_graph_data():
            initial = self.engine.get_dfa_graph_data()['initial_state']
            self.current_state_label.setText(f"Current State: {initial}")
            self._highlight_state(initial)
    
    def _on_play(self):
        """Start continuous animation."""
        if not self._current_result or self._is_animating:
            return
        
        self._is_animating = True
        self._animation_frame = 0
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.step_btn.setEnabled(False)
        
        self._animation_timer.start(self.FRAME_TIME_MS)
    
    def _on_pause(self):
        """Pause animation."""
        self._is_animating = False
        self._animation_timer.stop()
        
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.step_btn.setEnabled(True)
    
    def _on_step(self):
        """Advance one step."""
        if not self._current_result:
            return
        
        if self._current_step < len(self._current_result.steps):
            self._execute_step(self._current_result.steps[self._current_step])
            self._current_step += 1
            self.step_label.setText(
                f"Step: {self._current_step} / {len(self._current_result.steps)}"
            )
            self.step_changed.emit(self._current_step, len(self._current_result.steps))
            
            if self._current_step >= len(self._current_result.steps):
                self._finish_animation()
    
    def _on_reset(self):
        """Reset animation."""
        self._animation_timer.stop()
        self._is_animating = False
        self._current_step = 0
        self._animation_frame = 0
        self._input_string = ""
        
        self.stack_view.clear_stack()
        self.stack_view.set_stack(['Z'])
        self.stack_info.setText("Stack: [ Z ]")
        self.current_state_label.setText("Current State: -")
        self.current_state_label.setStyleSheet(
            "background-color: #313244; padding: 8px; border-radius: 4px; font-weight: bold;"
        )
        self._reset_diagram_highlights()
        self.transition_label.setText("δ(state, input, stack_top) → (new_state, stack_operation)")
        self.transition_label.setStyleSheet(
            "font-family: 'Cascadia Code'; font-size: 13px; padding: 10px;"
        )
        self.input_display.setText("")
        self.step_log.clear()
        
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.step_btn.setEnabled(True)
        self.step_label.setText("Step: 0 / 0")
        
        self._current_result = None
    
    def _animation_tick(self):
        """Called every frame during animation."""
        self._animation_frame += 1
        
        frames_per_transition = self.TRANSITION_DURATION_MS // self.FRAME_TIME_MS
        
        if self._animation_frame >= frames_per_transition:
            self._animation_frame = 0
            self._on_step()
            
            if self._current_step >= len(self._current_result.steps):
                self._animation_timer.stop()
                self._is_animating = False
    
    def _execute_step(self, step: TransitionStep):
        """Execute a single transition step."""
        # Update current state
        self.current_state_label.setText(f"Current State: {step.to_state}")

        # Highlight the corresponding flowchart node
        self._highlight_state(step.to_state)
        
        # Highlight edge
        from_keys = self._state_to_node_key(step.from_state)
        to_keys = self._state_to_node_key(step.to_state)
        
        if from_keys and to_keys:
            if not isinstance(from_keys, list): from_keys = [from_keys]
            if not isinstance(to_keys, list): to_keys = [to_keys]
            for fk in from_keys:
                for tk in to_keys:
                    self._highlight_edge(f"{fk}->{tk}")
        
        # Update stack visualization
        self.stack_view.set_stack(step.stack_after)
        
        # Update stack info text
        stack_str = ' '.join(step.stack_after) if step.stack_after else 'ε'
        self.stack_info.setText(f"Stack: [ {stack_str} ]")
        
        # Update input display with cursor at current position
        self._update_input_display(step.step_number)
        
        # Update step log with this transition
        action = step.pda_action if step.pda_action else "—"
        self.step_log.append(
            f'<span style="color: #6c7086;">  {step.step_number:>2} </span>'
            f'<span style="color: #cdd6f4;">{step.from_state}</span>'
            f'<span style="color: #6c7086;"> → </span>'
            f'<span style="color: #a6e3a1;">{step.to_state}</span>'
            f'<span style="color: #6c7086;">  |  </span>'
            f'<span style="color: #f9e2af;">\'{step.symbol}\'</span>'
            f'<span style="color: #6c7086;">  |  </span>'
            f'<span style="color: #cba6f7;">{action}</span>'
        )
        # Auto-scroll to bottom
        scrollbar = self.step_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Update transition display
        stack_before_top = step.stack_before[-1] if step.stack_before else 'ε'
        stack_after_str = ''.join(step.stack_after[-2:]) if len(step.stack_after) > 1 else (step.stack_after[0] if step.stack_after else 'ε')
        
        self.transition_label.setText(
            f"δ({step.from_state}, '{step.symbol}', {stack_before_top}) → "
            f"({step.to_state}, {stack_after_str})"
        )
        self.transition_label.setStyleSheet(
            "font-family: 'Cascadia Code'; font-size: 13px; padding: 10px; "
            "color: #a6e3a1;"
        )
    
    def _update_input_display(self, cursor_pos: int):
        """Update the input string display with a cursor highlighting the current position."""
        if not self._input_string:
            self.input_display.setText("")
            return
        
        parts = []
        for i, char in enumerate(self._input_string):
            if i < cursor_pos:
                # Already processed — dim green
                parts.append(f'<span style="color: #585b70;">{char}</span>')
            elif i == cursor_pos:
                # Current position — bright highlighted
                parts.append(
                    f'<span style="background-color: #f9e2af; color: #1e1e2e; '
                    f'padding: 2px 4px; border-radius: 3px; font-weight: bold;">{char}</span>'
                )
            else:
                # Not yet processed — normal
                parts.append(f'<span style="color: #cdd6f4;">{char}</span>')
        
        self.input_display.setText(''.join(parts))
    
    def _finish_animation(self):
        """Called when animation completes."""
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.step_btn.setEnabled(False)
        
        # Mark all input as processed
        if self._input_string:
            self._update_input_display(len(self._input_string))
        
        if self._current_result:
            if self._current_result.accepted:
                self.current_state_label.setStyleSheet(
                    "background-color: #1e3a2f; padding: 8px; border-radius: 4px; "
                    "font-weight: bold; color: #a6e3a1;"
                )
                self.step_log.append(
                    '<span style="color: #a6e3a1; font-weight: bold;">'
                    '✓ STRING ACCEPTED</span>'
                )
                # Highlight the final state and accept node on the diagram
                self._highlight_state(
                    self._current_result.final_state, accept_final=True
                )
            else:
                self.current_state_label.setStyleSheet(
                    "background-color: #3a1e2f; padding: 8px; border-radius: 4px; "
                    "font-weight: bold; color: #f38ba8;"
                )
                self.step_log.append(
                    '<span style="color: #f38ba8; font-weight: bold;">'
                    '✗ STRING REJECTED</span>'
                )
                self._highlight_state(self._current_result.final_state)
            
            self.animation_finished.emit(self._current_result.accepted)
    
    def _wheel_zoom_pda(self, event):
        """Handle mouse wheel for zooming the PDA diagram."""
        factor = 1.15
        if event.angleDelta().y() > 0:
            self.state_view.scale(factor, factor)
        else:
            self.state_view.scale(1 / factor, 1 / factor)
    
    def resizeEvent(self, event):
        """Handle resize to fit PDA diagram."""
        super().resizeEvent(event)
        rect = self.state_scene.sceneRect()
        if rect.isValid() and not rect.isEmpty():
            self.state_view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
