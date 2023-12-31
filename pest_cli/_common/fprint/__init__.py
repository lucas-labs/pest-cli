import json as jsonpy
from typing import Type, Union

import pygments
import yaml as yamlpy
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit.styles import Style
from pygments.lexer import Lexer
from pygments.lexers.data import JsonLexer, YamlLexer

from .. import styles
from ..components.component import Component
from .print_echo import echo as echo
from .print_tree import tree as tree


def _print_highlighted(text: str, style: Style, lexer: Lexer) -> None:
    tokens = list(pygments.lex(text, lexer=lexer))
    print_formatted_text(PygmentsTokens(tokens), style=style)


def json(object: object, indent: int = 2, style: Style = styles.json) -> None:
    code = jsonpy.dumps(object, indent=indent)
    _print_highlighted(code, style, JsonLexer())


def yaml(object: object, indent: int = 2, style: Style = styles.yaml) -> None:
    code = yamlpy.dump(object, indent=indent)
    _print_highlighted(code, style, YamlLexer())


def component(comp: Union[Component, Type[Component]]) -> None:
    if isinstance(comp, Type):
        comp = comp()

    print_formatted_text(comp.element, style=comp.style)
