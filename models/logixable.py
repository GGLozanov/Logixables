from data_structs.tree import TreeNode, Tree
from data_structs.stack import StackNode, Stack
from models.operators import Operator
import logixables as logix

class LogixableDefinition:
    # logixable_arg_relation = [(Logixable1, ['a', 'b']), (Logixable1, ['b', 'c'])] -> arg pattern matchup (from allowed args for current logixable) for inner logixables. Lookup consists of search **BY LOGIXABLE REFERENCE** (a.k.a. use "is")

    def __init__(self, split_postfix: list, allowed_args: list):
        self.split_postfix_input = split_postfix
        self.__last_validated_logixable_idx_offset = 0
        # self.__validate_allowed_args(split_postfix, allowed_args)
        self.expr_tree = Tree(self.__build_expression_tree(split_postfix, allowed_args))

    # TODO: !!! should validate while splitting into tokens and building tree !!!
    def __validate_allowed_args(self, split_postfix: list, allowed_args: list, in_rec: bool = False, calc_index: int = None) -> int | None:
        in_function = False
        logixable_names = [logixable.name for logixable in logix.logixables]
        operators = [o.value for o in Operator]
        cur_inner_logixable = None
        parsed_inner_args = 0
        for index in range(split_postfix):
            token = split_postfix[index]
            if token in operators:
                continue

            if token in logixable_names:
                cur_inner_logixable = (l for l in logix.logixables if token == l.name).next()
                in_function = True
                continue

            if in_function and token in logixable_names:
                # change idx upon coming back to offset already validated function
                if len(cur_inner_logixable.args) == parsed_inner_args:
                    # parsed all available/correct inner args; means this is not an inner function but another function call w/ an operator attached later on!
                    in_function = False
                    parsed_inner_args = 0
                index += self.__validate_allowed_args(split_postfix[index:], allowed_args, True, index)
                continue

            if in_function:
                if token[-1] != ',':
                    in_function = False
                    if in_rec:
                        return index # return offset from original split_postfix

                clean_token = token[:-1]
                if clean_token not in allowed_args:
                    raise ValueError('Argument \'%s\' in definition is not defined in allowed arguments!' % clean_token)
                parsed_inner_args += 1
            elif token not in allowed_args:
                    raise ValueError('Argument \'%s\' in definition is not defined in allowed arguments!' % token)
        return None # successful finish

    def __build_expression_tree(self, split_postfix: list, allowed_args: list, in_function: bool = False, tree_builder: Stack = Stack()) -> TreeNode:
        # TODO?: REFACTOR TO REMOVE logixable_arg_relation and TREAT FUNCTIONS AS OPERAND NODES WITH ARGUMENTS AS LEAF NODES

        # "func3(a, b): func1(a, func2(a, b)) & a" or in postfix: func1 a, func2 a, b a &
        # example complex input:
            # func(func(a)) + func1(a+b, b*a)*a 
            # postfix: func func a func1 a b, b a * + a * +
        # IF in_function AND space between args: operation inside func (not function call). IMPORTANT: Count pairs of no comma between and iterate until  find that many operators

        logixable_names = [logixable.name for logixable in logix.logixables]
        cur_inner_logixable: Logixable = None
        cur_inner_logixable_arg_count = None
        func_arg_children: list[TreeNode] = [] # argument mapping for a func if inside a function
        # count_inner_operation_pairs = -1 # don't count (0 if actually counting)
        operators = [o.value for o in Operator]
        parsed_inner_args = 0

        for index in range(split_postfix):
            token = split_postfix[index]
            if not token:
                raise ValueError("Empty token in postfix expression at %s index!" % index)

            if token in logixable_names:
                # function (the one defined here) inside function (the one called top-level) inside function (the one defined OVERALL for this LogixableDefinition)
                if in_function and len(cur_inner_logixable.args) == parsed_inner_args:
                    # parsed all available/correct inner args; means next stuff cannot be an inner function argument, but a new node w/ a new function call w/ an operator attached later on!
                    parsed_inner_args = 0
                    __last_validated_logixable_idx_offset = index
                    return TreeNode(None, func_arg_children) # value node; return only operands because there are no more inner functions (impossible)

                cur_inner_logixable = (l for l in logix.logixables if token == l.name).next()
                cur_inner_logixable_arg_count = len(cur_inner_logixable.allowed_args)

                # this should return a node that describes "func func a" or "func1 a b, b a * +" 
                # recursion until exit node and then add this one BIG logixable node and its arg relations children (whether they be args or logixables) to the tree
                parsed_inner_args += 1
                func_node = self.__build_expression_tree(split_postfix[index:], True, tree_builder)

                total_node = TreeNode(func_node.children + func_arg_children, func_node.value)
                if in_function:
                    return TreeNode(total_node, cur_inner_logixable)
                else:
                    tree_builder.push(total_node)
                    index += self.__last_validated_logixable_idx_offset
            elif token in operators:
                right = tree_builder.pop()
                left = tree_builder.pop()
                new_node = TreeNode([left, right], token)
                tree_builder.push(new_node)
            else:
                # MARK: Operands
                if not in_function:
                    if token not in allowed_args:
                        raise ValueError('Argument \'%s\' in definition is not defined in allowed arguments!' % token)
                    tree_builder.push(TreeNode(None, token))
                    continue
            
                # ----- Handle invalid argument count for function ----
                if parsed_inner_args > cur_inner_logixable_arg_count:
                    raise ValueError('Invalid argument count for function \'%s\'! Expected count was %s arguments but received %s instead!' % cur_inner_logixable.name, cur_inner_logixable_arg_count, parsed_inner_args)

                clean_token = token
                if token[-1] == ',':
                    clean_token = token[:-1]

                if clean_token not in allowed_args:
                    raise ValueError('Argument \'%s\' in definition is not defined in allowed arguments!' % clean_token)
                parsed_inner_args += 1

                func_arg_children.append(TreeNode(None, clean_token))

                # TODO: DELETE?
                # ----- VALID ARGUMENT NOW (NOT PART OF OPERATION INSIDE FUNC) ------
                # ----- ADD ARGUMENT TO RELATIONSHIP CHAIN ------
                # if cur_inner_logixable not in self.logixable_arg_relation:
                #     self.logixable_arg_relation.append((cur_inner_logixable, [token]))
                # else:
                #     idx = self.logixable_arg_relation.index(cur_inner_logixable)
                #     self.logixable_arg_relation[idx][1].append(token)

                # function argument OR invalid input
                # space between operands and no comma
        self.__last_validated_logixable_idx_offset = 0
        top_node = tree_builder.pop()

        if not tree_builder.is_empty:
            raise ValueError('Internal error! Expression tree builder stack is not empty!')

        return top_node

    def solve(self, node: TreeNode):
        # go down the tree and stack-ify it?
        # if going back in reverse: 
        #   if top-level parent is LOGIXABLE and has no logixables inside it: iterate between all children nodes, assign arguments from valid_args, and perform operations
        #   if child is argument: check argument value by indexing it with args and arg_values
        #   if child is operator: perform operation with last two children with operator
        #   if child is LOGIXABLE: call `.solve()` and coalesce the results together.
        #       then lookup logixable w/ is and place args accordingly
        #       if arg in lookup is LOGIXABLE AGAIN: recursion to `.solve()` to loop and further check argument relation
        #   continue until reach stack empty/bottom of tree?

        # if node.value is LogixableDefinition:

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

        self.definition.solve()

    def visualize(self):
        pass