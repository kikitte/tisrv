from pydantic import BaseModel


class WebLink(BaseModel):
    href: str
    rel: str
    type: str
    title: str
