#!/usr/bin/env bash
# SIMURA OS — top-level build entrypoint.
#
# Runs the archiso build inside a Docker Arch Linux container so we don't
# need an Arch host. Designed to work identically on developer laptops and in
# GitHub Actions.
#
# Usage:
#   ./scripts/build.sh                # build the ISO
#   ./scripts/build.sh --skip-pull    # skip `docker pull`
#   ./scripts/build.sh --shell        # drop into a shell in the build container
#   ./scripts/build.sh --keep-work    # keep /tmp/archiso-work on the host
#
# Outputs:
#   out/simura-<YYYY.MM.DD>-x86_64.iso
#   out/simura-<YYYY.MM.DD>-x86_64.iso.sha256

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${ROOT}/out"
WORK="${ROOT}/.work-archiso"

ARCH_IMAGE="archlinux:base-devel"
DOCKER="${DOCKER:-docker}"
SKIP_PULL=0
DROP_SHELL=0
KEEP_WORK=0

for arg in "$@"; do
    case "${arg}" in
        --skip-pull) SKIP_PULL=1 ;;
        --shell)     DROP_SHELL=1 ;;
        --keep-work) KEEP_WORK=1 ;;
        *) echo "unknown option: ${arg}" >&2; exit 64 ;;
    esac
done

mkdir -p "${OUT}" "${WORK}"

echo "==> SIMURA OS build"
echo "    repo root: ${ROOT}"
echo "    output:    ${OUT}"

if [[ ${SKIP_PULL} -eq 0 ]]; then
    echo "==> docker pull ${ARCH_IMAGE}"
    "${DOCKER}" pull "${ARCH_IMAGE}"
fi

# Render branding PNGs first (rsvg-convert lives in the Arch container).
# We pass the source repo into the container at /src.

# shellcheck disable=SC2016
INSIDE='
set -euo pipefail
cd /src

echo "==> populating pacman keyring"
pacman-key --init
pacman-key --populate archlinux

echo "==> installing build deps in container"
pacman -Sy --noconfirm --needed \
    archiso \
    git \
    grub \
    edk2-shell \
    libisoburn \
    squashfs-tools \
    librsvg \
    imagemagick \
    rsync \
    python-pip \
    python-build \
    python-wheel \
    python-installer \
    python-setuptools \
    base-devel >/dev/null

echo "==> rendering branding PNGs"
bash scripts/render-branding.sh

# Create a small progress_bar.png Plymouth needs (320×4 cyan).
mkdir -p branding/.rendered
if command -v convert >/dev/null 2>&1; then
    convert -size 320x4 xc:"#7c4dff" branding/.rendered/progress_bar.png
fi

echo "==> assembling archiso profile in /tmp/profile"
profile=/tmp/profile
rm -rf "${profile}"
cp -a archiso "${profile}"

# Ensure airootfs has the right mode bits.
chmod 0440 "${profile}/airootfs/etc/sudoers.d/simura"
mkdir -p "${profile}/airootfs/var/lib/simura"

# Drop branding PNGs into the live filesystem.
mkdir -p "${profile}/airootfs/usr/share/wallpapers/SIMURA/contents/images"
mkdir -p "${profile}/airootfs/usr/share/plymouth/themes/simura"
mkdir -p "${profile}/airootfs/usr/share/grub/themes/simura"
mkdir -p "${profile}/airootfs/usr/share/sddm/themes/simura"
mkdir -p "${profile}/airootfs/usr/share/calamares/branding/simura"
mkdir -p "${profile}/airootfs/etc/calamares/modules"
mkdir -p "${profile}/airootfs/etc/calamares"
mkdir -p "${profile}/airootfs/etc/skel/.config/Kvantum"
mkdir -p "${profile}/airootfs/etc/skel/.config/qt5ct/colors"
mkdir -p "${profile}/airootfs/etc/skel/.local/share/color-schemes"
mkdir -p "${profile}/airootfs/etc/skel/.local/share/konsole"
mkdir -p "${profile}/airootfs/usr/share/plasma/look-and-feel/org.simura.desktop/contents/layouts"

# Install the SIMURA logo at every hicolor size that we render so Plasma /
# panel widgets / window decorations all pick the best fit.
for sz in 16 22 24 32 48 64 96 128 192 256 384 512 1024; do
    src="branding/.rendered/simura-logo-${sz}.png"
    if [ -f "$src" ]; then
        dst="${profile}/airootfs/usr/share/icons/hicolor/${sz}x${sz}/apps"
        mkdir -p "$dst"
        cp "$src" "${dst}/simura-logo.png"
        cp "$src" "${dst}/simura-assistant.png"
    fi
done
cp branding/.rendered/wallpaper-default-3840x2160.png \
   "${profile}/airootfs/usr/share/wallpapers/SIMURA/contents/images/3840x2160.png"
cp branding/.rendered/wallpaper-dark-3840x2160.png \
   "${profile}/airootfs/usr/share/wallpapers/SIMURA-dark/contents/images/3840x2160.png" 2>/dev/null || true
cp branding/.rendered/simura-logo-256.png \
   "${profile}/airootfs/usr/share/plymouth/themes/simura/logo.png"
cp branding/.rendered/wallpaper-dark-1920x1080.png \
   "${profile}/airootfs/usr/share/plymouth/themes/simura/background.png"
cp branding/.rendered/progress_bar.png \
   "${profile}/airootfs/usr/share/plymouth/themes/simura/progress_bar.png" 2>/dev/null || true
cp branding/plymouth/simura.script \
   "${profile}/airootfs/usr/share/plymouth/themes/simura/simura.script"
cp branding/plymouth/simura.plymouth \
   "${profile}/airootfs/usr/share/plymouth/themes/simura/simura.plymouth"
cp branding/grub/theme.txt \
   "${profile}/airootfs/usr/share/grub/themes/simura/theme.txt"
cp -r branding/sddm/theme/. \
   "${profile}/airootfs/usr/share/sddm/themes/simura/"
cp branding/.rendered/simura-logo-256.png \
   "${profile}/airootfs/usr/share/sddm/themes/simura/logo.png" 2>/dev/null || true

# Plasma look-and-feel + KDE config files
cp -r themes/plasma/look-and-feel/. \
      "${profile}/airootfs/usr/share/plasma/look-and-feel/org.simura.desktop/"
cp themes/plasma/SIMURA.colors \
      "${profile}/airootfs/etc/skel/.local/share/color-schemes/SIMURA.colors"
cp themes/plasma/kdeglobals  "${profile}/airootfs/etc/skel/.config/kdeglobals"
cp themes/plasma/kwinrc      "${profile}/airootfs/etc/skel/.config/kwinrc"
cp -r themes/kvantum/SIMURA  "${profile}/airootfs/etc/skel/.config/Kvantum/SIMURA"
cp themes/konsole/SIMURA.profile     "${profile}/airootfs/etc/skel/.local/share/konsole/SIMURA.profile"
cp themes/konsole/SIMURA.colorscheme "${profile}/airootfs/etc/skel/.local/share/konsole/SIMURA.colorscheme"
mkdir -p "${profile}/airootfs/etc/skel/.config/gtk-3.0" \
         "${profile}/airootfs/etc/skel/.config/gtk-4.0"
cp themes/gtk/gtk-3.0/settings.ini "${profile}/airootfs/etc/skel/.config/gtk-3.0/settings.ini"
cp themes/gtk/gtk-4.0/settings.ini "${profile}/airootfs/etc/skel/.config/gtk-4.0/settings.ini"

# Kvantum manager preference
cat > "${profile}/airootfs/etc/skel/.config/Kvantum/kvantum.kvconfig" <<EOF
[General]
theme=SIMURA
EOF

# Calamares installer files
cp installer/calamares/settings.conf \
   "${profile}/airootfs/etc/calamares/settings.conf"
cp -r installer/calamares/branding/simura/. \
   "${profile}/airootfs/usr/share/calamares/branding/simura/"
cp branding/.rendered/simura-logo-256.png \
   "${profile}/airootfs/usr/share/calamares/branding/simura/logo.png"
cp branding/.rendered/simura-logo-256.png \
   "${profile}/airootfs/usr/share/calamares/branding/simura/welcome.png"
cp installer/calamares/modules/*.conf \
   "${profile}/airootfs/etc/calamares/modules/"

# Build the AI assistant wheel and stage it inside the airootfs so the
# image bundles a runnable simura-assistant binary even before pacman
# repos catch up.
echo "==> building simura-assistant wheel"
mkdir -p "${profile}/airootfs/opt/simura/wheels"
( cd ai-assistant && python -m build --wheel --no-isolation \
    --outdir "${profile}/airootfs/opt/simura/wheels" . )

# Drop a tiny launcher script in /usr/local/bin so the .desktop file can find it.
cat > "${profile}/airootfs/usr/local/bin/simura-assistant" <<EOF_LAUNCH
#!/usr/bin/env bash
# SIMURA Assistant launcher. Installs the bundled wheel into a per-user venv
# on first run, then exec\\\$s the assistant.
set -euo pipefail
VENV="\\\$HOME/.local/share/simura/venv"
if [[ ! -x "\\\$VENV/bin/simura-assistant" ]]; then
    python -m venv "\\\$VENV"
    "\\\$VENV/bin/pip" install --quiet --no-index --find-links /opt/simura/wheels simura-assistant \\\\
        || "\\\$VENV/bin/pip" install --quiet simura-assistant
fi
exec "\\\$VENV/bin/simura-assistant" "\\\$@"
EOF_LAUNCH
chmod +x "${profile}/airootfs/usr/local/bin/simura-assistant"

# Drop the assistant .desktop entry
mkdir -p "${profile}/airootfs/usr/share/applications"
cp ai-assistant/resources/simura-assistant.desktop \
   "${profile}/airootfs/usr/share/applications/simura-assistant.desktop"
cp branding/.rendered/simura-logo-256.png \
   "${profile}/airootfs/usr/share/icons/hicolor/256x256/apps/simura-assistant.png"

echo "==> running mkarchiso"
rm -rf .work-archiso
mkdir -p .work-archiso
mkarchiso -v -w /tmp/work -o /src/out "${profile}"

echo "==> writing checksum"
( cd /src/out && sha256sum simura-*.iso > "$(ls -1 simura-*.iso | head -1).sha256" )

echo "==> done — output:"
ls -lh /src/out
'

if [[ ${DROP_SHELL} -eq 1 ]]; then
    exec "${DOCKER}" run --rm -it --privileged \
        -v "${ROOT}:/src" \
        -w /src \
        "${ARCH_IMAGE}" bash
fi

"${DOCKER}" run --rm --privileged \
    -v "${ROOT}:/src" \
    -w /src \
    "${ARCH_IMAGE}" \
    bash -euo pipefail -c "${INSIDE}"

echo
echo "==> Build complete."
ls -lh "${OUT}"

if [[ ${KEEP_WORK} -eq 0 ]]; then
    rm -rf "${WORK}"
fi
