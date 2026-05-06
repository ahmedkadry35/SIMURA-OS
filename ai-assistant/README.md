# SIMURA Assistant

A native PyQt6 desktop app that wraps a **local Ollama** server to provide
chat, shell automation, file search, and app launching — all offline once a
model has been pulled.

## Architecture

```
   ┌──────────────────────────────────────────┐
   │   simura-assistant (PyQt6 UI)            │
   │                                          │
   │   ┌─────────────────────────────────┐    │
   │   │  ChatPanel  ToolPanel  History  │    │
   │   └──────────────┬──────────────────┘    │
   │                  │                       │
   │            ┌─────▼──────┐                │
   │            │ Controller │                │
   │            └─────┬──────┘                │
   │                  │                       │
   │   ┌──────────────┼──────────────┐        │
   │   ▼              ▼              ▼        │
   │ Ollama        ToolBox       History      │
   │ client     (shell, fs,     (sqlite)      │
   │ (HTTP)      apps, web)                   │
   └──────────────────────────────────────────┘
                 │
                 │   localhost:11434 (HTTP)
                 ▼
           ┌──────────┐
           │  Ollama  │
           │  daemon  │
           └──────────┘
```

- **`simura.controller`** — orchestrates: takes a user prompt, decides
  whether to run a tool, streams Ollama responses to the UI.
- **`simura.ollama`** — async HTTP client for the Ollama REST API
  (`/api/chat`, `/api/tags`, `/api/pull`).
- **`simura.tools`** — a small, *deliberately scoped* toolbox: `shell`
  (whitelisted commands only), `fs.search`, `fs.read`, `apps.launch`,
  `web.fetch`. The shell tool requires user confirmation for every call.
- **`simura.history`** — local SQLite store of conversations.
- **`simura.ui`** — PyQt6 widgets, theme, hotkey launcher.

## Key files

| Path                               | Purpose                                     |
|------------------------------------|---------------------------------------------|
| `src/simura/__main__.py`           | App entrypoint (`python -m simura`)         |
| `src/simura/controller.py`         | High-level conversation controller          |
| `src/simura/ollama.py`             | Ollama HTTP client                          |
| `src/simura/tools.py`              | Whitelisted tool implementations            |
| `src/simura/history.py`            | SQLite-backed conversation history          |
| `src/simura/ui/main_window.py`     | Main `QMainWindow` — chat surface           |
| `src/simura/ui/quick_launch.py`    | Compact "press Super+A" overlay             |
| `src/simura/config.py`             | Config defaults + load/save                 |
| `resources/simura-assistant.desktop` | Desktop entry installed system-wide       |
| `resources/simura-assistant.png`   | Icon (rendered from logo SVG at build)      |
| `packaging/PKGBUILD`               | Arch package definition                     |

## Running

```bash
# from the repo root, on a system with python-pyqt6 installed
python -m simura
```

By default the app talks to `http://localhost:11434` and uses model
`llama3.2:3b`. Both are configurable in `~/.config/simura/config.yaml`.

## Hotkey

The `simura-assistant.desktop` file installs a global shortcut binding
(`Super+A`) via Plasma's `kglobalshortcutsrc`. See
`archiso/airootfs/etc/skel/.config/kglobalshortcutsrc`.
