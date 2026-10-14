-- Настольная коллекция клуба
CREATE TABLE IF NOT EXISTS club_collection (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(200) NOT NULL UNIQUE,
    min_players  INT NOT NULL CHECK (min_players > 0),
    max_players  INT NOT NULL CHECK (max_players >= min_players),
    play_time    INT NOT NULL CHECK (play_time > 0),   -- минут
    genre        VARCHAR(100),
    copies       INT NOT NULL DEFAULT 1 CHECK (copies >= 0),
    added_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO club_collection (title, min_players, max_players, play_time, genre, copies) VALUES
    ('Каркассон',          2, 5,  45, 'Выкладывание тайлов', 2),
    ('Колонизаторы',       3, 4,  90, 'Экономическая',       1),
    ('Билет на поезд',     2, 5,  60, 'Семейная',            1),
    ('Кодовые имена',      2, 8,  15, 'Пати-игра',           3),
    ('Пандемия',           2, 4,  45, 'Кооперативная',       1)
ON CONFLICT (title) DO NOTHING;
