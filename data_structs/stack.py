class StackNode:
    def __init__(self, value) -> None:
        self.value = value
        self.prev = None

    def __str__(self) -> str:
        return str(self.value)

class Stack:
    def __init__(self, head: StackNode | None = None) -> None:
        self.head = head
        self.size = 0 if head is None else 1

    def push(self, node: StackNode):
        node.prev = self.head
        self.head = node
        self.size += 1

    def pop(self) -> StackNode:
        if self.size <= 0:
            raise ValueError("Cannot pop a stack with no elements!")
        self.size -= 1
        pop = self.head
        self.head = self.head.prev
        return pop

    def top(self) -> StackNode:
        return self.head

    def is_empty(self) -> bool:
        return self.size == 0

    # goes down the stack and prints values
    def __str__(self) -> str:
        result = ""
        temp = self.head
        if self.size == 0 :
            return "Empty"

        while temp != None:
            result += str(temp) 
            if temp.prev != None:
                result += "<-"
            temp = temp.prev
        return result