"""Config loading / saving for SIMURA Assistant.

Config lives at ``~/.config/simura/config.yaml`` and is created with sane
defaults on first run. The schema is small and intentionally easy for users
to edit by hand.
"""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml


def _default_config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "simura"


@dataclass
class Config:
    """Runtime configuration for the assistant."""

    ollama_host: str = "http://localhost:11434"
    model: str = "llama3.2:3b"
    fallback_models: list[str] = field(default_factory=lambda: ["qwen2.5:3b", "phi3:mini"])
    system_prompt: str = (
        "You are SIMURA Assistant, the built-in AI of SIMURA OS — a fast, "
        "Linux-based operating system. You help the user with shell tasks, "
        "file search, system configuration, and general questions. Be terse "
        "and accurate. When suggesting commands, format them in fenced code "
        "blocks so the UI can render a 'Run' button."
    )
    enable_tools: bool = True
    confirm_shell: bool = True   # always require explicit confirmation
    confirm_fs_writes: bool = True
    history_path: str = str(_default_config_dir() / "history.sqlite3")
    log_level: str = "INFO"


def _config_path(override: Path | None) -> Path:
    if override is not None:
        return override
    return _default_config_dir() / "config.yaml"


def load_config(override: Path | None = None) -> Config:
    path = _config_path(override)
    if not path.exists():
        cfg = Config()
        save_config(cfg, override)
        return cfg
    with path.open("r", encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh) or {}
    cfg = Config()
    for key, value in raw.items():
        if hasattr(cfg, key):
            setattr(cfg, key, value)
    return cfg


def save_config(cfg: Config, override: Path | None = None) -> None:
    path = _config_path(override)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(asdict(cfg), fh, sort_keys=False)
