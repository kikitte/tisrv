from fastapi import APIRouter, Request, HTTPException

from tisrv.api.models import CollectionBaseResource, TilesetsDirector, TilesetsList, TileSet
from tisrv.geo.error import UnsupportedTMSException, TileOutOfRange

router = APIRouter()


@router.get('/', response_model=list[CollectionBaseResource])
def get_collections(request: Request):
    app = request.app

    response = [c.api.simple_description() for c in app.state.geo.data['collections']]

    return response


@router.get('/{collectionId}', response_model=TilesetsDirector)
def get_collection(collectionId: str, request: Request):
    collection = get_collection_from_app(request.app, collectionId)

    response = collection.api.tilesets_director()

    return response


@router.get('/{collectionId}/tiles', response_model=TilesetsList)
def get_collection_tilesets(collectionId: str, request: Request):
    collection = get_collection_from_app(request.app, collectionId)

    response = collection.api.tilesets_list()

    return response


@router.get('/{collectionId}/tiles/{tileMatrixSetId}', response_model=TileSet)
async def get_collection_tileset(collectionId: str, tileMatrixSetId: str, request: Request):
    collection = get_collection_from_app(request.app, collectionId)

    try:
        response = collection.api.tileset(tileMatrixSetId)
    except UnsupportedTMSException as e:
        raise HTTPException(status_code=404, detail=e.msg)

    return response


@router.get('/{collectionId}/tiles/{tileMatrixSetId}/{tileMatrix}/{tileRow}/{tileCol}')
async def get_collection_tile(collectionId: str, tileMatrixSetId: str, tileMatrix: int, tileRow: int, tileCol: int,
                              request: Request):
    app = request.app
    collection = get_collection_from_app(app, collectionId)

    try:
        response = await collection.api.tile(tileMatrixSetId, tileMatrix, tileRow, tileCol, {'pool': app.state.db.pool})
    except (UnsupportedTMSException, TileOutOfRange) as e:
        raise HTTPException(status_code=404, detail=e.msg)

    return response


def get_collection_from_app(app, collectionId):
    collections = app.state.geo.data['collections']
    collection = [c for c in collections if c.id == collectionId]

    if not collection:
        raise HTTPException(status_code=404, detail=f'{collectionId} not found.')
    elif len(collection) > 1:
        raise HTTPException(status_code=500,
                            detail=f'Multiple collection instance for the collectionId: {collectionId}')
    else:
        return collection[0]
