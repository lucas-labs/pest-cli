from typing import final

from prompt_toolkit.styles import Style

from pest_cli._common import styles

from .component import Component


@final
class Logo(Component):
    @property
    def style(self) -> Style:
        return styles.default

    def render(self) -> str:
        logo = [
            '',
            '<sec> ▄▄▄▄  ▄▄▄▄ </sec>  <brand>   ▄▄▄▄▄    ▄▄▄▄   ▄▄▄▄    █   </brand>',
            '<sec> █▄▄█▄▄█▄▄█ </sec>  <brand>   █    █  █    █ █    ▀ ▀▀█▀▀▀</brand>',
            '<sec>▁▄████████▄▁</sec>  <brand>   █    █ █ ▀▀▀▀   ▀▀▀▀▀▄  █   </brand>',
            '<sec>━██<bg-brand>  </bg-brand>██<bg-brand>  </bg-brand>██━</sec>  <brand>   █▀▀▀▀  ▀▄▄▄▄   ▀▄▄▄▄▄▀  ▀▄▄ </brand>',  # noqa: E501
            '<sec>▔▀████████▀▔</sec>  <brand>   ▀                           </brand>',
            '<sec>   ▚▚  ▞▞   </sec>  <brand>                               </brand>',
            '\n',
        ]

        return '\n'.join(logo)
