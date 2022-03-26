from functools import lru_cache

from pydantic import BaseSettings, validator

from tisrv.geo.tms import global_tms_set, TileMatrixSets


class PgSettings(BaseSettings):
    host: str
    port: str
    username: str
    password: str
    dbname: str

    # asyncpg create_pool arguments
    pool_min_size: int = 1  # Number of connection the pool will be initialized with.
    pool_max_size: int = 5  # Max number of connections in the pool.
    pool_max_queries: int = 50000  # Number of queries after a connection is closed and replaced with a new connection.
    pool_max_inactive_connection_lifetime: int = 300  # Number of seconds after which inactive connections in the pool will be closed. Pass 0 to disable this mechanism.

    @property
    def dsn(self):
        return f'postgres://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}'

    class Config:
        env_prefix = 'pg_'
        env_file = '.env'


@lru_cache()
def get_pg_settings():
    return PgSettings()


class ApiSettings(BaseSettings):
    title: str = ''
    description: str = '',
    version: str = '',
    debug: bool = False

    class Config:
        env_prefix = 'api_'
        env_file = '.env'


@lru_cache()
def get_api_settings():
    return ApiSettings()


class _GeoSettings(BaseSettings):
    supported_tms_list: str

    @validator('supported_tms_list')
    def check_supported_tms(cls, v):
        if id in _GeoSettings.parse_tms_str(v):
            if not global_tms_set.has(id):
                raise ValueError(f'TMS {id} is unsupported.')
        return v

    @staticmethod
    def parse_tms_str(v):
        if len(v) == 0:
            raise ValueError('No TMS specified.')
        return [i.strip() for i in v.split(',')]

    class Config:
        env_prefix = 'geo_'
        env_file = '.env'


class GeoSettings:
    user_tms_set: TileMatrixSets

    def __init__(self, *, supported_tms_list):
        self.user_tms_set = TileMatrixSets(
            **{id: global_tms_set[id] for id in _GeoSettings.parse_tms_str(supported_tms_list)})


@lru_cache()
def get_geo_settings():
    settings = _GeoSettings()

    return GeoSettings(supported_tms_list=settings.supported_tms_list)
