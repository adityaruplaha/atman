from colorama import Fore, Style, init

def error(arg0, *args, **kwargs):
    return print(Fore.RED + Style.BRIGHT + arg0, *args, **kwargs)

def warning(arg0, *args, **kwargs):
    return print(Fore.YELLOW + arg0, *args, **kwargs)

def success(arg0, *args, **kwargs):
    return print(Fore.GREEN + arg0, *args, **kwargs)

def prompt(arg0, *args, **kwargs):
    print(Fore.BLUE + arg0, *args, **kwargs, end='')
    return input()