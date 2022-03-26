from morecantile.models import BoundingBox


def exapnd(bound: BoundingBox, size):
    return BoundingBox(left=bound.left - size, right=bound.right + size,
                       top=bound.top + size, bottom=bound.bottom - size)


def width(bound: BoundingBox):
    return bound.right - bound.left


def height(bound: BoundingBox):
    return bound.top - bound.bottom
