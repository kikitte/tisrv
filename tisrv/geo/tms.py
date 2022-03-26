from typing import Iterator
from morecantile import tms, TileMatrixSet


class TileMatrixSets:
    def __init__(self, **kwargs):
        self.__tms_map = dict(kwargs)

    def __contains__(self, identifier) -> bool:
        """ detect if a tms is supported by its id """
        return identifier in self.__tms_map

    def __getitem__(self, identifier) -> TileMatrixSet:
        return self.__tms_map[identifier]

    def __setitem__(self, identifier, tms: TileMatrixSet):
        if not identifier in self:
            raise KeyError(f'Already defined: {identifier}')
        self.__tms_map[identifier] = tms

    def __iter__(self) -> Iterator[TileMatrixSet]:
        return self.__tms_map.values().__iter__()

    def __len__(self):
        return self.__tms_map.__len__()


# the system provided tms
global_tms_set = TileMatrixSets(**tms.tms)
