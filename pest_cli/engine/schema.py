from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

from dataclass_wizard import YAMLWizard

PromptKind = Literal['text', 'choice']


@dataclass
class Prompt:
    label: str
    kind: PromptKind = field(default='text')
    choices: List[str] = field(default_factory=list)
    default: Optional[str] = None


@dataclass
class Property:
    """Schema for all pest schematics description files"""

    data_type: str
    type: Literal['argument', 'option']
    description: str
    default: Optional[str] = None
    prompt: Optional[Prompt] = None
    alternative: bool = field(default=False)


Properties: TypeAlias = Dict[str, Property]


@dataclass
class Schema(YAMLWizard):
    """Schema for all pest schematics description files"""

    name: str
    description: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    properties: Dict[str, Property] = field(default_factory=dict)
