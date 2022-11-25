from enum import Enum

class Operator(Enum):
    OR = 1
    AND = 2
    NOT = 3 # keyed by precedence