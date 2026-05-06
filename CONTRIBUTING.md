# Contributing to SIMURA OS

## Running tests locally

```bash
cd ai-assistant
python -m venv .venv && source .venv/bin/activate
pip install -e . pytest ruff
pytest -v
ruff check src/ tests/ --select=E,F,W,I,B,UP --ignore=E501
```

## Building the ISO locally

```bash
./scripts/build.sh
```

The build runs in a Docker Arch container, so you don't need an Arch host.
Output lands in `out/`.

## Branding changes

If you change anything under `branding/logo/` or `branding/wallpapers/`,
re-run `./scripts/render-branding.sh` to refresh the PNGs CI checks against.

## Code style

- Python: type hints, no `Any`, no `getattr`/`setattr` for known fields.
  The `ruff` rules in CI enforce a small subset of pyflakes/pycodestyle/
  isort/bugbear.
- Shell scripts: bash with `set -euo pipefail`. We run `shellcheck` in CI;
  fix warnings instead of disabling them.
- Configs (sysctl, systemd, calamares): include comments explaining *why*
  each non-default value is set. Future contributors will thank you.

## What CI checks

1. `pytest` for the assistant
2. `ruff check` for lint
3. `shellcheck` for every script we ship
4. archiso profile structural validation
5. branding PNG render dry-run
6. (push to `main` only) full ISO build inside an Arch container

## License

By contributing, you agree your contribution is licensed under GPL-3.0-or-later.
