# Welcome to SIMURA OS

This page is what the **Welcome to SIMURA OS** desktop shortcut opens after
the first boot of an installed SIMURA system.

## First 5 minutes

1. **Press `Super+A`** to open the SIMURA Assistant. The first time you do
   this, you'll see a notice that Ollama is downloading the default model —
   that runs in the background; you can keep using the rest of the system.
2. **Open Konsole** with `Super+T`, then run `fastfetch` to see your
   hardware. Run `htop` or `btop` to see live system stats.
3. **Open Discover** (`Discover` in the kickoff menu) to browse Flatpak
   apps from Flathub. Native apps live in `pacman` (`sudo pacman -S <pkg>`).
4. **Configure your firewall**: SIMURA enables UFW with `deny in / allow out`
   defaults. To allow incoming SSH:
   ```bash
   sudo ufw allow ssh
   ```
5. **Update the system**:
   ```bash
   sudo pacman -Syu          # native packages
   flatpak update            # Flatpak apps
   ```

## Hotkeys you'll actually use

| Combo            | What it does                                |
|------------------|---------------------------------------------|
| `Super+A`        | SIMURA Assistant (compact overlay)          |
| `Super+T`        | Konsole (terminal)                          |
| `Super+E`        | Dolphin (file manager)                      |
| `PrtSc`          | Spectacle (screenshot)                      |
| `Super+Shift+Q`  | Log out                                     |
| `Ctrl+Alt+T`     | Konsole (compatibility for Ubuntu muscle memory) |

## Where things live

| Thing                     | Location                                          |
|---------------------------|---------------------------------------------------|
| Branding / wallpapers     | `/usr/share/wallpapers/SIMURA/`                  |
| Plymouth theme            | `/usr/share/plymouth/themes/simura/`             |
| SDDM login theme          | `/usr/share/sddm/themes/simura/`                 |
| Plasma Look-and-Feel      | `/usr/share/plasma/look-and-feel/org.simura.desktop/` |
| Assistant app             | `/usr/local/bin/simura-assistant`                |
| Curated Flatpak list      | `/usr/share/simura/curated-flatpaks.list`        |
| First-boot config script  | `/usr/local/bin/simura-firstboot`                |
| Performance script        | `/usr/local/bin/simura-performance`              |
| Sysctl tuning             | `/etc/sysctl.d/99-simura.conf`                   |

## Reporting issues

https://github.com/ahmedkadry35/SIMURA-OS/issues — please include the output
of `fastfetch` and `journalctl -p err -b` if relevant.
