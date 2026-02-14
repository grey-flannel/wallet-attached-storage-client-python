# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python client library for the [Wallet Attached Storage](https://wallet.storage/spec) specification. Early-stage project (v0.1.0) with no runtime dependencies — source is in `src/wallet_attached_storage_client/`.

## Commands

All commands use `uv run` (no activating `.venv` directly).

```bash
# Lint & security
uv run ruff check                                          # ruff (primary linter)
uv run flake8 src tests                                    # flake8
uv run bandit -r src                                       # security scan (src)
uv run bandit -r tests -s B101                             # security scan (tests, allow assert)
uv run safety scan                                         # dependency vulnerability scan

# Test
uv run -m pytest -vv --cov=src --cov-report=term           # full suite with coverage
uv run -m pytest tests/test_foo.py -k "test_name"          # single test

# Build & publish
rm -rf dist && uv build
uv publish -t $(keyring get https://upload.pypi.org/legacy/ __token__)
```

## Project Configuration

- **Build**: hatchling
- **Python**: >=3.11
- **Ruff**: line-length 120, target py311, rules E/F/N/S (S101 ignored in tests)
- **Pytest**: `--import-mode=importlib`
- **Dev deps**: bandit, flake8, keyring, pytest, pytest-cov, ruff, safety

## Issue Tracking

Uses **bd (beads)** — not TodoWrite/TaskCreate/markdown files. See `AGENTS.md` for quick reference.
