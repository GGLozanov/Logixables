def binary_permutations(n) -> list:
    combinations = []
    # 1: in range 1 MSB + n (e.g. shifted)
    for i in range(1 << n):
        s = bin(i)[2:] # 2: to cancel out 0b notation
        s = '0'*(n - len(s)) + s # 3: convert to binary & add leftover 0 bits by length minus current size of bin
        combinations.append(list(map(bool, map(int, list(s))))) # map to list, to bool, and then list of vals
    return combinations