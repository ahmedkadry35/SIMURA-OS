# SIMURA OS — Privacy

## Telemetry

**SIMURA OS does not phone home.** There is no telemetry collector, no
crash-report uploader, no usage-analytics endpoint. The only outbound
connections SIMURA initiates by default are:

| Reason                                | Endpoint                                |
|---------------------------------------|------------------------------------------|
| Pacman package updates                | `https://geo.mirror.pkgbuild.com/` and Arch mirrors  |
| Flatpak (only when you install / update) | `https://dl.flathub.org/`             |
| Time sync                             | `pool.ntp.org` (via `systemd-timesyncd`) |
| First-boot Ollama install (one time)  | `https://ollama.com/install.sh`          |
| First-boot Ollama model pull (one time) | `https://registry.ollama.ai/`           |
| `fwupd` firmware metadata             | `https://fwupd.org/`                     |

Each of those is also off when you don't have a network connection.

## AI assistant

The SIMURA Assistant runs **entirely on your hardware**.

- Prompts go to `localhost:11434` (the Ollama daemon), never to a third
  party.
- Models live on disk in `~/.ollama/models/`.
- The assistant does NOT have a "send anonymized usage data" toggle because
  there is no usage-data sender to toggle.
- The "web fetch" tool is **off by default**; if you enable it, the
  assistant can fetch URLs *you ask it to* — your prompt + the URL leave
  your machine to that URL, just like opening a browser tab.

## Logs

Like every Linux distribution, SIMURA writes system logs to the systemd
journal (`journalctl`). These stay on your machine. To zero out journal
history at any time:

```bash
sudo journalctl --vacuum-time=1s
```

## Data on disk

The assistant stores conversation history at:

```
~/.config/simura/history.sqlite3
```

You can delete this file at any time — the next launch will recreate it
empty. There is no cloud backup of this database.
