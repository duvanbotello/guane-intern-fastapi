from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Dog(Base):
    __tablename__ = "dogs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    picture = Column(String)
    create_date = Column(String)
    is_adopted = Column(Boolean, default=False)
    id_user = Column(Integer, ForeignKey("users.id"))

    users = relationship("User", back_populates="dogs")
