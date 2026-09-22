"""Typed dictionary export interface."""

from typing import Protocol


class SupportsAsDict[T](Protocol):
    """An object whose asdict() result has type T."""

    def asdict(self) -> T: ...
