import click
import tomli

from pest_cli._common import fprint
from pest_cli._common.fprint.print_echo import echo

from . import cli as pestcli
from ._common.components.logo import Logo
from .cli.commands.generate import generate


@pestcli.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='show the version and exit')
def app(version: bool) -> None:
    """Pest CLI."""

    if version:
        with open('pyproject.toml', 'rb') as f:
            pyproject = tomli.load(f)

        echo(f'pest@<b><brand>v{pyproject["tool"]["poetry"]["version"]}</brand></b>')

        raise SystemExit(0)

    pass


app.add_command(generate)


def cli() -> None:
    fprint.component(Logo)

    try:
        app()  # type: ignore
    except SystemExit as se:
        if se.code != 0:
            raise se
    finally:
        print('')


if __name__ == '__main__':
    cli()
