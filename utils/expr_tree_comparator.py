import data_structs.tree as tr
import models.logixable as logix_blueprint
import models.operators as op
import data_structs.hash_table as ht

def compare_expr_trees(tree_one_node: tr.TreeNode, tree_two_node: tr.TreeNode,) -> bool:
    if tree_one_node is None and tree_two_node is None:
        return True
    operators = [operator.value for operator in op.Operator]
 
    if tree_one_node is not None and tree_two_node is not None:
        if tree_one_node.data != tree_two_node.data:
            if tree_one_node.data in operators and tree_two_node.data in operators:
                return False

            if isinstance(tree_one_node.data, logix_blueprint.Logixable):
                return compare_expr_trees(tree_one_node.definition.expr_tree.root, tree_two_node)
            elif isinstance(tree_two_node.data, logix_blueprint.Logixable):
                return compare_expr_trees(tree_one_node, tree_two_node.definition.expr_tree.root)

            return False
            
        if len(tree_one_node.children) != len(tree_two_node.children):
            return False
        
        for tree_one_child, tree_two_child in zip(tree_one_node.children, tree_two_node.children):
            if not compare_expr_trees(tree_one_child, tree_two_child):
                return False

        return True

    return False

# extracts mapped arguments for tree_one when compared with tree_two (e.g. tree_one is "[a, b, c]" but tree_two has "[as, dd, nn]" at those positions)
# expects trees are equal
# DFS-es to do so
def extract_expr_tree_args(tree_one_node: tr.TreeNode, tree_two_node: tr.TreeNode, mapped_arguments: ht.HashTable):
    if tree_one_node is None and tree_two_node is None:
        return
    operators = [operator.value for operator in op.Operator]
 
    if tree_one_node is not None and tree_two_node is not None:
        if tree_one_node.data != tree_two_node.data:
            if tree_one_node.data in operators and tree_two_node.data in operators:
                raise ValueError("AND tree for FIND not equal to logixable tree when check has passed! Can't map args!")

            if isinstance(tree_one_node.data, logix_blueprint.Logixable):
                extract_expr_tree_args(tree_one_node.definition.expr_tree.root, tree_two_node, mapped_arguments)
                return
            elif isinstance(tree_two_node.data, logix_blueprint.Logixable):
                extract_expr_tree_args(tree_one_node, tree_two_node.definition.expr_tree.root, mapped_arguments)
                return
            raise ValueError("AND tree for FIND not equal to logixable tree when check has passed! Can't map args!")
            
        if len(tree_one_node.children) != len(tree_two_node.children):
            raise ValueError("AND tree for FIND not equal to logixable tree when check has passed! Can't map args!")

        mapped_arguments.insert(tree_two_node.value, tree_one_node.value)

        for tree_one_child, tree_two_child in zip(tree_one_node.children, tree_two_node.children):
            extract_expr_tree_args(tree_one_child, tree_two_child, mapped_arguments)
            
        return

    raise ValueError("AND tree for FIND not equal to logixable tree when check has passed! Can't map args!")
    