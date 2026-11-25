# Changelog

## [0.1.0] - 2026-11-26

- Initial public version.
- Wrap the pinned upstream NotebookLM MCP server over stdio.
- Fail closed when `notebooklm-py` is not exactly 0.8.6.
- Confine local source paths to one corpus root and refuse credential-shaped names.
- Redact token, password, IP address and email patterns from text arguments.
- Add guard tests, CI, a release-verification workflow and an icon generator.
