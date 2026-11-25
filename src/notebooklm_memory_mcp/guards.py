"""Pure-stdlib guardrails applied to upstream tool arguments."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

EXPECTED_VERSION = "0.8.6"
DEFAULT_CORPUS = Path(__file__).resolve().parents[2] / "examples" / "corpus"

TEXT_KEYS = frozenset(
    {
        "text",
        "question",
        "content",
        "title",
        "new_title",
        "instructions",
        "custom_prompt",
        "style_prompt",
        "query",
        "message",
        "goal",
        "note",
        "filename",
    }
)
PATH_KEYS = frozenset({"path", "url"})

FORBIDDEN_NAME = re.compile(
    r"(^|[\\/])(\.env|.*\.key|.*token.*|storage_state\.json|master_token\.json|"
    r"config\.json|.*\.pfx|.*\.pem)$",
    re.IGNORECASE,
)

SECRET_PATTERNS = (
    (re.compile(r"tskey-auth-[A-Za-z0-9_-]+"), "[REDACTED_TSKEY]"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}", re.IGNORECASE), "Bearer [REDACTED]"),
    (
        re.compile(r"\b(password|passwd|api[_-]?key|secret)\s*[:=]\s*\S+", re.IGNORECASE),
        r"\1: [REDACTED]",
    ),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[REDACTED_IP]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
)


def allowed_root(root: Path | None = None) -> Path:
    """Resolve the one directory local source paths may point into."""
    if root is not None:
        return root.resolve()
    configured = os.environ.get("NOTEBOOKLM_MCP_ALLOWED_ROOTS")
    return Path(configured).resolve() if configured else DEFAULT_CORPUS.resolve()


def redact(value: str) -> str:
    """Replace credential-shaped values in an outbound text argument."""
    for pattern, replacement in SECRET_PATTERNS:
        value = pattern.sub(replacement, value)
    return value


def check_local_path(value: str, root: Path | None = None) -> str:
    """Refuse paths outside the corpus root or with credential-shaped names."""
    path = Path(value)
    if FORBIDDEN_NAME.search(path.name):
        raise ValueError(f"refused credential-shaped filename: {path.name}")
    base = allowed_root(root)
    resolved = (base / path if not path.is_absolute() else path).resolve()
    if resolved != base and base not in resolved.parents:
        raise ValueError("refused path outside allowed corpus root")
    return str(resolved)


def sanitize_args(value: Any, key: str | None = None, root: Path | None = None) -> Any:
    """Recursively redact text keys and confine local path keys."""
    if isinstance(value, str):
        if key in PATH_KEYS and "://" not in value:
            return check_local_path(value, root)
        if key in TEXT_KEYS:
            return redact(value)
        return value
    if isinstance(value, dict):
        return {k: sanitize_args(v, k, root) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_args(v, key, root) for v in value]
    return value


def check_version(installed: str) -> None:
    """Fail closed when the upstream package drifts from the pinned version."""
    if installed != EXPECTED_VERSION:
        raise SystemExit(f"pinned notebooklm-py=={EXPECTED_VERSION}, found {installed}")
