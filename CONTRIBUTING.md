# Contributing

Use Python 3.13 and uv. Set the repo-local git identity to your GitHub account before committing.

```powershell
uv sync --frozen
uv run pytest -q
uv run python -m compileall -q src tests tools
uv build
```

Keep changes to `src/notebooklm_memory_mcp/` covered by a test in `tests/`.
Never commit cookies, tokens, `.env` files, SSH keys, browser state or raw session
transcripts. Update `README.md` when a default, command or limit changes.
Open a pull request and let CI finish before asking for review.
