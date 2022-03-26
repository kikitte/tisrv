from fastapi import FastAPI
import asyncpg

from tisrv.settings import get_pg_settings


async def connect_to_db(app: FastAPI):
    pg_settings = get_pg_settings()
    app.state.db.pool = await asyncpg.create_pool(pg_settings.dsn,
                                                  min_size=pg_settings.pool_min_size,
                                                  max_size=pg_settings.pool_max_size,
                                                  max_queries=pg_settings.pool_max_queries,
                                                  max_inactive_connection_lifetime=pg_settings.pool_max_inactive_connection_lifetime)


async def close_connection(app: FastAPI):
    await app.state.db.pool.close()
