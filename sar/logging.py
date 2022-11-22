from rich.console import Console
from rich.theme import Theme
from rich.traceback import install

install()

# Themes
LogTheme = Theme({
    'info': 'blue',
    'warn': 'magenta',
    'danger': 'bold red',
    'success': 'green',
})

console = Console(theme=LogTheme)