from enum import StrEnum

class Operator(StrEnum):
    OR = '|'
    AND = '&'
    NOT = '!'
    LEFT_PARENTHESIS = '('
    RIGHT_PARENTHESIS = ')'