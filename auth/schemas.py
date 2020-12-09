from typing import Optional

from pydantic import BaseModel


class AuthUsersBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

    class Config:
        orm_mode = True


class DogsCreate(BaseModel):
    id: int
    pass


class AuthUsersInDB(AuthUsersBase):
    hashed_password: str
