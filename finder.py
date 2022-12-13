import models.logixable as logix_blueprint
from data_structs.tree import TreeNode, Tree
from models.operators import Operator
from utils.generic_combinatorics import permutations, combinations
import string
import copy

# TODO: Support trees with funcs inside funcs and operators inside func args
# TODO: Filter out trees like "a & b & c" when tree "b & a & c" is found as a solution
# TODO: Support trees with increasingly larger height (DP)
class LogixableFinder:
    
    # 3 sets: operator set, function set, argument set
    # function set and operator set get truncated depending on current_tree_height and allowed_arg length of each logixable in cur_logixables
    # then combinations from that are produced
    # then, each one gets called `.solve()` (each one is logixable) with **ALL** the rows of the truth table for **ALL** of the permutations of the allowed_args list in the LogixableDefinition [to test funca(a,b) and funca(b, a)]. 
    # The tree is solved and checked if it can be satisifed now
    # all trees which satisfy the condition are returned, all which do not => recursion
    # __exhausted_possible_combinations_for_iter reached once certain limit is reached --> the cutoff for all tree generations. If certain logixable depth is reached, abandon solution and raise exception?
    # Uses SOP
    def __find_logixable_tree_from_truth_table_internal(self, truth_table: list[list[bool]], 
            cur_logixables: list[logix_blueprint.Logixable],
            upper_node: TreeNode = None, current_tree_height: int = 0) -> list[logix_blueprint.LogixableDefinition]:
        at_top = upper_node is None or current_tree_height == 0
        
        max_args = len(truth_table[0])
        allowed_logixables = self.__generate_allowed_logixables(cur_logixables, max_args)
        allowed_args = string.ascii_lowercase[:max_args]
        operators = list(Operator)

        logixable_definitions: list[logix_blueprint.LogixableDefinition] = []
        candidate_solutions: list[list[Tree]] = [] # joined by OR or operator at the end
        sop_trees: list[Tree] = []
        sop_truth_table_rows = list(filter(lambda r: r[len(truth_table) - 1] == 1, truth_table))
        for sop_row in sop_truth_table_rows:
            sop_trees.append(self.__generate_SOP_tree(sop_row))
        candidate_solutions.append(sop_trees)

        tree_combinations = list(filter(lambda c: len(c) == 0, combinations(sop_trees)))
        for combination in tree_combinations:
            pass

        # if at_top:
            # generate pairs of operands applicable
            # operand_pairs = [(left_operand, right_operand) for idx, left_operand in enumerate(allowed_operands) for right_operand in allowed_operands[idx + 1:]]
            # top_trees: list[logix_blueprint.Tree] = []
            # for operands in operand_pairs:
            #     left = operands[0]
            #     right = operands[1]
            #     for operator in operators:
            #         top_trees.append(Tree(TreeNode([TreeNode(None, left), TreeNode(None, right)], str(operator))))

            # # contains arg permutations for logixables
            # top_logixable_candidates: list[logix_blueprint.LogixableDefinition] = [*list(map(lambda l: l.definition, allowed_logixables)), *list(map(lambda tt: logix_blueprint.LogixableDefinition(expr_tree=tt), top_trees))]

            # # SOLVE
            # # TODO: Handle logixables where you can't put the entire row in -> we can insert the entire row as long as all combinations are made because they just won't be indexed
            # for candidate in top_logixable_candidates:
            #     tree = candidate.expr_tree
            # valid_tree_ = list(filter(lambda lc: lc.definition.root.children is not None, top_logixable_candidates)) # omit top-level logixables FOR NOW TODO: Support func calls inside func calls

            # generate permutations

            # logixable_definition_triplets = [()] -> triplets with two operands and one operator from set
            # logixable_definition_candidates = map( ) -> map to logixabledefinition-s
            # for logixable_def in logixable_definition_candidates:
            #   self.__find_logixable_tree_from_truth_table_internal 
        # elif current_tree_height < self.__max_allowed_tree_height:
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
        for candidate_solution in candidate_solutions:
            candidate_tree = self.__generate_merger_tree(candidate_solution, Operator.OR)
            logixable_definitions.append(logix_blueprint.LogixableDefinition(expr_tree=candidate_tree))

        return logixable_definitions

    # gives allowed logixables with all permutations of args so that they work with truth table
    def __generate_allowed_logixables(self, cur_logixables: list[logix_blueprint.Logixable], max_args: int):
        allowed_logixables = list(filter(lambda l: len(l.args) <= max_args, cur_logixables))
        for logixable in allowed_logixables:
            for arg_perm in permutations(logixable.args):
                new_logix = copy.deepcopy(logixable)
                new_logix.args = arg_perm
                allowed_logixables.append(new_logix)
        return allowed_logixables

    def __generate_SOP_tree(self, sop_row: list[bool]) -> Tree:
        sop_row_args = sop_row[:-1]
        sop_nodes: list[TreeNode] = []
        for arg in sop_row_args:
            if arg == True:
                sop_nodes.append(TreeNode(None, arg))
            else:
                sop_nodes.append(TreeNode([arg], str(Operator.NOT)))
        return self.__generate_merger_tree(sop_nodes, Operator.AND)

    def __generate_merger_tree(self, trees: list[Tree], join_operator: Operator) -> Tree:
        nodes = list(map(lambda t: t.root, trees))
        return self.__generate_merger_tree(nodes, join_operator)

    def __generate_merger_tree(self, nodes: list[TreeNode], join_operator: Operator) -> Tree:
        if len(nodes) < 2 and join_operator != Operator.NOT:
            raise ValueError("Invalid nodes to construct operator tree")
        nodes_r = nodes[::-1]

        while len(nodes_r) != 0:
            if join_operator == Operator.NOT:
                node = nodes_r.pop()
                nodes_r.append(TreeNode([node], str(join_operator)))
            else:
                node_r = nodes_r.pop()
                node_l = nodes_r.pop()

                nodes_r.append(TreeNode([node_r, node_l], str(join_operator)))

        try:
            root = nodes_r.pop()
        except:
            raise ValueError("Internal error! Unbalanced amount of nodes for merger tree!")

        return Tree(root)
        
    def find_logixable_from_truth_table(self, truth_table: list[list[bool]], cur_logixables: list[logix_blueprint.LogixableDefinition]) -> list[logix_blueprint.Logixable]:
        if len(truth_table) != 0 and len(truth_table) != len(truth_table[0]):
            raise ValueError("Truth table must be a matrix!")

        logixable_trees: list[logix_blueprint.LogixableDefinition] = []
        self.__find_logixable_tree_from_truth_table_internal(truth_table, cur_logixables, logixable_trees)
        return logixable_trees