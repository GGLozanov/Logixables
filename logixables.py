import parser as p
from models.commands import Command
from models.logixable import logixables
import file_handler as fh

parser = p.Parser()
file_handler = fh.FileHandler()

def execute_command(subcommands: list[str]):
    command_keyword = parser.upper(subcommands[0])
    if command_keyword == Command.DEFINE:
        original_command = ' '.join(subcommands)  # parsing is special here so reset back to original input (kinda bad FIXME)
        
        logixable_signature = parser.extract_function_declaration_signature(original_command)
        logixable = parser.parse_function_signature(logixable_signature)
        logixable_names = [l.name for l in logixables]

        if logixable.name in logixable_names:
            raise ValueError("Cannot define a logixable with the same name!") # TODO: Support method overloading lol
        
        command_after_signature = parser.subtract(original_command, subcommands[0] + ' ' + logixable_signature)
        logixable_definition = parser.extract_function_definition(command_after_signature) 
        logixable_def = parser.parse_function_definition(logixable_definition, logixable.args)
        
        logixable.definition = logixable_def
        logixables.append(logixable)
        print("Successfully added function with name '%s' to the logixables!" % logixable.name)
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
        print("1. DEFINE Syntax: \'DEFINE func_name(arguments): \"postfix expression\"\'. \nAllowed operators: \"&\", \'!\', \'|\'.")
        print("Expression defined with DEFINE must have spaces between arguments in functions, operators, and operands! The function definition must also be wrapped in quotes!")
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