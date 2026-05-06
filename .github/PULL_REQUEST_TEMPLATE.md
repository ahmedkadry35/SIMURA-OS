## Summary

<!-- What does this PR change and why? -->

## Changes

<!-- Bullet list of the meaningful changes, grouped by area: archiso /
     branding / themes / AI assistant / installer / CI / docs. -->

## How to test

<!-- How a reviewer can verify this PR works. -->

## Screenshots / recordings

<!-- If this PR changes anything visual (themes, branding, login screen,
     desktop layout, AI assistant UI), attach screenshots or a short
     recording. -->

## Checklist

- [ ] `pytest` passes for `ai-assistant/`
- [ ] `ruff check ai-assistant/` is clean
- [ ] `shellcheck` is clean for changed shell scripts
- [ ] `archiso/profiledef.sh`, `packages.x86_64`, and bootloader configs are
      still internally consistent
- [ ] If branding/theme assets changed, `scripts/render-branding.sh` still
      runs end-to-end
- [ ] CI is green (lint + tests + ISO build on main)
