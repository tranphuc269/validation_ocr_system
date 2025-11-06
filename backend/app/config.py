from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    mongo_url: str = "mongodb://mongo:27017"
    mongo_db: str = "validation_ocr"
    storage_dir: str = "/data/storage"

    class Config:
        env_prefix = "VOS_"


settings = Settings()

# Ensure storage directories exist at import time
Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)
Path(f"{settings.storage_dir}/uploads").mkdir(parents=True, exist_ok=True)
Path(f"{settings.storage_dir}/samples").mkdir(parents=True, exist_ok=True)
Path(f"{settings.storage_dir}/user_inputs").mkdir(parents=True, exist_ok=True)


