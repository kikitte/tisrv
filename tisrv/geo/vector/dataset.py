from .collection import VectorCollection


class Dataset:
    schema: str
    collections: list[VectorCollection]

    def __init__(self, schema: str, collections: list[VectorCollection]):
        self.schema = schema
        self.collections = collections

    def api_response(self):
        return {
            'id': self.schema,
            'collections': [i.id for i in self.collections]
        }

    @property
    def id(self):
        return self.schema
