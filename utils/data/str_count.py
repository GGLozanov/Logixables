def str_count(data: str, count_char: str, count_start = 0):
    count = 0
    for char in data[count_start:]:
        if char == count_char:
            count += 1
    return count