class TreeNode:
    def __init__(self, children: list['TreeNode'] | None, value: any):
        self.children = children
        self.value = value

    def __str__(self) -> str:
        return "(Value %s -> %s)" % (self.value, self.children)

    def __repr__(self):
        return self.__str__()

class Tree:
    def __init__(self, root: 'TreeNode'):
        self.root = root

    def __str__(self) -> str:
        return "{ %s }" % self.root