#authentication handlers
import jwt
from datetime import datetime,timedelta
from app.core.config import settings
from pwdlib import PasswordHash


#initializing password hash and oauth2 password bearer
password_hash = PasswordHash.recommended()


#verifying unhashed and hashed passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

#hasing the password
def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


#creating an jwt token for authenticated user
def create_token(user_id: int,
                token_type: str,
                expires_time: timedelta | None = None ,
                unique_id: str | None = None ,
                secret: str | None = None) -> str:
    
    to_encode = {
        'uid': user_id,
        'type': token_type,
    }

    if unique_id:
        to_encode['jti'] = unique_id

    if secret:
        to_encode['secret'] = secret
        
    if expires_time:
        expire = datetime.utcnow() + expires_time

    to_encode.update({'exp': expire})

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
