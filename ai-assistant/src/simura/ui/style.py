"""Centralized Qt stylesheet for SIMURA Assistant.

Mirrors the SIMURA brand palette (see branding/PALETTE.md). Loaded once at
window creation and applied with ``widget.setStyleSheet(STYLE)``.
"""

# Brand tokens from branding/PALETTE.md, in case other modules import them.
NIGHT   = "#000814"
DEEP    = "#001233"
SURFACE = "#0a0e2a"
CYAN    = "#00e5ff"
BLUE    = "#00b8ff"
VIOLET  = "#7c4dff"
TEXT    = "#e6f1ff"
MUTED   = "#7a8aa6"

STYLE = f"""
QWidget {{
    background-color: {NIGHT};
    color: {TEXT};
    font-family: "Roboto", "Segoe UI", sans-serif;
    font-size: 14px;
}}

QFrame#card, QFrame#sidebar, QListView, QTreeView, QPlainTextEdit, QTextEdit {{
    background-color: {SURFACE};
    border: 1px solid #1b2350;
    border-radius: 12px;
}}

QFrame#header {{
    background-color: {DEEP};
    border-bottom: 1px solid {CYAN};
}}

QLineEdit, QPlainTextEdit, QTextEdit {{
    background-color: {SURFACE};
    color: {TEXT};
    selection-background-color: {CYAN};
    selection-color: {NIGHT};
    padding: 8px 10px;
    border-radius: 10px;
    border: 1px solid #1b2350;
}}

QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
    border: 1px solid {CYAN};
}}

QPushButton {{
    background-color: {DEEP};
    color: {CYAN};
    padding: 8px 16px;
    border-radius: 10px;
    border: 1px solid {CYAN};
}}
QPushButton:hover  {{ background-color: #002752; color: #ffffff; }}
QPushButton:pressed {{ background-color: {CYAN};   color: {NIGHT};   }}
QPushButton:disabled {{
    background-color: #08102a;
    color: {MUTED};
    border: 1px solid #1b2350;
}}

QPushButton#primary {{
    background-color: {CYAN};
    color: {NIGHT};
    border: 1px solid {CYAN};
    font-weight: 600;
}}
QPushButton#primary:hover  {{ background-color: {BLUE}; }}
QPushButton#primary:pressed {{ background-color: {VIOLET}; color: white; }}

QPushButton#ghost {{
    background-color: transparent;
    color: {MUTED};
    border: 1px solid transparent;
}}
QPushButton#ghost:hover {{ color: {TEXT}; border: 1px solid #1b2350; }}

QLabel#title  {{ font-size: 20px; font-weight: 600; color: {CYAN}; }}
QLabel#muted  {{ color: {MUTED}; }}

QListView::item:selected, QTreeView::item:selected {{
    background-color: rgba(0, 229, 255, 0.18);
    color: {TEXT};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: #1b2350;
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {CYAN}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QStatusBar {{
    background: {DEEP};
    color: {MUTED};
}}
"""
