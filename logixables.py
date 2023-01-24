import tools.logix_parser as p
import tools.finder as f
from models.commands import Command
import models.logixable as logix_blueprint
from utils.algo.find_logix_w_fail import find_logixable_with_fail
import tools.file_handler as fh
import tools.visualizer as vz
import atexit

parser = p.Parser()
file_handler = fh.FileHandler()
visualizer = vz.LogixableVisualizer()

def execute_command(original_command: str, subcommands: list[str]):
    command_keyword = parser.upper(subcommands[0])
    if command_keyword == Command.DEFINE:
        # ex. inputs:
        # DEFINE func1(a, b, c, d): "a b c d ! & | &"
        # DEFINE func2(a, b): "a b |"
        # DEFINE func(a, b, c): "func2 a, b c |"
        # DEFINE func5(a, b): "a b &" 

        # DEFINE func3(a, b): "func2 func2 a, b, b func2 a, b &"
        # DEFINE func4(a, b): "func2 func2 a, b, b b &"  
        # DEFINE func6(a, b): "func2 a, b func5 a, b &"

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
        signature = parser.extract_function_declaration_signature(original_command, False)
        func_call = parser.parse_function_signature_solve(signature)

        logixable = find_logixable_with_fail(func_call.name, logix_blueprint.logixables)

        arg_values = func_call.args # this actually contains values
        result = logixable.solve(arg_values)
        print("Result: " + str(result))
    elif command_keyword == Command.ALL:
        logixable = find_logixable_with_fail(subcommands[1], logix_blueprint.logixables)
        print(logixable.generate_truth_table())
    elif command_keyword == Command.FIND:
        # test TTs:
        # FIND 0 0 0: 0; 0 0 1: 1; 0 1 0: 0; 1 0 0: 1; 0 1 1: 1; 1 1 0: 0; 1 0 1: 1; 1 1 1: 0
        data = parser.subtract(original_command, subcommands[0] + ' ')

        from_file = file_handler.is_valid_tt_file(data)
        if from_file:
            data = file_handler.read_tt_file(data)

        truth_table = parser.parse_truth_table(data, from_file)
        finder = f.LogixableFinder()
        satisfied_definitions = finder.find_logixable_from_truth_table(truth_table, logix_blueprint.logixables)

        if len(satisfied_definitions) <= 0:
            print("No functions found to satisfy truth table!")
            return

        for (idx, definition) in enumerate(satisfied_definitions):
            print("Satisfactory Definition %s: %s" % (idx + 1, str(definition)))
    elif command_keyword == Command.VISUALIZE:
        logixable_name = subcommands[1]
        logixable = find_logixable_with_fail(logixable_name, logix_blueprint.logixables)
        visualizer.visualize(logixable)
    elif command_keyword == Command.HELP:
        print("1. DEFINE Syntax: \'DEFINE func_name(arguments): \"postfix expression\"\'. \nAllowed operators: \"&\", \'!\', \'|\'.")
        print(" Note: Expression defined with DEFINE must have spaces between arguments in functions, operators, and operands (commas between arguments as well if in a function call)! The function definition must also be wrapped in quotes!")
        print(" Example postfix syntax definition: 'DEFINE func1(a, b): \"func a, b b &\"' (translates to 'func(a, b) & b')")
        print("In need of postfix reference, please use: https://scanftree.com/Data_Structure/prefix-postfix-infix-online-converter")
        print("2. SOLVE Syntax: \'SOLVE func_name(1, 0, 1...)'. Solves a definedfunction with given arguments. \nFunction name must be in currently defined functions and take in arguments (1, 0)!")
        print("3. ALL Syntax: \'ALL func_name'. Displays a function's truth table. \nFunction name must be in currently defined functions!")
        print("4. FIND Syntax: \'FIND 0 0 0: 1; 0 0 1: 1...' or 'FIND file_name.txt'. Finds a function with the described truth table. NOTE: The syntax in the file should be deliminated by a newline character, not a semi-colon. The last value at any row in the truth table is the output of the previous elements in the row (they are arguments).")
        print("5. VISUALIZE Syntax: \'VISUALIZE func_name'. Visualizes a function's operations in the form of a tree.")
    elif command_keyword == Command.EXIT:
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