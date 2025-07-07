import io
import logging
from pathlib import Path
from typing import Set

from fastapi import UploadFile
from PIL import Image

from src.exceptions import ValidationError

logger = logging.getLogger(__name__)


class FileValidator:
    """Валидатор файлов"""
    
    def __init__(self, max_size: int, allowed_extensions: Set[str]):
        self.max_size = max_size
        self.allowed_extensions = {ext.lower() for ext in allowed_extensions}
    
    async def validate(self, file: UploadFile) -> None:
        """
        Основной метод валидации
        
        Args:
            file: Загруженный файл
            
        Raises:
            ValidationError: При ошибке валидации
        """
        # Проверка наличия файла
        if not file or not file.filename:
            raise ValidationError("The file is not provided")
        
        # Проверка расширения
        self._validate_extension(file.filename)
        
        # Проверка размера
        await self._validate_size(file)
        
        # Проверка содержимого
        await self._validate_image_content(file)
        
        logger.info(f"✅ The file has been validated: {file.filename}")
    
    def _validate_extension(self, filename: str) -> None:
        """Проверка расширения файла"""
        extension = Path(filename).suffix.lower().lstrip(".")
        
        if extension not in self.allowed_extensions:
            raise ValidationError(
                f"The '{extension}' extension is not allowed. "
                f"Allowed: {', '.join(self.allowed_extensions)}"
            )
    
    async def _validate_size(self, file: UploadFile) -> None:
        """Проверка размера файла"""
        content = await file.read()
        await file.seek(0)  # Сброс позиции
        
        file_size = len(content)
        
        if file_size == 0:
            raise ValidationError("The file is empty")
        
        if file_size > self.max_size:
            raise ValidationError(
                f"The file size {file_size} bytes exceeds"
                f"maximum {self.max_size} byte"
            )
    
    async def _validate_image_content(self, file: UploadFile) -> None:
        """Проверка содержимого как изображения"""
        try:
            content = await file.read()
            await file.seek(0)
            
            with Image.open(io.BytesIO(content)) as img:
                if img.width <= 0 or img.height <= 0:
                    raise ValidationError("Incorrect image dimensions")
                
                if img.format.lower() not in ["jpeg", "jpg", "png"]:
                    raise ValidationError(f"Unsupported format: {img.format}")
                    
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Invalid image file: {e}")

