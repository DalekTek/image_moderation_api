from functools import lru_cache
from typing import Set

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # API настройки Sightengine
    sightengine_api_user: str = Field(..., env="SIGHTENGINE_API_USER")
    sightengine_api_secret: str = Field(..., env="SIGHTENGINE_API_SECRET")
    
    # Модели для проверки
    moderation_models: str = Field(default="nudity-2.0", env="MODERATION_MODELS")
    
    # Настройки сервера
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Настройки модерации
    nsfw_threshold: float = Field(default=0.7, env="NSFW_THRESHOLD")
    
    # Настройки файлов
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    allowed_extensions: Set[str] = {"jpg", "jpeg", "png"}
    
    @validator("nsfw_threshold")
    def validate_threshold(cls, v: float) -> float:
        """Валидация порога NSFW"""
        if not 0 <= v <= 1:
            raise ValueError("The NSFW threshold should be between 0 and 1")
        return v
    
    @validator("moderation_models", pre=True)
    def clean_models(cls, v: str) -> str:
        """Очистка строки моделей от лишних символов"""
        return v.strip('\'"') if isinstance(v, str) else v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Получение настроек приложения"""
    return Settings()