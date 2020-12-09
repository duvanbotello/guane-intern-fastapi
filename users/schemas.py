from typing import List

from pydantic import BaseModel

from dogs.schemas import Dogs


class UsersBase(BaseModel):
    name: str
    last_name: str
    email: str


class UsersCreate(UsersBase):
    pass


class Users(UsersBase):
    id: int
    dogs: List[Dogs] = []

    class Config:
        orm_mode = True
