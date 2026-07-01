from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CloudWaste Sentinel"
    database_url: str = "sqlite:///./cloudwaste.db"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
