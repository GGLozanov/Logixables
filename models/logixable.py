from data_structs.stack import StackNode, Stack
from data_structs.tree import TreeNode, Tree
from models.operators import Operator
from utils.consume import consume
from utils.binary_permutations import binary_permutations
from utils.str_join import str_join

class LogixableDefinition:
    def __init__(self, split_postfix: list = [], allowed_args: list = [], expr_tree: Tree | None = None):
        self.split_postfix_input = split_postfix
        self.__last_validated_logixable_idx_offset = 0
        self.expr_tree = expr_tree if expr_tree is not None else Tree(self.__build_expression_tree(split_postfix, allowed_args))
        print(self.expr_tree)

    # this method makes me want to commit seppuku
    # TODO: Handle func(a | b, b) etc. by treating operands as functions and going in recursion for them too (this would be hard because of current postfix notation schema)
    # TODO: Maybe initiate search for operator when find "a b," pair of func args and then attach to first operator (non-recursive)
    # TODO: Handle no-arg methods/funcs
    def __build_expression_tree(self, split_postfix: list, allowed_args: list, upper_logixable: 'Logixable' = None, tree_builder: Stack = Stack()) -> TreeNode:
        logixable_names = [logixable.name for logixable in logixables]

        operators = [o.value for o in Operator]
        cur_inner_logixable: Logixable = None
        cur_inner_logixable_arg_count = None

        func_arg_children: list[TreeNode] = [] # argument mapping for a func's args if inside a function
        parsed_inner_args = 0
        in_function = upper_logixable is not None

        postfix_token_length = range(len(split_postfix))
        iter_range = iter(postfix_token_length)

        for index in iter_range:
            token = split_postfix[index]
            if not token:
                raise ValueError("Empty token in postfix expression at %s index!" % index)

            # function (the one defined here) inside function (the one called top-level) inside function (the one defined OVERALL for this LogixableDefinition)
            if in_function and len(allowed_args) == parsed_inner_args:
                # parsed all available/correct inner args; means next stuff cannot be an inner function argument, but a new node w/ a new function call w/ an operator attached later on!
                self.__last_validated_logixable_idx_offset += parsed_inner_args # idx offset to add after going back to top-level recursion (not +1  to cause reiteration and check for all conditions again)
                
                # clean func context here but it doesn't matter
                # parsed_inner_args = 0

                return TreeNode(None, func_arg_children) # value node; return only operands because there are no more inner functions (impossible)

            if token in logixable_names:
                if not in_function:
                    parsed_inner_args = 0

                cur_inner_logixable = next(l for l in logixables if token == l.name)
                cur_inner_logixable_arg_count = len(cur_inner_logixable.args)

                # this should return a node that describes "func func a" or "func1 a b, b a * +" 
                # recursion until exit node and then add this one BIG logixable node and its arg relations children (whether they be args or logixables) to the tree
                func_node = self.__build_expression_tree(split_postfix[index+1:], cur_inner_logixable.args, cur_inner_logixable, tree_builder)

                total_children = [func_node, *func_arg_children] if not isinstance(func_node.value, list) else func_node.value + func_arg_children

                total_node = TreeNode(total_children, cur_inner_logixable)
                if in_function:
                    self.__last_validated_logixable_idx_offset += len(upper_logixable.args)
                    return total_node
                else: 
                    # if node not exists w/ value cur_inner_logixable: add
                    # otherwise append to children
                    parsed_inner_args += self.__calculate_top_func_children_len(total_children)

                    still_in_func = parsed_inner_args != 0 and parsed_inner_args != cur_inner_logixable_arg_count
                    if not still_in_func:
                        parsed_inner_args = 0
                        cur_inner_logixable = None
                        cur_inner_logixable_arg_count = None
                        tree_builder.push(StackNode(total_node))
                    else:
                        self.__add_to_top_node_children(total_node, tree_builder)

                    # handle if a new function is next to call
                    # total_offset = self.__last_validated_logixable_idx_offset + index
                    # total_offset in postfix_token_length and split_postfix[total_offset] in logixable_names
                    if still_in_func:
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

                    total_node = TreeNode(None, token)

                    # hacks for top-level recursion where parsed_inner_args is added but in_function is False
                    if parsed_inner_args != 0 and parsed_inner_args != cur_inner_logixable_arg_count:
                        self.__add_to_top_node_children(total_node, tree_builder)
                        parsed_inner_args += 1
                    else:
                        parsed_inner_args = 0
                        cur_inner_logixable = None
                        cur_inner_logixable_arg_count = None
                        tree_builder.push(StackNode(total_node))

                    continue
            
                # ----- Handle invalid argument count for function ----
                if parsed_inner_args > len(allowed_args):
                    raise ValueError('Invalid argument count for function \'%s\'! Expected count was %s arguments but received %s instead!' % cur_inner_logixable.name, cur_inner_logixable_arg_count, parsed_inner_args)

                clean_token = token
                if token[-1] == ',':
                    clean_token = token[:-1]

                if clean_token not in allowed_args:
                    raise ValueError('Argument \'%s\' in definition is not defined in allowed arguments!' % clean_token)

                parsed_inner_args += 1

                func_arg_children.append(TreeNode(None, clean_token))
        self.__last_validated_logixable_idx_offset = 0
        top_node = tree_builder.pop()

        if not tree_builder.is_empty():
            raise ValueError('Invalid input! Please, check your expression syntax! Expression tree builder stack is not empty!')

        return top_node.value

    def __calculate_top_func_children_len(self, children: list) -> int:
        add = 0
        for child in children:
            if isinstance(child.value, TreeNode):
                add += len(child.value.args)
            else:
                add += 1    
        return add

    def __add_to_top_node_children(self, total_node: TreeNode, tree_builder: Stack):
        try:
            tb_top_node = tree_builder.pop()
        except:
            tree_builder.push(StackNode(total_node))
            return

        tb_top = tb_top_node.value
        if not isinstance(tb_top, TreeNode):
            raise ValueError("Internal error! Add to top node children called at wrong time!")
        tb_top.add_children([total_node])
        tb_top_node.value = tb_top
        tree_builder.push(tb_top_node)

    def solve(self, allowed_args: list[str], arg_values: list[str]) -> bool:
        return self.__solve(self.expr_tree.root, allowed_args, arg_values)

    def __solve(self, node: TreeNode, allowed_args: list[str], arg_values: list[bool]) -> bool:
        node_val = node.value
        node_children = node.children

        if node_children is None or len(node_children) == 0:
            return node_val # data node

        operators = [o.value for o in Operator]

        if isinstance(node_val, Logixable):
            return self.__solve_inner_logixable(node_val, allowed_args, arg_values)
        elif node_val in operators:
            if node_val != Operator.NOT:
                if len(node_children) != 2:
                    raise ValueError("Internal error! Binary operator cannot have more or fewer than two children")
                right = node_children[0]
                left = node_children[1]

                right_val = right.value
                left_val = left.value

                right_operand = None
                left_operand = None
                if isinstance(right_val, Logixable):
                    right_operand = self.__solve_inner_logixable(right_val, allowed_args, arg_values)
                elif right_val in operators:
                    right_operand = self.__solve(right, allowed_args, arg_values)
                else:
                     # this is a data node from here (e.g. arguments)
                    right_operand = arg_values[allowed_args.index(right_val)]

                if isinstance(left_val, Logixable):
                    left_operand = self.__solve_inner_logixable(left_val, allowed_args, arg_values)
                elif left_val in operators:
                    left_operand = self.__solve(left, allowed_args, arg_values)
                else:
                    left_operand = arg_values[allowed_args.index(left_val)]

                if node_val == Operator.AND:
                    return right_operand & left_operand
                elif node_val == Operator.OR:
                    return right_operand | left_operand
            else:
                if len(node_children) != 1:
                    raise ValueError("Internal error! Unary operator cannot have more or less than one child!")
                operand = arg_values[allowed_args.index(node_children[0].value)]
                
                if isinstance(operand, Logixable):
                    operand = self.__solve_inner_logixable(operand, allowed_args, arg_values)
                return not operand
                
        return node_val

    def __solve_inner_logixable(self, node_val: 'Logixable', allowed_args: list[str], arg_values: list[str]) -> bool:
        inner_logixable_allowed_args = node_val.args
        matching_logixable_args = filter(lambda e: e[0] in inner_logixable_allowed_args, allowed_args)
        matching_logixable_args_idxs = [allowed_args.index(matching_logixable_arg) for matching_logixable_arg in matching_logixable_args]
        matching_logixable_arg_values = [arg_values[matching_logixable_args_idx] for matching_logixable_args_idx in matching_logixable_args_idxs]

        # BAD REPEAT HERE FIXME
        memoized_solution = logixable_solution_in_memoized_solutions(node_val, arg_values)
        if memoized_solution is not None:
            return memoized_solution

        # access definition directly to override allowed args
        solution = node_val.definition.solve(allowed_args, matching_logixable_arg_values)
        memoized_solutions.append((node_val, arg_values, solution))
        return solution

class Logixable:
    def __init__(self, name: str, args: list, definition: LogixableDefinition = None) -> None:
        self.name = name
        self.args = args
        self.definition = definition
        pass

    def solve(self, arg_values: list[bool]) -> bool:
        if len(arg_values) != len(self.args):
            raise ValueError("Argument value count must be the same as arguments of function!")

        memoized_solution = logixable_solution_in_memoized_solutions(self, arg_values)
        if memoized_solution is not None:
            return memoized_solution
    
        solution = self.definition.solve(self.args, arg_values)
        memoized_solutions.append((self, arg_values, solution))
        return solution

    def define(self, split_postfix: str):
        self.definition = LogixableDefinition(split_postfix, self.args)

    def generate_truth_table(self) -> str:
        truth_table: list[str] = []
        perms = binary_permutations(len(self.args))

        truth_table.append(str_join(self.args, " | ") + " Result")
        for perm in perms:
            solution = self.solve(perm)
            truth_table.append(str_join(list(map(int, perm)), " | ") + ("%s" % int(solution)))
        return str_join(truth_table, "\n")

    def visualize(self):
        pass

    def __str__(self) -> str:
        return "(Name: %s. Allowed args: %s)" % (self.name, self.args)

    def __repr__(self) -> str:
        return self.__str__()

# global list of defined logixables for the program at any point; TODO: Save somewhere else
logixables: list[Logixable] = []

# FIXME: This should be moved (muahaha, all the spaghetti!)
# memoized solutions to use when solving already calculated funcs. Contains logixable reference (key), list of values for args (1-to-1 relationship), and answer to operation
memoized_solutions: list[(Logixable, list[int], bool)] = []

def logixable_solution_in_memoized_solutions(logixable: Logixable, arg_values: list[str]) -> bool | None:
    try:
        memoized_matching = next(m_s for m_s in memoized_solutions if m_s[0] is logixable and m_s[1] == arg_values)
        if memoized_matching is None:
            return None

        if len(memoized_matching) != 3:
            raise ValueError("Internal error! Memoized solution storage access failure!")

        return memoized_matching[2] # bool value stored as solution
    except StopIteration:
        return None
