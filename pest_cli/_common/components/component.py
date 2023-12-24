from abc import ABC, abstractmethod

from prompt_toolkit import HTML
from prompt_toolkit.styles import Style


class Component(ABC):
    def __init__(self) -> None:
        self.name = self.__class__.__name__.lower()
        self.description = self.__doc__

    @property
    def element(self) -> HTML:
        return HTML(f'<{self.name}>{self.render()}</{self.name}>')

    @property
    def style(self) -> Style:
        return Style([])

    @abstractmethod
    def render(self) -> str:
        ...

    def __repr__(self) -> str:
        return f'{self.name}{self.description and f": {self.description}"}'

    def __str__(self) -> str:
        return self.element.__str__()
