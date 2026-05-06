#!/usr/bin/env bash
# Render SIMURA branding SVGs to the PNG sizes used by Plymouth, GRUB, SDDM,
# Plasma wallpapers, neofetch logo, etc. Run from the repo root.
#
# Requirements: rsvg-convert (librsvg) OR inkscape. Falls back gracefully.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${ROOT}/branding/.rendered"
mkdir -p "${OUT}"

renderer=""
if command -v rsvg-convert >/dev/null 2>&1; then
    renderer="rsvg"
elif command -v inkscape >/dev/null 2>&1; then
    renderer="inkscape"
else
    echo "ERROR: need rsvg-convert (librsvg) or inkscape on PATH" >&2
    exit 1
fi

render() {
    local src="$1" dst="$2" w="$3" h="$4"
    case "${renderer}" in
        rsvg)
            rsvg-convert -w "${w}" -h "${h}" -o "${dst}" "${src}"
            ;;
        inkscape)
            inkscape --export-type=png --export-filename="${dst}" \
                     --export-width="${w}" --export-height="${h}" \
                     "${src}" >/dev/null
            ;;
    esac
    echo "  rendered ${dst} (${w}x${h})"
}

echo "==> SIMURA branding render"
echo "    renderer: ${renderer}"

# Logo at icon sizes
for sz in 16 22 24 32 48 64 96 128 192 256 384 512 1024; do
    render "${ROOT}/branding/logo/simura-logo.svg" \
           "${OUT}/simura-logo-${sz}.png" "${sz}" "${sz}"
done

# Wallpapers at common resolutions
for res in 1920x1080 2560x1440 3840x2160; do
    w="${res%x*}"
    h="${res#*x}"
    render "${ROOT}/branding/wallpapers/simura-default.svg" \
           "${OUT}/wallpaper-default-${res}.png" "${w}" "${h}"
    render "${ROOT}/branding/wallpapers/simura-dark.svg" \
           "${OUT}/wallpaper-dark-${res}.png" "${w}" "${h}"
done

# GRUB / Syslinux splash (640x480 background)
render "${ROOT}/branding/wallpapers/simura-dark.svg" \
       "${OUT}/splash-640x480.png" 640 480

echo "==> done; assets in ${OUT}"
