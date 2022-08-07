from colorama import Back, Fore, Style

DELETE_COLOR = Back.RED + Fore.BLACK
INSERT_COLOR = Back.GREEN + Fore.BLACK
REPLACE_COLOR = Back.BLUE + Fore.BLACK

NEWLINE = "\n"

LIGHT_MODE = False
if (LIGHT_MODE):
    DELETE_COLOR = Back.RED + Fore.WHITE
    INSERT_COLOR = Back.GREEN + Fore.WHITE
    REPLACE_COLOR = Back.BLUE + Fore.WHITE

def print_normal(msg: str):
    print(msg, end="")

def insert(msg: str) -> str:
    lines = []
    for line in msg.split(NEWLINE):
        content = INSERT_COLOR + line + Style.RESET_ALL
        lines.append(content)
    return NEWLINE.join(lines)

def print_insert(msg: str):
    print(insert(msg), end="")

def delete(msg: str) -> str:
    lines = []
    for line in msg.split(NEWLINE):
        content = DELETE_COLOR + line + Style.RESET_ALL
        lines.append(content)
    return NEWLINE.join(lines)

def print_delete(msg: str):
    print(delete(msg), end="")

def replace(msg: str) -> str:
    lines = []
    for line in msg.split(NEWLINE):
        content = REPLACE_COLOR + line + Style.RESET_ALL
        lines.append(content)
    return NEWLINE.join(lines)

def print_replace(msg: str):
    print(replace(msg), end="")
