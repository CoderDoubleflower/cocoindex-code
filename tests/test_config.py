"""Unit tests for Config loading."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from cocoindex_code.config import Config


class TestEmbeddingModel:
    """Tests for remote embedding model configuration."""

    def test_default_model_is_openai_embedding(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {"COCOINDEX_CODE_ROOT_PATH": str(tmp_path)},
            clear=False,
        ):
            os.environ.pop("COCOINDEX_CODE_EMBEDDING_MODEL", None)
            config = Config.from_env()
            assert config.embedding_model == "text-embedding-3-small"

    def test_rejects_legacy_local_model_prefix(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {
                "COCOINDEX_CODE_ROOT_PATH": str(tmp_path),
                "COCOINDEX_CODE_EMBEDDING_MODEL": (
                    "sbert/sentence-transformers/all-MiniLM-L6-v2"
                ),
            },
        ):
            try:
                Config.from_env()
            except ValueError as exc:
                assert (
                    "Local SentenceTransformers models are no longer supported" in str(exc)
                )
            else:
                raise AssertionError("Expected local embedding models to be rejected")

    def test_rejects_empty_embedding_model(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {
                "COCOINDEX_CODE_ROOT_PATH": str(tmp_path),
                "COCOINDEX_CODE_EMBEDDING_MODEL": "   ",
            },
        ):
            try:
                Config.from_env()
            except ValueError as exc:
                assert "COCOINDEX_CODE_EMBEDDING_MODEL cannot be empty" in str(exc)
            else:
                raise AssertionError("Expected empty embedding model to be rejected")


class TestExtraExtensions:
    """Tests for COCOINDEX_CODE_EXTRA_EXTENSIONS env var."""

    def test_empty_by_default(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {"COCOINDEX_CODE_ROOT_PATH": str(tmp_path)},
        ):
            os.environ.pop("COCOINDEX_CODE_EXTRA_EXTENSIONS", None)
            config = Config.from_env()
            assert config.extra_extensions == {}

    def test_parses_comma_separated(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {
                "COCOINDEX_CODE_ROOT_PATH": str(tmp_path),
                "COCOINDEX_CODE_EXTRA_EXTENSIONS": "rb,yaml,toml",
            },
        ):
            config = Config.from_env()
            assert config.extra_extensions == {".rb": None, ".yaml": None, ".toml": None}

    def test_trims_whitespace(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {
                "COCOINDEX_CODE_ROOT_PATH": str(tmp_path),
                "COCOINDEX_CODE_EXTRA_EXTENSIONS": " rb , yaml , ",
            },
        ):
            config = Config.from_env()
            assert config.extra_extensions == {".rb": None, ".yaml": None}

    def test_empty_string_gives_empty_dict(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {
                "COCOINDEX_CODE_ROOT_PATH": str(tmp_path),
                "COCOINDEX_CODE_EXTRA_EXTENSIONS": "",
            },
        ):
            config = Config.from_env()
            assert config.extra_extensions == {}

    def test_dot_prefix_passed_through(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {
                "COCOINDEX_CODE_ROOT_PATH": str(tmp_path),
                "COCOINDEX_CODE_EXTRA_EXTENSIONS": ".rb,yaml",
            },
        ):
            config = Config.from_env()
            assert config.extra_extensions == {"..rb": None, ".yaml": None}

    def test_parses_lang_mapping(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {
                "COCOINDEX_CODE_ROOT_PATH": str(tmp_path),
                "COCOINDEX_CODE_EXTRA_EXTENSIONS": "inc:php",
            },
        ):
            config = Config.from_env()
            assert config.extra_extensions == {".inc": "php"}

    def test_mixed_with_and_without_lang(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {
                "COCOINDEX_CODE_ROOT_PATH": str(tmp_path),
                "COCOINDEX_CODE_EXTRA_EXTENSIONS": "inc:php,yaml,tpl:html",
            },
        ):
            config = Config.from_env()
            assert config.extra_extensions == {".inc": "php", ".yaml": None, ".tpl": "html"}


class TestIncludePatterns:
    """Tests for COCOINDEX_CODE_INCLUDE_PATTERNS env var."""

    def test_empty_by_default(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {"COCOINDEX_CODE_ROOT_PATH": str(tmp_path)},
            clear=False,
        ):
            os.environ.pop("COCOINDEX_CODE_INCLUDE_PATTERNS", None)
            config = Config.from_env()
            assert config.include_patterns is None

    def test_parses_comma_separated_globs(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {
                "COCOINDEX_CODE_ROOT_PATH": str(tmp_path),
                "COCOINDEX_CODE_INCLUDE_PATTERNS": "**/*.cpp,**/*.h",
            },
        ):
            config = Config.from_env()
            assert config.include_patterns == ["**/*.cpp", "**/*.h"]

    def test_trims_whitespace(self, tmp_path: Path) -> None:
        with patch.dict(
            os.environ,
            {
                "COCOINDEX_CODE_ROOT_PATH": str(tmp_path),
                "COCOINDEX_CODE_INCLUDE_PATTERNS": " **/*.cpp , **/*.h , ",
            },
        ):
            config = Config.from_env()
            assert config.include_patterns == ["**/*.cpp", "**/*.h"]
