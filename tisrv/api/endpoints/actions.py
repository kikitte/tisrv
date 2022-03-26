from fastapi import APIRouter, Request

from tisrv.geo.actions import refresh_data as refresh_geo_data

router = APIRouter()


@router.post('/refersh')
async def refersh_data(request: Request):
    """
    fetch datasets and collections again from its data source
    """

    app = request.app

    geodata = await refresh_geo_data(app.state.db.pool)

    app.state.geo.data = geodata
