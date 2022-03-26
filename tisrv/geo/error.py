class GeoBaseException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class UnsupportedTMSException(GeoBaseException):
    pass


class TileOutOfRange(GeoBaseException):
    pass
