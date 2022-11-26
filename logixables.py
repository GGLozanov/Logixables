from parser import Parser
from models.commands import Command
from models.logixable import Logixable, LogixableDefinition

logixables: list[Logixable] = []
parser = Parser()

def execute_command(subcommands: list):
    command_keyword = subcommands[0]
    if command_keyword == Command.DEFINE:
        logixable = parser.parse_function_signature(subcommands[1])
        logixable_def = parser.parse_function_definition(subcommands[2], logixable.args)
        logixable.definition = logixable_def
        logixables.append(logixable)
    elif command_keyword == Command.SOLVE:
        pass
    elif command_keyword == Command.ALL:
        pass
    elif command_keyword == Command.FIND:
        pass
    elif command_keyword == Command.VISUALIZE:
        pass
    elif command_keyword == Command.HELP:
        print("DEFINE Syntax: \'DEFINE func_name(arguments): \"expression\"\'\nAllowed operators: \'&\', \'!\', \'|\'.")
        print("\nExpression defined w/ DEFINE must have spaces between operators and operands!")
        # TODO: define other commands

def main():
    print("Welcome to Logixables! Please, enter a valid command to get started!\n")
    print("Valid commands are: DEFINE, SOLVE, FIND, ALL, VISUALIZE, HELP, EXIT")

    while inp := input() != 'EXIT':
        try:
            subcommands = parser.parse_command(inp)
            # always has at least 2 commands
            execute_command(subcommands)
            print("-----------------\n")       
        except ValueError as err:
            print("\n%s" % err)

if __name__ == "__main__":
    main()