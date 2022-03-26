from fastapi import APIRouter

from .endpoints import tms as tile_matrix_sets, datasets, collections, actions

api_router = APIRouter()

api_router.include_router(tile_matrix_sets.router, prefix='/tileMatrixSets')
api_router.include_router(datasets.router, prefix='/datasets')
api_router.include_router(collections.router, prefix='/collections')
api_router.include_router(actions.router, prefix='/actions')
