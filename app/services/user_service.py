from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import Conflict

def get_by_email(db: Session, email: str) -> User | None:

    stmt = select(User).where(User.email == email)
    return db.scalars(stmt).first()

def get_by_username(db: Session, username: str) -> User | None:

    stmt = select(User).where(User.username == username)
    return db.scalars(stmt).first()

def create_user(db: Session, user_in: UserCreate) -> User:

    if get_by_email(db, user_in.email):
        raise Conflict(message=f"user with email {user_in.email} already exists!")
    

    if get_by_username(db, user_in.username):
        raise Conflict(message=f"User with usernaem {user_in.username} already exists!")
    
    hashed_pasword = get_password_hash(user_in.password)

    user_obj = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pasword,
    )

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    return user_obj


def authenticate_user(db: Session, username: str, password: str) -> User | None:

    user = get_by_username(db, username)

    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user