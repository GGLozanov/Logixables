# kill me
def str_join(input: list, join_char: str):
    result = ""
    for item in input:
        result += str(item) + join_char
    return result