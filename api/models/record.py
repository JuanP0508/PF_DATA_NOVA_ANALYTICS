from pydantic import BaseModel, Field
from typing import Literal

class EventRecord(BaseModel):
    event_time: str
    event_type: Literal["view", "purchase", "cart"]
    product_id: int
    category_id: int
    category_code: str
    brand: str
    price: float
    user_id: int
    user_session: str
    category_inferred: bool
    brand_inferred: bool