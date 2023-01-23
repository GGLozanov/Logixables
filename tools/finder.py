import models.logixable as logix_blueprint
from data_structs.tree import TreeNode, Tree
from data_structs.stack import Stack, StackNode
from data_structs.hash_table import HashTable
from models.operators import Operator, operators
from utils.algo.generic_combinatorics import combinations
from utils.algo.expr_tree_comparator import compare_expr_trees, extract_expr_tree_args
from utils.algo.qm_expression_simplifier import QMExpressionSimplifier, Minterm
from utils.data.str_count import str_count
from utils.data.str_join import str_join
import copy
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
            raise ValueError("Truth table c annot be empty!")

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

        # this handles matching logixables for AND trees using recursion to match their children
        # TODO: Support matching for current candidate solutions as done below
        # TODO: Think of way to optimise ^ as well as current implementation as this is not really memory nor complexity efficient
        for tree in simplified_expression_sop_trees:
            new_trees = self.__find_matching_logixable_in_sop(simplified_expression_sop_trees, tree, allowed_args, cur_logixables, True)

            if new_trees != None:
                for t in new_trees:
                    sop_trees_new_rec = list(simplified_expression_sop_trees)
                    for s_tree in sop_trees_new_rec:
                        if tree == s_tree:
                            sop_trees_new_rec.remove(s_tree)

                    sop_trees_new_rec.append(t)
                    candidate_logixable_pair_solutions.append(sop_trees_new_rec)

        tree_combinations = list(filter(lambda c: len(c) != 0, combinations(simplified_expression_sop_trees)))
        for combination in tree_combinations:
            total_tree = combination[0]
            if len(combination) != 1:
                total_tree = self.__generate_merger_tree_w_trees(combination, Operator.OR)
            new_logixable_solo_tree = self.__find_matching_logixable_in_sop(simplified_expression_sop_trees, total_tree, allowed_args, cur_logixables)
            if new_logixable_solo_tree != None:
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
                candidate_tree = self.__generate_merger_tree_w_trees(candidate_solution, Operator.OR)
            logixable_definitions.append(logix_blueprint.LogixableDefinition(expr_tree=candidate_tree))

        return logixable_definitions

    def __find_matching_logixable_in_sop(self, simplified_expression_sop_trees: list[Tree], cur_total_tree: Tree, allowed_args: list[str], cur_logixables: list[logix_blueprint.Logixable], recursive_enabled = False) -> Tree | list[Tree] | None:
        for logixable in cur_logixables:
            if self.__compare_expr_tree_with_logixable(tree=cur_total_tree, logixable=logixable):
                # extract arg map for total_tree
                arg_map: HashTable = HashTable(len(allowed_args))
                self.__extract_tree_arg_mapping_for_logixable(cur_total_tree, logixable, arg_map)
                valid_arg_order: list[str] = []

                # lookup args and associate their positions in a valid way
                for arg in logixable.args:
                    valid_total_tree_arg = arg_map.find(arg)
                    valid_arg_order.append(valid_total_tree_arg)

                # context-updated logixable
                new_logixable = logix_blueprint.Logixable(logixable.name, valid_arg_order, cur_total_tree)
                # convert logixable to individual tree
                new_logixable_solo_tree = Tree(TreeNode(list(map(lambda a: TreeNode(None, a), valid_arg_order)), new_logixable))

                return new_logixable_solo_tree
            elif recursive_enabled:
                total_sop_trees_new = []
                cur_total_tree_root = cur_total_tree.root

                if cur_total_tree_root.children == None:
                    return None

                for child_idx in range(len(cur_total_tree_root.children)):
                    child = cur_total_tree_root.children[child_idx]
                    if child is None:
                        continue

                    if child.value in operators:
                        # TODO: Support function inside function; switch to True and parse as parsed after recursive calls
                        rec_logixable_tree = self.__find_matching_logixable_in_sop(simplified_expression_sop_trees, Tree(child), allowed_args, cur_logixables, False)
                        if rec_logixable_tree != None:
                            # FIXME: This isn't really memory-efficient x_x
                            cur_tree_cpy = copy.deepcopy(cur_total_tree)
                            cur_tree_cpy.root.children[child_idx] = rec_logixable_tree.root
                            total_sop_trees_new.append(cur_tree_cpy)
                return total_sop_trees_new
        return None


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
        if len(expression_minterms) == 1 and str_count(expression_minterms[0].bin_value, "-") == len(expression_minterms[0].implicants):
            return Tree(TreeNode(None, 'True'))

        # convert to list of treenodes and join with OR
        nodes: list[TreeNode] = []
        for minterm in expression_minterms:
            args_stack = Stack()
            iter_minterm_val = minterm.bin_value[2:]
            for idx in range(len(iter_minterm_val)): # skip out 0b
                char = iter_minterm_val[idx]
                if char == "0":
                    args_stack.push(StackNode(TreeNode([TreeNode(None, allowed_args[idx])], Operator.NOT)))
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