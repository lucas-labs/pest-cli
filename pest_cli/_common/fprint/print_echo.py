from typing import IO, Any, Optional

from prompt_toolkit import HTML, print_formatted_text
from rich import print
from rich.markdown import Markdown

from .. import styles


def echo(
    message: Optional[Any] = None,
    file: Optional[IO[Any]] = None,
    nl: bool = True,
    err: bool = False,
    color: Optional[bool] = None,
) -> None:
    # ctx = get_current_context(silent=True)
    if isinstance(message, HTML):
        print_formatted_text(message, style=styles.default)
    elif isinstance(message, Markdown):
        print(message)
    else:
        print_formatted_text(HTML(message or ''), style=styles.default)
