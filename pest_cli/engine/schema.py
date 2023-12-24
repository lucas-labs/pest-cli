from dataclasses import dataclass, field
from typing import Literal, TypeAlias

from dataclass_wizard import YAMLWizard

PromptKind = Literal['text', 'choice']


@dataclass
class Prompt:
    label: str
    kind: PromptKind = field(default='text')
    choices: list[str] = field(default_factory=list)
    default: str | None = None


@dataclass
class Property:
    """Schema for all pest schematics description files"""

    data_type: str
    type: Literal['argument', 'option']
    description: str
    default: str | None = None
    prompt: Prompt | None = None
    alternative: bool = field(default=False)


Properties: TypeAlias = dict[str, Property]


@dataclass
class Schema(YAMLWizard):
    """Schema for all pest schematics description files"""

    name: str
    description: str | None = None
    aliases: list[str] = field(default_factory=list)
    properties: dict[str, Property] = field(default_factory=dict)
