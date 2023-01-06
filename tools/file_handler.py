import models.logixable as logix_blueprint
import data_structs.tree
import json
import utils.algo.find_logix_w_fail
from utils.data.str_begins_ends_with import ends_with

class FileHandler:
    file_name = "logixables"
    tt_file_extensions = [".csv", ".txt"]

    def save_logixables(self, logixables: list[logix_blueprint.Logixable]):
        file = open("%s.txt" % self.file_name, "w")
        logixables_serialized = json.dumps([logixable.__dict__ for logixable in logixables], default=lambda o: o.__dict__)
        file.write(logixables_serialized)
        file.close()

    def read_logixables(self) -> list[logix_blueprint.Logixable]:
        try:
            file = open("%s.txt" % self.file_name, "r+")
            file_data = file.read()
            file.close()
            json_data = json.loads(file_data)
            logixables = []
            for json_element in json_data:
                definition = json_element["definition"]
                try:
                    definition_tree = definition["expr_tree"]["root"]
                except:
                    definition_tree = definition["expr_tree"]
                tree = data_structs.tree.Tree(self.__read_logixable_tree(definition_tree["children"], definition_tree["value"], logixables))

                logixable = logix_blueprint.Logixable(
                    json_element["name"], 
                    json_element["args"], 
                    logix_blueprint.LogixableDefinition(definition["split_postfix_input"], json_element["args"], tree))
                logixables.append(logixable)
            return logixables
        except FileNotFoundError:
            return []

    def is_valid_tt_file(self, name: str) -> bool:
        return ends_with(name, self.tt_file_extensions)

    def read_tt_file(self, name: str):
        try:
            file = open("%s" % name, "r+")
        except FileNotFoundError:
            raise ValueError("Invalid file name! File cannot be found!")
        data = file.read()
        return data

    def __read_logixable_tree(self, children, value: any, cur_logixables: list[logix_blueprint.Logixable]) -> data_structs.tree.TreeNode:
        if children is None:
            return data_structs.tree.TreeNode(None, value)

        parsed_children = []
        for child in children:
            child_val = child["value"]
            node_val = None
            if "name" in child_val and "args" in child_val:
                # logixable inside (these are always lower down because there's no way to define otherwise)
                node_val = utils.algo.find_logix_w_fail.find_logixable_with_fail(child_val["name"], cur_logixables)
            else:
                node_val = child_val

            if "children" in child and child["children"] != None:
                inner_parsed_children = []
                for inner_child in child["children"]:
                    inner_parsed_children.append(self.__read_logixable_tree(inner_child["children"], inner_child["value"], cur_logixables))
                parsed_children.append(data_structs.tree.TreeNode(inner_parsed_children, node_val))
            else:
                parsed_children.append(data_structs.tree.TreeNode(None, node_val))

        if "name" in value and "args" in value:
            value = utils.algo.find_logix_w_fail.find_logixable_with_fail(value["name"], cur_logixables)
        
        upper_node = data_structs.tree.TreeNode(parsed_children, value)
        return upper_node
        