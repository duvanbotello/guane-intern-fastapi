from pydantic import BaseModel


class DogsBase(BaseModel):
    name: str
    picture: str
    create_date: str
    is_adopted: bool


class DogsCreate(DogsBase):
    id_user: int
    pass


class Dogs(DogsBase):
    id: int
    id_user: int

    class Config:
        orm_mode = True
