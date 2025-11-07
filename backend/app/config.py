from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    mongo_url: str = "mongodb://mongo:27017"
    mongo_db: str = "validation_ocr"
    storage_dir: str = "/data/storage"
    storage_backend: str = "LOCAL"  # LOCAL or MINIO

    minio_endpoint: str | None = None
    minio_access_key: str | None = None
    minio_secret_key: str | None = None
    minio_bucket: str | None = None
    minio_secure: bool = True
    minio_region: str | None = None

    class Config:
        env_prefix = "VOS_"


settings = Settings()

# Ensure storage directories exist for local backend
if settings.storage_backend.upper() == "LOCAL":
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)
    Path(f"{settings.storage_dir}/uploads").mkdir(parents=True, exist_ok=True)
    Path(f"{settings.storage_dir}/samples").mkdir(parents=True, exist_ok=True)
    Path(f"{settings.storage_dir}/user_inputs").mkdir(parents=True, exist_ok=True)


