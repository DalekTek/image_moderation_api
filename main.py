import logging
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import Settings, get_settings
from src.services.moderation_service import ModerationService
from src.exceptions import ValidationError, ModerationError

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("🚀 Запуск приложения")
    yield
    logger.info("🛑 Остановка приложения")


def create_app() -> FastAPI:
    """Фабрика для создания FastAPI приложения"""
    app = FastAPI(
        title="Image Moderation API",
        description="API для модерации изображений",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    return app


app = create_app()


def get_moderation_service(settings: Settings = Depends(get_settings)) -> ModerationService:
    """Dependency Injection для сервиса модерации"""
    return ModerationService(settings)


@app.get("/")
async def root() -> Dict[str, str]:
    """Корневой эндпоинт для проверки работоспособности"""
    return {"message": "Image Moderation API работает"}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Эндпоинт для проверки здоровья сервиса"""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/moderate")
async def moderate_image(
    file: UploadFile = File(...),
    service: ModerationService = Depends(get_moderation_service),
) -> JSONResponse:
    """
    Основной эндпоинт для модерации изображений
    
    Args:
        file: Загружаемый файл изображения
        service: Сервис модерации
        
    Returns:
        JSONResponse с результатом модерации
        
    Raises:
        HTTPException: При ошибках валидации или модерации
    """
    try:
        logger.info(f"📸 Получен запрос на модерацию: {file.filename}")
        
        # Выполнение модерации
        result = await service.moderate_image(file)
        
        logger.info(f"✅ Модерация завершена: {result['status']}")
        return JSONResponse(content=result, status_code=200)
        
    except ValidationError as e:
        logger.warning(f"❌ Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except ModerationError as e:
        logger.error(f"🔥 Ошибка модерации: {e}")
        raise HTTPException(status_code=503, detail="Сервис модерации недоступен")
        
    except Exception as e:
        logger.error(f"💥 Неожиданная ошибка: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
