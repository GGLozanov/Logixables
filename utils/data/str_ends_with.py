def __ends_with(inp: str, suff: str) -> bool:
    suff_l = len(suff)
    inp_diff = len(inp) - suff_l
    inp_at_suff = inp[inp_diff:]
    return inp_at_suff == suff

def ends_with(inp: str, suffx: list[str]) -> bool:
    for suff in suffx:
        if __ends_with(inp, suff):
            return True
    return False