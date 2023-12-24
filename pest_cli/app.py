# from InquirerPy.resolver import prompt
# from InquirerPy.utils import InquirerPyQuestions


from pest_cli._common import fprint

from . import cli as pestcli
from ._common.components.logo import Logo
from .cli.commands.generate import generate


@pestcli.group
def app() -> None:
    pass


def cli() -> None:
    fprint.component(Logo)
    app.add_command(generate)

    try:
        app()
    except SystemExit as se:
        if se.code != 0:
            raise se
    finally:
        print('')


if __name__ == '__main__':
    cli()
