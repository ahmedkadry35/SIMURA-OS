"""Centralized Qt stylesheet for SIMURA Assistant.

Mirrors the SIMURA brand palette (see branding/PALETTE.md). Loaded once at
window creation and applied with ``widget.setStyleSheet(STYLE)``.
"""

# Brand tokens from branding/PALETTE.md.
NIGHT     = "#06031a"
DEEP      = "#100747"
SURFACE   = "#1a0a3f"
VIOLET    = "#7c4dff"
AMETHYST  = "#a26bff"
LAVENDER  = "#c39bff"
TEXT      = "#e6e0ff"
MUTED     = "#8c80b4"

# Compatibility aliases — older code or downstream packages may import these.
CYAN = VIOLET
BLUE = AMETHYST

STYLE = f"""
QWidget {{
    background-color: {NIGHT};
    color: {TEXT};
    font-family: "Roboto", "Segoe UI", sans-serif;
    font-size: 14px;
}}

QFrame#card, QFrame#sidebar, QListView, QTreeView, QPlainTextEdit, QTextEdit {{
    background-color: {SURFACE};
    border: 1px solid #2a1a6a;
    border-radius: 12px;
}}

QFrame#header {{
    background-color: {DEEP};
    border-bottom: 1px solid {VIOLET};
}}

QLineEdit, QPlainTextEdit, QTextEdit {{
    background-color: {SURFACE};
    color: {TEXT};
    selection-background-color: {VIOLET};
    selection-color: #ffffff;
    padding: 8px 10px;
    border-radius: 10px;
    border: 1px solid #2a1a6a;
}}

QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
    border: 1px solid {VIOLET};
}}

QPushButton {{
    background-color: {DEEP};
    color: {LAVENDER};
    padding: 8px 16px;
    border-radius: 10px;
    border: 1px solid {VIOLET};
}}
QPushButton:hover  {{ background-color: #1c0e6a; color: #ffffff; }}
QPushButton:pressed {{ background-color: {VIOLET}; color: #ffffff; }}
QPushButton:disabled {{
    background-color: #150a32;
    color: {MUTED};
    border: 1px solid #2a1a6a;
}}

QPushButton#primary {{
    background-color: {VIOLET};
    color: #ffffff;
    border: 1px solid {VIOLET};
    font-weight: 600;
}}
QPushButton#primary:hover  {{ background-color: {AMETHYST}; }}
QPushButton#primary:pressed {{ background-color: {LAVENDER}; color: {NIGHT}; }}

QPushButton#ghost {{
    background-color: transparent;
    color: {MUTED};
    border: 1px solid transparent;
}}
QPushButton#ghost:hover {{ color: {TEXT}; border: 1px solid #2a1a6a; }}

QLabel#title  {{ font-size: 20px; font-weight: 600; color: {LAVENDER}; }}
QLabel#muted  {{ color: {MUTED}; }}

QListView::item:selected, QTreeView::item:selected {{
    background-color: rgba(124, 77, 255, 0.22);
    color: {TEXT};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: #2a1a6a;
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {VIOLET}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QStatusBar {{
    background: {DEEP};
    color: {MUTED};
}}
"""
