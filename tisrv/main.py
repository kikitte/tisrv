from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import State

from .api.api import api_router
from .db import connect_to_db, close_connection
from .geo.actions import refresh_data as refresh_geo_data
from .settings import get_api_settings

api_settings = get_api_settings()

app = FastAPI(title=api_settings.title,
              description=api_settings.description,
              version=api_settings.version,
              debug=api_settings.debug)

# configure app
app.add_middleware(CORSMiddleware,
                   allow_origins=['*'],
                   allow_credentials=True,
                   allow_methods=['*'],
                   allow_headers=['*'], )

'''
pool: asyncpg.Pool - An instance of Pool
'''
app.state.db = State()
'''
data: {'collections': List[Any], 'datasets': List[Any]} - collections and datasets container
'''
app.state.geo = State()


@app.on_event('startup')
async def on_api_startup():
    await connect_to_db(app)
    app.state.geo.data = await refresh_geo_data(app.state.db.pool)


@app.on_event('shutdown')
async def on_api_shutdown():
    await close_connection(app)


app.include_router(api_router)
