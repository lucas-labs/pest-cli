from enum import Flag, auto
from pathlib import Path
from typing import Any, Mapping, Protocol, TypeAlias, Union, runtime_checkable

Tree: TypeAlias = Mapping[str, Union[dict[str, 'FileProtocol'], 'FileProtocol']]
'''Represents a directory tree'''


class DiffMode(Flag):
    NEW = auto()
    OVERRIDE = auto()


class FileProtocol(Protocol):
    """Protocol for the representation of a file"""

    def __eq__(self, other: object) -> bool:
        ...

    def compile(self, ctx: Mapping[str, Any]) -> None:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def rel_path(self) -> Path:
        ...

    @property
    def path(self) -> Path:
        ...

    @path.setter
    def path(self, path: Path) -> None:
        ...

    @property
    def size(self) -> int:
        ...

    @property
    def size_str(self) -> str:
        ...

    @property
    def type(self) -> str:
        ...

    @property
    def content(self) -> str:
        ...

    @content.setter
    def content(self, content: str) -> None:
        ...

    @property
    def checksum(self) -> str | None:
        ...

    @property
    def exists(self) -> bool:
        ...

    @property
    def compiled_content(self) -> str | None:
        ...

    @property
    def compiled_path(self) -> Path | None:
        ...

    @property
    def compiled_rel_path(self) -> Path | None:
        ...

    @property
    def compiled_checksum(self) -> str | None:
        ...


@runtime_checkable
class FileDiffProtocol(FileProtocol, Protocol):
    @property
    def mode(self) -> DiffMode:
        ...
