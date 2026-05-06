"""Compact "press Super+A" overlay launcher.

Single-line input + streaming response area, frameless and centered. Falls
back to plain QDialog if the system doesn't allow frameless windows.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ..config import Config
from ..controller import Controller
from .style import CYAN, MUTED, STYLE
from .workers import ChatWorker


class QuickLaunch(QDialog):
    def __init__(self, cfg: Config) -> None:
        super().__init__()
        self.cfg = cfg
        self.controller = Controller(cfg)
        self._worker: ChatWorker | None = None

        self.setWindowTitle("SIMURA")
        self.setStyleSheet(STYLE)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.resize(720, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("SIMURA")
        title.setObjectName("title")
        layout.addWidget(title)

        layout.addWidget(QLabel(f"{cfg.model} · ⌘ Enter to ask", objectName="muted"))

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Ask SIMURA…")
        self.input_edit.returnPressed.connect(self._send)
        layout.addWidget(self.input_edit)

        self.transcript = QTextEdit()
        self.transcript.setReadOnly(True)
        layout.addWidget(self.transcript, 1)

        close_btn = QPushButton("Close (Esc)")
        close_btn.setObjectName("ghost")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.reject)
        self.input_edit.setFocus()

    def _send(self) -> None:
        prompt = self.input_edit.text().strip()
        if not prompt or self._worker is not None:
            return
        self.input_edit.clear()
        self.transcript.append(
            f'<span style="color:{CYAN}; font-weight:600;">You:</span> {prompt}'
        )
        self.transcript.append(
            f'<span style="color:{MUTED}; font-weight:600;">SIMURA:</span> '
        )

        self._worker = ChatWorker(self.controller, prompt)
        self._worker.chunk.connect(self._on_chunk)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_chunk(self, chunk: str) -> None:
        cursor = self.transcript.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.transcript.setTextCursor(cursor)
        self.transcript.insertPlainText(chunk)

    def _on_done(self, _ok: bool, err: str) -> None:
        if err:
            self.transcript.append(f'<span style="color:#ff4757;">Error: {err}</span>')
        self._worker = None
