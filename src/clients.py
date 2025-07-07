import logging
from typing import Dict, Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.exceptions import APIError

logger = logging.getLogger(__name__)


class SightengineClient:
    """Клиент для Sightengine API"""
    
    def __init__(self, api_user: str, api_secret: str, models: str):
        self.api_user = api_user
        self.api_secret = api_secret
        self.models = models
        self.api_url = "https://api.sightengine.com/1.0/check.json"
        
        # HTTP клиент с настройками безопасности
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=5, max_keepalive_connections=2),
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        reraise=True
    )
    async def check_content(self, image_data: bytes) -> Dict[str, Any]:
        """
        Проверка контента через Sightengine API
        
        Args:
            image_data: Данные изображения
            
        Returns:
            Результат проверки
            
        Raises:
            APIError: При ошибке API
        """
        try:
            logger.info("🔍 Sending a request to Sightengine")
            
            # Подготовка данных
            payload = {
                "models": self.models,
                "api_user": self.api_user,
                "api_secret": self.api_secret,
            }
            files = {"media": ("image.jpg", image_data, "image/jpeg")}
            
            # Отправка запроса
            response = await self.client.post(
                self.api_url, 
                data=payload, 
                files=files
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Проверка статуса в ответе
            if result.get("status") != "success":
                error_msg = result.get("error", {}).get("message", "Unknown error")
                raise APIError(f"The Sightengine API error: {error_msg}")
            
            logger.info("✅ Received a response from Sightengine")
            return result
            
        except httpx.HTTPStatusError as e:
            raise APIError(f"HTTP error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise APIError(f"Network error: {e}")
    
    async def close(self) -> None:
        """Закрытие клиента"""
        await self.client.aclose()
