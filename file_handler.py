import models.logixable as logix_blueprint
import data_structs.tree
import json
import utils.find_logix_w_fail

class FileHandler:
    file_name = "logixables"

    def save_logixables(self, logixables: list[logix_blueprint.Logixable]):
        file = open("%s.txt" % self.file_name, "w")
        logixables_serialized = json.dumps([logixable.__dict__ for logixable in logixables], default=lambda o: o.__dict__)
        file.write(logixables_serialized)
        file.close()

    def read_logixables(self) -> list[logix_blueprint.Logixable]:
        try:
            import json
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
                tree = self.__read_logixable_tree(definition_tree["children"], definition_tree["value"], logixables)

                logixable = logix_blueprint.Logixable(
                    json_element["name"], 
                    json_element["args"], 
                    logix_blueprint.LogixableDefinition(definition["split_postfix_input"], json_element["args"], tree))
                logixables.append(logixable)
            return logixables
        except FileNotFoundError:
            return []

    def __read_logixable_tree(self, children: list[dict], value: any, cur_logixables: list[logix_blueprint.Logixable]) -> data_structs.tree.Tree:
        parsed_children = []
        for child in children:
            child_val = child["value"]
            node_val = None
            if "name" in child_val and "args" in child_val:
                # logixable inside (these are always lower down because there's no way to define otherwise)
                node_val = utils.find_logix_w_fail.find_logixable_with_fail(child_val["name"], cur_logixables)
            else:
                node_val = child_val
            parsed_children.append(data_structs.tree.TreeNode(child["children"], node_val))
        root = data_structs.tree.TreeNode(parsed_children, value)
        return data_structs.tree.Tree(root)
        