from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # database
    DATABASE_URL: str
    REDIS_URL: str

    # mailing
    MAIL_PASSWORD: str

    # cloudinary
    CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # JWT
    JWT_SECRETE: str
    JWT_ALGO: str

    # Configurations
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


Config = Settings()
