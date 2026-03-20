from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import Conflict
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


async def get_by_email(db: AsyncSession, email: str) -> User | None:

    stmt = await db.execute(select(User).where(User.email == email))
    return stmt.scalar_one_or_none()


async def get_by_username(db: AsyncSession, username: str) -> User | None:

    stmt = await db.execute(select(User).where(User.username == username))
    return stmt.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:

    if await get_by_email(db, user_in.email) is not None:
        raise Conflict(message=f"user with email {user_in.email} already exists!")

    if await get_by_username(db, user_in.username) is not None:
        raise Conflict(message=f"User with usernaem {user_in.username} already exists!")

    hashed_pasword = get_password_hash(user_in.password)

    user_obj = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pasword,
    )

    db.add(user_obj)
    await db.commit()
    await db.refresh(user_obj)

    return user_obj


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:

    user = await get_by_username(db, username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
