from pydantic import BaseModel


class CollectionBaseResource(BaseModel):
    id: str
    description: str
