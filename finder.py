import models.logixable as logix_blueprint
from data_structs.tree import TreeNode, Tree
from data_structs.stack import Stack, StackNode
from data_structs.hash_table import HashTable
from models.operators import Operator
from utils.algo.generic_combinatorics import combinations
from utils.algo.expr_tree_comparator import compare_expr_trees, extract_expr_tree_args
from utils.algo.qm_expression_simplifier import QMExpressionSimplifier, Minterm
from utils.data.str_count import str_count
from utils.data.str_join import str_join
import string

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

        max_args = len(truth_table[0]) - 1
        allowed_args = string.ascii_lowercase[:max_args]

        # TODO: Use bitwise operations; can make SOP generation faster
        candidate_logixable_pair_solutions: list[list[Tree]] = [] # joined by OR or operator at the end
        # expect all tt rows to be equal; extract only where TRUE (e.g. extract minterms) and omit result element
        sop_truth_table_rows = list(map(lambda mt: mt[:-1], list(filter(lambda r: r[len(truth_table[0]) - 1] == 1, truth_table))))

        sop_simplifier = QMExpressionSimplifier()
        expression_minterms = sop_simplifier.simplify(allowed_args, [self.__tt_row_to_binary(tt_row) for tt_row in sop_truth_table_rows])
        
        simplified_expression_sop_trees = self.__convert_qm_minterms_to_tree(expression_minterms, allowed_args)

        candidate_logixable_pair_solutions.append(simplified_expression_sop_trees) # append original expression

        tree_combinations = list(filter(lambda c: len(c) != 0, combinations(simplified_expression_sop_trees)))
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
                    new_logixable_solo_tree = Tree(TreeNode(list(map(lambda a: TreeNode(None, a), valid_arg_order)), new_logixable))

                    # remove every instance of component from trees contained new logixable tree in original SOP expression
                    sop_trees_new = list(simplified_expression_sop_trees)
                    for tree in combination:
                        if tree in sop_trees_new:
                            sop_trees_new.remove(tree)

                    # add the new logixable tree which replaces the combination that matches the logixable's expression tree to the original SOP expression
                    # order doesn't matter since joined by OR with equal precedence
                    sop_trees_new.append(new_logixable_solo_tree)
                    # add the new SOP expression to the candidate solution
                    candidate_logixable_pair_solutions.append(sop_trees_new)

                    # do the same for all current candidate solutions
                    for cur_candidate_solution in candidate_logixable_pair_solutions:
                        new_candidate_solution = list(cur_candidate_solution)
                        has_func = False
                        for tree in combination:
                            if tree in sop_trees_new:
                                has_func = True
                                new_candidate_solution.remove(tree)
                        if has_func:
                            new_candidate_solution.append(new_logixable_solo_tree)
                            candidate_logixable_pair_solutions.append(new_candidate_solution)
 
        for candidate_solution in candidate_logixable_pair_solutions:
            candidate_tree = candidate_solution[0]
            if len(candidate_solution) > 1:
                candidate_tree = self.__generate_merger_tree(candidate_solution, Operator.OR)
            logixable_definitions.append(logix_blueprint.LogixableDefinition(expr_tree=candidate_tree))

        return logixable_definitions

    def __tt_row_to_binary(self, tt_row: list[bool]):
        return '0b' + str_join(['1' if x else '0' for x in tt_row], '')

    def __extract_tree_arg_mapping_for_logixable(self, tree: Tree, logixable: logix_blueprint.Logixable, arg_map: HashTable):
        logixable_expr_tree = logixable.definition.expr_tree
        extract_expr_tree_args(tree.root, logixable_expr_tree.root, arg_map)

    def __compare_expr_tree_with_logixable(self, tree: Tree, logixable: logix_blueprint.Logixable) -> bool:
        logixable_expr_tree = logixable.definition.expr_tree
        return compare_expr_trees(tree.root, logixable_expr_tree.root)

    def __convert_qm_minterms_to_tree(self, expression_minterms: list[Minterm], allowed_args: list[str]) -> list[Tree]:
        # pure 0 is 
        if len(expression_minterms) == 0:
            return Tree(TreeNode(None, 'False'))
        
        # only dashes means an expression that's always true
        if len(expression_minterms) == 1 and str_count(expression_minterms[0].bin_value, "-") == len(self._variables):
            return Tree(TreeNode(None, 'True'))

        # convert to list of treenodes and join with OR
        nodes: list[TreeNode] = []
        for minterm in expression_minterms:
            args_stack = Stack()
            iter_minterm_val = minterm.bin_value[2:]
            for idx in range(len(iter_minterm_val)): # skip out 0b
                char = iter_minterm_val[idx]
                if char == "0":
                    args_stack.push(StackNode(TreeNode([allowed_args[idx]], Operator.NOT)))
                elif char == "1":
                    args_stack.push(StackNode(TreeNode(None, allowed_args[idx])))

                    if args_stack.size <= 1:
                        continue

                    r = args_stack.pop().value
                    l = args_stack.pop().value
                    operands = [l, r]
                    args_stack.push(StackNode(TreeNode(operands, Operator.AND)))                    
            nodes.append(args_stack.pop().value)
        
        return list(map(lambda n: Tree(n), nodes[::-1]))

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