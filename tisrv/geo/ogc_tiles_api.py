import abc


class GeoResourceApi(abc.ABC):
    @abc.abstractmethod
    def simple_description(self):
        pass

    @abc.abstractmethod
    def tilesets_director(self):
        pass

    @abc.abstractmethod
    def tilesets_list(self):
        pass

    @abc.abstractmethod
    def tileset(self, tms_id):
        pass

    @abc.abstractmethod
    def tile(self, tms_id, tile_matrix, tile_row, tile_col, extra_params):
        pass
