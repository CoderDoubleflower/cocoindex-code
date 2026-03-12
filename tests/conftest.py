"""Pytest configuration and fixtures."""

import os
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path

import cocoindex as coco
import numpy as np
import pytest
import pytest_asyncio

# === Environment setup BEFORE any cocoindex_code imports ===
# Create test directory and set it BEFORE any module imports
_TEST_DIR = Path(tempfile.mkdtemp(prefix="cocoindex_test_"))
os.environ["COCOINDEX_CODE_ROOT_PATH"] = str(_TEST_DIR)
os.environ["COCOINDEX_CODE_EMBEDDING_MODEL"] = "text-embedding-3-small"


@pytest.fixture(scope="session")
def test_codebase_root() -> Path:
    """Session-scoped test codebase directory."""
    return _TEST_DIR


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def coco_runtime() -> AsyncIterator[None]:
    """
    Set up CocoIndex runtime context for the entire test session.

    Uses session-scoped event loop to ensure CocoIndex environment
    persists across all tests.
    """
    async with coco.runtime():
        yield


@pytest.fixture(autouse=True)
def mock_remote_embeddings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace network embeddings with a deterministic local test double."""
    from cocoindex_code.shared import embedder

    vocabulary = [
        "fibonacci",
        "database",
        "connect",
        "query",
        "neural",
        "machine",
        "learning",
        "authentication",
        "login",
        "python",
        "javascript",
        "typescript",
        "function",
        "server",
        "hello",
    ]

    async def fake_embed(
        text: str,
        is_query: bool = False,
        prompt_name: str | None = None,
    ) -> np.ndarray:
        del is_query, prompt_name
        lowered = text.lower()
        vector = np.array(
            [float(lowered.count(token)) for token in vocabulary],
            dtype="float32",
        )
        if not vector.any():
            vector[0] = 1.0
        norm = np.linalg.norm(vector)
        if norm:
            vector = vector / norm
        return vector

    monkeypatch.setattr(embedder, "embed", fake_embed)
