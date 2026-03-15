"""Shared context keys, embedder factory, and CodeChunk schema."""

from __future__ import annotations

import logging
import pathlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Union

import cocoindex as coco
from cocoindex.connectors import sqlite
import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from cocoindex.ops.litellm import LiteLLMEmbedder
    from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder

from .settings import EmbeddingSettings

logger = logging.getLogger(__name__)

SBERT_PREFIX = "sbert/"

# Models that define a "query" prompt for asymmetric retrieval.
_QUERY_PROMPT_MODELS = {"nomic-ai/nomic-embed-code", "nomic-ai/CodeRankEmbed"}

# Type alias
Embedder = Union["SentenceTransformerEmbedder", "LiteLLMEmbedder"]

# Context keys
EMBEDDER = coco.ContextKey[Embedder]("embedder")
SQLITE_DB = coco.ContextKey[sqlite.ManagedConnection]("index_db", tracked=False)
CODEBASE_DIR = coco.ContextKey[pathlib.Path]("codebase", tracked=False)

# Module-level variable — set by daemon at startup (needed for CodeChunk annotation).
embedder: Embedder | None = None

# Query prompt name — set alongside embedder by create_embedder().
query_prompt_name: str | None = None


class _TestEmbedder:
    """Deterministic local embedder for tests.

    Keeps daemon and CLI tests hermetic without pulling large ML dependencies or
    hitting remote embedding APIs.
    """

    _vocabulary = (
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
    )

    async def embed(
        self,
        text: str,
        is_query: bool | str | None = None,
        prompt_name: str | None = None,
    ) -> NDArray[np.float32]:
        del is_query, prompt_name
        lowered = text.lower()
        vector = np.array(
            [float(lowered.count(token)) for token in self._vocabulary],
            dtype="float32",
        )
        if not vector.any():
            vector[0] = 1.0
        norm = np.linalg.norm(vector)
        if norm:
            vector = vector / norm
        return vector


def create_embedder(settings: EmbeddingSettings) -> Embedder:
    """Create and return an embedder instance based on settings.

    Also sets the module-level ``embedder`` and ``query_prompt_name`` variables.
    """
    global embedder, query_prompt_name

    if settings.provider == "test":
        query_prompt_name = None
        instance = _TestEmbedder()
        logger.info("Embedding model (test): %s", settings.model)
    elif settings.provider == "sentence-transformers":
        from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder

        model_name = settings.model
        # Strip the legacy sbert/ prefix if present
        if model_name.startswith(SBERT_PREFIX):
            model_name = model_name[len(SBERT_PREFIX) :]

        query_prompt_name = "query" if model_name in _QUERY_PROMPT_MODELS else None
        instance: Embedder = SentenceTransformerEmbedder(
            model_name,
            device=settings.device,
            trust_remote_code=True,
        )
        logger.info("Embedding model: %s | device: %s", settings.model, settings.device)
    else:
        from cocoindex.ops.litellm import LiteLLMEmbedder

        embedder_kwargs: dict[str, str] = {}
        if settings.api_base is not None:
            embedder_kwargs["api_base"] = settings.api_base
        embedder_kwargs["encoding_format"] = settings.encoding_format
        instance = LiteLLMEmbedder(settings.model, **embedder_kwargs)
        query_prompt_name = None
        logger.info(
            "Embedding model (LiteLLM): %s | api_base: %s | encoding_format: %s",
            settings.model,
            settings.api_base,
            settings.encoding_format,
        )

    embedder = instance
    return instance


@dataclass
class CodeChunk:
    """Schema for storing code chunks in SQLite."""

    id: int
    file_path: str
    language: str
    content: str
    start_line: int
    end_line: int
    embedding: Annotated[NDArray, embedder]  # type: ignore[type-arg]
