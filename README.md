# Клуб настольных игр — Docker Compose

Лабораторная работа «Контейнеризация многокомпонентных приложений с помощью Docker Compose».
Студент: Реверчук Захар Игоревич, группа 223-321.

**Вариант №30 — Настольные игры**
- Web-сервис: поиск игр по числу игроков и времени партии.
- Данные в БД: настольная коллекция клуба.

## Архитектура

| Сервис        | Технологии              | Назначение                                                        | Порт |
|---------------|-------------------------|-------------------------------------------------------------------|------|
| `frontend`    | HTML/CSS/JS + nginx     | Веб-интерфейс, проксирует `/api/*` на backend                     | 8080 → 80 (наружу) |
| `backend`     | Python, FastAPI, psycopg| REST API, CRUD по коллекции, интеграция с web-service             | 8000 (внутри сети) |
| `db`          | PostgreSQL 16           | Таблица `club_collection`, инициализация из `db/init.sql`         | 5432 (внутри сети) |
| `web-service` | Python, FastAPI         | Каталог игр, поиск по `players` и `max_time`                      | 5001 (внутри сети) |

```
Браузер ──► frontend (nginx) ──/api──► backend ──► db (PostgreSQL)
                                          └──────► web-service
```

Все контейнеры объединены в bridge-сеть `app_net`. `backend` стартует только после того,
как `db` и `web-service` прошли healthcheck. Данные БД хранятся в volume `db_data`.

## Запуск

```bash
cp .env.example .env      # необязательно — значения по умолчанию заданы в docker-compose.yml
docker compose up -d --build
```

Открыть http://localhost:8080

Остановка: `docker compose down` (с удалением данных БД: `docker compose down -v`).

## Функции интерфейса

1. **«Показать коллекцию клуба»** — выборка игр из PostgreSQL через backend (`GET /api/collection`).
   Форма ниже добавляет игру в БД (`POST /api/collection`), кнопка ✕ — удаляет (`DELETE /api/collection/{id}`).
2. **«Найти игры»** — запрос к web-сервису через backend (`GET /api/search?players=4&max_time=60`).
   Backend помечает игры, которые уже есть в клубе; остальные можно добавить в коллекцию кнопкой «+ в коллекцию».

## API

| Метод | Путь                       | Описание                                  |
|-------|----------------------------|-------------------------------------------|
| GET   | `/api/collection`          | Список игр коллекции клуба                |
| POST  | `/api/collection`          | Добавить игру (при совпадении названия увеличивает число копий) |
| DELETE| `/api/collection/{id}`     | Удалить игру                              |
| GET   | `/api/search`              | Поиск игр в web-сервисе (`players`, `max_time`) |
| GET   | `/api/health`              | Проверка работоспособности                |

Пример:
```bash
curl "http://localhost:8080/api/search?players=2&max_time=30"
curl -X POST http://localhost:8080/api/collection -H "Content-Type: application/json" \
     -d '{"title":"Азул","min_players":2,"max_players":4,"play_time":40,"genre":"Абстрактная"}'
```

## Структура

```
boardgames-docker-lab/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── frontend/      Dockerfile, nginx.conf, src/ (index.html, app.js, style.css)
├── backend/       Dockerfile, main.py, requirements.txt
├── db/            init.sql
└── web-service/   Dockerfile, service.py, requirements.txt
```
