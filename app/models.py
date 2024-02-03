from pydantic import BaseModel

class Target(BaseModel):
    name: str
    url: str
