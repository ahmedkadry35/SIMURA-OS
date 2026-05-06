# SIMURA Plymouth theme

Files in this directory are installed to `/usr/share/plymouth/themes/simura/`
during ISO build and (once SIMURA is installed) during package post-install.

## Image assets

The `.script` references PNGs that are generated from SVGs at build time:

| File               | Generated from                              | Notes                |
|--------------------|---------------------------------------------|----------------------|
| `background.png`   | `branding/wallpapers/simura-dark.svg`       | scaled to 1920x1080  |
| `logo.png`         | `branding/logo/simura-logo.svg`             | scaled to 256×256    |
| `progress_bar.png` | drawn at build time (`scripts/build.sh`)    | 320×4 cyan stripe    |

## Activating

After installing the theme files:

```bash
plymouth-set-default-theme -R simura
```

This regenerates the initramfs so Plymouth picks up the theme on next boot.
