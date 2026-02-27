from typing import Any
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    id: Any
    __name__: str

    # Automatically generate __tablename__ from class name 
    # (e.g., 'User' model -> 'user' table)
    @property
    def __tablename__(cls) -> str:
        return cls.__name__.lower()