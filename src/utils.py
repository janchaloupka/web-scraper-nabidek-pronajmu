from typing import Iterable

def flatten(xs):
    """https://stackoverflow.com/a/2158532
    """
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x
