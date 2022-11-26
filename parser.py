from data_structs.stack import Stack, StackNode
from models.commands import Command
from models.logixable import Logixable, LogixableDefinition
from models.operators import Operator
from logixables import logixables;

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
    
    def __validate_function_sig_syntax(self, func_sig: str):
        # check has "(" and next parentheses have "):" ONLY AT THE END OF THE STRING
        # otherwise invalid func declaration
        # check "):" ends the string, otherwise ALWAYS error
            
        pass

    def parse_function_definition(self, definition: str, allowed_args: list) -> LogixableDefinition:
        # handle split by ' ' and no space POSTFIX (later infix)
        # handle "" and having no ""
        # no handling of if no space between ":" and definition
        # detect unallowed args used (easy with ' ' but if spliced together, check if contains? Harder to implement) 
        self.__validate_function_def_syntax(func_def=definition)

        # remove quotes if there are
        if definition[0] and definition[-1] == '""':
            definition = definition[1:-1]

        # assume tokens split by space as for now and that they are postfix
        postfix = self.__split(definition, ' ')

        self.__validate_allowed_args(postfix, allowed_args)

        return LogixableDefinition(postfix)
    
    def __validate_function_def_syntax(self, func_def: str):
        if not func_def:
            raise ValueError("Function definition cannot be empty!")

        if not self.__balanced_parentheses(func_def):
            raise ValueError("Function definition has an unbalanced number of parentheses!")

    def __validate_allowed_args(self, split_postfix: str, allowed_args: list):
        in_function = False
        logixable_names = [logixable.name for logixable in logixables]
        for index, token in enumerate(split_postfix):
            if token in logixable_names:
                in_function = True
                continue

            if in_function and token in logixable_names:
                self.__validate_allowed_args(split_postfix[index:], allowed_args)

            while token[-1] == ',' and in_function:
                if token not in allowed_args:
                    raise ValueError("Argument %s in definition is not defined in allowed arguments!" % token[:-1])

            in_function = False

        pass

    def __parse_truth_table(self):
        pass

    # checks only for '(' and ')'
    def __balanced_parentheses(input):
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
