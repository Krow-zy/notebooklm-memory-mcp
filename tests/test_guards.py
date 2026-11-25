from pathlib import Path

import pytest

from notebooklm_memory_mcp.guards import (
    EXPECTED_VERSION,
    check_local_path,
    check_version,
    redact,
    sanitize_args,
)


def test_redaction_removes_credential_shaped_values() -> None:
    safe = redact(
        "tskey-auth-abcdef123456 Bearer sk-123456789012 "
        "password=1234 ip 192.168.0.106 mail owner@example.com"
    )
    assert "tskey-auth-abcdef" not in safe and "REDACTED_TSKEY" in safe
    assert "sk-123456789012" not in safe and "REDACTED" in safe
    assert "1234" not in safe and "192.168.0.106" not in safe
    assert "owner@example.com" not in safe and "REDACTED_EMAIL" in safe


def test_local_paths_are_confined_to_the_corpus(tmp_path: Path) -> None:
    assert check_local_path("notes.md", root=tmp_path) == str(tmp_path / "notes.md")
    nested = tmp_path / "nested"
    nested.mkdir()
    assert check_local_path("nested/notes.md", root=tmp_path) == str(nested / "notes.md")


@pytest.mark.parametrize("bad", ["../.env", "token.txt", "config.json", "key.pem"])
def test_credential_shaped_filenames_are_refused(tmp_path: Path, bad: str) -> None:
    with pytest.raises(ValueError, match="refused credential-shaped filename"):
        check_local_path(bad, root=tmp_path)


def test_absolute_path_outside_corpus_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="refused path outside"):
        check_local_path(str(tmp_path.parent / "outside.md"), root=tmp_path)


def test_sanitize_args_keeps_plain_values_and_urls(tmp_path: Path) -> None:
    safe = sanitize_args(
        {
            "path": "notes.md",
            "question": "what happened?",
            "url": "https://example.com/doc",
            "id": "abc",
            "list": ["secret=xyz", 7],
            "note": "secret=xyz",
        },
        root=tmp_path,
    )
    assert safe["path"] == str(tmp_path / "notes.md")
    assert safe["question"] == "what happened?"
    assert safe["url"] == "https://example.com/doc"
    assert safe["id"] == "abc"
    assert safe["list"] == ["secret=xyz", 7]
    assert safe["note"] == "secret: [REDACTED]"


def test_version_pin_fails_closed() -> None:
    assert EXPECTED_VERSION == "0.8.6"
    check_version(EXPECTED_VERSION)
    with pytest.raises(SystemExit, match="pinned notebooklm-py==0.8.6"):
        check_version("0.8.7")
