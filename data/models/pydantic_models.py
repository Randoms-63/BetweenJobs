from pydantic import BaseModel
from datetime import datetime, date


class UserResponse (BaseModel):

    id: int
    created_at: datetime
    first_name: str
    last_name: str
    is_admin: bool
    date_of_birth: date
    email: str
    employer_id: int | None

    class Config:
        orm_mode = True