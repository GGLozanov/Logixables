class TreeNode:
    def __init__(self, children: list['TreeNode'] | None, value: any):
        self.children = children
        self.value = value

    def __str__(self) -> str:
        # TODO: Serialise tree for file
        return ""

class Tree:
    def __init__(self, root: 'TreeNode'):
        self.root = root