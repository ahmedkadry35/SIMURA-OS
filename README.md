# SIMURA OS

> **A real, bootable Linux distribution.** Arch base + KDE Plasma + a
> futuristic visual identity + an offline AI assistant powered by a local
> Ollama daemon. Designed to be fast, modern, secure, and cohesive — without
> any of the "outperforms Windows by magic" claims you'll see elsewhere.

[![CI](https://github.com/ahmedkadry35/SIMURA-OS/actions/workflows/ci.yml/badge.svg)](https://github.com/ahmedkadry35/SIMURA-OS/actions/workflows/ci.yml)

| | |
|---|---|
| **Base**           | Arch Linux (rolling), Linux kernel + linux-firmware |
| **Desktop**        | KDE Plasma 6 (Wayland default, X11 fallback)        |
| **Display manager**| SDDM with custom SIMURA theme                       |
| **Installer**      | Calamares with SIMURA branding + slideshow          |
| **AI assistant**   | `simura-assistant` (PyQt6) → local Ollama daemon    |
| **Default shell**  | zsh + Starship + autosuggestions + syntax-highlight |
| **Default fonts**  | Roboto / JetBrains Mono Nerd / Fira Code Nerd       |
| **Performance**    | zram, earlyoom, BBR, CPU governor auto-tune         |
| **Security**       | UFW, fail2ban, AppArmor, hardened sysctls           |
| **Software**       | Native pacman + Flatpak (Flathub) + a curated list  |

---

## Project layout

```
SIMURA-OS/
├── archiso/             # archiso build profile (kernel, packages, airootfs)
│   ├── profiledef.sh
│   ├── pacman.conf
│   ├── packages.x86_64
│   ├── syslinux/        # BIOS bootloader configs
│   ├── efiboot/         # UEFI bootloader configs
│   ├── grub/            # GRUB UEFI eltorito + loopback configs
│   └── airootfs/        # Live root filesystem overlay (/etc, /usr, ...)
├── branding/            # Logo SVGs, wallpapers, palette, Plymouth, GRUB, SDDM
├── themes/              # Plasma color scheme + Kvantum + Konsole + GTK
├── ai-assistant/        # PyQt6 SIMURA Assistant app (Ollama-powered)
├── installer/           # Calamares config + branding
├── scripts/             # build.sh + render-branding.sh
├── ci/                  # CI helper scripts (none yet — workflows live in .github/)
├── docs/                # Architecture, welcome, privacy
└── .github/workflows/   # CI (lint+tests+ISO build) + Release
```

---

## Building the ISO

You **don't need an Arch host** to build SIMURA OS. The build runs `archiso`
inside a Docker Arch container, so any Linux box with Docker can produce
the ISO.

### Prerequisites

- Docker (or compatible runtime exposed as `docker`)
- ~10 GB free disk
- A working network connection (the build downloads ~3 GB of Arch packages)

### Build

```bash
git clone https://github.com/ahmedkadry35/SIMURA-OS.git
cd SIMURA-OS
./scripts/build.sh
```

When the build finishes (~30–60 min depending on your link), you'll find
the ISO + checksum in `out/`:

```
out/simura-2026.05.06-x86_64.iso
out/simura-2026.05.06-x86_64.iso.sha256
```

### Building only the assistant

The PyQt6 assistant has no dependency on the rest of the OS:

```bash
cd ai-assistant
pip install -e .
simura-assistant            # opens main window
simura-assistant --quick    # opens the compact overlay
simura-assistant --prompt "explain zram in one paragraph"
```

It needs a running Ollama daemon (`ollama serve`) and a pulled model
(`ollama pull llama3.2:3b`). Both are wired up automatically on first boot
of an installed SIMURA system via `simura-firstboot.service`.

---

## Booting the ISO

### In QEMU (UEFI)

```bash
qemu-system-x86_64 \
    -enable-kvm -m 4096 -smp 4 \
    -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE.fd \
    -drive if=pflash,format=raw,file=OVMF_VARS.fd \
    -cdrom out/simura-*.iso \
    -boot d
```

### On real hardware

Flash the ISO to a USB stick:

```bash
sudo dd if=out/simura-*.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

Then boot from USB. UEFI Secure Boot is **not** supported in the current
build (we don't sign the bootloader yet); disable Secure Boot or boot in
CSM/Legacy mode.

---

## What's actually different from upstream Arch?

This is the honest list. SIMURA does **not** ship a custom kernel or invent
new performance primitives — it ships *opinionated, well-tested defaults*
that most Arch users would otherwise have to assemble themselves.

| Area              | Default                                                      |
|-------------------|--------------------------------------------------------------|
| Boot splash       | Plymouth `simura` theme (cyan pulsing logo)                  |
| Login             | SDDM + custom SIMURA QML theme                               |
| Desktop           | Plasma 6 with `org.simura.desktop` Look-and-Feel package     |
| Theme             | Kvantum SIMURA + Breeze-Dark window decorations              |
| Wallpaper         | 4K SIMURA-branded SVG, scaled per display                    |
| Memory            | zram = min(RAM/2, 8 GiB), `swappiness=10`, earlyoom enabled  |
| Network           | TCP BBR + cake qdisc by default                              |
| Firewall          | UFW enabled (`deny in / allow out`) on first boot            |
| Brute-force       | fail2ban enabled for sshd                                    |
| MAC               | AppArmor enabled                                             |
| Audit             | auditd enabled                                               |
| Battery           | CPU governor `performance` on AC, `schedutil` on battery     |
| I/O               | `mq-deadline` for SSDs, `bfq` for HDDs                       |
| Firmware updates  | `fwupd` ready                                                |
| AI assistant      | `simura-assistant` + Ollama, local-only, hotkey `Super+A`    |
| Apps              | Flatpak + Flathub preconfigured, curated list under `/usr/share/simura/curated-flatpaks.list` |
| Shell             | zsh + Starship + ripgrep + fd + bat + eza                    |

---

## Contributing

Issues and PRs welcome.

- Run `pytest` from `ai-assistant/` before pushing assistant changes.
- Run `shellcheck scripts/*.sh archiso/airootfs/usr/local/bin/*` for shell.
- CI builds the ISO on every push to `main`; keep `packages.x86_64`
  internally consistent (no removed packages, no upstream typos).

See [`.github/PULL_REQUEST_TEMPLATE.md`](./.github/PULL_REQUEST_TEMPLATE.md).

## License

SIMURA OS as a project is GPL-3.0-or-later. Individual upstream components
(Linux kernel, KDE Plasma, etc.) ship under their own licenses; nothing
shipped here changes that.
