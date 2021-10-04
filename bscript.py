import sys, json
from BScript import (
    execute,
    __version__,
    BS_object,
    flatten,
    BS_function,
    BS_async_function,
)
from pyjsparser import parse
import os
import traceback


def get_item(liste, i):
    print(liste)
    return liste[int(i)]


class debug(object):
    @staticmethod
    def type(*args):

        for arg in args:
            print(type(arg))

    @staticmethod
    def type_iterators(*args):
        for arg in flatten(args):
            print(type(arg))

    @staticmethod
    def type_iterators_val(*args):
        for arg in flatten(args):
            print(arg, type(arg))

    
    @staticmethod
    def log(*args,**kwargs):
        print(args)
        print(kwargs)
class console:
    text = "selami"

    @staticmethod
    def log(*args):
        print(*args)

import random
variables = {
    "exit": sys.exit,
    "type": type,
    "console": console(),
    "format": lambda text, **kwargs: text.format(**kwargs),
    "get_item": get_item,
    "int": int,
    "test_dict": [1, 2, 3, 4],
    "debug": debug(),
    "dict":dict,
    "print":print,
    "random":random,
    "json":json
}

executor = execute.BS_executor(variables=variables, sandbox_mode=False,use_reserved=True,max_loop=float("inf"))


def find_start_curly_brackets(terminal_input):
    for line in terminal_input[::-1]:
        result = False
        if line == "{":
            result = True
        elif line == " ":
            pass
        elif line == "\n":
            pass
        else:
            result = False
        while result and not find_end_curly_brackets(terminal_input):
            extra_input = input("... ")

            terminal_input += "\n" + find_start_curly_brackets(extra_input)
        return terminal_input


def find_end_curly_brackets(terminal_input):
    for line in terminal_input[::-1]:

        if line == "}":
            return True
        elif line == " ":
            pass
        elif line == "\n":
            pass
        else:
            return False


def terminal():
    print(f"BScript {__version__}")
    debug = False
    while 1:
        terminal_input = input(">>> ")
        if not terminal_input:
            continue
        elif terminal_input == "on debug mode .":
            debug = True
            print("Debug mode is enabled")
        elif terminal_input == "off debug mode .":
            debug = True
            print("Debug mode is disabled")
        terminal_input = find_start_curly_brackets(terminal_input)
        try:
            parsed = parse(terminal_input)
            executor(parsed, True)
            if debug:
                print(parsed)
        except Exception as e:
            traceback.print_exc()


def main(filename=None, lang="en"):

    if filename:
        with open(filename, "r", encoding="utf8") as f:
            read = f.read()
            with open("test.json", "w") as j:
                json.dump(parse(read), j, indent=2)

        executor(parse(read))
        # print(executor.variables.__globals__)
    else:
        terminal()


if __name__ == "__main__":
    main(*sys.argv[1:])
