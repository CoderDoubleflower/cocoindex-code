from __future__ import annotations

import io
import os

from cocoindex_code.progress import TerminalProgress


class FakeTTY(io.StringIO):
    def isatty(self) -> bool:
        return True


def test_terminal_progress_uses_single_line_for_tty(monkeypatch) -> None:
    monkeypatch.setattr(
        "shutil.get_terminal_size",
        lambda fallback: os.terminal_size(fallback),
    )
    stream = FakeTTY()
    progress = TerminalProgress(stream)

    progress.emit("Indexing... 1s elapsed, 1 files, 10 chunks")
    progress.emit("Indexing... 2s elapsed, 2 files, 20 chunks")
    progress.finish()

    assert stream.getvalue() == (
        "\rIndexing... 1s elapsed, 1 files, 10 chunks"
        "\rIndexing... 2s elapsed, 2 files, 20 chunks\n"
    )


def test_terminal_progress_falls_back_to_line_output_for_non_tty() -> None:
    stream = io.StringIO()
    progress = TerminalProgress(stream)

    progress.emit("Indexing...")
    progress.emit("Indexing... 1s elapsed")
    progress.finish()

    assert stream.getvalue() == "Indexing...\nIndexing... 1s elapsed\n"


def test_terminal_progress_clears_previous_tty_content(monkeypatch) -> None:
    monkeypatch.setattr(
        "shutil.get_terminal_size",
        lambda fallback: os.terminal_size(fallback),
    )
    stream = FakeTTY()
    progress = TerminalProgress(stream)
    first = "Indexing... 10s elapsed, 10 files, 100 chunks"
    second = "Indexing... done"

    progress.emit(first)
    progress.emit(second)
    progress.finish()

    expected = f"\r{first}\r{second.ljust(len(first))}\n"
    assert stream.getvalue() == expected
