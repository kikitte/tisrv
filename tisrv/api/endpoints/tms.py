from fastapi import APIRouter, Request, HTTPException
from morecantile import TileMatrixSet

from tisrv.settings import get_geo_settings

router = APIRouter()


def simple_tms_description(tms: TileMatrixSet, path: str):
    return {
        'id': tms.identifier,
        'title': tms.title,
        'links': [
            {
                'rel': 'self',
                'type': 'application/json',
                'title': f'The JSON representation of the {tms.identifier} tiling scheme definition',
                'href': f'{path}{tms.identifier}'
            }
        ]
    }


@router.get('/')
async def get_tms_list(request: Request):
    tms_list = get_geo_settings().user_tms_set

    tms_response = {
        'tileMatrixSets': [
            simple_tms_description(i, request.url.path) for i in tms_list
        ]
    }
    return tms_response


@router.get('/{tileMatrixSetId}')
async def get_tms_detail(tileMatrixSetId: str):
    tms_list = get_geo_settings().user_tms_set

    if tileMatrixSetId not in tms_list:
        raise HTTPException(status_code=404)

    return full_tms_description(tms_list[tileMatrixSetId])


def full_tms_description(tms: TileMatrixSet):
    return {
        'id': tms.identifier,
        'title': tms.title,
        'wellKnownScaleSet': tms.wellKnownScaleSet,
        # We decide to use EPSG CRS Reference, see https://docs.opengeospatial.org/DRAFTS/17-083r4.html#_crstype
        'crs': f'EPSG:{tms.crs.to_epsg()}',
        'tileMatrices': [
            {
                'id': t.identifier,
                'title': t.title, 'keywords': t.keywords,
                'tileWidth': t.tileWidth, 'tileHeight': t.tileHeight,
                'scaleDenominator': t.scaleDenominator, 'cellSize': tms._resolution(t),
                'matrixWidth': t.matrixWidth, 'matrixHeight': t.matrixHeight,
                # In the newest version of 'OGC Two Dimensional Tile Matrix Set and Tile Set Metadata', topLeftCorner is replaced with 'cornerOfOrigin' and 'pointOfOrigin'
                'cornerOfOrigin': 'topLeft', 'pointOfOrigin': t.topLeftCorner
            }
            for t in tms.tileMatrix
        ]
    }
