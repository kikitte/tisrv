from morecantile import BoundingBox
from pydantic import BaseModel

from .weblink import WebLink
from tisrv.geo.vector.collection import VectorCollectionProp


class TilesetsDirector(BaseModel):
    props: list[VectorCollectionProp]
    # /req/geodata-tilesets/desc-links:
    # the API SHALL include at least one of three link with the href
    # pointing to tilesets list for geospatial data resources and with rel
    links: list[WebLink]


class TilesetSimple(BaseModel):
    dataType: str
    crs: str
    tileMatrixSetURI: str
    # a link to the tileMatrixSet defintion, a link to the tileset
    links: list[WebLink]


class TileMatrixLimit(BaseModel):
    tileMatrix: str
    minTileRow: int
    maxTileRow: int
    minTileCol: int
    maxTileCol: int


class TileSet(TilesetSimple):
    bounds: BoundingBox | None
    tileMatrixSetLimits: list[TileMatrixLimit]


class TilesetsList(BaseModel):
    tilesets: list[TilesetSimple]
