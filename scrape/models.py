from pydantic import BaseModel

class Business(BaseModel):
    next_door_url: str
    name: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    categories: list[str] | None = None
