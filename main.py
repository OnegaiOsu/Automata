#!/usr/bin/env python3
"""
Automata Theory Visualizer
==========================

A desktop application for visualizing DFA, CFG, and PDA representations
of regular expressions with animated string processing.

Author: Generated for Automata Theory education
License: MIT
"""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.main_window import MainWindow


def main():
    """Application entry point."""
    # High DPI support
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Automata Theory Visualizer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AutomataViz")
    
    # Set default font
    font = QFont("Helvetica Neue", 10)
    font.setWeight(QFont.Weight.Medium)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
