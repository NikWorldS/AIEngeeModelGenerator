# Запуск через docker compose
Почти не сложно. По шагам:
1) склонировать проект себе
2) на основе `.env.example` настроить файл с переменными среды `.env` (данные для Postgres будут применены именно из файла)
3) в папку qdrant_snapshot сохранить файл снапшота с готовой коллекцией для рестора (нужна для миграции готовой коллекции в контейнер)
4) забилдить через `docker compose build`
5) запустить через `docker compose up`


## env:
- OLLAMA_MODEL_NAME - имя модели из регистра Ollama, что будет использоваться для генерации
- 
- QDRANT_HOST - хост для БД qdrant (можно оставить по умолнчанию из документации qdrant)
- QDRANT_PORT - порт для БД qdrant (можно оставить по умолнчанию из документации qdrant)
- QDRANT_COLLECTION_NAME - название коллекции для qdrant, выбирайте любое
- 
- GENERATION_TIMEOUT_SECONDS - время для отброса генерации, в секундах
- 
- POSTGRES_HOST - хост для Postgres
- POSTGRES_PORT - порт для Postgres
- POSTGRES_DB - название базы данных
- POSTGRES_USER - имя пользователя
- POSTGRES_PASSWORD - пароль для пользователя

## Endpoints
Тестовый - GET `/test/useless_endpoint` - возвращает то, что это бесполезный эндпоинт

Основной - POST `/script/generate`:
- Принимает `json` в формате
  ```json
  {"prompt": "..."}
  ```

- Возвращает:
  ```json
  {"script": "..."}
  ```
