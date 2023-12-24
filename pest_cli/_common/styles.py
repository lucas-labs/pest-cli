from prompt_toolkit.styles import Style

from . import theme

json = Style.from_dict(
    {
        'pygments.keyword': f'{theme.yellow} nobold',
        'pygments.name.tag': f'{theme.red} nobold',
        'pygments.literal.string.double': f'{theme.green}',
        'pygments.literal.number': f'{theme.yellow}',
    }
)

yaml = Style.from_dict(
    {
        'pygments.literal.string': f'{theme.green}',
        'pygments.name.tag': f'{theme.red} nobold',
        'pygments.literal.scalar.plain': f'{theme.green}',
    }
)


default = Style.from_dict(
    {
        'brand': f'{theme.brand}',
        'sec': f'{theme.secondary}',
        'blue': f'{theme.blue}',
        'green': f'{theme.green}',
        'red': f'{theme.red}',
        'yellow': f'{theme.yellow}',
        'purple': f'{theme.purple}',
        'cyan': f'{theme.cyan}',
        'pink': f'{theme.pink}',
        'white': f'{theme.white}',
        'black': f'{theme.black}',
        'bg-brand': f'bg:{theme.brand}',
        'bg-sec': f'bg:{theme.secondary}',
        'bg-blue': f'bg:{theme.blue}',
        'bg-green': f'bg:{theme.green}',
        'bg-red': f'bg:{theme.red}',
        'bg-yellow': f'bg:{theme.yellow}',
        'bg-purple': f'bg:{theme.purple}',
        'bg-cyan': f'bg:{theme.cyan}',
        'bg-pink': f'bg:{theme.pink}',
        'bg-white': f'bg:{theme.white}',
        'bg-black': f'bg:{theme.black}',
    }
)

inquirer = {
    'questionmark': f'{theme.secondary} bold',
    'answermark': f'{theme.brand} bold',
    'answer': f'{theme.brand}',
    'input': f'{theme.secondary} italic',
    'question': '',
    'answered_question': '',
    'instruction': '#abb2bf',
    'long_instruction': '#abb2bf',
    'pointer': f'{theme.brand}',
    'checkbox': f'{theme.brand}',
    'separator': '',
    'skipped': '#5c6370',
    'validator': '',
    'marker': '#e5c07b',
    'fuzzy_prompt': '#c678dd',
    'fuzzy_info': '#abb2bf',
    'fuzzy_border': '#4b5263',
    'fuzzy_match': '#c678dd',
    'spinner_pattern': '#e5c07b',
    'spinner_text': '',
}
