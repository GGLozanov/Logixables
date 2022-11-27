from data_structs.stack import Stack, StackNode
from models.commands import Command
from models.operators import Operator
import models.logixable as logix_blueprint

# TODO: DEFINE ACCEPTABLE CHARSET FOR ARGS (ASCII?)
# TODO: HANDLE DIFFERENT PARENTHESES OBFUSCATING INPUT

class Parser:
    # returns list of subcommands (keywords, inputs, etc.) split by ' '
    def parse_command(self, command: str) -> list:
        if not command:
            raise ValueError('Command cannot be empty!')
        
        subcommands = self.__split(command, ' ')

        if subcommands[0] not in Command:
            raise ValueError('Command not in defined commands! Please, enter a valid command!')

        if not subcommands[1]:
            raise ValueError('Invalid function definiton! Cannot be empty!')
        
        # min requirement is 2 subcommands/inputs
        
        return list

    # parse a function definition from DEFINE and return
    # this treats postfix for now
    # returns a logixable w/o a definition
    def parse_function_signature(self, func: str) -> logix_blueprint.Logixable:
        self.__validate_function_sig_syntax(func)

        arg_start = 0
        arg_end = 0
        func_args = []
        func_name = ''
        for index, char in enumerate(func):
            if char == Operator.LEFT_PARENTHESIS:
                func_name = input[0:index]
                arg_start = index
            
            if char == Operator.RIGHT_PARENTHESIS:
                arg_end = index

            if arg_start != 0 and arg_end != 0:
                func_args = self.__split(input[arg_start:arg_end], ',') # everything after func name
                if not func_args:
                    func_args = self.__split(input[arg_start:arg_end], ', ') # try w/ space if it doesn't work

        return logix_blueprint.Logixable(func_name, func_args)
    
    def __validate_function_sig_syntax(self, func_sig: str, check_for_colon: bool = True):
        if not func_sig or len(func_sig) <= 2:
            raise ValueError("Function signature cannot be empty/invalid!")
    
        left_parentheses_count = func_sig.count(Operator.LEFT_PARENTHESIS)
        right_parentheses_count = func_sig.count(Operator.RIGHT_PARENTHESIS)

        if left_parentheses_count != 1 or right_parentheses_count != 1:
            raise ValueError("Function signature should have only one pair of parentheses!")

        if func_sig[0] == Operator.LEFT_PARENTHESIS:
            raise ValueError("Function signature must have argument signature denoted at a valid starting position!")

        if check_for_colon:
            if func_sig[-1] != ':' or func_sig[-2] != Operator.RIGHT_PARENTHESIS:
                raise ValueError("Invalid function signature! Function signature must contain colon and closing parenthesis!")
        elif func_sig[-1] != Operator.RIGHT_PARENTHESIS:
            raise ValueError("Function signature within function definition requires closing parethesis!")

    def parse_function_definition(self, definition: str, allowed_args: list) -> logix_blueprint.LogixableDefinition:
        # handle split by ' ' and no space POSTFIX (later infix)
        # no handling of if no space between ":" and definition -> prolly not
        # detect unallowed args used (easy with ' ' but if spliced together, check if contains? Harder to implement) -> assume spaces as of now
        self.__validate_function_def_syntax(func_def=definition)

        # remove quotes if there are
        if definition[0] and definition[-1] == '""':
            definition = definition[1:-1]

        # assume tokens split by space as for now and that they are postfix
        postfix = self.__split(definition, ' ')

        return logix_blueprint.LogixableDefinition(postfix, allowed_args)
    
    def __validate_function_def_syntax(self, func_def: str):
        if not func_def:
            raise ValueError("Function definition cannot be empty!")

        if not self.__balanced_parentheses(func_def):
            raise ValueError("Function definition has an unbalanced number of parentheses!")    

    def parse_truth_table(self):
        pass

    # checks only for '(' and ')'
    def __balanced_parentheses(input) -> bool:
        parentheses = Stack()

        for char in input:
            if char == Operator.LEFT_PARENTHESIS:
                parentheses.push(StackNode(char))
            elif char == Operator.RIGHT_PARENTHESIS:
                parentheses.pop()

        return parentheses.is_empty()
    
    # TODO: This should replace `__parseFunction` when infix is supported
    def shunting_yard(self, ):
        # check num of opening braces == num of closing braces (balanced braces; stack)
        operators = Stack(StackNode())
        operands = Stack(StackNode()) 

    def __split(input, delimiter):
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
