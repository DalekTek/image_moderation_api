import logging
from typing import Dict, Any

from fastapi import UploadFile

from src.config import Settings
from src.exceptions import ModerationError, ValidationError
from src.validators import FileValidator
from src.clients import SightengineClient
from src.analyzers import ContentAnalyzerFactory

logger = logging.getLogger(__name__)


class ModerationService:
    """Сервис модерации изображений"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        
        # Создание компонентов
        self.validator = FileValidator(
            max_size=settings.max_file_size,
            allowed_extensions=settings.allowed_extensions
        )
        
        self.client = SightengineClient(
            api_user=settings.sightengine_api_user,
            api_secret=settings.sightengine_api_secret,
            models=settings.moderation_models
        )
        
        self.analyzers = ContentAnalyzerFactory.create_analyzers(
            settings.moderation_models
        )
    
    async def moderate_image(self, file: UploadFile) -> Dict[str, Any]:
        """
        Модерация изображения
        
        Args:
            file: Загруженный файл
            
        Returns:
            Результат модерации
            
        Raises:
            ValidationError: При ошибке валидации
            ModerationError: При ошибке модерации
        """
        try:
            # Валидация файла
            await self.validator.validate(file)
            
            # Получение содержимого
            content = await file.read()
            await file.seek(0)
            
            # Анализ через API
            api_result = await self.client.check_content(content)
            
            # Анализ результатов
            return self._analyze_results(api_result)
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Moderation error: {e}")
            raise ModerationError(f"Couldn't complete moderation: {e}")
    
    def _analyze_results(self, api_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализ результатов от API
        
        Args:
            api_result: Результат от API
            
        Returns:
            Решение о модерации
        """
        violations = []
        scores = {}
        
        # Анализ каждым анализатором
        for analyzer in self.analyzers:
            is_violation, score, reason = analyzer.analyze(
                api_result, 
                self.settings.nsfw_threshold
            )
            
            # Сохранение результата
            analyzer_name = analyzer.__class__.__name__.replace("Analyzer", "").lower()
            scores[f"{analyzer_name}_score"] = score
            
            if is_violation and reason:
                violations.append(reason)
        
        # Формирование ответа
        if violations:
            return {
                "status": "REJECTED",
                "reason": ", ".join(violations),
                "scores": scores
            }
        else:
            return {
                "status": "OK",
                "scores": scores
            }
    
    async def close(self) -> None:
        """Закрытие сервиса"""
        await self.client.close()
