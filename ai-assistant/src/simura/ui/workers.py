"""QThread workers for streaming Ollama interactions off the GUI thread."""
from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from ..controller import Controller
from ..ollama import OllamaError


class ChatWorker(QThread):
    """Run a single ``Controller.ask()`` call in a background thread.

    Emits:
        chunk(str): each streamed response token
        done(bool, str): completion signal — (ok, error_message_or_empty)
    """

    chunk = pyqtSignal(str)
    done  = pyqtSignal(bool, str)

    def __init__(self, controller: Controller, prompt: str) -> None:
        super().__init__()
        self._controller = controller
        self._prompt = prompt

    def run(self) -> None:
        try:
            for chunk in self._controller.ask(self._prompt):
                self.chunk.emit(chunk)
            self.done.emit(True, "")
        except OllamaError as exc:
            self.done.emit(False, str(exc))
        except Exception as exc:  # pragma: no cover - last-resort safety net
            self.done.emit(False, f"unexpected error: {exc}")


class ModelPullWorker(QThread):
    """Pull a model in the background and emit progress events."""

    progress = pyqtSignal(dict)
    done     = pyqtSignal(bool, str)

    def __init__(self, controller: Controller) -> None:
        super().__init__()
        self._controller = controller

    def run(self) -> None:
        try:
            for evt in self._controller.ensure_default_model():
                self.progress.emit(evt if isinstance(evt, dict) else {"raw": evt})
            self.done.emit(True, "")
        except OllamaError as exc:
            self.done.emit(False, str(exc))
        except Exception as exc:  # pragma: no cover
            self.done.emit(False, f"unexpected error: {exc}")
