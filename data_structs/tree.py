class TreeNode:
    def __init__(self, children: list['TreeNode'] | None, value: any):
        self.value = value
        self.children = children

    def add_children(self, children: list['TreeNode']):
        if self.children is not None:
            self.children += children
        else:
            self.children = children

    def __str__(self) -> str:
        return "(Value %s -> %s)" % (self.value, self.children)

    def __repr__(self):
        return self.__str__()

class Tree:
    def __init__(self, root: 'TreeNode'):
        self.root = root

    def __str__(self) -> str:
        return "{ %s }" % self.root

    def __repr__(self):
        return self.__str__()