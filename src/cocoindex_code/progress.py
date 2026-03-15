"""Terminal progress rendering helpers."""

from __future__ import annotations

import shutil
import sys
from typing import TextIO


class TerminalProgress:
    """Render progress updates on a single terminal line when possible."""

    def __init__(self, stream: TextIO | None = None) -> None:
        self._stream = sys.stdout if stream is None else stream
        self._interactive = self._stream.isatty()
        self._last_width = 0
        self._active = False

    def emit(self, message: str) -> None:
        """Emit a progress update."""
        if not self._interactive:
            self._stream.write(f"{message}\n")
            self._stream.flush()
            return

        line = self._truncate(message)
        width = max(self._last_width, len(line))
        self._stream.write("\r")
        self._stream.write(line.ljust(width))
        self._stream.flush()
        self._last_width = width
        self._active = True

    def finish(self) -> None:
        """Finish the current progress line."""
        if self._interactive and self._active:
            self._stream.write("\n")
            self._stream.flush()
        self._active = False

    def _truncate(self, message: str) -> str:
        columns = shutil.get_terminal_size(fallback=(100, 24)).columns
        width = max(columns - 1, 20)
        if len(message) <= width:
            return message
        if width <= 3:
            return message[:width]
        return f"{message[: width - 3]}..."
