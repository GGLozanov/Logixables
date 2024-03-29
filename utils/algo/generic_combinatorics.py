def combinations(items):
    if len(items) == 0:
        return [[]]
    cs = []
    for c in combinations(items[1:]):
        cs += [c, c+[items[0]]]
    return cs

def permutations(elements):
    if len(elements) <= 1:
        yield elements
        return
    for perm in permutations(elements[1:]):
        for i in range(len(elements)):
            yield perm[:i] + elements[0:1] + perm[i:]