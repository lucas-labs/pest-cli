from gettext import gettext as _
from typing import Any, Callable, List, Optional, Tuple, Type, Union

import click
from click.core import Context
from click.decorators import _AnyCallable

from .._common.fprint import echo
from ..engine.schema import Prompt
from .help_formatter import PestHelpFormatter

# a little bit of monkey patching, just because I can.
# Don't do this at home and don't tell anyone I did this 🤫
setattr(click.core, 'echo', echo)
setattr(click.exceptions, 'echo', echo)
setattr(click, 'echo', echo)
click.Context.formatter_class = PestHelpFormatter


def format_options(self: click.Command, ctx: Context, formatter: click.HelpFormatter) -> None:
    opts = []
    for param in self.get_params(ctx):
        rv = param.get_help_record(ctx)
        if rv is not None:
            zero = f'<ansiwhite>{rv[0]}</ansiwhite>'
            rv = (zero, rv[1])
            opts.append(rv)

    if opts:
        with formatter.section(_('Options')):
            formatter.write_dl(opts)


def format_help(self: click.Command, ctx: Context, formatter: click.HelpFormatter) -> None:
    self.format_usage(ctx, formatter)
    self.format_help_text(ctx, formatter)
    self.format_options(ctx, formatter)
    self.format_epilog(ctx, formatter)


class Argument(click.Argument):
    def type_cast_value(self, ctx: Context, value: Any) -> Any:
        if isinstance(value, Prompt):
            return value

        return super().type_cast_value(ctx, value)


class Option(click.Option):
    def type_cast_value(self, ctx: Context, value: Any) -> Any:
        if isinstance(value, Prompt):
            return value

        return super().type_cast_value(ctx, value)


class Command(click.Command):
    def __init__(self, *args: Any, aliases: Optional[list] = None, **kwargs: Any):
        self.aliases = aliases
        super().__init__(*args, **kwargs)

    format_options = format_options

    def get_help_option(self, ctx: Context) -> Optional['Option']:
        """Returns the help option object."""
        help_options = self.get_help_option_names(ctx)

        if not help_options or not self.add_help_option:
            return None

        def show_help(ctx: Context, param: click.Parameter, value: str) -> None:
            if value and not ctx.resilient_parsing:
                echo(ctx.get_help(), color=ctx.color)
                ctx.exit()

        return Option(
            help_options,
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=show_help,
            help=_('show this message and exit.'),
        )


class Group(click.Group):
    command_class: Type[click.Command] = Command

    @property
    def group_class(self) -> Type[click.Group]:
        return self.__class__

    def __init__(self, *args: Any, aliases: Optional[list] = None, **kwargs: Any):
        self.aliases = aliases
        super().__init__(*args, **kwargs)

    def format_options(self, ctx: Context, formatter: click.HelpFormatter) -> None:
        format_options(self, ctx, formatter)
        self.format_commands(ctx, formatter)

    def format_commands(self, ctx: Context, formatter: click.HelpFormatter) -> None:
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue
            if cmd.hidden:
                continue

            commands.append((subcommand, cmd))

        # allow for 3 times the default spacing
        if len(commands):
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

            rows = []
            for subcommand, cmd in commands:
                help = cmd.get_short_help_str(limit)
                command_aliases = getattr(cmd, 'aliases', [])
                subcommand = f'<ansiwhite>{subcommand}</ansiwhite>'
                subcommand = (
                    (f'{subcommand}' f'|{", ".join(command_aliases)}' if command_aliases else '')
                    if command_aliases
                    else subcommand
                )

                rows.append((subcommand, help))

            if rows:
                with formatter.section(_('Commands')):
                    formatter.write_dl(rows)

    def format_help(self, ctx: Context, formatter: click.HelpFormatter) -> None:
        format_help(self, ctx, formatter)

    def command(
        self, *args: Any, aliases: List[str] = [], **kwargs: Any
    ) -> Union[Callable[[Callable[..., Any]], click.Command], click.Command]:
        return super().command(*args, aliases=aliases, **kwargs)

    def get_command(self, ctx: Context, cmd_name: str) -> Optional[click.Command]:
        command = self.commands.get(cmd_name)
        if command is not None:
            return command

        # let's try by alias
        command = next(
            (
                command
                for command in self.commands.values()
                if cmd_name in getattr(command, 'aliases', [])
            ),
            None,
        )

        return command

    def resolve_command(
        self, ctx: Context, args: List[str]
    ) -> Tuple[Optional[str], Optional[click.Command], List[str]]:
        return super().resolve_command(ctx, args)

    def get_help_option(self, ctx: Context) -> Optional['Option']:
        """Returns the help option object."""
        help_options = self.get_help_option_names(ctx)

        if not help_options or not self.add_help_option:
            return None

        def show_help(ctx: Context, param: click.Parameter, value: str) -> None:
            if value and not ctx.resilient_parsing:
                echo(ctx.get_help(), color=ctx.color)
                ctx.exit()

        return Option(
            help_options,
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=show_help,
            help=_('show this message and exit'),
        )


def command(
    name: Optional[Union[_AnyCallable, str]] = None,
    aliases: List[str] = [],
    **attrs: Any,
) -> Union[Command, Callable[[_AnyCallable], Command]]:
    return click.command(name, cls=Command, aliases=aliases, **attrs)  # type: ignore


def group(
    name: Union[str, _AnyCallable, None] = None,
    aliases: List[str] = [],
    **attrs: Any,
) -> Callable:
    return click.group(name, cls=Group, aliases=aliases, **attrs)  # type: ignore
