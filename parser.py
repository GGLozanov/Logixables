from data_structs.stack import Stack, StackNode
from models.commands import Command
from models.operators import Operator
from models.logixable import *

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
                # THIS SHOULD USE AN ACTUAL .SPLIT() BECAUSE NO WAY AM I IMPLEMENTING KNUTH-MORRIS-PRAT TO OPTIMISE THIS TO SEARCH WITHIN SUBSTRINGS BECAUSE OF REQUIREMENTs
                func_args = [a.strip() for a in self.__split(args, ',')] # everything after func name
                if not func_args:
                    func_args = [a.strip() for a in self.__split(args, ', ')] # try w/ space if it doesn't work

        return Logixable(func_name, func_args)

    # these 2 funcs below are for parsing the DEFINE command
    def extract_function_declaration_signature(self, command: str) -> str:
        func_command = self.__slice_after_delim_occurrences(command, ' ') # get after first command and start analysing function
        closing_brace_found = False
        for index, char in enumerate(func_command):
            if closing_brace_found and (char == ':' or char == ' '):
                # accept both space and colon
                return func_command[:index] 

            if char == Operator.RIGHT_PARENTHESIS:
                closing_brace_found = True
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

    def parse_function_definition(self, definition: str, allowed_args: list) -> LogixableDefinition:
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

        return LogixableDefinition(postfix, allowed_args)
    
    def __validate_function_def_syntax(self, func_def: str):
        if not func_def:
            raise ValueError("Function definition cannot be empty!")

        if not self.__balanced_parentheses(func_def):
            raise ValueError("Function definition has an unbalanced number of parentheses!")    

    def parse_truth_table(self):
        pass

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
