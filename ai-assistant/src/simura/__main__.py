"""Entrypoint for `python -m simura` and the `simura-assistant` console script.

Parses CLI flags, ensures Ollama is reachable (or shows a helpful first-run
dialog), then launches the Qt main window.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox

from .config import Config, load_config
from .ollama import OllamaClient, OllamaError
from .ui.main_window import MainWindow
from .ui.quick_launch import QuickLaunch

log = logging.getLogger("simura")


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="simura-assistant",
        description="SIMURA OS — local AI assistant (Ollama-backed).",
    )
    p.add_argument("--quick", action="store_true",
                   help="Open the compact quick-launch overlay instead of the main window.")
    p.add_argument("--prompt", type=str, default=None,
                   help="Send a single prompt and print the streamed response to stdout.")
    p.add_argument("--config", type=Path, default=None,
                   help="Path to a custom config YAML file.")
    p.add_argument("--model", type=str, default=None,
                   help="Override the configured Ollama model for this run.")
    p.add_argument("-v", "--verbose", action="count", default=0,
                   help="Increase log verbosity (-v, -vv).")
    return p


def _setup_logging(verbosity: int) -> None:
    level = logging.WARNING - 10 * min(verbosity, 2)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )


def _run_headless(cfg: Config, prompt: str) -> int:
    """Send a single prompt without spinning up the Qt UI; print streamed response."""
    client = OllamaClient(cfg.ollama_host)
    try:
        for chunk in client.chat_stream(cfg.model, [{"role": "user", "content": prompt}]):
            sys.stdout.write(chunk)
            sys.stdout.flush()
        sys.stdout.write("\n")
        return 0
    except OllamaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    _setup_logging(args.verbose)

    cfg = load_config(args.config)
    if args.model:
        cfg.model = args.model

    if args.prompt is not None:
        return _run_headless(cfg, args.prompt)

    app = QApplication(sys.argv)
    app.setApplicationName("SIMURA Assistant")
    app.setOrganizationName("SIMURA OS")
    app.setDesktopFileName("simura-assistant")

    icon_path = Path("/usr/share/icons/hicolor/256x256/apps/simura-assistant.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Sanity-check Ollama; if the daemon is down, surface a friendly dialog
    # but still let the user open the UI (they may want to read history).
    client = OllamaClient(cfg.ollama_host)
    if not client.is_reachable():
        QMessageBox.information(
            None,
            "Ollama not running",
            ("The Ollama daemon is not reachable at "
             f"{cfg.ollama_host}.\n\nStart it with:\n\n"
             "    sudo systemctl start ollama\n\n"
             "On first boot SIMURA OS will pull the default model "
             f"({cfg.model}) automatically when you have internet."),
        )

    if args.quick:
        win: object = QuickLaunch(cfg)
    else:
        win = MainWindow(cfg)

    win.show()
    if hasattr(win, "raise_"):
        win.raise_()
    if hasattr(win, "activateWindow"):
        win.activateWindow()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
