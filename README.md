# AI Engee Model Generator (FastAPI)

Backend-сервис для генерации скриптов Engee по текстовому промпту.

Сервис принимает `prompt`, собирает контекст из Qdrant и запрашивает ответ у локальной модели в Ollama.  
Ответ возвращается в формате JSON с полем `script`.

## Что делает сервис

- Поднимает HTTP API на FastAPI.
- Принимает запросы на генерацию по маршруту `POST /script/generate`.
- Использует:
  - Qdrant для поиска релевантного контекста.
  - SentenceTransformer для эмбеддингов.
  - Ollama для генерации финального скрипта.

## Требования

- Windows + PowerShell
- Python 3.14 (или совместимая версия)
- Docker Desktop
- Ollama

## Установка

```powershell
cd C:\codex\AIEngeeModelGenerator-feature-fastapi_app
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Конфигурация

Создай файл `.env` в корне проекта:

```env
OLLAMA_MODEL_NAME=qwen3.5:4b
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=base_collection
GENERATION_TIMEOUT_SECONDS=300
```

Пояснения:

- `OLLAMA_MODEL_NAME` — имя модели из `ollama list`.
- `GENERATION_TIMEOUT_SECONDS` — таймаут генерации в секундах.

## Запуск зависимостей

### 1. Qdrant

```powershell
docker run -d --name qdrant -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

Проверка:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:6333/collections
```

### 2. Ollama

Установка (если не установлен):

```powershell
winget install --id Ollama.Ollama -e
```

Скачивание модели:

```powershell
ollama pull qwen3.5:4b
ollama list
```

Если сервис Ollama не запущен:

```powershell
ollama serve
```

## Запуск приложения

```powershell
cd C:\codex\AIEngeeModelGenerator-feature-fastapi_app
.\.venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

## Проверка работоспособности

### 1. Проверка root-эндпоинта

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8001/
```

Ожидаемый ответ:

```json
{"message":"This is root page and nothing more"}
```

### 2. Проверка генерации

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8001/script/generate `
  -ContentType "application/json" `
  -Body '{"prompt":"два блока Constant, затем Add, затем Out1"}'
```

Ожидаемый формат ответа:

```json
{"script":"..."}
```

## API

### `POST /script/generate`

Тело запроса:

```json
{"prompt":"текст запроса"}
```

Ограничения:

- `prompt` от 3 до 2000 символов.

Ответ:

```json
{"script":"сгенерированный скрипт"}
```

## Частые проблемы

- `Generation error ... model ... input_value=None`  
  - Не найдена переменная `OLLAMA_MODEL_NAME` (проверь `.env` и перезапусти backend).

- `Model timeout` / HTTP 504  
  - Увеличь `GENERATION_TIMEOUT_SECONDS` в `.env` и перезапусти backend.

- `listen tcp 127.0.0.1:11434 ... only one usage ...`  
  - Ollama уже запущен, второй `ollama serve` не нужен.

## Остановка

- Остановить backend: `Ctrl + C` в окне с `uvicorn`.
- Остановить Qdrant:

```powershell
docker stop qdrant
```
