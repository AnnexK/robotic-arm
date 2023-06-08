from typing import TypeVar, MutableSequence, Callable


# Quickselect выполняет поиск k-го наименьшего элемента в S,
# также разделяя массив на меньшие и большие этого элемента
# меньшие имеют индекс меньше k, большие - больше
# less возвращает true, если первый аргумент меньше правого
T = TypeVar("T")


def quickselect(S: MutableSequence[T], k: int, less: Callable[[T, T], bool]):
    left = 0
    right = len(S) - 1

    while left < right:
        x = S[k]
        i = left
        j = right

        while True:
            while less(S[i], x):
                i += 1
            while less(x, S[j]):
                j -= 1
            if i <= j:
                S[i], S[j] = S[j], S[i]
                i += 1
                j -= 1
            if i > j:
                break
        if j < k:
            left = i
        if k < i:
            right = j
