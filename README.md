# Image Moderation API

Сервер для модерации изображений с использованием Sightengine API.

## Описание

API принимает изображения и определяет наличие нежелательного контента по настраиваемому набору правил 
(нагота, насилие, оружие и т.д.), используя машинное обучение от [Sightengine](https://sightengine.com/).

## Возможности

- ✅ Проверка по нескольким категориям (нагота, насилие, оружие и др.), настраиваемым через `.env`.
- ✅ Модерация изображений форматов JPG, JPEG, PNG.
- ✅ Установка чувствительности для всех правил модерации.
- ✅ Проверка размера и формата файлов перед обработкой.
- ✅ Асинхронная обработка запросов на базе FastAPI.
- ✅ Безопасная обработка запросов
- ✅ Подробное логгирование


## Установка и настройка

### 1. Клонирование репозитория

```bash
git clone https://github.com/DalekTek/image_moderation_api
cd image_moderation_api
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env` в корневой директории проекта:

```env
# Обязательные настройки
SIGHTENGINE_API_USER="your_sightengine_api_user_key"
SIGHTENGINE_API_SECRET="your_sightengine_api_secret_key"

# Настройте, какие категории проверять (перечислите через запятую)
# Доступные модели: nudity-2.0, violence, weapon, gore, recreational_drug, alcohol, offensive
MODERATION_MODELS="nudity-2.0,violence,weapon"

# Опциональные настройки
HOST=127.0.0.1
PORT=8000
DEBUG=false

NSFW_THRESHOLD=0.7
MAX_FILE_SIZE=10485760 # 10MB
```

### 4*. Получение API ключей Sightengine

1. Зарегистрируйтесь на [Sightengine](https://sightengine.com/)
2. Перейдите в ваш Dashboard. 
3. Перейдите в раздел API Keys 
4. Скопируйте ваш API user ключ в переменную `SIGHTENGINE_API_USER` в файле `.env`
5. Скопируйте ваш API secret ключ в переменную `SIGHTENGINE_API_SECRET` в файле `.env`

## Запуск приложения

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Эндпоинты

### POST /moderate

Основной эндпоинт для модерации изображений.

**Параметры:**
- `file` (multipart/form-data): Файл изображения (.jpg, .jpeg, .png)

**Ответы:**

✅ **Успешная модерация (безопасное изображение):**
```json
{
  "status": "OK",
  "scores": {
    "nudity_score": 0.05,
    "violence_score": 0.1,
    "weapon_score": 0.02
  }
}
```

❌ **Обнаружен нежелательный контент:**
```json
{
  "status": "REJECTED",
  "reason": "Nudity content, Violence content",
  "scores": {
    "nudity_score": 0.85,
    "violence_score": 0.91,
    "weapon_score": 0.1
  }
}
```

🚫 **Ошибка валидации:**
```json
{
  "detail": "File extension 'gif' not allowed. Allowed extensions: jpg, jpeg, png"
}
```

### `GET /` и `GET /health`

Эндпоинты для проверки работоспособности и здоровья сервиса.

## Примеры использования

### cURL

```bash
# Модерация изображения
curl -X POST \
  -F "file=@example.jpg" \
  http://localhost:8000/moderate

# Проверка работоспособности
curl http://localhost:8000/

# Проверка здоровья сервиса
curl http://localhost:8000/health
```

### Python `requests`

```python
import requests

# Модерация изображения
with open('example.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/moderate', files=files)
    print(response.json())
```

### Postman

1. Создайте POST запрос на `http://localhost:8000/moderate`
2. В разделе Body выберите "form-data"
3. Добавьте ключ "file" типа "File"
4. Выберите изображение для загрузки
5. Отправьте запрос

## Архитектура проекта

```
image-moderation-api/
├── main.py                          # Основное приложение FastAPI
├── requirements.txt                 # Зависимости проекта
├── README.md                        # Документация
├── .env                             # Переменные окружения (создать)
└── src/
    ├── services/
    │   ├── __init__.py
    │   └── moderation_service.py    # Cервис модерации
    ├── __init__.py
    ├── analyzers.py
    ├── clients.py                   
    ├── config.py                    # Конфигурация приложения
    ├── exceptions.py                # Пользовательские исключения
    └── validators.py                # Валидатор изображений
```
## Использование с Docker

Вы можете запустить приложение в контейнере.

**Dockerfile:**
```dockerfile
# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY ./src ./src
COPY main.py .

# Открываем порт
EXPOSE 8000

# Запускаем приложение через uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Сборка и запуск:**
```bash
# Сборка образа
docker build -t image-moderation-api .

# Запуск контейнера с передачей .env файла
docker run -d -p 8000:8000 --env-file .env --name moderation-app image-moderation-api
```

## Настройки

| Переменная окружения     | Описание                    | Значение по умолчанию        |
|--------------------------|-----------------------------|------------------------------|
| `SIGHTENGINE_API_USER`   | API user ключ Sightengine   | **Обязательно**              |
| `SIGHTENGINE_API_SECRET` | API secret ключ Sightengine | **Обязательно**              |
| `MODERATION_MODELS`      | Категории проверки          | `nudity-2.0,violence,weapon` |
| `HOST`                   | Хост сервера                | `127.0.0.1`                  |
| `PORT`                   | Порт сервера                | `8000`                       |
| `DEBUG`                  | Режим отладки               | `false`                      |
| `NSFW_THRESHOLD`         | Порог NSFW (0.0-1.0)        | `0.7`                        |
| `MAX_FILE_SIZE`          | Макс. размер файла (байты)  | `10485760` (10MB)            |


## Форматирование кода и проверка стиля
```bash
black .
isort .

flake8 .
```

## Логгирование

Приложение ведет подробные логи:
- Консольный вывод для разработки
- Файловые логи в `logs/app.log`
- Структурированное логгирование всех операций
- Отслеживание ошибок и производительности

## Лицензия

MIT License
