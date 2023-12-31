from enum import Flag, auto
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Protocol, Union, runtime_checkable

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

Tree: TypeAlias = Mapping[str, Union[Dict[str, 'FileProtocol'], 'FileProtocol']]
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
    def checksum(self) -> Optional[str]:
        ...

    @property
    def exists(self) -> bool:
        ...

    @property
    def compiled_content(self) -> Optional[str]:
        ...

    @property
    def compiled_path(self) -> Optional[Path]:
        ...

    @property
    def compiled_rel_path(self) -> Optional[Path]:
        ...

    @property
    def compiled_checksum(self) -> Optional[str]:
        ...


@runtime_checkable
class FileDiffProtocol(FileProtocol, Protocol):
    @property
    def mode(self) -> DiffMode:
        ...
