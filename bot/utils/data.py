from typing import Sequence


def flatten(seq: Sequence[str | int | float | Sequence[str]]) -> Sequence[str | int | float]:
    result = []
    for item in seq:
        if not isinstance(item, Sequence):
            result.append(item)
        else:
            for value in item:
                result.append(value)
    return result
