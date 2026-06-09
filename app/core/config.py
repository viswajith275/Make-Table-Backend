from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "TimeTable Backend Remake"
    sync_database_url: str = ""
    frontend_url: str = ""
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    redis_url: str = ""
    google_client_key: str = ""
    google_client_secret: str = ""

    @property
    def database_url(self) -> str:
        # add +asyncpg
        return self.sync_database_url.replace("postgresql://", "postgresql+asyncpg://")


settings = Settings()
