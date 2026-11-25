<p align="center"><img src="assets/icon-256.png" alt="notebooklm-memory-mcp icon" width="120"></p>
<h1 align="center">notebooklm-memory-mcp</h1>
<p align="center">Guarded NotebookLM MCP for Droid and Claude Code</p>
<p align="center">
  <a href="https://github.com/Krow-zy/notebooklm-memory-mcp/actions/workflows/ci.yml"><img src="https://github.com/Krow-zy/notebooklm-memory-mcp/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT license"></a>
  <img src="https://img.shields.io/badge/python-3.13-blue.svg" alt="Python 3.13">
</p>

Local NotebookLM MCP server with pinned dependencies, corpus-only paths, and no cookie or token forwarding.

Built for AI agents that need session memory and context engineering on Windows. It keeps the upstream client pinned and stops credential-shaped names and common secret patterns from reaching tool calls.

- [What and why](#what-and-why)
- [Usage](#usage)
- [Configuration](#configuration)
- [How it works](#how-it-works)
- [Privacy and security](#privacy-and-security)
- [Run it](#run-it)
- [Build from source](#build-from-source)
- [Limits, stated plainly](#limits-stated-plainly)
- [Repository layout](#repository-layout)
- [Releasing](#releasing)
- [License](#license)

## What and why

`notebooklm-py` exposes NotebookLM to MCP clients, but it accepts arbitrary file paths and text arguments and keeps its own browser session. This package starts that upstream server over stdio, pins the dependency version, and applies guardrails before each tool call. Diagnostics go to stderr so stdout stays MCP JSON-RPC.

## Usage

| Command | What it does |
| --- | --- |
| `notebooklm-memory-mcp` | Starts the guarded server over stdio. |
| `pytest -q` | Runs the guard tests. |
| `python -m compileall -q src tests tools` | Checks Python syntax. |
| `uv build` | Builds a wheel and source distribution. |

Point your MCP client at `examples/mcp.json`. It contains a stdio command and a corpus path, with no cookie or token values.

## Configuration

| Key | Default | Meaning |
| --- | --- | --- |
| `NOTEBOOKLM_MCP_ALLOWED_ROOTS` | `<repo>/examples/corpus` | Directory for local source paths. Relative paths resolve inside it; absolute paths outside it are refused. |

## How it works

| What you see | Where it comes from |
| --- | --- |
| Startup exits on a version mismatch | `check_version()` compares `importlib.metadata.version("notebooklm-py")` with `EXPECTED_VERSION = "0.8.6"`. |
| Refused source path | `check_local_path()` rejects credential-shaped filenames and paths outside the corpus root. |
| Redacted argument | `redact()` replaces 5 token, password, IP address and email patterns in 13 text keys. |
| Upstream tools | `notebooklm.mcp.server.create_server()` plus `GuardMiddleware` on every tool call. |

## Privacy and security

This repository ships no browser cookies, master token, `.env` file, SSH key or raw transcript. The upstream client manages its login state under `~/.notebooklm/`; treat that directory as a credential and never add it to a notebook source. The guard is defense in depth, not a sandbox: curate corpus files yourself.

## Run it

Python 3.13 and uv 0.12.13 or newer are required. A NotebookLM account is needed for upstream calls, but this repository performs no login. No administrator rights are needed.

```powershell
git clone https://github.com/Krow-zy/notebooklm-memory-mcp.git
cd notebooklm-memory-mcp
uv sync --frozen
uv run pytest -q
uv run notebooklm-memory-mcp
```

## Build from source

```powershell
uv sync --frozen
uv run python -m compileall -q src tests tools
uv run pytest -q
uv build
```

The build writes `dist/*.whl` and `dist/*.tar.gz`. Regenerate the committed icon with `uv run python tools/generate-icon.py`.

## Limits, stated plainly

- Pinned to `notebooklm-py==0.8.6`; startup fails closed on any other version.
- Redaction covers 5 regex patterns and 13 named text keys. Other formats are not detected.
- The path guard does not inspect file contents, so corpus files must be curated manually.
- NotebookLM's upload endpoint rejects `.html`; keep HTML out of the corpus.
- No login flow is implemented here; upstream owns browser auth and session storage.
- No release is published by pushing a tag; publishing is a separate manual workflow run.
- Memory and CPU floor have not been measured. The process inherits Python and upstream browser dependencies.

## Repository layout

| Path | Contents |
| --- | --- |
| `src/notebooklm_memory_mcp/` | Server wrapper, guard middleware and guard functions. |
| `tests/` | Guard tests. |
| `examples/` | MCP client config and a curated corpus placeholder. |
| `assets/` | Committed 256 px icon. |
| `tools/` | Icon regeneration script. |
| `.github/workflows/` | CI and release-verification workflows. |

## Releasing

Pushing `v0.1.0` runs the Release workflow's verify job: tests, version/tag check and build. Publishing requires running the same workflow with `publish=true`; no GitHub release is created by this initial commit.

## License

MIT - 2026 Krow-zy

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Canonical copy: [LICENSE](LICENSE).
