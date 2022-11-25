from parser import Parser
from models.commands import Command

logixables = []
parser = Parser()

def execute_command(subcommands: list):
    command_keyword = subcommands[0]
    if command_keyword == Command.DEFINE:
        logixable = parser.parse_function_signature(subcommands[1])
        logixable.definition = LogixableD
    elif command_keyword == Command.HELP:
        print("DEFINE Syntax: 'DEFINE func_name(arguments): "expression"'\nAllowed operators: '&', '!', '|'.")
        # TODO: define other commands

def main():
    print("Welcome to Logixables! Please, enter a valid command to get started!\n")
    print("Valid commands are: DEFINE, SOLVE, FIND, ALL, VISUALIZE, HELP, EXIT")

    while inp := input() != 'EXIT':
        subcommands = parser.parse_command(inp)
        # always has at least 2 commands
        execute_command(subcommands)
        print("-----------------\n")        

if __name__ == "__main__":
    main()