# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Automata Theory Visualizer.
Bundles the application with Graphviz binaries for standalone Windows executable.

Usage:
    pyinstaller build.spec

Prerequisites:
    1. Install Graphviz: https://graphviz.org/download/
    2. Set GRAPHVIZ_PATH below to your Graphviz installation
    3. Install dependencies: pip install -r requirements.txt
"""

import os
import sys
from pathlib import Path

# Configuration
APP_NAME = 'AutomataVisualizer'
MAIN_SCRIPT = 'main.py'

# Find Graphviz installation
# Check local folder first, then common Windows installation paths
spec_dir = os.path.dirname(os.path.abspath(SPEC))
GRAPHVIZ_PATHS = [
    os.path.join(spec_dir, 'Graphviz-14.1.2-win64', 'bin'),  # Local folder
    r'C:\Program Files\Graphviz\bin',
    r'C:\Program Files (x86)\Graphviz\bin',
    os.path.expanduser(r'~\AppData\Local\Programs\Graphviz\bin'),
    os.environ.get('GRAPHVIZ_PATH', ''),
]

graphviz_bin = None
for path in GRAPHVIZ_PATHS:
    if path and os.path.exists(path) and os.path.isfile(os.path.join(path, 'dot.exe')):
        graphviz_bin = path
        break

# Graphviz binaries to bundle
graphviz_binaries = []
if graphviz_bin:
    print(f"Found Graphviz at: {graphviz_bin}")
    # Essential Graphviz executables
    graphviz_exes = ['dot.exe', 'neato.exe', 'fdp.exe', 'sfdp.exe', 'circo.exe', 'twopi.exe']
    for exe in graphviz_exes:
        exe_path = os.path.join(graphviz_bin, exe)
        if os.path.exists(exe_path):
            graphviz_binaries.append((exe_path, 'graphviz'))
    
    # Also include required DLLs
    for dll in os.listdir(graphviz_bin):
        if dll.endswith('.dll'):
            dll_path = os.path.join(graphviz_bin, dll)
            graphviz_binaries.append((dll_path, 'graphviz'))
    
    # Include config file if present
    config6 = os.path.join(os.path.dirname(graphviz_bin), 'lib', 'graphviz', 'config6')
    if os.path.exists(config6):
        graphviz_binaries.append((config6, 'graphviz'))
else:
    print("WARNING: Graphviz not found! The application may not render diagrams correctly.")
    print("Please install Graphviz from https://graphviz.org/download/")

# Analysis
a = Analysis(
    [MAIN_SCRIPT],
    pathex=[],
    binaries=graphviz_binaries,
    datas=[
        ('resources', 'resources'),
    ],
    hiddenimports=[
        'automata',
        'automata.fa',
        'automata.fa.dfa',
        'automata.fa.nfa',
        'automata.pda',
        'automata.pda.dpda',
        'graphviz',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    noarchive=False,
    optimize=0,
)

# Remove unnecessary files to reduce size
a.binaries = [b for b in a.binaries if not b[0].startswith('api-ms-')]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here: icon='resources/icon.ico'
)
