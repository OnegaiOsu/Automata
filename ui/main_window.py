"""
Main Window - Primary application window with expression selection,
string input, and tabbed visualization views.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLineEdit, QPushButton, QTabWidget,
    QLabel, QMessageBox, QFrame, QSizePolicy, QSplitter
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from core.automata_engine import AutomataEngine
from .dfa_panel import DFAPanel
from .cfg_panel import CFGPanel
from .pda_panel import PDAPanel


class MainWindow(QMainWindow):
    """Main application window for Automata Visualizer."""
    
    def __init__(self):
        super().__init__()
        
        self.engine = AutomataEngine()
        
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        
        # Load first expression by default
        self._on_expression_changed(0)
    
    def _setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle("Automata Theory Visualizer")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Load stylesheet
        try:
            import os
            style_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'resources', 'styles.qss'
            )
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Could not load stylesheet: {e}")
    
    def _setup_ui(self):
        """Set up the main UI layout with left sidebar."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout: sidebar | visualization
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== LEFT SIDEBAR =====
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 15, 15, 15)
        sidebar_layout.setSpacing(12)
        
        # Expression selector
        expr_label = QLabel("Expression")
        expr_label.setObjectName("sidebarLabel")
        sidebar_layout.addWidget(expr_label)
        
        self.expression_combo = QComboBox()
        self.expression_combo.addItems(self.engine.get_expression_names())
        sidebar_layout.addWidget(self.expression_combo)
        
        # Regex display (read-only label style)
        self.regex_display = QLabel("")
        self.regex_display.setObjectName("regexDisplay")
        self.regex_display.setWordWrap(True)
        sidebar_layout.addWidget(self.regex_display)
        
        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setObjectName("sidebarSeparator")
        sidebar_layout.addWidget(sep1)
        
        # Test String input
        input_label = QLabel("Test String")
        input_label.setObjectName("sidebarLabel")
        sidebar_layout.addWidget(input_label)
        
        self.string_input = QLineEdit()
        self.string_input.setPlaceholderText("Enter string...")
        sidebar_layout.addWidget(self.string_input)
        
        # Alphabet hint
        self.alphabet_hint = QLabel("Alphabet: {a, b}")
        self.alphabet_hint.setObjectName("hint")
        sidebar_layout.addWidget(self.alphabet_hint)
        
        # Test button
        self.test_btn = QPushButton("Test")
        sidebar_layout.addWidget(self.test_btn)
        
        # Result label
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.result_label)
        
        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setObjectName("sidebarSeparator")
        sidebar_layout.addWidget(sep2)
        
        # View selector buttons
        view_label = QLabel("View")
        view_label.setObjectName("sidebarLabel")
        sidebar_layout.addWidget(view_label)
        
        self.dfa_btn = QPushButton("DFA")
        self.dfa_btn.setObjectName("viewBtn")
        self.dfa_btn.setCheckable(True)
        self.dfa_btn.setChecked(True)
        sidebar_layout.addWidget(self.dfa_btn)
        
        self.cfg_btn = QPushButton("CFG")
        self.cfg_btn.setObjectName("viewBtn")
        self.cfg_btn.setCheckable(True)
        sidebar_layout.addWidget(self.cfg_btn)
        
        self.pda_btn = QPushButton("PDA")
        self.pda_btn.setObjectName("viewBtn")
        self.pda_btn.setCheckable(True)
        sidebar_layout.addWidget(self.pda_btn)
        
        # Spacer
        sidebar_layout.addStretch()
        
        # State count at bottom
        self.state_count_label = QLabel("States: 0")
        self.state_count_label.setObjectName("hint")
        sidebar_layout.addWidget(self.state_count_label)
        
        main_layout.addWidget(sidebar)
        
        # ===== VISUALIZATION AREA =====
        viz_container = QWidget()
        viz_layout = QVBoxLayout(viz_container)
        viz_layout.setContentsMargins(0, 0, 0, 0)
        viz_layout.setSpacing(0)
        
        # Stacked panels (we'll show/hide instead of using tabs)
        self.dfa_panel = DFAPanel(self.engine)
        self.cfg_panel = CFGPanel(self.engine)
        self.pda_panel = PDAPanel(self.engine)
        
        # Use QTabWidget but hide the tab bar
        self.tab_widget = QTabWidget()
        self.tab_widget.tabBar().setVisible(False)
        self.tab_widget.addTab(self.dfa_panel, "DFA")
        self.tab_widget.addTab(self.cfg_panel, "CFG")
        self.tab_widget.addTab(self.pda_panel, "PDA")
        
        viz_layout.addWidget(self.tab_widget)
        
        main_layout.addWidget(viz_container, 1)
    
    def _connect_signals(self):
        """Connect UI signals to handlers."""
        self.expression_combo.currentIndexChanged.connect(self._on_expression_changed)
        self.test_btn.clicked.connect(self._on_test_string)
        self.string_input.returnPressed.connect(self._on_test_string)
        
        # View buttons
        self.dfa_btn.clicked.connect(lambda: self._switch_view(0))
        self.cfg_btn.clicked.connect(lambda: self._switch_view(1))
        self.pda_btn.clicked.connect(lambda: self._switch_view(2))
        
        # Animation finished signals
        self.dfa_panel.animation_finished.connect(self._on_animation_finished)
        self.cfg_panel.animation_finished.connect(self._on_animation_finished)
        self.pda_panel.animation_finished.connect(self._on_animation_finished)
    
    def _switch_view(self, index: int):
        """Switch between DFA, CFG, PDA views."""
        self.tab_widget.setCurrentIndex(index)
        
        # Update button states
        self.dfa_btn.setChecked(index == 0)
        self.cfg_btn.setChecked(index == 1)
        self.pda_btn.setChecked(index == 2)
    
    def _on_expression_changed(self, index: int):
        """Handle expression selection change."""
        expression_names = self.engine.get_expression_names()
        if index < 0 or index >= len(expression_names):
            return
        
        name = expression_names[index]
        success = self.engine.set_expression(name)
        
        if success:
            # Update regex display
            self.regex_display.setText(self.engine.current_expression)
            
            # Update alphabet hint
            alphabet = self.engine.alphabet
            self.alphabet_hint.setText(f"Alphabet: {{{', '.join(sorted(alphabet))}}}")
            
            # Update state count
            self.state_count_label.setText(f"States: {self.engine.state_count}")
            
            # Check for state warning
            if self.engine.states_warning:
                QMessageBox.warning(
                    self,
                    "Large DFA Warning",
                    f"The DFA for this expression has {self.engine.state_count} states "
                    f"(exceeds {self.engine.MAX_STATES_WARNING}).\n\n"
                    "This may affect visualization performance. "
                    "The DFA has been minimized for optimal representation.",
                    QMessageBox.StandardButton.Ok
                )
            
            # Clear previous results
            self.result_label.setText("")
            self.result_label.setStyleSheet("")
            self.string_input.clear()
            
            # Update all panels
            self.dfa_panel.build_graph()
            self.cfg_panel.update_grammar()
            self.pda_panel.build_diagram()
    
    def _on_test_string(self):
        """Handle test string button click."""
        input_string = self.string_input.text().strip()
        if input_string.lower() == "null" or input_string == "ε":
            input_string = ""
        
        if not input_string and self.string_input.text().strip().lower() != "null" and self.string_input.text().strip() != "ε" and self.string_input.text().strip() != "":
            QMessageBox.information(
                self,
                "Input Required",
                "Please enter a string to test.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Validate string
        is_valid, message = self.engine.validate_string(input_string)
        
        if "Invalid symbol" in message:
            alphabet = self.engine.alphabet
            QMessageBox.warning(
                self,
                "Invalid Input",
                f"{message}\n\nPlease use only symbols from the alphabet: "
                f"{{{', '.join(sorted(alphabet))}}}",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Start visualization based on current tab
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:  # DFA
            self.dfa_panel.process_string(input_string)
        elif current_tab == 1:  # CFG
            self.cfg_panel.process_string(input_string)
        elif current_tab == 2:  # PDA
            self.pda_panel.process_string(input_string)
    
    def _on_animation_finished(self, accepted: bool):
        """Handle animation completion."""
        if accepted:
            self.result_label.setText("ACCEPTED")
            self.result_label.setObjectName("accepted")
        else:
            self.result_label.setText("REJECTED")
            self.result_label.setObjectName("rejected")
        
        # Force style refresh
        self.result_label.setStyle(self.result_label.style())
