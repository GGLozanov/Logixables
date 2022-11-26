from enum import StrEnum

class Command(StrEnum):
    FIND = 'FIND'
    DEFINE = 'DEFINE'
    SOLVE = 'SOLVE'
    VISUALIZE = 'VISUALIZE'
    HELP = 'HELP'
    ALL = 'ALL'