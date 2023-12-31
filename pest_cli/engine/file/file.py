from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping, Optional

import jinja2

from ..._common.fprint.print_echo import echo
from .types import DiffMode, FileProtocol


def compile_jinja(template: str, ctx: Mapping[str, Any]) -> str:
    return jinja2.Template(template, keep_trailing_newline=True, trim_blocks=False).render(**ctx)


@dataclass
class File:
    """concrete class for the representation of a schematic file"""

    name: str = field(init=False)
    rel_path: Path
    path: Path
    __size: int = field(init=False)
    __type: str = field(init=False)
    __content: str = field(init=False)
    __checksum: Optional[str] = field(init=False)
    __exists: bool = field(init=False, default=False)
    __compiled_content: Optional[str] = field(init=False, default=None)
    __compiled_path: Optional[Path] = field(init=False, default=None)
    __compiled_rel_path: Optional[Path] = field(init=False, default=None)
    __compiled_checksum: Optional[str] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self.name = self.path.name
        self.__type = self.path.suffix

        if self.path.exists():
            self.__size = self.path.stat().st_size
            self.content = self.path.read_text(encoding='utf8')
        else:
            self.__size = 0
            self.__content = ''
            self.__exists = False
            self.__checksum = None

    @classmethod
    def from_path(cls, path: Path, root: Path = Path.cwd()) -> 'File':
        """create a File object from a path"""
        if path.is_absolute():
            rel_path = path.relative_to(root)
        else:
            rel_path = path

        return cls(path=path, rel_path=rel_path)

    @classmethod
    def from_paths(cls, paths: List[Path], root: Path = Path.cwd()) -> Dict[Path, 'File']:
        """create a dictionary of File objects from a list of paths"""
        return {path: File.from_path(path) for path in paths}

    def refresh(self) -> None:
        self.__post_init__()

    @property
    def size(self) -> int:
        return self.__size

    @property
    def size_str(self) -> str:
        file_size_str = ''
        if self.__size < 1000:
            file_size_str = f'{self.__size}b'
        elif self.__size < 1000000:
            file_size_str = f'{self.__size / 1000}kb'
        elif self.__size < 1000000000:
            file_size_str = f'{self.__size / 1000000}mb'
        elif self.__size < 1000000000000:
            file_size_str = f'{self.__size / 1000000000}gb'
        elif self.__size < 1000000000000000:
            file_size_str = f'{self.__size / 1000000000000}tb'
        else:
            file_size_str = f'{self.__size / 1000000000000000}pb'

        return file_size_str

    @property
    def type(self) -> str:
        return self.__type

    @property
    def content(self) -> str:
        return self.__content

    @content.setter
    def content(self, content: str) -> None:
        self.__content = content
        self.__checksum = sha256(self.__content.encode()).hexdigest()
        self.__exists = True

    @property
    def checksum(self) -> Optional[str]:
        return self.__checksum

    @property
    def exists(self) -> bool:
        return self.__exists

    @property
    def compiled_content(self) -> Optional[str]:
        return self.__compiled_content

    @compiled_content.setter
    def compiled_content(self, content: Optional[str]) -> None:
        self.__compiled_content = content

    @property
    def compiled_path(self) -> Optional[Path]:
        return self.__compiled_path

    @compiled_path.setter
    def compiled_path(self, path: Optional[Path]) -> None:
        self.__compiled_path = path

    @property
    def compiled_rel_path(self) -> Optional[Path]:
        return self.__compiled_rel_path

    @compiled_rel_path.setter
    def compiled_rel_path(self, path: Optional[Path]) -> None:
        self.__compiled_rel_path = path

    @property
    def compiled_checksum(self) -> Optional[str]:
        return self.__compiled_checksum

    @compiled_checksum.setter
    def compiled_checksum(self, checksum: Optional[str]) -> None:
        self.__compiled_checksum = checksum

    def compile(self, ctx: Mapping[str, Any]) -> None:
        self.__compiled_content = compile_jinja(str(self.__content), ctx)
        self.__compiled_path = Path(compile_jinja(str(self.path).replace('.jinja', ''), ctx))
        self.__compiled_rel_path = Path(
            compile_jinja(str(self.rel_path).replace('.jinja', ''), ctx)
        )
        self.__compiled_checksum = sha256(self.__compiled_content.encode()).hexdigest()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, File):
            return False

        self_rel_path = str(self.compiled_rel_path or self.rel_path)
        other_rel_path = str(other.compiled_rel_path or other.rel_path)

        self_checksum = self.compiled_checksum or self.checksum
        other_checksum = other.compiled_checksum or other.checksum

        return str(self_rel_path) == str(other_rel_path) and self_checksum == other_checksum


@dataclass
class DiffFile(File):
    mode: DiffMode

    @classmethod
    def from_file(cls, file: FileProtocol, mode: DiffMode = DiffMode.NEW) -> 'DiffFile':
        obj = cls(path=file.path, rel_path=file.rel_path, mode=mode)
        obj.compiled_content = file.compiled_content
        obj.compiled_path = file.compiled_path
        obj.compiled_rel_path = file.compiled_rel_path
        obj.compiled_checksum = file.compiled_checksum

        return obj


IGNORED = ['.git', '.vscode', '.idea', '__pycache__', '.venv', '.pytest_cache', '.nox', 'dist']


class FlatFileTree:
    __tree: MutableMapping[Path, FileProtocol] = {}

    def __init__(
        self,
        path: Path = Path.cwd(),
        root_path: Optional[Path] = None,
    ) -> None:
        self.path = path
        self.root_path = root_path or path
        self.__tree = self.__flat_tree()

    def compile(self, ctx: Dict[str, Any]) -> None:
        if ctx:
            current = list(self.__tree.items())

            for path, file in current:
                # update path with compiled jinja template
                new_path = Path(compile_jinja(str(path).replace('.jinja', ''), ctx))
                file.compile(ctx)
                self.__tree[new_path] = file

                # if new path is different from old path, delete old path
                if new_path != path:
                    del self.__tree[path]

    def merge(self, other: 'FlatFileTree') -> None:
        self.__tree.update(other.tree())

    def __flat_tree(self) -> Dict[Path, FileProtocol]:
        tree: Dict[Path, FileProtocol] = {}

        for entry in self.path.iterdir():
            if entry.name in IGNORED:
                continue

            if entry.is_file():
                try:
                    tree[entry.relative_to(self.root_path)] = File(
                        path=entry, rel_path=entry.relative_to(self.root_path)
                    )
                except UnicodeDecodeError as e:
                    echo(f'<brand>[warn]</brand> {entry.relative_to(self.root_path)}: {e}')
            elif entry.is_dir():
                tree.update(FlatFileTree(entry, self.root_path).tree())

        return tree

    def get(self, path: Path) -> Optional[FileProtocol]:
        return self.__tree.get(path)

    def tree(self) -> MutableMapping[Path, FileProtocol]:
        return self.__tree

    def __len__(self) -> int:
        return len(self.__tree)

    def diff(self, other: 'FlatFileTree') -> 'FlatFileTree':
        diff_tree = FlatFileTree()
        diff_tree.__tree = self.__diff_tree(other)  # type: ignore
        return diff_tree

    def would_override(self) -> bool:
        result = any(
            isinstance(file, DiffFile) and file.mode == DiffMode.OVERRIDE
            for file in self.__tree.values()
        )

        return result

    def __diff_tree(self, other: 'FlatFileTree') -> Dict[Path, DiffFile]:
        diff_tree: Dict[Path, DiffFile] = {}

        for path, file in self.__tree.items():
            other_file = other.get(path)
            if other_file is None:
                # if the file does not exist in the other tree, it is new
                diff_tree[path] = DiffFile.from_file(file, DiffMode.NEW)
            elif file != other_file:
                # if the file exists in the other tree but is different, it is modified
                diff_tree[path] = DiffFile.from_file(file, DiffMode.OVERRIDE)

        return diff_tree
