# SIMURA OS — Architecture

This document explains how the pieces of SIMURA OS fit together at a level
of detail useful for contributors and security reviewers.

## Boot flow

1. **Firmware** loads the bootloader from the ESP (UEFI) or the MBR/eltorito
   image (BIOS). Configs:
   - `archiso/efiboot/loader/` and `archiso/grub/` for UEFI
   - `archiso/syslinux/` for BIOS / PXE
2. **Bootloader** loads `/<INSTALL_DIR>/boot/x86_64/vmlinuz-linux` plus
   the appropriate microcode initramfs and `initramfs-linux.img`.
3. **Kernel + initramfs** mount the squashfs root from the ISO (live boot)
   or a real partition (installed system).
4. **Plymouth** renders the SIMURA boot splash from
   `/usr/share/plymouth/themes/simura/`.
5. **systemd** runs `multi-user.target`, then `graphical.target`:
   - `NetworkManager`, `bluetooth`, `cups`, `chrony`/`systemd-timesyncd`
   - `simura-performance.service` applies CPU governor + I/O scheduler
   - `simura-firstboot.service` runs once on the installed system to enable
     UFW, AppArmor, fail2ban, install Ollama, and pull the default model.
   - `sddm.service` shows the SIMURA login screen.
6. **SDDM → Plasma** loads the `org.simura.desktop` Look-and-Feel package,
   which wires up wallpaper, color scheme, panel layout, and the Kvantum
   widget style.

## AI assistant

```
              ┌─────────────────────────────┐
   Super+A → │     simura-assistant         │
              │    (PyQt6 desktop app)      │
              └─────────────┬───────────────┘
                            │ HTTP (localhost:11434)
                            ▼
                   ┌────────────────┐
                   │   ollama.service │
                   │   (binary)       │
                   └────────────────┘
                            │
                            ▼
                  Local model files
                  (~/.ollama/models/)
```

- The assistant **never** talks to a network endpoint other than
  `localhost:11434` unless the user explicitly enables a tool that needs the
  internet (e.g., `web.fetch`, off by default).
- `simura-firstboot.service` installs Ollama on first boot via the official
  installer (`https://ollama.com/install.sh`) and starts `ollama.service`.
- The default model (`llama3.2:3b`) is pulled in a background unit
  (`simura-pull-default-model`); the user can run
  `simura-pull-models <model>` later to add more.

## Packages

`archiso/packages.x86_64` is the source of truth for what ships in the live
ISO. The list is grouped by purpose; lines starting with `#` are comments
and ignored by `mkarchiso`. When adding/removing packages:

1. Verify the package exists in `[core]`, `[extra]`, or `[multilib]` —
   AUR packages cannot be installed directly by archiso.
2. Run `./scripts/build.sh` locally; CI also rebuilds on every push to
   `main`.

## Performance defaults

The two big levers SIMURA pulls:

1. **zram** (`/etc/systemd/zram-generator.conf`) — gives the system
   compressed RAM-backed swap, dramatically extending effective memory
   under pressure. Configured for `min(RAM/2, 8 GiB)` with zstd.
2. **earlyoom** (`/etc/default/earlyoom`) — kills the largest memory hog
   *before* the kernel OOM killer, preventing the multi-minute lockups that
   plague Linux desktops under heavy memory pressure.

Plus the smaller knobs in `/etc/sysctl.d/99-simura.conf`:

- `vm.swappiness=10` so we don't swap eagerly when most memory is page cache
- BBR + cake for modern TCP behavior
- Hardened network/kernel settings (rp_filter, kptr_restrict, etc.)

## Security defaults

- **UFW**: `deny in / allow out`; enabled on first boot.
- **fail2ban**: ssh jail enabled by default; bans 5 failures in 10 min for 1 h.
- **AppArmor + auditd**: enabled at first boot.
- **Sysctl hardening**: see `archiso/airootfs/etc/sysctl.d/99-simura.conf`.
- **Module blacklist**: deprecated network protocols (DCCP, SCTP, RDS, TIPC)
  blocked.
- **Disk encryption**: Calamares offers LUKS at install time.

## What we explicitly do *not* claim

- We don't ship a custom kernel — we ship Arch's `linux` package. Patching
  the kernel for "ultra-fast performance" is not something a single
  distribution can credibly do better than upstream + the major hardening
  tree (`linux-hardened`).
- We don't ship custom drivers — `linux-firmware` covers the same hardware
  every other Linux distribution does.
- Plymouth, KDE, Calamares, Ollama are all upstream projects; we ship them
  with our config and branding, nothing more.
- "Outperforming Windows / macOS" is a marketing claim, not an engineering
  one. We ship sane defaults that make SIMURA fast for typical desktop
  workloads on typical hardware.
