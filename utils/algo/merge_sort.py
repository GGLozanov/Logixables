def merge_sort(arr: list):
    if len(arr) <= 1:
        return

    mid = len(arr) // 2 # rounding

    l = arr[:mid]
    r = arr[mid:]

    merge_sort(l)
    merge_sort(r)

    i = j = k = 0

    # rebuild arr
    while i < len(l) and j < len(r):
        if l[i] <= r[j]:
            arr[k] = l[i]
            i += 1
        else:
            arr[k] = r[j]
            j += 1
        k += 1

    # strap on leftovers from l
    while i < len(l):
        arr[k] = l[i]
        i += 1
        k += 1

    # strap on leftovers from r
    while j < len(r):
        arr[k] = r[j]
        j += 1
        k += 1