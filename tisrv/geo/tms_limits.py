from dataclasses import dataclass

from morecantile import BoundingBox, TileMatrixSet, Tile


@dataclass
class TileMatrixLimit:
    tile_matrix: int
    min_tile_row: int
    max_tile_row: int
    min_tile_col: int
    max_tile_col: int

    def to_dict(self):
        return {
            'tileMatrix': self.tile_matrix,
            'minTileRow': self.min_tile_row,
            'maxTileRow': self.max_tile_row,
            'minTileCol': self.min_tile_col,
            'maxTileCol': self.max_tile_col
        }


class TileMatrixSetLimits:
    _limits_map: dict[int, TileMatrixLimit]

    def __init__(self, tms: TileMatrixSet, bounds: BoundingBox, zooms: list[int]):
        self._limits_map = {z: self._tile_matrix_limit(tms, bounds, z) for z in zooms}

    def _tile_matrix_limit(self, tms: TileMatrixSet, bounds: BoundingBox, zoom: int) -> TileMatrixLimit:
        xmin, ymin, xmax, ymax = bounds

        ul_tile = tms._tile(xmin, ymax, zoom)
        lr_tile = tms._tile(xmax, ymin, zoom)

        return TileMatrixLimit(tile_matrix=zoom,
                               min_tile_col=ul_tile.x, max_tile_col=lr_tile.x,
                               min_tile_row=ul_tile.y, max_tile_row=lr_tile.y)

    def __contains__(self, tile: Tile):
        if tile.z not in self._limits_map:
            return False

        limits = self._limits_map[tile.z]

        if tile.x < limits.min_tile_col or tile.x > limits.max_tile_col or \
                tile.y < limits.min_tile_row or tile.y > limits.max_tile_row:
            return False

        return True

    def to_list(self):
        return [i.to_dict() for i in self._limits_map.values()]
