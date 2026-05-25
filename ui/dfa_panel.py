"""
DFA Panel - Deterministic Finite Automaton visualization.

Renders the DFA graph via Graphviz (DOT → PNG) and supports step-by-step
animated string processing with state/edge highlighting.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QLabel, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QBrush, QColor

from typing import Optional

from core.automata_engine import AutomataEngine, ProcessingResult, TransitionStep
from .graphviz_renderer import build_dfa_dot, render_dot_to_pixmap, BG


class DFAPanel(QWidget):
    """Panel for DFA visualization with animated string processing."""

    # Signals
    animation_finished = pyqtSignal(bool)  # Emits acceptance result
    step_changed = pyqtSignal(int, int)     # Current step, total steps

    STEP_INTERVAL_MS = 500  # milliseconds between auto-play steps

    def __init__(self, engine: AutomataEngine, parent=None):
        super().__init__(parent)
        self.engine = engine

        # Animation state
        self._current_result: Optional[ProcessingResult] = None
        self._current_step = 0
        self._is_animating = False
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._auto_step)

        # Current pixmap item in scene
        self._pixmap_item: Optional[QGraphicsPixmapItem] = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Graphics view for DFA diagram
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor(BG)))

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
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

    # ------------------------------------------------------------------
    # Graph rendering
    # ------------------------------------------------------------------

    def build_graph(self):
        """Build the DFA graph visualization from engine data."""
        self._render_dfa()

    def _render_dfa(
        self,
        highlight_nodes: set[str] | None = None,
        highlight_edges: set[tuple[str, str]] | None = None,
        active_node: str | None = None,
    ):
        """Render the DFA DOT to a pixmap and display it."""
        dot = build_dfa_dot(
            self.engine,
            highlight_nodes=highlight_nodes,
            highlight_edges=highlight_edges,
            active_node=active_node,
        )
        try:
            pixmap = render_dot_to_pixmap(dot)
        except Exception as e:
            print(f"DFA render failed: {e}")
            return

        self.scene.clear()
        self._pixmap_item = self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(self._pixmap_item.boundingRect())

        # Fit to view
        self.view.resetTransform()
        self.view.fitInView(
            self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio
        )

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------

    def process_string(self, input_string: str):
        """Start processing a string through the DFA."""
        self._on_reset()
        self._current_result = self.engine.process_string_dfa(input_string)
        self._current_step = 0

        total_steps = len(self._current_result.steps)
        self.step_label.setText(f"Step: 0 / {total_steps}")

        # Highlight initial state
        data = self.engine.get_dfa_graph_data()
        if data:
            initial = str(data["initial_state"])
            self._render_dfa(active_node=initial)

    def _on_play(self):
        """Start continuous animation."""
        if not self._current_result or self._is_animating:
            return
        self._is_animating = True
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.step_btn.setEnabled(False)
        self._animation_timer.start(self.STEP_INTERVAL_MS)

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
            self.step_changed.emit(
                self._current_step, len(self._current_result.steps)
            )

            if self._current_step >= len(self._current_result.steps):
                self._finish_animation()

    def _auto_step(self):
        """Called by the play timer to advance one step."""
        if not self._current_result:
            self._on_pause()
            return

        self._on_step()

        if self._current_step >= len(self._current_result.steps):
            self._on_pause()

    def _on_reset(self):
        """Reset animation to initial state."""
        self._animation_timer.stop()
        self._is_animating = False
        self._current_step = 0
        self._current_result = None

        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.step_btn.setEnabled(True)
        self.step_label.setText("Step: 0 / 0")

        # Re-render without highlights
        self._render_dfa()

    def _execute_step(self, step: TransitionStep):
        """Execute a single transition step visually."""
        from_s = str(step.from_state)
        to_s = str(step.to_state)

        self._render_dfa(
            highlight_nodes={from_s},
            highlight_edges={(from_s, to_s)},
            active_node=to_s,
        )

    def _finish_animation(self):
        """Called when animation completes."""
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.step_btn.setEnabled(False)

        if self._current_result:
            # Final state highlighting: green for accepted, red for rejected
            final = str(self._current_result.final_state)
            if self._current_result.accepted:
                self._render_dfa(active_node=final)
            else:
                # Re-render with red final state
                from .graphviz_renderer import RED, SURFACE
                dot = build_dfa_dot(self.engine)
                # Inject red highlight for the final state
                old = f'"{final}" ['
                red_attrs = (
                    f'"{final}" [fillcolor="#3a1e2f", color="{RED}", penwidth=5, '
                )
                dot = dot.replace(old, red_attrs, 1)
                try:
                    pixmap = render_dot_to_pixmap(dot)
                    self.scene.clear()
                    self._pixmap_item = self.scene.addPixmap(pixmap)
                    self.scene.setSceneRect(self._pixmap_item.boundingRect())
                    self.view.resetTransform()
                    self.view.fitInView(
                        self.scene.sceneRect(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                    )
                except Exception:
                    pass

            self.animation_finished.emit(self._current_result.accepted)

    # ------------------------------------------------------------------
    # Zoom / resize
    # ------------------------------------------------------------------

    def _wheel_zoom(self, event):
        """Handle mouse wheel for zooming."""
        factor = 1.15
        if event.angleDelta().y() > 0:
            self.view.scale(factor, factor)
        else:
            self.view.scale(1 / factor, 1 / factor)

    def resizeEvent(self, event):
        """Handle resize to fit graph."""
        super().resizeEvent(event)
        if self.scene.sceneRect().isValid() and not self.scene.sceneRect().isEmpty():
            self.view.fitInView(
                self.scene.sceneRect(),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
