from pathlib import Path
from typing import cast

import click
from InquirerPy.utils import get_style

from pest_cli import cli
from pest_cli._common import styles

from ....engine.schema import Schema
from ... import Group
from .subcommand import get_callback

CWD = Path.cwd()
SCHEMATICS_PATH = Path(Path(__file__).parent, './../../../', 'schematics').resolve()

SCHEMATICS = [
    'application',
]


generate = Group(
    name='generate',
    aliases=['g'],
)


for name in SCHEMATICS:
    SCHEMA_PATH = Path(SCHEMATICS_PATH, name, 'schema.yaml')
    inq_style = get_style(styles.inquirer)
    schema: Schema = cast(Schema, Schema.from_yaml_file(str(SCHEMA_PATH)))

    cb = get_callback(name, SCHEMA_PATH, CWD, schema)

    cmd = cli.Command(
        name=schema.name,
        aliases=schema.aliases,
        callback=cb,
        help=cb.__doc__,
    )

    for prop_name, prop in schema.properties.items():
        if prop.type == 'argument':
            default_val = (
                prop.prompt if prop.default is None and prop.prompt is not None else prop.default
            )

            cmd.params.append(
                cli.Argument(
                    param_decls=[prop_name],
                    default=default_val,
                )
            )
            pass
        elif prop.type == 'option':
            default_val = (
                prop.prompt if prop.default is None and prop.prompt is not None else prop.default
            )

            args = {}
            if default_val is not None:
                args['default'] = default_val

            cmd.params.append(
                cli.Option(
                    param_decls=[f'--{prop_name}'],
                    type=(
                        click.Choice(prop.prompt.choices)
                        if prop.prompt and prop.prompt.kind == 'choice'
                        else str
                    ),
                    help=prop.description,
                    **args,
                )
            )

    # append --yes (-y) option which will be available for all schematics
    # and will skip all prompts (and make the command raise if any required
    # argument/option is missing)
    cmd.params.append(
        cli.Option(
            param_decls=['--yes', '-y'],
            is_flag=True,
            help='skip all prompts, including confirmations',
        )
    )

    # append --cwd option which will be available for all schematics
    # and will allow the user to specify the root directory for the
    # generated files
    cmd.params.append(
        cli.Option(
            param_decls=['--cwd'],
            type=click.Path(exists=True, file_okay=False, dir_okay=True),
            default=str(CWD),
            help='the root directory for the generated files (default: current directory)',
        )
    )

    generate.add_command(cmd)
