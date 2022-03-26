from typing import NamedTuple

from asyncpg import Pool
from morecantile import Tile
from fastapi import Response

from tisrv.geo import bounding_box_helper
from tisrv.resources.mime import MimeTypes
from .collection import VectorCollection
from ..error import UnsupportedTMSException, TileOutOfRange
from ..ogc_tiles_api import GeoResourceApi


class TileQueryParams(NamedTuple):
    # the properties should be included in the tile
    properties: list[str]
    # the maximum feature number per tile, default is 5000
    limit = 5000
    # the tile extent in tile coordinate space, default is 4096
    resolution = 4096
    # the buffer distance in tile coordinate space to optionally clip geometries. default is 256
    buffer = 256

    @staticmethod
    def from_collection(collection: VectorCollection):
        params = TileQueryParams(properties=[f'"{p.name}"' for p in collection.props])
        # ST_ASMVT use feature_id_name as Feature ID and any subsequent column will be added as a property
        # so this reserve the id column in the feature properties
        if collection.id_column:
            params.properties.append(f'"{collection.id_column}"')

        return params


class VectorCollectionApi(GeoResourceApi):
    def __init__(self, collection: VectorCollection):
        self.collection = collection

    def simple_description(self):
        return {
            'id': self.collection.id,
            'description': self.collection.description
        }

    def tilesets_director(self):
        return {
            'props': self.collection.props,
            'links': [
                {
                    'title': '',
                    'rel': 'http://www.opengis.net/def/rel/ogc/1.0/tilesets-vector',
                    'type': 'application/json',
                    'href': f'/collections/{self.collection.id}/tiles'
                }
            ]
        }

    def tilesets_list(self):
        return {
            'tilesets': [
                {
                    'dataType': 'vector',
                    # FIXME: same as tileset api
                    # 'crs': '',
                    # FIXME: same as tileset api
                    # 'tileMatrixSetURI': '',
                    'links': [
                        {
                            'href': f'/tileMatrixSets/{tms.identifier}',
                            'rel': 'http://www.opengis.net/def/rel/ogc/1.0/tiling-scheme',
                            'type': 'application/json',
                            'title': tms.identifier,
                        },
                        {
                            'href': f'/collections/{self.collection.id}/tiles/{tms.identifier}',
                            'rel': 'self',
                            'type': 'application/json',
                            'title': f'{self.collection.id} ({tms.identifier})',
                        }
                    ]
                }
                for tms in self.collection.supported_tms_set
            ]
        }

    def tileset(self, tms_id):
        if tms_id not in self.collection.supported_tms_set:
            raise UnsupportedTMSException(f'{tms_id} is not supported.')

        tms = self.collection.supported_tms_set[tms_id]
        tms_crs_epsg = tms.crs.to_epsg()

        return {
            'dataType': 'vector',
            # FIXME: no crs is introduced in the tileset response requirement. so ignore it here
            'crs': '',
            # FIXME: can't fetch any infomation about the tileMatrixSetURI from morecantile, so ignore it here
            'tileMatrixSetURI': '',
            'bounds': self.collection.bounds[tms_crs_epsg] if tms_crs_epsg in self.collection.bounds else None,
            'tileMatrixSetLimits': self.collection.limits[tms.identifier].to_list(),
            'links': [
                {
                    'href': f'/tileMatrixSets/{tms.identifier}',
                    'rel': 'http://www.opengis.net/def/rel/ogc/1.0/tiling-scheme',
                    'type': 'application/json',
                    'title': tms.identifier,
                },
                {
                    'href': f'/collections/{self.collection.id}/tiles/{tms_id}/{{tileMatrix}}/{{tileRow}}/{{tileCol}}',
                    'rel': 'item',
                    'type': 'application/vnd.mapbox-vector-tile',
                    'title': self.collection.table,
                    'templated': True,
                }
            ]
        }

    async def tile(self, tms_id, tile_matrix, tile_row, tile_col, extra_params):
        collection = self.collection

        if tms_id not in collection.supported_tms_set:
            raise UnsupportedTMSException(f'{tms_id} is not supported.')

        tile = Tile(tile_col, tile_row, tile_matrix)
        limits = collection.limits[tms_id]

        if tile not in limits:
            raise TileOutOfRange(f'tile {tile_matrix}/{tile_row}/{tile_col} out of range')

        tms = collection.supported_tms_set[tms_id]
        tms_csr_epsg = tms.crs.to_epsg()

        query_parameters = TileQueryParams.from_collection(collection)

        tile_bounds = tms.xy_bounds(tile)
        tile_bounds_query = bounding_box_helper.exapnd(tile_bounds, bounding_box_helper.width(tile_bounds)
                                                       * query_parameters.buffer / query_parameters.resolution)

        sql_tile_bounds = f'ST_MakeEnvelope({tile_bounds.left}, {tile_bounds.bottom}, {tile_bounds.right}, {tile_bounds.top}, {tms_csr_epsg})'
        sql_tile_bounds_query = f'ST_MakeEnvelope({tile_bounds_query.left}, {tile_bounds_query.bottom}, {tile_bounds_query.right}, {tile_bounds_query.top}, {tms_csr_epsg})'

        mvt_param_list = [f"'{collection.id}'", str(query_parameters.resolution), f"'{collection.geometry_column}'", ]
        if collection.id_column:
            mvt_param_list.append(f"'{collection.id_column}'")

        sql_parameters = {
            'TileSQL': sql_tile_bounds,
            'QuerySQL': sql_tile_bounds_query,
            'FilterSQL': '',
            'TileSrid': tms_csr_epsg,
            'Resolution': query_parameters.resolution,
            'Buffer': query_parameters.buffer,
            'Properties': '' if not query_parameters.properties else (', ' + ', '.join(query_parameters.properties)),
            'MvtParams': ', '.join(mvt_param_list),
            'Schema': collection.schema,
            'Table': collection.table,
            'GeometryColumn': collection.geometry_column,
            'Srid': collection.srid,
            'Limit': f'LIMIT {query_parameters.limit}'
        }

        sql_tile = '''
    	SELECT ST_AsMVT(mvtgeom, {MvtParams}) FROM (
    		SELECT ST_AsMVTGeom(
    			ST_Transform(ST_Force2D(t."{GeometryColumn}"), {TileSrid}),
    			bounds.geom_clip,
    			{Resolution},
    			{Buffer}
    		  ) AS "{GeometryColumn}"
    		  {Properties}
    		FROM "{Schema}"."{Table}" t, (
    			SELECT {TileSQL} AS geom_clip,
    				   ST_Transform({QuerySQL}, {Srid}) AS geom_query
    			) bounds
    		WHERE ST_Intersects(t."{GeometryColumn}", bounds.geom_query)
    			{FilterSQL}
    		{Limit}
    	) mvtgeom
        '''.format(**sql_parameters)

        pool: Pool = extra_params['pool']

        content = await pool.fetchval(sql_tile)

        return Response(content, media_type=MimeTypes.mvt.value)
