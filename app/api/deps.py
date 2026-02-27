import jwt
from sqlalchemy import select, delete
from datetime import datetime, timedelta
import secrets
from typing import Annotated, Generator
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Request
from app.core.config import settings
from app.models.token import UserToken
from app.db.session import SessionLocal
from app.models.user import User


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Fromating the token
async def get_token_from_cookie(request: Request) -> str:

    token = request.cookies.get('access_token')

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not Authenticated')
    
    if token.startswith('Bearer '):
        token = token.split(' ')[1]

    return token

#decoding and verifying the jwt token
async def get_current_user(token: Annotated[str, Depends(get_token_from_cookie)],
                            db: Session = Depends(get_db)) -> User | None:

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get('uid')

        if user_id is None or payload.get('type') != 'access':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token Invalid or expired')
        
        stmt = select(User).where(User.id == user_id)

        return db.scalars(stmt).first()
    
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token Invalid or expired')

# checking the user is not banned or revoked by the admin
async def get_current_active_user(
    current_user: Annotated[User | None, Depends(get_current_user)],
) -> User:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found!')
    
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    return current_user

def validate_refresh_token(refresh_token: str, db: Session) -> int:
        
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])

        token_type = payload.get('type')
        secret = payload.get('secret')
        user_id = payload.get('uid')

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
        
        if token_type != "refresh":

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Invalid Token {token_type}')
        
        token_id = int(payload.get('jti')) # type: ignore
        stmt = select(UserToken).where(UserToken.id == token_id, UserToken.user_id == user_id)

        token = db.scalars(stmt).first()

        if not token or token.refresh_key != secret:
            #token may be stolen
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token revoked or Invalid')
        
        return user_id
        
def delete_refresh_token(refresh_token: str | None, db: Session) -> None:
    if refresh_token:
    
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])

        token_id = int(payload.get('jti')) # type: ignore

        stmt = delete(UserToken).where(UserToken.id == token_id)

        db.execute(stmt)
        db.commit()

def create_refresh_token(db: Session, user_id: int) -> UserToken:
    
    session_secret = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    token = UserToken(user_id=user_id, expires_at=expires_at, refresh_key=session_secret)

    db.add(token)
    db.commit()
    db.refresh(token)

    return token