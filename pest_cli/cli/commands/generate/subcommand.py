from pathlib import Path
from typing import Any, Protocol

from InquirerPy.prompts.confirm import ConfirmPrompt as prompt_confirm
from InquirerPy.prompts.input import InputPrompt as prompt_text
from InquirerPy.prompts.list import ListPrompt as prompt_choice
from InquirerPy.utils import get_style

from pest_cli import cli
from pest_cli._common import fprint, styles
from pest_cli.cli.commands.generate import schematic

from ...._common.fprint.print_echo import echo
from ....engine.file.file import FlatFileTree
from ....engine.schema import Schema


class SubcommandCallback(Protocol):
    ...


def get_callback(
    name: str, schema_path: Path, working_dir: Path, schema: Schema
) -> SubcommandCallback:
    def cb(**kwargs: Any) -> None:
        # prompt for missing arguments
        kwargs = prompt_kwargs(**kwargs)

        # get alternative templates
        alternative_templates = get_alternative_template_names(schema, kwargs)

        alternative_diffs = []
        for template in alternative_templates:
            alternative_diffs.append(
                get_diff(
                    name=name,
                    root_path=working_dir,
                    schematics_path=schema_path,
                    ctx=kwargs,
                    alternative=template,
                )
            )

        diff = get_diff(
            name=name,
            root_path=working_dir,
            schematics_path=schema_path,
            ctx=kwargs,
        )

        for alternative_diff in alternative_diffs:
            diff.merge(alternative_diff)

        if len(diff) == 0:
            echo('<green>❱</green> All files are up to date =) Bye!')
            exit(0)

        echo('\n<brand>❱</brand> the following files will be generated: \n')
        fprint.tree(diff.tree(), '.', with_extras=True, highlight_extensions=['.py'])

        if diff.would_override():
            echo(
                '\n<brand><b>WARNING</b></brand>: <ansiwhite>this operation will '
                'override existing files</ansiwhite>'
            )

        print()

        if prompt_confirm(
            message='Generate files?',
            default=True,
            style=get_style(styles.inquirer),
        ).execute():
            echo('\n<brand>❱</brand> generating files...')

            schematic.generate_schematic_files(diff, working_dir)

            echo('<green>❱ done =)</green>')

    cb.__name__ = schema.name
    cb.__doc__ = schema.description or ''

    return cb


def prompt_kwargs(**kwargs: cli.Prompt) -> dict[str, Any]:
    inq_style = get_style(styles.inquirer)

    for key, prompt in kwargs.items():
        if isinstance(prompt, cli.Prompt):
            if prompt.kind == 'text':
                kwargs[key] = prompt_text(
                    message=prompt.label,
                    style=inq_style,
                ).execute()
            elif prompt.kind == 'choice':
                kwargs[key] = prompt_choice(
                    message=prompt.label, choices=prompt.choices, style=inq_style
                ).execute()

    return kwargs


def get_alternative_template_names(schema: Schema, kwards: dict[str, Any]) -> list[str]:
    alternative_keys = []
    for prop_name, prop in schema.properties.items():
        if prop.alternative:
            alternative_keys.append(prop_name.replace('-', '_'))

    alternative_template = []
    for key in alternative_keys:
        if key in kwards:
            alternative_template.append(f'template-[{kwards[key]}]')

    return alternative_template


def get_diff(
    name: str,
    root_path: Path,
    schematics_path: Path,
    ctx: dict[str, Any],
    alternative: str | None = None,
) -> FlatFileTree:
    schematic_files_path = Path(
        schematics_path.parent, 'template' if not alternative else alternative
    )
    if not schematic_files_path.exists():
        cli.echo(
            f'\n<red><b>[Error]</b></red> No template files found '
            f'for <ansiwhite>{name}</ansiwhite>'
        )
        exit(1)

    root = FlatFileTree(Path(root_path))
    schematics = FlatFileTree(schematic_files_path)
    schematics.compile(ctx=ctx)

    return schematics.diff(root)
