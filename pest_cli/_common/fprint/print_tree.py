from pathlib import Path
from typing import Mapping, TypedDict, Unpack

from ...engine.file.types import DiffMode, FileDiffProtocol, FileProtocol, Tree
from . import at, fg
from .print_echo import echo


class PrintTreeOptions(TypedDict, total=False):
    highlight_extensions: list[str]


def build_tree(files: Mapping[Path, FileProtocol]) -> Tree:
    tree = {}
    for path in sorted(files.keys()):
        parts = path.parts
        current_level = tree
        for part in parts[:-1]:
            current_level = current_level.setdefault(part, {})
        current_level[parts[-1]] = files[path]
    return tree


def show_as_tree(
    files: Mapping[Path, FileProtocol] | list[FileProtocol],
    root: str | Path = '.',
    indent: str = '',
    with_extras: bool = True,
    **kwargs: Unpack[PrintTreeOptions],
) -> None:
    if isinstance(files, list):
        files = {file.path: file for file in files}

    echo(fg.brand(at.b(root)))
    tree = build_tree(files)
    display_tree(tree, indent, with_extras, **kwargs)


def get_indent(is_last: bool, indent: str) -> tuple[str, str]:
    if is_last:
        line = '╰── '
        new_indent = indent + '    '
    else:
        line = '├── '
        new_indent = indent + '│   '

    return line, new_indent


def display_tree(
    tree: Tree,
    indent: str = '',
    with_extras: bool = True,
    **kwargs: Unpack[PrintTreeOptions],
) -> None:
    sorted_items = sorted(tree.items(), key=lambda x: (isinstance(x[1], dict), x))
    highlight_extensions = kwargs.get('highlight_extensions', [])

    for i, (key, value) in enumerate(sorted_items):
        is_dir = isinstance(value, dict)
        line, new_indent = get_indent(i == len(sorted_items) - 1, indent)

        should_highlight = not is_dir and any(key.endswith(ext) for ext in highlight_extensions)

        extra = ''

        if not is_dir and with_extras:
            if isinstance(value, FileDiffProtocol):
                if value.mode == DiffMode.OVERRIDE:
                    extra += '<red> ⇐ overrides existing file</red>'

        # color = fg.brand if is_dir else fg.noop
        color = fg.brand if is_dir else fg.green if should_highlight else fg.noop
        attrs = at.b if is_dir else at.noop
        label = color(attrs(key))

        echo(f'{indent}{line}{label}{extra}')

        if value and is_dir:
            display_tree(value, new_indent, with_extras, **kwargs)


def tree(
    files: Mapping[Path, FileProtocol] | list[FileProtocol],
    root: str | Path = '.',
    with_extras: bool = True,
    **kwargs: Unpack[PrintTreeOptions],
) -> None:
    show_as_tree(files, root, with_extras=with_extras, **kwargs)
