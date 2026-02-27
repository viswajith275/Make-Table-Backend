from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "TimeTable Backend Remake"
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    redis_url: str


settings = Settings()