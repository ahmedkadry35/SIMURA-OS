"""Minimal HTTP client for the local Ollama REST API.

Documented at https://github.com/ollama/ollama/blob/main/docs/api.md.
We rely only on:

  - ``GET  /api/tags``  — list available models.
  - ``POST /api/chat``  — chat completion (streaming JSON-Lines).
  - ``POST /api/pull``  — pull a model (streaming JSON-Lines).

We deliberately use ``requests`` (sync + iter_lines) instead of an async
client so the Qt UI thread can drive streaming via ``QThread`` workers.
"""
from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from typing import Any

import requests

log = logging.getLogger(__name__)


class OllamaError(RuntimeError):
    """Wrapper for any failure interacting with the Ollama daemon."""


class OllamaClient:
    """Tiny synchronous Ollama client used by the assistant.

    Methods that "stream" yield strings (response token chunks). The caller
    is responsible for moving them off the GUI thread (the UI uses a
    ``QThread`` worker for this — see ``ui/main_window.py``).
    """

    def __init__(self, host: str = "http://localhost:11434", timeout: float = 120.0) -> None:
        self._host = host.rstrip("/")
        self._timeout = timeout

    # -------- introspection -------------------------------------------------

    def is_reachable(self) -> bool:
        """Cheap health check; returns False on any network error."""
        try:
            r = requests.get(f"{self._host}/api/tags", timeout=2)
            return r.ok
        except requests.RequestException as exc:  # pragma: no cover - exercised at runtime
            log.debug("Ollama unreachable: %s", exc)
            return False

    def list_models(self) -> list[dict[str, Any]]:
        try:
            r = requests.get(f"{self._host}/api/tags", timeout=self._timeout)
            r.raise_for_status()
            data = r.json()
        except requests.RequestException as exc:
            raise OllamaError(f"failed to list models: {exc}") from exc
        return list(data.get("models", []))

    def has_model(self, model: str) -> bool:
        try:
            return any(m.get("name") == model for m in self.list_models())
        except OllamaError:
            return False

    # -------- chat ----------------------------------------------------------

    def chat_stream(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        options: dict[str, Any] | None = None,
    ) -> Iterator[str]:
        """Stream a chat response token-by-token.

        ``messages`` is a list of ``{"role": "...", "content": "..."}`` dicts
        following the Ollama / OpenAI chat schema.
        """
        payload: dict[str, Any] = {"model": model, "messages": messages, "stream": True}
        if options:
            payload["options"] = options
        try:
            with requests.post(
                f"{self._host}/api/chat",
                json=payload,
                stream=True,
                timeout=self._timeout,
            ) as r:
                r.raise_for_status()
                for raw_line in r.iter_lines(decode_unicode=True):
                    if not raw_line:
                        continue
                    try:
                        event = json.loads(raw_line)
                    except json.JSONDecodeError:
                        log.warning("ollama: skipping non-JSON line: %r", raw_line[:120])
                        continue
                    if "error" in event:
                        raise OllamaError(event["error"])
                    chunk = event.get("message", {}).get("content")
                    if chunk:
                        yield chunk
                    if event.get("done"):
                        return
        except requests.RequestException as exc:
            raise OllamaError(f"chat request failed: {exc}") from exc

    # -------- pulling models -----------------------------------------------

    def pull(self, model: str) -> Iterator[dict[str, Any]]:
        """Stream pull progress events for ``model``.

        Each event is the parsed JSON object from a single Ollama
        progress line (e.g. ``{"status": "pulling manifest"}`` or
        ``{"status": "downloading", "completed": 12345, "total": 67890}``).
        Callers can use this to drive a progress bar.
        """
        try:
            with requests.post(
                f"{self._host}/api/pull",
                json={"name": model, "stream": True},
                stream=True,
                timeout=None,  # downloads can be long
            ) as r:
                r.raise_for_status()
                for raw_line in r.iter_lines(decode_unicode=True):
                    if not raw_line:
                        continue
                    try:
                        event = json.loads(raw_line)
                    except json.JSONDecodeError:
                        continue
                    if "error" in event:
                        raise OllamaError(event["error"])
                    yield event
        except requests.RequestException as exc:
            raise OllamaError(f"pull failed: {exc}") from exc
