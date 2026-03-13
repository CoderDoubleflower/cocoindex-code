"""Configuration management for cocoindex-code."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_DEFAULT_MODEL = "text-embedding-3-small"
_DEFAULT_ENCODING_FORMAT = "float"
_LEGACY_LOCAL_MODEL_PREFIX = "sbert/"
_VALID_ENCODING_FORMATS = {"float", "base64", "bytes", "bytes_only"}


def _find_root_with_marker(start: Path, markers: list[str]) -> Path | None:
    """Walk up from start, return first directory containing any marker."""
    current = start
    while True:
        if any((current / m).exists() for m in markers):
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def _discover_codebase_root() -> Path:
    """Discover the codebase root directory.

    Discovery order:
    1. Find nearest parent with `.cocoindex_code` directory (re-anchor to previously-indexed tree)
    2. Find nearest parent with any common project root marker
    3. Fall back to current working directory
    """
    cwd = Path.cwd()

    # First, look for existing .cocoindex_code directory
    root = _find_root_with_marker(cwd, [".cocoindex_code"])
    if root is not None:
        return root

    # Then, look for common project root markers
    markers = [".git", "pyproject.toml", "package.json", "Cargo.toml", "go.mod"]
    root = _find_root_with_marker(cwd, markers)
    return root if root is not None else cwd


def _load_embedding_model() -> str:
    """Load and validate the configured embedding model."""
    model = os.environ.get("COCOINDEX_CODE_EMBEDDING_MODEL", _DEFAULT_MODEL).strip()
    if not model:
        raise ValueError("COCOINDEX_CODE_EMBEDDING_MODEL cannot be empty.")
    if model.startswith(_LEGACY_LOCAL_MODEL_PREFIX):
        raise ValueError(
            "Local SentenceTransformers models are no longer supported. "
            "Set COCOINDEX_CODE_EMBEDDING_MODEL to a LiteLLM-compatible remote model, "
            "for example `text-embedding-3-small`."
        )
    return model


def _load_encoding_format() -> str:
    """Load and validate the embedding encoding format."""
    value = os.environ.get("COCOINDEX_CODE_ENCODING_FORMAT", _DEFAULT_ENCODING_FORMAT).strip()
    if not value:
        return _DEFAULT_ENCODING_FORMAT
    if value not in _VALID_ENCODING_FORMATS:
        valid = ", ".join(sorted(_VALID_ENCODING_FORMATS))
        raise ValueError(
            "COCOINDEX_CODE_ENCODING_FORMAT must be one of "
            f"{valid}. Got: {value!r}."
        )
    return value


@dataclass
class Config:
    """Configuration loaded from environment variables."""

    codebase_root_path: Path
    embedding_model: str
    api_base: str | None
    encoding_format: str
    index_dir: Path
    include_patterns: list[str] | None
    extra_extensions: dict[str, str | None]

    @classmethod
    def from_env(cls) -> Config:
        """Load configuration from environment variables."""
        root_path_str = os.environ.get("COCOINDEX_CODE_ROOT_PATH")
        if root_path_str:
            root = Path(root_path_str).resolve()
        else:
            root = Path.cwd()

        api_base = os.environ.get("COCOINDEX_CODE_API_BASE", "").strip() or None
        encoding_format = _load_encoding_format()
        index_dir = root / ".cocoindex_code"

        raw_include_patterns = os.environ.get("COCOINDEX_CODE_INCLUDE_PATTERNS", "")
        include_patterns = [
            pattern.strip()
            for pattern in raw_include_patterns.split(",")
            if pattern.strip()
        ]

        raw_extra = os.environ.get("COCOINDEX_CODE_EXTRA_EXTENSIONS", "")
        extra_extensions: dict[str, str | None] = {}
        for token in raw_extra.split(","):
            token = token.strip()
            if not token:
                continue
            if ":" in token:
                ext, lang = token.split(":", 1)
                extra_extensions[f".{ext.strip()}"] = lang.strip() or None
            else:
                extra_extensions[f".{token}"] = None

        return cls(
            codebase_root_path=root,
            embedding_model=_load_embedding_model(),
            api_base=api_base,
            encoding_format=encoding_format,
            index_dir=index_dir,
            include_patterns=include_patterns or None,
            extra_extensions=extra_extensions,
        )

    @property
    def target_sqlite_db_path(self) -> Path:
        """Path to the vector index SQLite database."""
        return self.index_dir / "target_sqlite.db"

    @property
    def cocoindex_db_path(self) -> Path:
        """Path to the CocoIndex state database."""
        return self.index_dir / "cocoindex.db"


# Module-level singleton — imported directly by all modules that need configuration
config: Config = Config.from_env()
