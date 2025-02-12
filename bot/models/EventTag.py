from pydantic import BaseModel, Field


class EventTag(BaseModel):
    """
    Модель тега, получаемого с помощью API
    """
    type_code: int = Field(default="",alias="tag_code")
    description: str
