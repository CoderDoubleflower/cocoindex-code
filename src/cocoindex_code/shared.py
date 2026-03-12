"""Shared singletons: config, embedder, and CocoIndex lifecycle."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Annotated

import cocoindex as coco
from cocoindex.connectors import sqlite
from cocoindex.connectors.localfs import FilePath, register_base_dir
from cocoindex.ops.litellm import LiteLLMEmbedder
from numpy.typing import NDArray

from .config import config

logger = logging.getLogger(__name__)

_embedder_kwargs: dict[str, str] = {}
if config.api_base is not None:
    _embedder_kwargs["api_base"] = config.api_base

embedder: LiteLLMEmbedder = LiteLLMEmbedder(config.embedding_model, **_embedder_kwargs)
query_prompt_name: str | None = None
logger.info(
    "Embedding model (remote API via LiteLLM): %s | api_base: %s",
    config.embedding_model,
    config.api_base,
)

# Context key for SQLite database (connection managed in lifespan)
SQLITE_DB = coco.ContextKey[sqlite.SqliteDatabase]("sqlite_db")
# Context key for codebase root directory (provided in lifespan)
CODEBASE_DIR = coco.ContextKey[FilePath]("codebase_dir")


@coco.lifespan
def coco_lifespan(builder: coco.EnvironmentBuilder) -> Iterator[None]:
    """Set up database connection."""
    # Ensure index directory exists
    config.index_dir.mkdir(parents=True, exist_ok=True)

    # Set CocoIndex state database path
    builder.settings.db_path = config.cocoindex_db_path

    # Provide codebase root directory to environment
    builder.provide(CODEBASE_DIR, register_base_dir("codebase", config.codebase_root_path))

    # Connect to SQLite with vector extension
    conn = sqlite.connect(str(config.target_sqlite_db_path), load_vec="auto")
    builder.provide(SQLITE_DB, sqlite.register_db("index_db", conn))

    yield

    conn.close()


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
