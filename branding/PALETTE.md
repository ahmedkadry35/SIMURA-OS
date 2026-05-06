# SIMURA OS Visual Identity

## Color palette

| Token             | Hex       | Usage                                          |
| ----------------- | --------- | ---------------------------------------------- |
| `simura-night`    | `#000814` | Primary background (OLED-friendly true dark)   |
| `simura-deep`    | `#001233` | Secondary background, panels                   |
| `simura-surface`  | `#0a0e2a` | Card surfaces, dialog backgrounds              |
| `simura-cyan`     | `#00e5ff` | **Primary accent** — interactive, highlights   |
| `simura-blue`     | `#00b8ff` | Secondary accent — links, focus rings          |
| `simura-violet`   | `#7c4dff` | Tertiary accent — gradients, AI assistant glow |
| `simura-text`     | `#e6f1ff` | Primary text on dark backgrounds               |
| `simura-muted`    | `#7a8aa6` | Secondary text                                 |
| `simura-success`  | `#00d27a` | Success states                                 |
| `simura-warning`  | `#ffb020` | Warning states                                 |
| `simura-danger`   | `#ff4757` | Error states                                   |

## Typography

| Role         | Font                          |
| ------------ | ----------------------------- |
| UI body      | Roboto                        |
| UI display   | Roboto                        |
| Monospace    | JetBrains Mono Nerd Font      |
| Code editor  | Fira Code Nerd Font           |
| Terminal     | MesloLGS Nerd Font            |

## Logo usage

- Default: `branding/logo/simura-logo.svg`
- Monochrome (currentColor): `branding/logo/simura-logo-mono.svg`
- Minimum render size: 16×16. Below that, use a single-glyph "S" mark.
- Clear-space: at least one hexagon edge length on all sides.
- Do not stretch, recolor outside the palette, or add drop-shadows.

## Wallpapers

- Default: `branding/wallpapers/simura-default.svg` (4K, includes centered logo)
- Minimal: `branding/wallpapers/simura-dark.svg` (4K, logo-free)

PNG variants are generated at build time by `scripts/render-branding.sh`.
