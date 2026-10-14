"""Web-сервис «Настольные игры»: поиск игр по числу игроков и времени партии."""
from typing import Optional

from fastapi import FastAPI, Query

app = FastAPI(title="Board Games Search Service")

GAMES = [
    {"title": "Каркассон", "min_players": 2, "max_players": 5, "play_time": 45, "genre": "Выкладывание тайлов", "rating": 7.4},
    {"title": "Колонизаторы", "min_players": 3, "max_players": 4, "play_time": 90, "genre": "Экономическая", "rating": 7.1},
    {"title": "Билет на поезд", "min_players": 2, "max_players": 5, "play_time": 60, "genre": "Семейная", "rating": 7.4},
    {"title": "Кодовые имена", "min_players": 2, "max_players": 8, "play_time": 15, "genre": "Пати-игра", "rating": 7.6},
    {"title": "Пандемия", "min_players": 2, "max_players": 4, "play_time": 45, "genre": "Кооперативная", "rating": 7.6},
    {"title": "Диксит", "min_players": 3, "max_players": 6, "play_time": 30, "genre": "Пати-игра", "rating": 7.2},
    {"title": "Покорение Марса", "min_players": 1, "max_players": 5, "play_time": 120, "genre": "Стратегия", "rating": 8.4},
    {"title": "Крылья", "min_players": 1, "max_players": 5, "play_time": 70, "genre": "Движок", "rating": 8.1},
    {"title": "Азул", "min_players": 2, "max_players": 4, "play_time": 40, "genre": "Абстрактная", "rating": 7.8},
    {"title": "Остров духов", "min_players": 1, "max_players": 4, "play_time": 120, "genre": "Кооперативная", "rating": 8.3},
    {"title": "Манчкин", "min_players": 3, "max_players": 6, "play_time": 90, "genre": "Карточная", "rating": 6.0},
    {"title": "Имаджинариум", "min_players": 3, "max_players": 7, "play_time": 40, "genre": "Пати-игра", "rating": 6.9},
    {"title": "Мафия", "min_players": 6, "max_players": 20, "play_time": 40, "genre": "Социальная дедукция", "rating": 6.5},
    {"title": "Сплендор", "min_players": 2, "max_players": 4, "play_time": 30, "genre": "Семейная", "rating": 7.4},
    {"title": "Серп", "min_players": 1, "max_players": 5, "play_time": 115, "genre": "Стратегия", "rating": 8.1},
    {"title": "Взрывные котята", "min_players": 2, "max_players": 5, "play_time": 15, "genre": "Карточная", "rating": 6.3},
    {"title": "Цитадели", "min_players": 2, "max_players": 8, "play_time": 60, "genre": "Карточная", "rating": 7.0},
    {"title": "Глумхэвен", "min_players": 1, "max_players": 4, "play_time": 120, "genre": "Приключения", "rating": 8.6},
    {"title": "Шакал", "min_players": 2, "max_players": 4, "play_time": 60, "genre": "Семейная", "rating": 7.0},
    {"title": "Свинтус", "min_players": 2, "max_players": 10, "play_time": 20, "genre": "Карточная", "rating": 6.2},
]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/games/search")
def search_games(
    players: Optional[int] = Query(None, ge=1, description="Количество игроков"),
    max_time: Optional[int] = Query(None, ge=1, description="Максимальное время партии, мин"),
):
    result = [
        g for g in GAMES
        if (players is None or g["min_players"] <= players <= g["max_players"])
        and (max_time is None or g["play_time"] <= max_time)
    ]
    result.sort(key=lambda g: g["rating"], reverse=True)
    return {"players": players, "max_time": max_time, "count": len(result), "games": result}
