from data_structs.stack import Stack, StackNode
from models.commands import Command
from models.logixable import Logixable, LogixableDefinition
from models.operators import Operator

class Parser:
    def __init__(self):
        print("parse")

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
    def parse_function_signature(self, func: str) -> Logixable:
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

        return Logixable(func_name, func_args)
    
    def __validate_function_sig_syntax(self, func: str):
        # check has "(" and next parentheses have "):" ONLY AT THE END OF THE STRING
        # otherwise invalid func declaration
        # check "):" ends the string
        pass

    def __parse_function_definition(self, definition: str, allowed_args: list) -> LogixableDefinition:
        # handle split by ' ' and no space POSTFIX (later infix)
        # handle "" and having no ""
        # detect unallowed args used (easy with ' ' but if spliced together, check if contains? Harder to implement) 
        pass

    def __parse_truth_table(self):
        pass
    
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

    # TODO: This should replace `__parseFunction` when infix is supported
    def shunting_yard(self, ):
        # check num of opening braces == num of closing braces (balanced braces; stack)
        operators = Stack(StackNode())
        operands = Stack(StackNode()) 
