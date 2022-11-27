import parser as p
from models.commands import Command
from models.logixable import logixables
import file_handler as fh

parser = p.Parser()
file_handler = fh.FileHandler()

def execute_command(subcommands: list):
    command_keyword = parser.upper(subcommands[0])
    if command_keyword == Command.DEFINE:
        logixable = parser.parse_function_signature(subcommands[1])
        logixable_def = parser.parse_function_definition(subcommands[2], logixable.args)
        logixable.definition = logixable_def
        logixables.append(logixable)
    elif command_keyword == Command.SOLVE:
        # logixable = parser.parse_logixable_name_from_signature()
        pass
    elif command_keyword == Command.ALL:
        pass
    elif command_keyword == Command.FIND:
        pass
    elif command_keyword == Command.VISUALIZE:
        pass
    elif command_keyword == Command.HELP:
        print("DEFINE Syntax: \'DEFINE func_name(arguments): \"expression\"\'. \nAllowed operators: \"&\", \'!\', \'|\'.")
        print("\nExpression defined w/ DEFINE must have spaces between operators and operands!")
        # TODO: define other commands
    elif command_keyword == Command.EXIT:
        print('EXITING NOW!')
        exit(0)

def main():
    print("Welcome to Logixables! Please, enter a valid command to get started!\n")
    print("Valid commands are: DEFINE, SOLVE, FIND, ALL, VISUALIZE, HELP, EXIT")
    
    inp = input()
    while True:
        try:
            subcommands = parser.parse_command(inp)
            print("-----------------")
            execute_command(subcommands)
            print("-----------------")       
        except ValueError as err:
            print("%s" % err)
        inp = input()

if __name__ == "__main__":
    main()