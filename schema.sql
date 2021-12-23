CREATE TABLE IF NOT EXISTS users_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESATAMP DEFAULT CURRENT_TIMESTAMP,
    chat_id INTEGER NOT NULL,
    command TEXT NOT NULL,
    town_id INTEGER NOT NULL,
    check_in TEXT,
    check_out TEXT
    min_price INTEGER,
    max_price INTEGER,
    min_distance INTEGER,
    max_distance INTEGER,
    results_num integer NOT NULL,
    photos_num INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS town_ids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    destinationId INTEGER NOT NULL UNIQUE,
    caption TEXT
);

CREATE TABLE IF NOT EXISTS hotels (
    id INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    address TEXT,
    distance TEXT
);

CREATE TABLE IF NOT EXISTS hotel_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_id INTEGER NOT NULL,
    url TEXT,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id)
);

CREATE TABLE IF NOT EXISTS search_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_history_id INTEGER NOT NULL,
    hotel_id INTEGER NOT NULL,
    hotel_price TEXT,
    FOREIGN KEY (user_history_id) REFERENCES users_history(id),
    FOREIGN KEY (hotel_id) REFERENCES hotels(id)
);
