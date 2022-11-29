from data_structs.stack import StackNode, Stack
from data_structs.tree import TreeNode, Tree
from models.operators import Operator
from utils.consume import consume

class LogixableDefinition:
    # logixable_arg_relation = [(Logixable1, ['a', 'b']), (Logixable1, ['b', 'c'])] -> arg pattern matchup (from allowed args for current logixable) for inner logixables. Lookup consists of search **BY LOGIXABLE REFERENCE** (a.k.a. use "is")

    def __init__(self, split_postfix: list, allowed_args: list):
        self.split_postfix_input = split_postfix
        self.__last_validated_logixable_idx_offset = 0
        self.__tree_builder = Stack()
        self.expr_tree = Tree(self.__build_expression_tree(split_postfix, allowed_args, tree_builder=self.__tree_builder))
        print(self.expr_tree)

    # this method makes me want to commit seppuku
    # TODO: Handle func(a | b, b) etc.
    def __build_expression_tree(self, split_postfix: list, allowed_args: list, upper_logixable: 'Logixable' = None, tree_builder: Stack = Stack()) -> TreeNode:
        # "func3(a, b): func1(a, func2(a, b)) & a" or in postfix: func1 a, func2 a, b a &
        # example complex input:
            # func(func(a)) + func1(a+b, b*a)*a 
            # postfix: func func a func1 a b, b a * + a * +
        # IF in_function AND space between args: operation inside func (not function call). IMPORTANT: Count pairs of no comma between and iterate until find that many operators
        logixable_names = [logixable.name for logixable in logixables]
        cur_inner_logixable: Logixable = None
        cur_inner_logixable_arg_count = None
        func_arg_children: list[TreeNode] = [] # argument mapping for a func's args if inside a function
        operators = [o.value for o in Operator]
        parsed_inner_args = 0
        in_function = upper_logixable is not None

        postfix_token_length = range(len(split_postfix))
        iter_range = iter(postfix_token_length)
        for index in iter_range:
            token = split_postfix[index]
            print("TKN: " + token)
            if not token:
                raise ValueError("Empty token in postfix expression at %s index!" % index)

            # function (the one defined here) inside function (the one called top-level) inside function (the one defined OVERALL for this LogixableDefinition)
            # print("UPP LOGIX: " + str(upper_logixable) if upper_logixable is not None else 'NOTHING')
            # print("PARSED INN_ : " + str(parsed_inner_args))
            if in_function and len(allowed_args) == parsed_inner_args:
                # parsed all available/correct inner args; means next stuff cannot be an inner function argument, but a new node w/ a new function call w/ an operator attached later on!
                self.__last_validated_logixable_idx_offset += parsed_inner_args # idx offset to add after going back to top-level recursion (not +1  to cause reiteration and check for all conditions again)
                parsed_inner_args = 0
                return TreeNode(None, func_arg_children) # value node; return only operands because there are no more inner functions (impossible)

            if token in logixable_names:
                cur_inner_logixable = next(l for l in logixables if token == l.name)
                cur_inner_logixable_arg_count = len(cur_inner_logixable.args)

                # this should return a node that describes "func func a" or "func1 a b, b a * +" 
                # recursion until exit node and then add this one BIG logixable node and its arg relations children (whether they be args or logixables) to the tree
                parsed_inner_args += 1
                print("ENTERING REC;")
                func_node = self.__build_expression_tree(split_postfix[index+1:], cur_inner_logixable.args, cur_inner_logixable, tree_builder)

                total_children = [func_node, *func_arg_children] if func_node.value is not list else func_node.value + func_arg_children

                total_node = TreeNode(total_children, cur_inner_logixable)
                if in_function:
                    self.__last_validated_logixable_idx_offset += len(upper_logixable.args)
                    return total_node
                else: 
                    # if node not exists w/ value cur_inner_logixable: add
                    # otherwise append to children
                    existing_node = self.__find_logixable_in_tree_builder(cur_inner_logixable, tree_builder)
                    if existing_node is None:  
                        tree_builder.push(StackNode(total_node))
                    else:
                        existing_node.value.add_children(total_children)

                    # handle if a new function is next to call
                    total_offset = self.__last_validated_logixable_idx_offset + index
                    if total_offset in postfix_token_length and split_postfix[total_offset] in logixable_names:
                        self.__last_validated_logixable_idx_offset -= 1
            
                    consume(iter_range, self.__last_validated_logixable_idx_offset)
                    self.__last_validated_logixable_idx_offset = 0
            elif token in operators:
                if token == Operator.LEFT_PARENTHESIS or token == Operator.RIGHT_PARENTHESIS:
                    raise ValueError("Invalid input! Postfix expressions should not have parentheses!")

                new_node = None
                if token != Operator.NOT:
                    right = tree_builder.pop().value
                    left = tree_builder.pop().value
                    new_node = TreeNode([left, right], token)
                else:
                    unary = tree_builder.pop().value
                    new_node = TreeNode([unary], token)

                tree_builder.push(StackNode(new_node))
            else:
                if not in_function:
                    if token not in allowed_args:
                        raise ValueError('Argument \'%s\' in definition is not defined in allowed arguments!' % token)
                    print("PUSHING NORMAL OPERANT")
                    tree_builder.push(StackNode(TreeNode(None, token)))
                    continue
            
                # ----- Handle invalid argument count for function ----
                if parsed_inner_args > len(allowed_args):
                    raise ValueError('Invalid argument count for function \'%s\'! Expected count was %s arguments but received %s instead!' % cur_inner_logixable.name, cur_inner_logixable_arg_count, parsed_inner_args)

                clean_token = token
                if token[-1] == ',':
                    clean_token = token[:-1]

                if clean_token not in allowed_args:
                    raise ValueError('Argument \'%s\' in definition is not defined in allowed arguments!' % clean_token)
                print("PUSHING FUNC OPERANT")

                parsed_inner_args += 1

                func_arg_children.append(TreeNode(None, clean_token))
        self.__last_validated_logixable_idx_offset = 0
        top_node = tree_builder.pop()

        if not tree_builder.is_empty():
            raise ValueError('Invalid input! Please, check your expression syntax! Expression tree builder stack is not empty!')

        return top_node.value

    # yeah this is the downside to using a LL here but it's needed
    # this would've been in the stack class had it not required explicitly checking tree nodes
    def __find_logixable_in_tree_builder(self, value: 'Logixable', tree_builer: Stack) -> StackNode:
        if tree_builer.size == 0:
            return None

        temp = tree_builer.head
        while temp != None:
            if isinstance(temp.value, TreeNode) and temp.value.value == value:
                return temp
            temp = temp.prev
        return None


    def solve(self, node: TreeNode):
        # go down the tree and stack-ify it?
        # if going back in reverse: 
        #   if top-level parent is LOGIXABLE and has no logixables inside it: iterate between all children nodes, assign arguments from valid_args, and perform operations
        #   if child is argument: check argument value by indexing it with args and arg_values
        #   if child is operator: perform operation with last two children with operator
        #   if child is LOGIXABLE: call `.solve()` and coalesce the results together.
        #       then lookup logixable w/ is and place args accordingly
        #       if arg in lookup is LOGIXABLE AGAIN: recursion to `.solve()` to loop and further check argument relation
        #       if VALUES correspond to LOGIXABLE args from memoized_solutions array: USE MEMOIZED SOLUTION!
        #   continue until reach stack empty/bottom of tree?

        # if node.value is LogixableDefinition:

        # TODO: Add any solved logixables to memoized_solutions array

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

    def __str__(self) -> str:
        return "(Name: %s. Allowed args: %s)" % (self.name, self.args)

    def __repr__(self) -> str:
        return self.__str__()

# global list of defined logixables for the program at any point; TODO: Save somewhere else
logixables: list[Logixable] = []
# memoized solutions to use when solving already calculated funcs. Contains logixable reference (key), list of values for args (1-to-1 relationship), and answer to operation
memoized_solutions: list[(Logixable, list[int], bool)] = []