from data_structs.stack import Stack, StackNode
from models.commands import Command
from models.operators import Operator
from models.logixable import *
from utils.algo.binary_permutations import binary_permutations

# TODO: DEFINE ACCEPTABLE CHARSET FOR ARGS (ASCII?)
# TODO: HANDLE DIFFERENT PARENTHESES OBFUSCATING INPUT

class Parser:
    # returns list of subcommands (keywords, inputs, etc.) split by ' '
    def parse_command(self, command: str) -> list:
        if not command:
            raise ValueError('Command cannot be empty!')
        
        unfiltered_subcommands = self.__split(command, ' ')
        subcommands = list(filter(lambda x: x.strip(), unfiltered_subcommands)) # remove whitespaces
        commands = [c.value for c in Command]
        def_command = self.upper(subcommands[0])
        if def_command not in commands:
            raise ValueError('Command not in defined commands! Please, enter a valid command!')

        # this isn't totally accurate because it might split until any space is reached but still means there are at least 2 args for commands that need them
        if len(subcommands) < 2 and def_command != Command.EXIT and def_command != Command.HELP:
            raise ValueError('Invalid command argument! Cannot be empty!')
        
        # min requirement is 2 subcommands/inputs
        
        return subcommands

    # parse a function definition from DEFINE and return
    # this treats postfix for now
    # returns a logixable w/o a definition
    def parse_function_signature(self, func: str) -> Logixable:
        self.__validate_function_sig_syntax(func)

        arg_start = 0
        arg_end = 0
        func_args = []
        func_name = ''
        for index, char in enumerate(func):
            if char == Operator.LEFT_PARENTHESIS:
                func_name = func[0:index]
                arg_start = index + 1
            
            if char == Operator.RIGHT_PARENTHESIS:
                arg_end = index

            # TODO: Convert to charset check
            if arg_start == 0 and char == ' ':
                raise ValueError("Invalid character in function signature! Character '%s' is not allowed!" % char)

            if arg_start != 0 and arg_end != 0:
                args = func[arg_start:arg_end]
                # this should use an actual, more sophisticated .split()
                # because substring optimisation requires something a la Knuth-Morris-Pratt algorithm
                func_args = [a.strip() for a in self.__split(args, ',')] # everything after func name
                if not func_args:
                    func_args = [a.strip() for a in self.__split(args, ', ')] # try w/ space if it doesn't work

        return Logixable(func_name, func_args)

    def parse_function_signature_solve(self, func: str) -> Logixable:
        func_call = self.parse_function_signature(func)
        func_args = func_call.args
        bool_func_args: list[bool] = []
        for arg in func_args:
            if arg != "1" and arg != "0":
                raise ValueError("Invalid function call input! Function arguments should be either 1 or 0!")
            bool_func_args.append(bool(int(arg)))

        func_call.args = bool_func_args
        return func_call

    # these 2 funcs below are for parsing the DEFINE command
    def extract_function_declaration_signature(self, command: str, check_delims: bool = True) -> str:
        func_command = self.__slice_after_delim_occurrences(command, ' ') # get after first command and start analysing function
        closing_brace_found = False
        for index, char in enumerate(func_command):
            if closing_brace_found:
                if check_delims and char == ':' or char == ' ':
                    # accept both space and colon
                    return func_command[:index]
                else:
                    return func_command[:index]

            if char == Operator.RIGHT_PARENTHESIS:
                closing_brace_found = True
                if index == len(func_command) - 1:
                    return func_command # parenthesis at end
        raise ValueError("Could not parse function from command correctly! Please, ensure the function is closed with a right parenthesis and has a colon/whitespace after its declaration along with a definition!")

    # pass command after signature (there may be other chars but just find quote)
    def extract_function_definition(self, command_after_signature: str) -> str:
        if command_after_signature[-1] != '"':
            raise ValueError("Invalid function definition! Could not find end quote for definition end!")
        for index, char in enumerate(command_after_signature):
            if char == '"':
                return command_after_signature[index+1:-1]
        raise ValueError("Invalid function definition! Could not find begin quote for definition start!")

    def __validate_function_sig_syntax(self, func_sig: str):
        if not func_sig or len(func_sig) <= 2:
            raise ValueError("Function signature cannot be empty/invalid!")

        left_parentheses_count = func_sig.count(Operator.LEFT_PARENTHESIS)
        right_parentheses_count = func_sig.count(Operator.RIGHT_PARENTHESIS)

        if left_parentheses_count == 0 or right_parentheses_count == 0:
            raise ValueError("Function signature should be enclosed by a pair of parentheses!")
        
        if left_parentheses_count != 1 or right_parentheses_count != 1:
            raise ValueError("Function signature should be enclosed by a pair of parentheses!")

        if func_sig[0] == Operator.LEFT_PARENTHESIS:
            raise ValueError("Function signature must have argument signature denoted at a valid starting position!")

        if func_sig[-1] != Operator.RIGHT_PARENTHESIS:
            raise ValueError("Function signature within function definition requires closing parethesis!")

    def clean_function_definition(self, definition: str) -> str:
        # handle split by ' ' and no space POSTFIX (later infix)
        # no handling of if no space between ":" and definition -> prolly not
        # detect unallowed args used (easy with ' ' but if spliced together, check if contains? Harder to implement) -> assume spaces as of now
        self.__validate_function_def_syntax(func_def=definition)

        # remove quotes if there are
        if len(definition) > 2:
            if definition[0] == '"':
                if definition[-1] == '"':
                    definition = definition[1:-1]
                else:
                    raise ValueError("No end quote for function definition '%s'!" % definition)
            elif definition[-1] == '"':
                raise ValueError("No starting quote for function definition '%s'!" % definition)

        # assume tokens split by space as for now and that they are postfix
        postfix = self.__split(definition, ' ')

        return postfix
    
    def __validate_function_def_syntax(self, func_def: str):
        if not func_def:
            raise ValueError("Function definition cannot be empty!")

        if not self.__balanced_parentheses(func_def):
            raise ValueError("Function definition has an unbalanced number of parentheses!")    

    # different formats for TT in file and not in file (for file, there are no semicolons; without, there are)
    # TODO: Should trim spaces here.
    def parse_truth_table(self, raw_data: str, from_file: bool) -> list[list[bool]]:
        truth_table: list[list[bool]] = []
        split_char = ';'
        if from_file:
            split_char = '\n'

        split_data_initial = self.__split(raw_data, split_char)
        if len(split_data_initial) <= 1:
            raise ValueError("Truth table must have at least two rows! Please, check your input!")

        split_data = []
        for idx in range(len(split_data_initial)):
            row = split_data_initial[idx]
            new_row = self.__split(row, ' ')
            if len(new_row) < 1:
                raise ValueError("Truth table rows are of insufficient length! There must be at least 2 parameters (one argument and one output)!")
            last_arg = new_row[-2]
            if not last_arg:
                raise ValueError("Arguments cannot be empty!")

            new_row[-2] = last_arg[:-1] # remove ':' character
            new_row = list(filter(lambda n: n != "", new_row))
            split_data.append(new_row)

        split_data_l = len(split_data)

        if split_data_l == 0:
            raise ValueError("Truth table must not be empty and be deliminated by '; ' or a newline character if used from file!")
        
        expected_row_length = len(split_data[0])

        if expected_row_length < 1:
            raise ValueError("Truth table must not be empty and be deliminated by '; ' or a newline character if used from file!")

        max_arg_count = expected_row_length - 1

        if split_data_l != 2 ** max_arg_count:
            raise ValueError("Truth table must account for all variants of arguments and their outputs!")

        arg_rows = []
        converted_tt = [[True if num == "1" else False if num == "0" else None for num in row] for row in split_data]
        for arg_row in converted_tt:
            if not all(value == False or value == True for value in arg_row):
                raise ValueError("Truth table must ONLY contain ones and zeroes!")
            arg_rows.append(arg_row[:-1]) # used to test permutation adherence; convert to int

        arg_perms = binary_permutations(max_arg_count) # generate arguments expected to be in TT
        for perm in arg_perms:
            if perm not in arg_rows:
                raise ValueError("Truth table must account for all variants of arguments and their outputs! Please, check your argument values and make sure there are no duplicates!")

        return converted_tt

    # checks only for '(' and ')'
    def __balanced_parentheses(self, input) -> bool:
        parentheses = Stack()

        for char in input:
            if char == Operator.LEFT_PARENTHESIS:
                parentheses.push(StackNode(char))
            elif char == Operator.RIGHT_PARENTHESIS:
                parentheses.pop()

        return parentheses.is_empty()
    
    # TODO: This should replace `__parseFunction` when infix is supported
    def shunting_yard(self):
        # check num of opening braces == num of closing braces (balanced braces; stack)
        operators = Stack(StackNode())
        operands = Stack(StackNode()) 

    def __slice_after_delim_occurrences(self, input: str, delimiter, delim_occur_threshold = 1) -> str:
        threshold = 0
        for index, char in enumerate(input):
            if threshold == delim_occur_threshold:
                return input[index:]
            if char == delimiter:
                threshold += 1
        return input

    def __split(self, input, delimiter) -> list[str]:
        if not delimiter:
            raise ValueError("Empty Separator")

        if not input:
            return [input]

        start = 0
        result = []
        for index, char in enumerate(input):
            if char == delimiter:
                result.append(input[start:index])
                start = index + 1
        if start == 0:
            return [input]
        result.append(input[start:index + 1])
        
        return result

    def subtract(self, input: str, replace: str) -> str:
        if input.startswith(replace):
            return input[len(replace):] 
        return input

    def upper(self, input: str):
        return "".join(map(lambda c: chr(ord(c) - 32) if 97 <= ord(c) <= 122 else c, input))
