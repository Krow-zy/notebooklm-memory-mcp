# Security policy

## Reporting

Report vulnerabilities through a private GitHub security advisory for this repository.
Do not open a public issue for a credential leak or an exploitable flaw.

## What this project stores

The server keeps no database, no log file and no credential file in this repository.
The upstream client manages its own browser session under `~/.notebooklm/`; treat that
directory as a credential and never add it to a notebook source.

## Guardrails

Startup exits when `notebooklm-py` is not exactly 0.8.6. Local source paths are confined
to `NOTEBOOKLM_MCP_ALLOWED_ROOTS`; credential-shaped filenames are refused and a fixed set
of token, password, IP address and email patterns is redacted from text arguments.
The guard is defense in depth, not a sandbox. Curate corpus files manually.
