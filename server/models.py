from pydantic import BaseModel

class Item(BaseModel):
    price_uah: int
    object_count: int
    region: str
