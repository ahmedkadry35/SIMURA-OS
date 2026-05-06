"""Main SIMURA Assistant window — full chat surface with sidebar history."""
from __future__ import annotations

import time
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..config import Config
from ..controller import Controller
from .style import CYAN, MUTED, STYLE
from .workers import ChatWorker


class MainWindow(QMainWindow):
    def __init__(self, cfg: Config) -> None:
        super().__init__()
        self.cfg = cfg
        self.controller = Controller(cfg)
        self._worker: ChatWorker | None = None

        self.setWindowTitle("SIMURA Assistant")
        self.resize(1100, 720)
        self.setStyleSheet(STYLE)

        self._build_ui()
        self._refresh_history()

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+N"), self, self._new_conversation)
        QShortcut(QKeySequence("Ctrl+L"), self, self._focus_input)
        QShortcut(QKeySequence("Ctrl+Return"), self.input_edit, self._send)

    # -------- UI construction ---------------------------------------------

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)
        self.setCentralWidget(root)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(12, 12, 12, 12)
        sb_layout.setSpacing(8)

        title = QLabel("SIMURA Assistant")
        title.setObjectName("title")
        sb_layout.addWidget(title)

        sb_layout.addWidget(QLabel(f"Model: {self.cfg.model}", objectName="muted"))

        new_btn = QPushButton("New conversation")
        new_btn.setObjectName("primary")
        new_btn.clicked.connect(self._new_conversation)
        sb_layout.addWidget(new_btn)

        sb_layout.addWidget(QLabel("History", objectName="muted"))
        self.history_list = QListWidget()
        self.history_list.itemActivated.connect(self._open_conversation)
        sb_layout.addWidget(self.history_list, 1)

        root_layout.addWidget(sidebar)

        # Conversation pane
        pane = QFrame()
        pane.setObjectName("card")
        pane_layout = QVBoxLayout(pane)
        pane_layout.setContentsMargins(16, 16, 16, 16)
        pane_layout.setSpacing(12)

        self.transcript = QTextEdit()
        self.transcript.setReadOnly(True)
        self.transcript.setAcceptRichText(True)
        self.transcript.setStyleSheet(
            "QTextEdit { background-color: transparent; border: none; padding: 0; }"
        )
        pane_layout.addWidget(self.transcript, 1)

        self.input_edit = QPlainTextEdit()
        self.input_edit.setPlaceholderText(
            "Ask SIMURA anything…  (Ctrl+Enter to send)"
        )
        self.input_edit.setFixedHeight(96)
        pane_layout.addWidget(self.input_edit)

        bottom = QHBoxLayout()
        bottom.addStretch(1)
        self.cancel_btn = QPushButton("Stop")
        self.cancel_btn.setObjectName("ghost")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        bottom.addWidget(self.cancel_btn)

        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("primary")
        self.send_btn.clicked.connect(self._send)
        bottom.addWidget(self.send_btn)
        pane_layout.addLayout(bottom)

        root_layout.addWidget(pane, 1)

        status = QStatusBar()
        status.showMessage(f"Ready · {self.cfg.ollama_host}")
        self.setStatusBar(status)

    # -------- conversation actions ----------------------------------------

    def _new_conversation(self) -> None:
        self.controller.reset()
        self.transcript.clear()
        self._append_system("New conversation. Ask anything.")
        self._refresh_history()

    def _focus_input(self) -> None:
        self.input_edit.setFocus()

    def _send(self) -> None:
        prompt = self.input_edit.toPlainText().strip()
        if not prompt or self._worker is not None:
            return
        self.input_edit.clear()
        self._append_user(prompt)
        self._begin_assistant_message()

        self.send_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.statusBar().showMessage("Thinking…")

        self._worker = ChatWorker(self.controller, prompt)
        self._worker.chunk.connect(self._append_assistant_chunk)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _cancel(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            # Best-effort: Ollama doesn't expose an inflight cancel, so we just
            # flag this side and stop emitting chunks once the thread finishes.
            self._worker.requestInterruption()
            self.statusBar().showMessage("Cancellation requested…")

    def _on_done(self, ok: bool, err: str) -> None:
        self._worker = None
        self.send_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        if ok:
            self.statusBar().showMessage(
                f"Done at {datetime.now().strftime('%H:%M:%S')}"
            )
        else:
            self._append_system(f"Error: {err}")
            self.statusBar().showMessage("Error")
        self._refresh_history()

    # -------- transcript helpers ------------------------------------------

    def _append_user(self, text: str) -> None:
        ts = datetime.now().strftime("%H:%M")
        self.transcript.append(
            f'<div style="margin: 12px 0;">'
            f'<span style="color:{CYAN}; font-weight:600;">You</span> '
            f'<span style="color:{MUTED}; font-size:11px;">{ts}</span><br>'
            f'<span>{_html_escape(text)}</span></div>'
        )

    def _begin_assistant_message(self) -> None:
        ts = datetime.now().strftime("%H:%M")
        self.transcript.append(
            f'<div style="margin: 12px 0;">'
            f'<span style="color:#7c4dff; font-weight:600;">SIMURA</span> '
            f'<span style="color:{MUTED}; font-size:11px;">{ts}</span><br>'
            f'<span id="assistant-current"></span></div>'
        )
        self._assistant_buffer = ""

    def _append_assistant_chunk(self, chunk: str) -> None:
        # Append plaintext (the model can emit any HTML-unsafe content).
        self._assistant_buffer += chunk
        cursor = self.transcript.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.transcript.setTextCursor(cursor)
        self.transcript.insertPlainText(chunk)

    def _append_system(self, text: str) -> None:
        self.transcript.append(
            f'<div style="margin: 8px 0; color:{MUTED}; font-style: italic;">{_html_escape(text)}</div>'
        )

    def _refresh_history(self) -> None:
        self.history_list.clear()
        for cid, ts, preview in self.controller.history.list_conversations():
            when = time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))
            label = preview if preview else "(empty)"
            item = QListWidgetItem(f"{when}\n{label}")
            item.setData(Qt.ItemDataRole.UserRole, cid)
            self.history_list.addItem(item)

    def _open_conversation(self, item: QListWidgetItem) -> None:
        cid = item.data(Qt.ItemDataRole.UserRole)
        self.controller.load(cid)
        self.transcript.clear()
        for msg in self.controller.history.load(cid):
            if msg.role == "user":
                self._append_user(msg.content)
            elif msg.role == "assistant":
                self._begin_assistant_message()
                self._append_assistant_chunk(msg.content)
            elif msg.role == "system":
                self._append_system(msg.content)


def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace("\n", "<br>")
    )
