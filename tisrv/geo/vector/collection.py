from collections import namedtuple
from typing import Iterable

from asyncpg import Pool
from asyncpg import Record
from morecantile import BoundingBox

from tisrv.settings import get_geo_settings
from tisrv.geo.ogc_tiles_api import GeoResourceApi
from tisrv.geo.tms_limits import TileMatrixSetLimits

VectorCollectionProp = namedtuple('VectorCollectionProps', ['name', 'type', 'description', 'order'])


class VectorCollection():
    id: str
    schema: str
    table: str
    description: str
    geometry_column: str
    srid: int
    geometry_type: str
    id_column: str
    props: list[VectorCollectionProp]
    bounds: dict[str, BoundingBox]  # collection's data bounds in different crs
    limits: dict[str, TileMatrixSetLimits]  # tms_id -> TileMatrixSetLimits

    api: GeoResourceApi

    def __init__(self, record: Record):
        for key in record.keys():
            if key != 'props':
                setattr(self, key, record[key])
            else:
                record_props = record[key]
                self.props = [VectorCollectionProp._make(p) for p in record_props]

        self._supported_tms_set = []

    @property
    def supported_tms_set(self):
        return get_geo_settings().user_tms_set

    async def update_metadata(self, pool: Pool):
        """ Update metadata for current collection """

        if len(self.supported_tms_set):
            srid_list = [s.crs.to_epsg() for s in self.supported_tms_set]

            ''' update bounding box '''
            sql_bound = collection_bounds_sql(self, srid_list)
            records_bound = await pool.fetch(sql_bound)

            self.bounds = {}
            if records_bound[0]['xmin'] is None:
                sql_bound = collection_bounds_sql(self, srid_list, exact=True)
                records_bound = await pool.fetch(sql_bound)

            for record_bound in records_bound:
                self.bounds[record_bound['srid']] = BoundingBox(record_bound['xmin'], record_bound['ymin'],
                                                                record_bound['xmax'], record_bound['ymax'])

            ''' update tileMatrixSet limits'''
            self.limits = {}
            for tms in self.supported_tms_set:
                srid_list = tms.crs.to_epsg()
                self.limits[tms.identifier] = TileMatrixSetLimits(tms, self.bounds[srid_list],
                                                                  zooms=[int(i.identifier) for i in tms.tileMatrix])


def collection_bounds_sql(collection: VectorCollection, srid_list: list[int], exact=False):
    """
    get the bounds of collection and transform to native bound with each specificed srid
    """

    srid_set = set(srid_list)
    srid_set.add(collection.srid)

    sql_estimated_bound = f"SELECT ST_SetSRID(ST_EstimatedExtent('{collection.schema}', '{collection.table}', '{collection.geometry_column}'), {collection.srid}) AS geom"
    sql_exact_bound = f'SELECT ST_SetSRID(ST_Extent("{collection.geometry_column}"), {collection.srid}) AS geom FROM "{collection.schema}"."{collection.table}"'

    query_sql = f'''
    WITH ext AS (
        SELECT
            srids.srid AS srid,
            ST_Transform(bound.geom, srids.srid) AS geom
        FROM 
            ({sql_exact_bound if exact else sql_estimated_bound}) AS bound,
            (VALUES {', '.join(f"({s})" for s in srid_set)}) AS srids (srid)
    )
    SELECT 
        ext.srid  AS srid,
        ST_XMin(ext.geom) AS xmin,
        ST_YMin(ext.geom) AS ymin,
        ST_XMax(ext.geom) AS xmax,
        ST_YMax(ext.geom) AS ymax
    FROM ext
    '''

    return query_sql
