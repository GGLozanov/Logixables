from data_structs.binary_tree import TreeNode
from logixables import logixables

class LogixableDefinition:
    def __init__(self, split_postfix: list):
        self.postfix_input = split_postfix
        self.__buildExpressionTree(split_postfix)

    def __buildExpressionTree(split_postfix: list) -> TreeNode:
        # TODO: Handle function being called inside function: e.g. definition ("func3(a, b): func1(a, func2(a, b)) & a")
        # or in postfix: func1 a, func2 a, b a &

        pass

class Logixable:
    def __init__(self, name: str, args: list, definition: LogixableDefinition = None) -> None:
        self.name = name
        self.args = args
        self.definition = definition
        pass

    def solve(self, arg_values: list):
        if len(arg_values) != len(self.args):
            raise ValueError("Argument value count must be the same as arguments of function!")

        # go down the tree and stack-ify it?
        # if going back in reverse: 
        #   if argument: check argument value by indexing it with args and arg_values
        #   if operator: perform operation with last two arguments' values with operator
        #   if LOGIXABLE: call `.solve()` and coalesce the results together
        #   continue until reach stack empty/bottom of tree?
        pass

    def visualize(self):
        pass