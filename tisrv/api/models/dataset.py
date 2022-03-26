from pydantic import BaseModel


class DatasetResource(BaseModel):
    id: str
    collections: list[str]
