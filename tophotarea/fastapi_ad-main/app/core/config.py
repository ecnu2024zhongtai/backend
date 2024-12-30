from pydantic_settings import BaseSettings  # 使用 pydantic-settings 包中的 BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "your_secret_key"

    class Config:
        env_file = ".env"

settings = Settings()
