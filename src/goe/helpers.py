from random import randint

from pygae.math import Vec2Like


def ascii2tuple(grid: str) -> list[Vec2Like]:
    """Convert a table into a vector list.

    Takes a multi-line string containing dots (.) and hashes (#) and converts them to a list of 2d
    vectors where the set of resulting vectors identifies the position of the hashes in the ascii
    art.

    Note, vectors are centered on the ascii string.

    Returns:
        list[Vec2Like]: A list of vectors representing the location if the given hashes.
    """

    ret: list[Vec2Like] = []
    max_x, max_y = 0, 0

    for y, line in enumerate(grid.strip(" ").split('\n')):
        max_y = max(max_y, y)

        for x, c in enumerate(line.strip(" ")):
            max_x = max(max_x, x)
            if c == "#":
                ret.append((x, y))

    return [
        ((x-max_x // 2),(y-max_y // 2))
        for x,y in ret
    ]


def random_field(width: int, height: int):
    half_x: int = width // 2
    half_y: int = height // 2
    for y in range(height):
        for x in range(width):
            if randint(0, 10) < 2:
                yield (x-half_x, y-half_y)


def normalize_value(value: int|float, min_value: int|float, max_value: int|float) -> float:
    return (value - min_value) / (max_value - min_value)
