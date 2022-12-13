import models.logixable as logix_blueprint
from data_structs.tree import TreeNode, Tree
from models.operators import Operator
from utils.permutations import permutations
import string
import copy

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
    # TODO: Filter out trees like "a & b & c" when tree "b & a & c" is found as a solution
    # TODO: Support trees with increasingly larger height (DP)
    def __find_logixable_tree_from_truth_table_internal(self, truth_table: list[list[bool]], 
            cur_logixables: list[logix_blueprint.Logixable], logixable_definitions: list[logix_blueprint.LogixableDefinition],
            cur_tree: Tree = None,
            upper_node_parent: TreeNode = None,
            upper_node: TreeNode = None, current_tree_height: int = 0):
        at_top = upper_node is None or current_tree_height == 0
        
        max_args = len(truth_table[0])
        allowed_logixables = self.__generate_allowed_logixables(cur_logixables, max_args)
        allowed_args = string.ascii_lowercase[:max_args]
        allowed_operands = [*allowed_logixables, allowed_args] # plug in args as well in the allowed operands
        operators = list(Operator)

        if at_top:
            # generate pairs of operands applicable
            operand_pairs = [(left_operand, right_operand) for idx, left_operand in enumerate(allowed_operands) for right_operand in allowed_operands[idx + 1:]]
            top_trees: list[logix_blueprint.Tree] = []
            for operands in operand_pairs:
                left = operands[0]
                right = operands[1]
                for operator in operators:
                    top_trees.append(Tree(TreeNode([TreeNode(None, left), TreeNode(None, right)], str(operator))))

            # contains arg permutations for logixables
            top_logixable_candidates: list[logix_blueprint.LogixableDefinition] = [*list(map(lambda l: l.definition, allowed_logixables)), *list(map(lambda tt: logix_blueprint.LogixableDefinition(expr_tree=tt), top_trees))]

            # SOLVE
            # TODO: Handle logixables where you can't put the entire row in -> we can insert the entire row as long as all combinations are made because they just won't be indexed
            for candidate in top_logixable_candidates:
                tree = candidate.expr_tree
                

    

            valid_tree_ = list(filter(lambda lc: lc.definition.root.children is not None, top_logixable_candidates)) # omit top-level logixables FOR NOW TODO: Support func calls inside func calls

            # generate permutations

            # logixable_definition_triplets = [()] -> triplets with two operands and one operator from set
            # logixable_definition_candidates = map( ) -> map to logixabledefinition-s
            # for logixable_def in logixable_definition_candidates:
            #   self.__find_logixable_tree_from_truth_table_internal 

            pass
        elif current_tree_height < self.__max_allowed_tree_height:
            # if upper node is logixable:
            #   check using logixable inside logixable

            #if isinstance(upper_node, logix_blueprint.Logixable):
                # do not add defined logixables to this node; instead, replace it (e.g. disallow function in function)
                # pass

            # self.__find_logixable_from_truth_table_internal_depth_handle(truth_table, cur_logixables, logixable_definitions, cur_tree, upper_node, current_tree_height + 1)
            # for child in children:
                # if not isinstance(child, Logixable): ?
                #   invalid (everything should be wrapped in a logixable)   
            #     possible_logixable_arg_permutations = [LogixableDefinition(allowed_args=(permutation --> ['a', 'b'], ['b', 'a']), expr_tree=child.definition.tree)]
            #     for permutation in possible_logixable_arg_permutations:
            #       valid_solution = True
            #       for row in truth_table:
            #            valid_solution &= permutation.solve(row)
            #       if valid_solution:
            #           logixable_definitions.append(permutation)
            #    pass

            # return None # reached top
            pass
        else:
            raise RecursionError()

    # gives allowed logixables with all permutations of args so that they work with truth table
    def __generate_allowed_logixables(self, cur_logixables: list[logix_blueprint.Logixable], max_args: int):
        allowed_logixables = list(filter(lambda l: len(l.args) <= max_args, cur_logixables))
        for logixable in allowed_logixables:
            for arg_perm in permutations(logixable.args):
                new_logix = copy.deepcopy(logixable)
                new_logix.args = arg_perm
                allowed_logixables.append(new_logix)
        return allowed_logixables
    
    def __find_logixable_from_truth_table_internal_depth_handle(self, truth_table: list[list[bool]], 
            cur_logixables: list[logix_blueprint.Logixable], logixable_definitions: list[logix_blueprint.LogixableDefinition], 
            cur_tree: Tree = None,
            upper_node: TreeNode = None, upper_node_parent: TreeNode = None,
            current_tree_height: int = 0):
            at_top = upper_node is None or current_tree_height == 0
            try:
                return self.__find_logixable_tree_from_truth_table_internal(truth_table, cur_logixables, logixable_definitions, upper_node, upper_node_parent, cur_tree, current_tree_height + 1)
            except RecursionError:
                if at_top:
                    # terminate execution for this tree specifically (don't add?)
                    # will this work??
                    return
                else:
                    raise RecursionError() # delegate to top
                

    def find_logixable_from_truth_table(self, truth_table: list[list[bool]], cur_logixables: list[logix_blueprint.LogixableDefinition]) -> list[logix_blueprint.Logixable]:
        if len(truth_table) != 0 and len(truth_table) != len(truth_table[0]):
            raise ValueError("Truth table must be a matrix!")

        logixable_trees: list[logix_blueprint.LogixableDefinition] = []
        self.__find_logixable_tree_from_truth_table_internal(truth_table, cur_logixables, logixable_trees)
        return logixable_trees