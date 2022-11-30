import parser as p
from models.commands import Command
from models.logixable import logixables
import file_handler as fh

parser = p.Parser()
file_handler = fh.FileHandler()

def execute_command(original_command: str, subcommands: list[str]):
    command_keyword = parser.upper(subcommands[0])
    if command_keyword == Command.DEFINE:
        # ex. inputs:
        # DEFINE una(a, b, c, d): "a b c d ! & | &"
        # DEFINE funda(a, b): "a b |"
        # DEFINE fr(a, b): "funda funda a, b, b funda a, b &"
        # DEFINE fur(a, b): "funda funda a, b, b b &"  
        # DEFINE fud(a, b): "a b &" 
        # DEFINE fd(a, b): "funda a, b fud a, b &"

        logixable_signature = parser.extract_function_declaration_signature(original_command)
        logixable = parser.parse_function_signature(logixable_signature)
        logixable_names = [l.name for l in logixables]

        if logixable.name in logixable_names:
            raise ValueError("Cannot define a logixable with the same name!") # TODO: Support method overloading lol
        
        command_after_signature = parser.subtract(original_command, subcommands[0] + ' ' + logixable_signature)
        logixable_definition_postfix = parser.extract_function_definition(command_after_signature) 
        logixable_definition_postfix_clean = parser.clean_function_definition(logixable_definition_postfix)
        
        logixable.define(logixable_definition_postfix_clean)
        logixables.append(logixable)
        print("Successfully added function with name '%s' to the logixables!" % logixable.name)
    elif command_keyword == Command.SOLVE:
        # this should return a tuple of (func name, func args) but just use logixable as a box/wrapper type
        # FIXME: Can't use this method if validating arguments w/ charset because charset for SOLVE and DEFINE would differ
        signature = parser.extract_function_declaration_signature(original_command, False)
        func_call = parser.parse_function_signature_solve(signature)

        logixable = find_logixable_with_fail(func_call.name)

        arg_values = func_call.args # this actually contains values
        result = logixable.solve(arg_values)
        print("RESULT: " + str(result))
    elif command_keyword == Command.ALL:
        logixable = find_logixable_with_fail(subcommands[1])
        print(logixable.generate_truth_table())
    elif command_keyword == Command.FIND:
        pass
    elif command_keyword == Command.VISUALIZE:
        pass
    elif command_keyword == Command.HELP:
        print("1. DEFINE Syntax: \'DEFINE func_name(arguments): \"postfix expression\"\'. \nAllowed operators: \"&\", \'!\', \'|\'.")
        print("Expression defined with DEFINE must have spaces between arguments in functions, operators, and operands (commas between arguments as well if in a function call)! The function definition must also be wrapped in quotes!")
        print("Example postfix syntax definition: 'DEFINE func1(a, b): \"func a, b b &\"' (translates to 'func(a, b) & b')")
        print("In need of postfix reference, please use: https://scanftree.com/Data_Structure/prefix-postfix-infix-online-converter")
        # TODO: define other commands
    elif command_keyword == Command.EXIT:
        print('EXITING NOW!')
        exit(0)

def find_logixable_with_fail(name: str):
    try:
        logixable = next(l for l in logixables if name == l.name)
    except:
        raise ValueError("No Logixable found with the name provided in the command! Please, check the name and try again!")

    return logixable

def main():
    print("Welcome to Logixables! Please, enter a valid command to get started!\n")
    print("Valid commands are: DEFINE, SOLVE, FIND, ALL, VISUALIZE, HELP, EXIT")
    
    inp = input()
    while True:
        try:
            subcommands = parser.parse_command(inp)
            print("-----------------")
            execute_command(inp, subcommands)
            print("-----------------")       
        except ValueError as err:
            print("%s" % err)
        inp = input()

if __name__ == "__main__":
    main()