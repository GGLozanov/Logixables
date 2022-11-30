def binary_permutations(n) -> list:
    combinations = []
    # in range 1 MSB + n (e.g. shifted)
    for i in range(1 << n):
        s = bin(i)[2:] # 2: to cancel out MSB
        s = '0'*(n - len(s)) + s
        combinations.append(list(map(bool, map(int, list(s))))) # map to list, to bool, and then list of vals
    return combinations