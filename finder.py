import models.logixable as logix_blueprint
from data_structs.tree import TreeNode, Tree
from models.operators import Operator
import string

class LogixableFinder:
    
    def __init__(self):
        self.__max_allowed_tree_height = 4 

    # 3 sets: operator set, function set, argument set
    # function set and operator set get truncated depending on current_tree_height and allowed_arg length of each logixable in cur_logixables
    # then combinations from that are produced
    # then, each one gets called `.solve()` (each one is logixable) with **ALL** the rows of the truth table for **ALL** of the permutations of the allowed_args list in the LogixableDefinition [to test funca(a,b) and funca(b, a)]. 
    # The tree is solved and checked if it can be satisifed now
    # all trees which satisfy the condition are returned, all which do not => recursion
    # __exhausted_possible_combinations_for_iter reached once certain limit is reached --> the cutoff for all tree generations. If certain logixable depth is reached, abandon solution and raise exception?
    # TODO: Exclude combinations with operators that don't make sense/reduplicate logic (like putting "!" when the upper node is "!")
    # TODO: Support trees with funcs inside funcs and operators inside func args
    # TODO: Support trees with increasingly larger height (DP)
    def __find_logixable_tree_from_truth_table_internal(self, truth_table: list[list[bool]], 
            cur_logixables: list[logix_blueprint.Logixable], logixable_definitions: list[logix_blueprint.LogixableDefinition],
            cur_tree: Tree = None,
            upper_node: TreeNode = None, current_tree_height: int = 0) -> TreeNode | None:
        cur_node: TreeNode = None
        at_top = upper_node is None or current_tree_height == 0
        
        max_args = len(truth_table[0])
        allowed_logixables = list(filter(lambda l: len(l.args) <= max_args))
        allowed_operands = [*allowed_logixables, string.ascii_lowercase[:max_args]] # plug in args as well in the allowed operands
        operators = list(Operator)

        if at_top:
            # operator combinations w/ and w/o funcs
            # logixable_definitions.append()
            # only operators w/ just funcs with args <= max_args or just 2 args (if max_args >= 2) or funcs and 1 arg.
            
            # logixable_definition_triplets = [()] -> triplets with two operands and one operator from set
            # logixable_definition_candidates = map( ) -> map to logixabledefinition-s
            # for logixable_def in logixable_definition_candidates:
            #   self.__find_logixable_tree_from_truth_table_internal 

            pass
        elif current_tree_height < self.__max_allowed_tree_height:
            # if upper node is logixable:
            #   check using logixable inside logixable
            if cur_node is None:
                raise ValueError("Internal error! Tree is deep enough for a current node to exist!")

            #if isinstance(upper_node, logix_blueprint.Logixable):
                # do not add defined logixables to this node; instead, replace it (e.g. disallow function in function)
                # pass

            children = self.__find_logixable_from_truth_table_internal_depth_handle(truth_table, cur_logixables, logixable_definitions, cur_tree, upper_node, current_tree_height + 1)
            for child in children:
                # if not isinstance(child, Logixable): ?
                #   invalid (everything should be wrapped in a logixable)   
            #     possible_logixable_arg_permutations = [LogixableDefinition(allowed_args=(permutation --> ['a', 'b'], ['b', 'a']), expr_tree=child.definition.tree)]
            #     for permutation in possible_logixable_arg_permutations:
            #       valid_solution = True
            #       for row in truth_table:
            #            valid_solution &= permutation.solve(row)
            #       if valid_solution:
            #           logixable_definitions.append(permutation)
                pass

            # return None # reached top
            pass
        else:
            raise RecursionError()
    
    # TODO: Validate truth table using binary permutation generator (check for exact match)

    def __find_logixable_from_truth_table_internal_depth_handle(self, truth_table: list[list[bool]], 
            cur_logixables: list[logix_blueprint.Logixable], logixable_definitions: list[logix_blueprint.LogixableDefinition], 
            cur_tree: Tree = None,
            upper_node: TreeNode = None, current_tree_height: int = 0) -> TreeNode | None:
            at_top = upper_node is None or current_tree_height == 0
            try:
                return self.__find_logixable_tree_from_truth_table_internal(truth_table, cur_logixables, logixable_definitions, upper_node, cur_tree, current_tree_height + 1)
            except RecursionError:
                if at_top:
                    # terminate execution for this tree specifically (don't add?)
                    # will this work??
                    return None
                else:
                    raise RecursionError() # delegate to top
                

    def find_logixable_from_truth_table(self, truth_table: list[list[bool]], cur_logixables: list[logix_blueprint.LogixableDefinition]) -> list[logix_blueprint.Logixable]:
        logixable_trees: list[logix_blueprint.LogixableDefinition] = []
        self.__find_logixable_tree_from_truth_table_internal(truth_table, cur_logixables, logixable_trees)
        return logixable_trees