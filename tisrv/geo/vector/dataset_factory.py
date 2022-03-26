from collections import defaultdict
from .dataset import Dataset
from .collection import VectorCollection

def collections_to_datasets(collections: list[VectorCollection]):
    dataset_collections = defaultdict(list)

    for collection in collections:
        dataset_collections[collection.schema].append(collection)

    datasets = [Dataset(schema, items) for schema, items in dataset_collections.items()]

    return datasets
