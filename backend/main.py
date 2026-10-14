"""Backend: REST API клуба настольных игр (PostgreSQL + интеграция с web-service)."""
import os
from typing import Optional

import httpx
import psycopg
from fastapi import FastAPI, HTTPException, Query
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

DB_DSN = (
    f"host={os.getenv('DB_HOST', 'db')} port={os.getenv('DB_PORT', '5432')} "
    f"dbname={os.getenv('DB_NAME', 'boardgames')} user={os.getenv('DB_USER', 'club')} "
    f"password={os.getenv('DB_PASSWORD', 'club_pass')}"
)
WEB_SERVICE_URL = os.getenv("WEB_SERVICE_URL", "http://web-service:5001")

app = FastAPI(title="Board Games Club API")


class GameIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    min_players: int = Field(ge=1)
    max_players: int = Field(ge=1)
    play_time: int = Field(ge=1)
    genre: Optional[str] = None
    copies: int = Field(default=1, ge=0)


def query(sql: str, params: tuple = (), fetch: str = "all"):
    with psycopg.connect(DB_DSN, row_factory=dict_row) as conn:
        cur = conn.execute(sql, params)
        if fetch == "all":
            return cur.fetchall()
        if fetch == "one":
            return cur.fetchone()
        return None


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/collection")
def list_collection():
    return query("SELECT * FROM club_collection ORDER BY added_at DESC, id DESC")


@app.post("/api/collection", status_code=201)
def add_game(game: GameIn):
    if game.max_players < game.min_players:
        raise HTTPException(400, "max_players не может быть меньше min_players")
    row = query(
        """INSERT INTO club_collection (title, min_players, max_players, play_time, genre, copies)
           VALUES (%s, %s, %s, %s, %s, %s)
           ON CONFLICT (title) DO UPDATE SET copies = club_collection.copies + EXCLUDED.copies
           RETURNING *""",
        (game.title, game.min_players, game.max_players, game.play_time, game.genre, game.copies),
        fetch="one",
    )
    return row


@app.delete("/api/collection/{game_id}", status_code=204)
def delete_game(game_id: int):
    row = query("DELETE FROM club_collection WHERE id = %s RETURNING id", (game_id,), fetch="one")
    if row is None:
        raise HTTPException(404, "Игра не найдена")


@app.get("/api/search")
def search(players: Optional[int] = Query(None, ge=1), max_time: Optional[int] = Query(None, ge=1)):
    params = {k: v for k, v in {"players": players, "max_time": max_time}.items() if v is not None}
    try:
        resp = httpx.get(f"{WEB_SERVICE_URL}/games/search", params=params, timeout=5)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Web-сервис недоступен: {e}")
    data = resp.json()
    owned = {r["title"] for r in query("SELECT title FROM club_collection")}
    for g in data["games"]:
        g["in_collection"] = g["title"] in owned
    return data
