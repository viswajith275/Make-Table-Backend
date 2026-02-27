from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
# import uuid    use as a secondary level of primary for security
from typing import TYPE_CHECKING
from datetime import datetime
from app.db.base_class import Base



class UserToken(Base):

    __tablename__ = 'user_tokens' # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    refresh_key: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    expires_at: Mapped[datetime] = mapped_column()

    #relationships
    user: Mapped['User'] = relationship("User",back_populates='tokens') # type: ignore