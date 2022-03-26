from asyncpg import Pool

from .vector.collection_factory import query_collections
from .vector.dataset_factory import collections_to_datasets


async def refresh_data(pool: Pool):
    vector_collections = await query_collections(pool)
    vector_datasets = collections_to_datasets(vector_collections)

    collections = []
    datasets = []

    collections.extend(vector_collections)
    datasets.extend(vector_datasets)

    return {
        'collections': collections,
        'datasets': datasets,
    }
