from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import Conflict, BadRequest, NotFound
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, PasswordUpdationRequest
from typing import Dict


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


async def update_username(
    db: AsyncSession, user_patch: UserUpdate, user_id: int
) -> User:

    stmt = await db.execute(select(User).where(User.id == user_id))

    user_obj = stmt.scalar_one_or_none()
    if user_obj is None:
        raise NotFound(message="User not found!")

    patch_data = user_patch.model_dump(exclude_unset=True)

    if not patch_data:
        raise BadRequest("Nothing to be updated!")

    username = patch_data.get("username", None)
    if username is not None:
        stmt = await db.execute(
            select(exists().where(User.username == username, User.id != user_id))
        )
        existing = stmt.scalar()

        if existing:
            raise Conflict("Username is taken!")

    for key, value in patch_data.items():
        setattr(user_obj, key, value)

    await db.commit()

    await db.refresh(user_obj)

    return user_obj


async def update_user_password(
    db: AsyncSession, password_patch: PasswordUpdationRequest, user_id: int
) -> Dict[str, str]:

    stmt = await db.execute(select(User).where(User.id == user_id))
    user_obj = stmt.scalar_one_or_none()

    if user_obj is None:
        raise NotFound(message="User not found")
    if not verify_password(password_patch.current_password, user_obj.hashed_password):
        raise BadRequest("Incorrect password!")

    if verify_password(password_patch.new_password, user_obj.hashed_password):
        raise BadRequest("New Password should not be same as old password!")

    user_obj.hashed_password = get_password_hash(password_patch.new_password)

    await db.commit()

    return {"message": "Password updated successfully!"}
