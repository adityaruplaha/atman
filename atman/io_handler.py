from colorama import Fore, Style

import pypager
import os

def error(arg0, *args, **kwargs):
    return print(Fore.RED + Style.BRIGHT + arg0, *args, **kwargs)

def warning(arg0, *args, **kwargs):
    return print(Fore.YELLOW + arg0, *args, **kwargs)

def success(arg0, *args, **kwargs):
    return print(Fore.GREEN + arg0, *args, **kwargs)

def prompt(arg0, *args, **kwargs):
    print(Fore.BLUE + arg0, *args, **kwargs, end='')
    return input()

def page_text_from_file(filename):
    root_path = os.path.dirname(os.path.abspath(__file__))
    source = pypager.pager.FileSource(filename=root_path+"/texts/"+filename)
    p = pypager.pager.Pager()
    p.add_source(source)
    p.run()