import models.logixable as logix_blueprint
from data_structs.tree import TreeNode, Tree
from data_structs.stack import Stack, StackNode
from data_structs.hash_table import HashTable, HashTableNode
from models.operators import Operator
from utils.generic_combinatorics import permutations, combinations
from utils.expr_tree_comparator import compare_expr_trees, extract_expr_tree_args
import string
import copy

# TODO: Support trees with funcs inside funcs and operators inside func args
# TODO: Filter out trees like "a & b & c" when tree "b & a & c" is found as a solution
# TODO: Support trees with increasingly larger height (DP)
class LogixableFinder:
    # uses SOP to find applicable functions (a more sophisticated method should be employed for further usage, such as a genetic algorithm -- but this serves well as a base-case scenario)
    # TODO: Convert TT to binary to save space
    def find_logixable_from_truth_table(self, truth_table: list[list[bool]], cur_logixables: list[logix_blueprint.Logixable]) -> list[logix_blueprint.LogixableDefinition]:
        # further validation is expected to have already been performed by parser
        if len(truth_table) <= 0:
            raise ValueError("Truth table cannot be empty!")

        logixable_definitions: list[logix_blueprint.LogixableDefinition] = []

        max_args = len(truth_table[0])
        allowed_args = string.ascii_lowercase[:max_args]

        # TODO: Use bitwise operations; can make SOP generation faster
        candidate_solutions: list[list[Tree]] = [] # joined by OR or operator at the end
        sop_trees: list[Tree] = []
        sop_truth_table_rows = list(filter(lambda r: r[len(truth_table[0]) - 1] == 1, truth_table)) # expect all tt rows to be equal; extract only where TRUE
        for sop_row in sop_truth_table_rows:
            sop_trees.append(self.__generate_SOP_tree(sop_row, allowed_args))

        # TODO: Need Quine-McCluskey simplification here otherwise function-matching won't work
        candidate_solutions.append(sop_trees)

        tree_combinations = list(filter(lambda c: len(c) != 0, combinations(sop_trees)))
        for combination in tree_combinations:
            total_tree = combination[0]
            if len(combination) != 1:
                total_tree = self.__generate_merger_tree_w_trees(combination, Operator.OR)

            for logixable in cur_logixables:
                if self.__compare_expr_tree_with_logixable(tree=total_tree, logixable=logixable):
                    # extract arg map for total_tree
                    arg_map: HashTable = HashTable(len(allowed_args))
                    self.__extract_tree_arg_mapping_for_logixable(total_tree, logixable, arg_map)
                    valid_arg_order: list[str] = []

                    # lookup args and associate their positions in a valid way
                    for arg in logixable.args:
                        valid_total_tree_arg = arg_map.find(arg)
                        valid_arg_order.append(valid_total_tree_arg)

                    # context-updated logixable
                    new_logixable = logix_blueprint.Logixable(logixable.name, valid_arg_order, total_tree)
                    # convert logixable to individual tree
                    new_logixable_solo_tree = Tree(TreeNode(map(lambda a: TreeNode(None, a), valid_arg_order), new_logixable))

                    # remove every instance of component from trees contained new logixable tree in original SOP expression
                    sop_trees_new = list(sop_trees)
                    for tree in combination:
                        if tree in sop_trees_new:
                            sop_trees_new.remove(tree)

                    # add the new logixable tree which replaces the combination that matches the logixable's expression tree to the original SOP expression
                    sop_trees_new.append(new_logixable_solo_tree)
                    # add the new SOP expression to the candidate solution
                    candidate_solutions.append(sop_trees_new)

                    # do the same for all current candidate solutions
                    for cur_candidate_solution in candidate_solutions:
                        new_candidate_solution = list(cur_candidate_solution)
                        has_func = False
                        for tree in combination:
                            if tree in sop_trees_new:
                                has_func = True
                                new_candidate_solution.remove(tree)
                        if has_func:
                            new_candidate_solution.append(new_logixable_solo_tree)
                            candidate_solutions.append(new_candidate_solution)
 
        for candidate_solution in candidate_solutions:
            candidate_tree = self.__generate_merger_tree(candidate_solution, Operator.OR)
            logixable_definitions.append(logix_blueprint.LogixableDefinition(expr_tree=candidate_tree))

        return logixable_definitions

    def __extract_tree_arg_mapping_for_logixable(self, tree: Tree, logixable: logix_blueprint.Logixable, arg_map: HashTable):
        logixable_expr_tree = logixable.definition.expr_tree
        extract_expr_tree_args(tree.root, logixable_expr_tree.root, arg_map)

    def __compare_expr_tree_with_logixable(self, tree: Tree, logixable: logix_blueprint.Logixable) -> bool:
        logixable_expr_tree = logixable.definition.expr_tree
        return compare_expr_trees(tree.root, logixable_expr_tree.root)

    # gives allowed logixables with all permutations of args so that they work with truth table
    def __generate_logixable_arg_perm(self, cur_logixables: list[logix_blueprint.Logixable], max_args: int):
        allowed_logixables = list(filter(lambda l: len(l.args) <= max_args, cur_logixables))
        for logixable in allowed_logixables:
            for arg_perm in permutations(logixable.args):
                new_logix = copy.deepcopy(logixable)
                new_logix.args = arg_perm
                allowed_logixables.append(new_logix)
        return allowed_logixables

    def __generate_SOP_tree(self, sop_row: list[bool], allowed_args: list) -> Tree:
        sop_row_args = sop_row[:-1]
        sop_nodes: list[TreeNode] = []
        for index, arg in enumerate(sop_row_args):
            if arg == True:
                sop_nodes.append(TreeNode(None, allowed_args[index]))
            else:
                sop_nodes.append(TreeNode([allowed_args[index]], Operator.NOT.value))
        return self.__generate_merger_tree(sop_nodes, Operator.AND)

    def __generate_merger_tree_w_trees(self, trees: list[Tree], join_operator: Operator) -> Tree:
        nodes = list(map(lambda t: t.root, trees))
        return self.__generate_merger_tree(nodes, join_operator)

    def __generate_merger_tree(self, nodes: list[TreeNode], join_operator: Operator) -> Tree:
        if len(nodes) < 2 and join_operator != Operator.NOT:
            raise ValueError("Invalid nodes to construct operator tree")
        
        # FIXME: this is a pointless mapping but required to keep using Stack as per requirements
        stack_head = StackNode(nodes[0])
        nodes_r_stack = Stack(stack_head)
        for node in nodes[1:]:
            new_stack_node = StackNode(node)
            nodes_r_stack.push(new_stack_node)
        # -------------------------------------------------------

        while nodes_r_stack.size > 1:
            if join_operator == Operator.NOT:
                node = nodes_r_stack.pop().value
                nodes_r_stack.push(StackNode(TreeNode([node], str(join_operator))))
            else:
                node_r = nodes_r_stack.pop().value
                node_l = nodes_r_stack.pop().value

                nodes_r_stack.push(StackNode(TreeNode([node_l, node_r], str(join_operator))))

        try:
            root = nodes_r_stack.pop().value
        except:
            raise ValueError("Internal error! Unbalanced amount of nodes for merger tree!")

        return Tree(root)