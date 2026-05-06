#!/usr/bin/env bash
# shellcheck disable=SC2034
#
# SIMURA OS — archiso profile definition.
# Built on top of the upstream `releng` profile shape so the rest of the
# archiso tooling treats it identically.

iso_name="simura"
iso_label="SIMURA_$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_publisher="SIMURA OS <https://github.com/ahmedkadry35/SIMURA-OS>"
iso_application="SIMURA OS Live/Installer ISO"
iso_version="$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y.%m.%d)"
install_dir="simura"
buildmodes=('iso')
bootmodes=(
  'bios.syslinux.mbr'
  'bios.syslinux.eltorito'
  'uefi-ia32.grub.esp'
  'uefi-x64.grub.esp'
  'uefi-ia32.grub.eltorito'
  'uefi-x64.grub.eltorito'
)
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
# zstd: ~5x faster than xz to build, ISO is ~10% larger but build fits in CI.
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '15' '-b' '1M')
bootstrap_tarball_compression=(zstd -c -T0 --auto-threads=logical --long -19)
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/etc/gshadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/root/.gnupg"]="0:0:700"
  ["/usr/local/bin/choose-mirror"]="0:0:755"
  ["/usr/local/bin/Installation_guide"]="0:0:755"
  ["/usr/local/bin/livecd-sound"]="0:0:755"
  ["/usr/local/bin/simura-firstboot"]="0:0:755"
  ["/usr/local/bin/simura-assistant"]="0:0:755"
  ["/usr/local/bin/simura-pull-models"]="0:0:755"
  ["/etc/sudoers.d/simura"]="0:0:440"
)
