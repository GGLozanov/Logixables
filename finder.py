import models.logixable as logix_blueprint
from data_structs.tree import TreeNode

class LogixableFinder:
    
    def __init__(self):
        self.__max_allowed_tree_height = 20 

    # 2 sets: operator set and function set
    # function set and operator set get truncated depending on current_tree_height and allowed_arg length of each logixable in cur_logixables
    # then combinations from that are produced
    # THEN, combinations with the associated argument values for each **logixable** in the combination is produced (argument associations are added as children nodes)
    # then, each one gets called `.solve()` and the tree is solved and checked if it can be satisifed now
    # all trees which satisfy the condition are returned, all who are not => recursion
    # __exhausted_possible_combinations_for_iter reached once certain limit is reached? If certain logixable depth is reached, abandon solution and raise exception?
    def __find_logixable_tree_from_truth_table_internal(self, truth_table: list[bool], 
            cur_logixables: list[logix_blueprint.Logixable], logixable_definitions: list[logix_blueprint.LogixableDefinition], 
            upper_node: TreeNode = None, current_tree_height: int = 0) -> TreeNode | None:
        # use binary permutations here for logixables to test different combinations to see which one can be added to tree (call .solve())
        # if function: add all valid argument value combinations as children nodes to logixable (then call .solve())
        cur_node: TreeNode = None
        
        max_args = len(truth_table[0])
        if current_tree_height == 0:
            if max_args > 2:
                # operator
                # try solution w/ curr
                # logixables.append

                # logixable_definitions.append(LogixableDefinition( Tree(TreeNode(operator, children))))
            # only operators w/ just funcs with args <= max_args or just 2 args (if max_args >= 2) or funcs and 1 arg.
        elif current_tree_height == 1:
            # self.__find_logixable_tree_from_truth_table_internal(truth_table, cur_logixables, cur_node, current_tree_height + 1)
            pass
        elif current_tree_height < self.__max_allowed_tree_height:
            # if upper node is logixable:
            #   check using logixable inside logixable

            if cur_node is None:
                raise ValueError("Internal error! Tree is deep enough for a current node to exist!")

            # children = __find_logixable_tree_from_truth_table_internal(truth_table, cur_logixables, logixable_definitions, upper_node, current_tree_height + 1)
            # log
            # return None # reached top
            pass
        else:
            raise RecursionError()
    
    def __find_logixable_from_truth_table_internal_depth_handle(self, truth_table: list[bool], 
            cur_logixables: list[logix_blueprint.Logixable], logixable_definitions: list[logix_blueprint.LogixableDefinition], 
            upper_node: TreeNode = None, current_tree_height: int = 0):
            try:
                self.__find_logixable_from_truth_table_internal_depth_handle
            except RecursionError as err:
                

    def find_logixable_from_truth_table(self, truth_table: list[bool], cur_logixables: list[logix_blueprint.LogixableDefinition]) -> list[logix_blueprint.Logixable]:
        logixable_trees: list[logix_blueprint.LogixableDefinition] = []
        self.__find_logixable_tree_from_truth_table_internal(truth_table, cur_logixables, logixable_trees)
        return logixable_trees