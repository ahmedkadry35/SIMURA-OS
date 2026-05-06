"""High-level conversation controller used by both the main window and the
quick-launch overlay. Wraps :class:`OllamaClient`, :class:`History`, and the
toolbox in a single object that the UI threads can drive.

The UI runs streaming chat on a ``QThread`` worker (see
``ui/main_window.py``); this module exposes plain Python iterators so it
remains testable from the command line via ``simura-assistant --prompt``.
"""
from __future__ import annotations

import logging
import time
from collections.abc import Iterator

from .config import Config
from .history import History, Message
from .ollama import OllamaClient, OllamaError

log = logging.getLogger(__name__)


class Controller:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.client = OllamaClient(cfg.ollama_host)
        self.history = History(cfg.history_path)
        self.conversation_id = History.new_conversation_id()
        self._messages: list[dict[str, str]] = [
            {"role": "system", "content": cfg.system_prompt},
        ]

    # -------- conversation management -------------------------------------

    def reset(self) -> None:
        """Start a new conversation; previous messages remain in history."""
        self.conversation_id = History.new_conversation_id()
        self._messages = [{"role": "system", "content": self.cfg.system_prompt}]

    def load(self, conversation_id: str) -> None:
        msgs = self.history.load(conversation_id)
        self.conversation_id = conversation_id
        self._messages = [{"role": m.role, "content": m.content}
                          for m in msgs if m.role != "tool"]
        if not self._messages or self._messages[0].get("role") != "system":
            self._messages.insert(0, {"role": "system", "content": self.cfg.system_prompt})

    # -------- single-shot prompt ------------------------------------------

    def ask(self, prompt: str) -> Iterator[str]:
        """Send ``prompt`` and stream the assistant's response chunks."""
        user_msg = Message(role="user", content=prompt, created_at=time.time())
        self.history.append(self.conversation_id, user_msg)
        self._messages.append({"role": "user", "content": prompt})

        accumulated: list[str] = []
        try:
            for chunk in self.client.chat_stream(self.cfg.model, self._messages):
                accumulated.append(chunk)
                yield chunk
        except OllamaError as exc:
            err = f"\n\n[error: {exc}]"
            accumulated.append(err)
            yield err

        full = "".join(accumulated)
        self._messages.append({"role": "assistant", "content": full})
        self.history.append(
            self.conversation_id,
            Message(role="assistant", content=full,
                    model=self.cfg.model, created_at=time.time()),
        )

    # -------- model bootstrapping ----------------------------------------

    def ensure_default_model(self) -> Iterator[dict]:
        """Yield pull-progress events if the default model isn't installed."""
        if self.client.has_model(self.cfg.model):
            return iter(())
        log.info("pulling default model %s", self.cfg.model)
        return self.client.pull(self.cfg.model)
