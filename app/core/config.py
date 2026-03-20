from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "TimeTable Backend Remake"
    database_url: str = ""
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    redis_url: str = ""

    @property
    def sync_database_url(self) -> str:
        # removes +asyncpg from the async
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")


settings = Settings()
