# SIMURA OS Visual Identity

## Color palette

| Token             | Hex       | Usage                                                  |
| ----------------- | --------- | ------------------------------------------------------ |
| `simura-night`    | `#06031a` | Primary background (OLED-friendly true dark, slight violet) |
| `simura-deep`     | `#100747` | Secondary background, side panels                      |
| `simura-surface`  | `#1a0a3f` | Card surfaces, dialog backgrounds                      |
| `simura-violet`   | `#7c4dff` | **Primary accent** — interactive, highlights, focus    |
| `simura-amethyst` | `#a26bff` | Hover state, secondary accent                          |
| `simura-lavender` | `#c39bff` | Tertiary accent — gradients, AI assistant glow         |
| `simura-text`     | `#e6e0ff` | Primary text on dark backgrounds                       |
| `simura-muted`    | `#8c80b4` | Secondary text                                         |
| `simura-success`  | `#00d27a` | Success states                                         |
| `simura-warning`  | `#ffb020` | Warning states                                         |
| `simura-danger`   | `#ff4757` | Error states                                           |

> Earlier versions of SIMURA used a cyan-primary palette
> (`#00e5ff` / `#00b8ff`) — kept here for reference. The current identity is
> violet-primary to align with the Win11-style purple-mountain wallpaper and
> the SIMURA "S" logo gradient.

## Typography

| Role         | Font                          |
| ------------ | ----------------------------- |
| UI body      | Roboto                        |
| UI display   | Roboto                        |
| Monospace    | JetBrains Mono Nerd Font      |
| Code editor  | Fira Code Nerd Font           |
| Terminal     | MesloLGS Nerd Font            |

## Logo usage

- Default: `branding/logo/simura-logo.svg` (violet gradient "S")
- Monochrome (currentColor): `branding/logo/simura-logo-mono.svg`
- Minimum render size: 16×16. Below that, use a single-glyph "S" mark.
- Clear-space: at least one stroke-width on all sides.
- Do not stretch, recolor outside the palette, or add drop-shadows.

## Wallpapers

- Default: `branding/wallpapers/simura-default.svg` (4K, purple mountains + crescent planet)
- Minimal: `branding/wallpapers/simura-dark.svg` (4K, no mountains, just deep-space ambience)

PNG variants are generated at build time by `scripts/render-branding.sh`.
