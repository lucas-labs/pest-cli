import os
from pathlib import Path

from ...._common.fprint.print_echo import echo
from ....engine.file.file import FlatFileTree


def generate_schematic_files(files: FlatFileTree, root: Path) -> None:
    """for each file in the file tree, write the file to disk

    warn: this function overrides files if they already exist
    """

    for _, file in files.tree().items():
        path = file.compiled_rel_path
        content = file.compiled_content

        if path is None or content is None:
            echo(f'<brand>WARNING</brand>: skipping file: {path}, no content or write path')
            continue

        final_path = root / path
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(final_path, 'w', encoding='utf-8') as f:
            f.write(content)
