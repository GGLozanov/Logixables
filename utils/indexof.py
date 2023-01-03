def index_of(l: list, element):
    for index, li in enumerate(l):
        if li == element:
            return index
    raise ValueError("Item %s not in list" % str(element))