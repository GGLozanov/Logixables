import logix_parser as p
import finder as f
from models.commands import Command
import models.logixable as logix_blueprint
from utils.algo.find_logix_w_fail import find_logixable_with_fail
import file_handler as fh
import atexit

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
        logixable_names = [l.name for l in logix_blueprint.logixables]

        if logixable.name in logixable_names:
            raise ValueError("Cannot define a logixable with the same name!") # TODO: Support method overloading lol
        
        command_after_signature = parser.subtract(original_command, subcommands[0] + ' ' + logixable_signature)
        logixable_definition_postfix = parser.extract_function_definition(command_after_signature) 
        logixable_definition_postfix_clean = parser.clean_function_definition(logixable_definition_postfix)
        
        logixable.define(logixable_definition_postfix_clean)
        logix_blueprint.logixables.append(logixable)
        print("Successfully added function with name '%s' to the logixables!" % logixable.name)
    elif command_keyword == Command.SOLVE:
        # this should return a tuple of (func name, func args) but just use logixable as a box/wrapper type
        # FIXME: Can't use this method if validating arguments w/ charset because charset for SOLVE and DEFINE would differ
        signature = parser.extract_function_declaration_signature(original_command, False)
        func_call = parser.parse_function_signature_solve(signature)

        logixable = find_logixable_with_fail(func_call.name, logix_blueprint.logixables)

        arg_values = func_call.args # this actually contains values
        result = logixable.solve(arg_values)
        print("RESULT: " + str(result))
    elif command_keyword == Command.ALL:
        logixable = find_logixable_with_fail(subcommands[1], logix_blueprint.logixables)
        print(logixable.generate_truth_table())
    elif command_keyword == Command.FIND:
        # data = 
        # from_file = 
        # truth_table = parser.parse_truth_table(data, from_file)
        finder = f.LogixableFinder()
        test_tt = [[0, 0, 0], [1, 1, 1], [1, 0, 1], [0, 1, 1]]
        satisfied_definitions = finder.find_logixable_from_truth_table(test_tt, logix_blueprint.logixables)
        if len(satisfied_definitions) <= 0:
            print("No functions found to satisfy truth table!")
            return

        # FIXME: More user-friendly formatting
        for (idx, definition) in enumerate(satisfied_definitions):
            print("Satisfactory Definition %s: %s" % (idx + 1, str(definition.expr_tree)))
    elif command_keyword == Command.VISUALIZE:
        pass
    elif command_keyword == Command.HELP:
        print("1. DEFINE Syntax: \'DEFINE func_name(arguments): \"postfix expression\"\'. \nAllowed operators: \"&\", \'!\', \'|\'.")
        print("Expression defined with DEFINE must have spaces between arguments in functions, operators, and operands (commas between arguments as well if in a function call)! The function definition must also be wrapped in quotes!")
        print("Example postfix syntax definition: 'DEFINE func1(a, b): \"func a, b b &\"' (translates to 'func(a, b) & b')")
        print("In need of postfix reference, please use: https://scanftree.com/Data_Structure/prefix-postfix-infix-online-converter")
        print("2. SOLVE Syntax: \'SOLVE func_name(1, 0, 1...)'. Solves a definedfunction with given arguments. \nFunction name must be in currently defined functions and take in arguments (1, 0)!")
        print("3. ALL Syntax: \'ALL func_name'. Displays a function's truth table. \nFunction name must be in currently defined functions!")
        print("4. FIND Syntax: \'FIND 0 0 0 1; 0 0 1 1...' or 'FIND file_name.txt'. Finds a function with the described truth table. \nTruth table must be a matrix with N rows and columns. The last value at any row is the output of the previous elements in the row (they are arguments).")
        print("5. VISUALIZE Syntax: \'VISUALIZE func_name'. Visualizes a function's operations in the form of a tree.")
    elif command_keyword == Command.EXIT:
        print('EXITING NOW!')
        exit(0)

def exit_handler():
    file_handler.save_logixables(logix_blueprint.logixables)

def main():
    print("Welcome to Logixables! Please, enter a valid command to get started!\n")
    print("Valid commands are: DEFINE, SOLVE, FIND, ALL, VISUALIZE, HELP, EXIT")

    atexit.register(exit_handler)
    logix_blueprint.logixables = file_handler.read_logixables()

    try:
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
    except KeyboardInterrupt:
        return

if __name__ == "__main__":
    main()