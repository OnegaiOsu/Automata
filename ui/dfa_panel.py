"""
DFA Panel - Animated DFA visualization with step-by-step string processing.
Uses QGraphicsView for rendering and QTimer for 120fps animation.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsTextItem, QGraphicsLineItem, QGraphicsPathItem,
    QLabel, QSizePolicy, QGraphicsItem
)
from PyQt6.QtCore import (
    Qt, QTimer, QPointF, QRectF, pyqtSignal, QLineF
)
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QPainterPath, QFont,
    QPainter, QPolygonF
)
import math
from typing import Optional
from core.automata_engine import AutomataEngine, ProcessingResult, TransitionStep


class StateNode(QGraphicsEllipseItem):
    """Visual representation of a DFA state."""
    
    def __init__(self, state_id, x: float, y: float, radius: float = 35):
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.state_id = str(state_id).strip('"')  # Strip any quotes from state names
        self.radius = radius
        self.setPos(x, y)
        
        # Default appearance
        self.default_pen = QPen(QColor("#89b4fa"), 3)
        self.highlight_pen = QPen(QColor("#f9e2af"), 5)
        self.active_pen = QPen(QColor("#a6e3a1"), 5)
        self.default_brush = QBrush(QColor("#313244"))
        self.highlight_brush = QBrush(QColor("#45475a"))
        self.active_brush = QBrush(QColor("#1e3a2f"))
        
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)
        
        # State label — clean display name
        display_name = self.state_id
        self.label = QGraphicsTextItem(display_name, self)
        self.label.setDefaultTextColor(QColor("#cdd6f4"))
        font_size = 10 if len(display_name) > 2 else 12
        font = QFont("Segoe UI", font_size, QFont.Weight.Bold)
        self.label.setFont(font)
        
        # Center the label
        rect = self.label.boundingRect()
        self.label.setPos(-rect.width() / 2, -rect.height() / 2)
        
        self._is_final = False
        self._is_initial = False
        self._inner_circle = None
    
    def set_final(self, is_final: bool):
        """Mark state as final (accepting) with double circle."""
        self._is_final = is_final
        if is_final:
            inner_radius = self.radius - 6
            self._inner_circle = QGraphicsEllipseItem(
                -inner_radius, -inner_radius,
                inner_radius * 2, inner_radius * 2,
                self
            )
            self._inner_circle.setPen(QPen(QColor("#89b4fa"), 2))
            self._inner_circle.setBrush(QBrush(Qt.BrushStyle.NoBrush))
    
    def set_initial(self, is_initial: bool):
        """Mark state as initial."""
        self._is_initial = is_initial
    
    def highlight(self, active: bool = False):
        """Highlight this state."""
        if active:
            self.setPen(self.active_pen)
            self.setBrush(self.active_brush)
        else:
            self.setPen(self.highlight_pen)
            self.setBrush(self.highlight_brush)
    
    def reset_appearance(self):
        """Reset to default appearance."""
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)


class TransitionEdge(QGraphicsPathItem):
    """Visual representation of a DFA transition."""
    
    def __init__(self, from_node: StateNode, to_node: StateNode, label: str):
        super().__init__()
        self.from_node = from_node
        self.to_node = to_node
        self.label_text = label
        
        # Default appearance
        self.default_pen = QPen(QColor("#6c7086"), 2)
        self.highlight_pen = QPen(QColor("#f9e2af"), 4)
        self.active_pen = QPen(QColor("#a6e3a1"), 4)
        
        self.setPen(self.default_pen)
        
        # Create label
        self.label = QGraphicsTextItem(label)
        self.label.setDefaultTextColor(QColor("#a6adc8"))
        font = QFont("Segoe UI", 10)
        self.label.setFont(font)
        
        # Arrow head
        self.arrow = QGraphicsPolygonItem()
        self.arrow.setBrush(QBrush(QColor("#6c7086")))
        self.arrow.setPen(QPen(Qt.PenStyle.NoPen))
        
        self._update_path()
    
    def _update_path(self):
        """Update the path based on node positions."""
        path = QPainterPath()
        
        start = self.from_node.pos()
        end = self.to_node.pos()
        
        if self.from_node == self.to_node:
            # Self-loop
            radius = self.from_node.radius
            loop_size = 30
            
            # Position loop above the state
            cx = start.x()
            cy = start.y() - radius - loop_size
            
            path.moveTo(start.x() - 10, start.y() - radius)
            path.cubicTo(
                cx - loop_size, cy - loop_size,
                cx + loop_size, cy - loop_size,
                start.x() + 10, start.y() - radius
            )
            
            # Arrow pointing down-right
            arrow_points = [
                QPointF(start.x() + 10, start.y() - radius),
                QPointF(start.x() + 5, start.y() - radius - 10),
                QPointF(start.x() + 18, start.y() - radius - 5)
            ]
            self.arrow.setPolygon(QPolygonF(arrow_points))
            
            # Label position
            self.label.setPos(cx - self.label.boundingRect().width() / 2,
                             cy - loop_size - 15)
        else:
            # Regular edge
            dx = end.x() - start.x()
            dy = end.y() - start.y()
            length = math.sqrt(dx * dx + dy * dy)
            
            if length == 0:
                return
            
            # Normalize
            dx /= length
            dy /= length
            
            # Start and end points on circle edges
            start_point = QPointF(
                start.x() + dx * self.from_node.radius,
                start.y() + dy * self.from_node.radius
            )
            end_point = QPointF(
                end.x() - dx * self.to_node.radius,
                end.y() - dy * self.to_node.radius
            )
            
            # Curve the line slightly for parallel edges
            mid = QPointF((start_point.x() + end_point.x()) / 2,
                         (start_point.y() + end_point.y()) / 2)
            
            # Perpendicular offset
            offset = 20
            mid_offset = QPointF(mid.x() - dy * offset, mid.y() + dx * offset)
            
            path.moveTo(start_point)
            path.quadTo(mid_offset, end_point)
            
            # Arrow head at end
            arrow_size = 12
            angle = math.atan2(end_point.y() - mid_offset.y(),
                             end_point.x() - mid_offset.x())
            
            arrow_points = [
                end_point,
                QPointF(end_point.x() - arrow_size * math.cos(angle - math.pi/6),
                       end_point.y() - arrow_size * math.sin(angle - math.pi/6)),
                QPointF(end_point.x() - arrow_size * math.cos(angle + math.pi/6),
                       end_point.y() - arrow_size * math.sin(angle + math.pi/6))
            ]
            self.arrow.setPolygon(QPolygonF(arrow_points))
            
            # Label at midpoint
            self.label.setPos(mid_offset.x() - self.label.boundingRect().width() / 2,
                             mid_offset.y() - self.label.boundingRect().height() / 2)
        
        self.setPath(path)
    
    def highlight(self, active: bool = False):
        """Highlight this edge."""
        if active:
            self.setPen(self.active_pen)
            self.arrow.setBrush(QBrush(QColor("#a6e3a1")))
        else:
            self.setPen(self.highlight_pen)
            self.arrow.setBrush(QBrush(QColor("#f9e2af")))
    
    def reset_appearance(self):
        """Reset to default appearance."""
        self.setPen(self.default_pen)
        self.arrow.setBrush(QBrush(QColor("#6c7086")))


class QGraphicsPolygonItem(QGraphicsItem):
    """Simple polygon item for arrow heads."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._polygon = QPolygonF()
        self._brush = QBrush(Qt.GlobalColor.white)
        self._pen = QPen(Qt.PenStyle.NoPen)
    
    def setPolygon(self, polygon: QPolygonF):
        self.prepareGeometryChange()
        self._polygon = polygon
        self.update()
    
    def setBrush(self, brush: QBrush):
        self._brush = brush
        self.update()
    
    def setPen(self, pen: QPen):
        self._pen = pen
        self.update()
    
    def boundingRect(self) -> QRectF:
        return self._polygon.boundingRect()
    
    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawPolygon(self._polygon)


class DFAPanel(QWidget):
    """Panel for DFA visualization with animated string processing."""
    
    # Signals
    animation_finished = pyqtSignal(bool)  # Emits acceptance result
    step_changed = pyqtSignal(int, int)     # Current step, total steps
    
    # Animation timing for 120fps
    FRAME_TIME_MS = 8  # ~120fps (8.33ms rounded)
    TRANSITION_DURATION_MS = 400  # 400ms per transition (48 frames)
    
    def __init__(self, engine: AutomataEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        
        # State
        self._nodes: dict[str, StateNode] = {}
        self._edges: list[TransitionEdge] = []
        self._current_result: Optional[ProcessingResult] = None
        self._current_step = 0
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._animation_tick)
        self._animation_frame = 0
        self._is_animating = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Graphics view for DFA diagram
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#11111b")))
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.view.setMinimumSize(600, 400)
        
        # Enable wheel zoom
        self.view.wheelEvent = self._wheel_zoom
        
        layout.addWidget(self.view, 1)
        
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
        
        # Step indicator
        self.step_label = QLabel("Step: 0 / 0")
        self.step_label.setObjectName("status")
        controls_layout.addWidget(self.step_label)
        
        layout.addLayout(controls_layout)
    
    def _compute_graphviz_layout(self, states, transitions, initial_state, final_states) -> dict:
        """Use Graphviz to compute optimal node positions."""
        try:
            import graphviz
            import os
            import sys
            
            # Add local Graphviz to PATH
            if getattr(sys, 'frozen', False):
                # Bundled with PyInstaller
                bundle_dir = sys._MEIPASS
                graphviz_bin = os.path.join(bundle_dir, 'graphviz')
            else:
                # Development - use local Graphviz folder
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                graphviz_bin = os.path.join(app_dir, 'Graphviz-14.1.2-win64', 'bin')
            
            if os.path.exists(graphviz_bin):
                os.environ['PATH'] = graphviz_bin + os.pathsep + os.environ.get('PATH', '')
            
            # Create a directed graph
            dot = graphviz.Digraph(engine='dot')
            dot.attr(rankdir='LR')  # Left to right flow
            dot.attr('node', shape='circle', width='0.5', fixedsize='true')
            dot.attr('graph', nodesep='0.4', ranksep='0.6', splines='true')
            
            # Add nodes
            for state in states:
                state_str = str(state)
                shape = 'doublecircle' if state_str in final_states else 'circle'
                dot.node(state_str, state_str, shape=shape)
            
            # Add invisible start node pointing to initial
            dot.node('__start__', '', shape='none', width='0', height='0')
            dot.edge('__start__', initial_state)
            
            # Add edges (group by source-target pair)
            edge_labels = {}
            for from_state, trans in transitions.items():
                for symbol, to_state in trans.items():
                    key = (str(from_state), str(to_state))
                    if key not in edge_labels:
                        edge_labels[key] = []
                    edge_labels[key].append(symbol)
            
            for (f, t), symbols in edge_labels.items():
                label = ','.join(sorted(symbols))
                dot.edge(f, t, label=label)
            
            # Render to get positions
            dot.format = 'plain'
            output = dot.pipe().decode('utf-8')
            
            # Parse plain format: node name x y width height
            positions = {}
            scale = 120  # Scale for node spacing (larger = more readable)
            
            for line in output.strip().split('\n'):
                parts = line.split()
                if parts[0] == 'node' and parts[1] != '__start__':
                    # Strip quotes that graphviz adds around names with special chars
                    name = parts[1].strip('"')
                    x = float(parts[2]) * scale
                    y = -float(parts[3]) * scale
                    positions[name] = (x, y)
            
            # Center the positions
            if positions:
                min_x = min(p[0] for p in positions.values())
                min_y = min(p[1] for p in positions.values())
                positions = {k: (v[0] - min_x, v[1] - min_y) for k, v in positions.items()}
            
            return positions
            
        except Exception as e:
            print(f"Graphviz layout failed: {e}, falling back to circular")
            return self._fallback_circular_layout(states, initial_state)
    
    def _wheel_zoom(self, event):
        """Handle mouse wheel for zooming."""
        factor = 1.15
        if event.angleDelta().y() > 0:
            self.view.scale(factor, factor)
        else:
            self.view.scale(1 / factor, 1 / factor)
    
    def _fallback_circular_layout(self, states, initial_state) -> dict:
        """Fallback circular layout if Graphviz fails."""
        positions = {}
        state_list = sorted(str(s) for s in states)
        num_states = len(state_list)
        radius = max(200, num_states * 30)
        angle_step = 2 * math.pi / num_states
        
        for i, state in enumerate(state_list):
            angle = i * angle_step - math.pi / 2
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            positions[state] = (x, y)
        
        return positions

    def build_graph(self):
        """Build the DFA graph visualization from engine data."""
        self.scene.clear()
        self._nodes.clear()
        self._edges.clear()
        
        data = self.engine.get_dfa_graph_data()
        if not data:
            # Show placeholder message
            text = self.scene.addText("No DFA loaded. Select an expression above.")
            text.setDefaultTextColor(QColor("#6c7086"))
            text.setFont(QFont("Helvetica", 14))
            return
        
        states = data['states']
        transitions = data['transitions']
        initial_state = str(data['initial_state'])
        final_states = set(str(s) for s in data['final_states'])
        
        # Use Graphviz for layout computation
        positions = self._compute_graphviz_layout(states, transitions, initial_state, final_states)
        
        num_states = len(states)
        node_radius = 28 if num_states > 15 else 35
        
        for state_str, (x, y) in positions.items():
            node = StateNode(state_str, x, y, radius=node_radius)
            node.set_initial(state_str == initial_state)
            node.set_final(state_str in final_states)
            
            self._nodes[state_str] = node
            self.scene.addItem(node)
        
        # Create edges
        edge_map = {}  # Track edges between state pairs
        
        for from_state, trans in transitions.items():
            from_state_str = str(from_state)
            if from_state_str not in self._nodes:
                continue
                
            # Group by target
            target_symbols = {}
            for symbol, to_state in trans.items():
                to_state_str = str(to_state)
                if to_state_str not in self._nodes:
                    continue
                key = (from_state_str, to_state_str)
                if key not in target_symbols:
                    target_symbols[key] = []
                target_symbols[key].append(symbol)
            
            for (f, t), symbols in target_symbols.items():
                label = ','.join(sorted(symbols))
                edge = TransitionEdge(self._nodes[f], self._nodes[t], label)
                self._edges.append(edge)
                self.scene.addItem(edge)
                self.scene.addItem(edge.label)
                self.scene.addItem(edge.arrow)
        
        # Add initial state arrow
        if initial_state in self._nodes:
            node = self._nodes[initial_state]
            start_x = node.pos().x() - 80
            start_y = node.pos().y()
            
            arrow_line = self.scene.addLine(
                start_x, start_y,
                node.pos().x() - node.radius - 5, start_y,
                QPen(QColor("#89b4fa"), 3)
            )
            
            # Arrow head
            arrow_points = [
                QPointF(node.pos().x() - node.radius, start_y),
                QPointF(node.pos().x() - node.radius - 12, start_y - 6),
                QPointF(node.pos().x() - node.radius - 12, start_y + 6)
            ]
            arrow_head = QGraphicsPolygonItem()
            arrow_head.setPolygon(QPolygonF(arrow_points))
            arrow_head.setBrush(QBrush(QColor("#89b4fa")))
            self.scene.addItem(arrow_head)
        
        # Set scene rect with padding and fit to view
        rect = self.scene.itemsBoundingRect()
        rect.adjust(-80, -80, 80, 80)
        self.scene.setSceneRect(rect)
        
        # Reset transform and fit entire graph in view
        self.view.resetTransform()
        self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
    
    def process_string(self, input_string: str):
        """Start processing a string through the DFA."""
        self._on_reset()
        
        self._current_result = self.engine.process_string_dfa(input_string)
        self._current_step = 0
        
        total_steps = len(self._current_result.steps)
        self.step_label.setText(f"Step: 0 / {total_steps}")
        
        # Highlight initial state
        if self.engine.get_dfa_graph_data():
            initial = str(self.engine.get_dfa_graph_data()['initial_state'])
            if initial in self._nodes:
                self._nodes[initial].highlight(active=True)
    
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
        """Reset animation to initial state."""
        self._animation_timer.stop()
        self._is_animating = False
        self._current_step = 0
        self._animation_frame = 0
        
        # Reset all node and edge appearances
        for node in self._nodes.values():
            node.reset_appearance()
        for edge in self._edges:
            edge.reset_appearance()
        
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.step_btn.setEnabled(True)
        self.step_label.setText("Step: 0 / 0")
        
        self._current_result = None
    
    def _animation_tick(self):
        """Called every frame during animation."""
        self._animation_frame += 1
        
        # Check if transition is complete (400ms = 48 frames at 120fps)
        frames_per_transition = self.TRANSITION_DURATION_MS // self.FRAME_TIME_MS
        
        if self._animation_frame >= frames_per_transition:
            self._animation_frame = 0
            self._on_step()
            
            if self._current_step >= len(self._current_result.steps):
                self._animation_timer.stop()
                self._is_animating = False
    
    def _execute_step(self, step: TransitionStep):
        """Execute a single transition step visually."""
        # Reset previous highlights
        for node in self._nodes.values():
            node.reset_appearance()
        for edge in self._edges:
            edge.reset_appearance()
        
        from_state_str = str(step.from_state)
        to_state_str = str(step.to_state)
        
        # Highlight from state
        if from_state_str in self._nodes:
            self._nodes[from_state_str].highlight(active=False)
        
        # Highlight transition edge
        for edge in self._edges:
            if (edge.from_node.state_id == from_state_str and
                edge.to_node.state_id == to_state_str and
                step.symbol in edge.label_text):
                edge.highlight(active=True)
                break
        
        # Highlight to state (active)
        if to_state_str in self._nodes:
            self._nodes[to_state_str].highlight(active=True)
    
    def _finish_animation(self):
        """Called when animation completes."""
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.step_btn.setEnabled(False)
        
        if self._current_result:
            # Final state highlighting
            final_state = str(self._current_result.final_state)
            if final_state in self._nodes:
                node = self._nodes[final_state]
                if self._current_result.accepted:
                    node.setPen(QPen(QColor("#a6e3a1"), 6))
                    node.setBrush(QBrush(QColor("#1e3a2f")))
                else:
                    node.setPen(QPen(QColor("#f38ba8"), 6))
                    node.setBrush(QBrush(QColor("#3a1e2f")))
            
            self.animation_finished.emit(self._current_result.accepted)
    
    def resizeEvent(self, event):
        """Handle resize to fit graph."""
        super().resizeEvent(event)
        if self.scene.sceneRect().isValid() and not self.scene.sceneRect().isEmpty():
            self.view.fitInView(
                self.scene.sceneRect(),
                Qt.AspectRatioMode.KeepAspectRatio
            )
