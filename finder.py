import models.logixable as logix_blueprint
from data_structs.tree import TreeNode

class LogixableFinder:
    def __init__(self):
        pass

    def __find_logixable_from_truth_table_internal(self, truth_table: list[bool], logixables: list[logix_blueprint.Logixable]) -> TreeNode:
        # use binary permutations here for logixables to test different combinations to see which one can be added to tree (call .solve())
        
        max_args = len(truth_table[0])
        if max_args > 2:
            # operator
            # logixables.append
            return

    def find_logixable_from_truth_table(self, truth_table: list[bool]) -> list[logix_blueprint.Logixable]:
        logixables: list[logix_blueprint.Logixable] = []
        self.__find_logixable_from_truth_table_internal(truth_table)
        return logixables
        
    