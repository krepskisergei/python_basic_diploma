PRAGMA foreing_keys=on;

CREATE TABLE "sessions"(
    "id" INTEGER NOT NULL,
    "chat_id" INTEGER NOT NULL,
    "query_time" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "command" VARCHAR(10) NOT NULL,
    "location_id" INTEGER DEFAULT NULL,
    "check_in" DATE DEFAULT NULL,
    "check_out" DATE DEFAULT NULL,
    "price_min" REAL DEFAULT NULL,
    "price_max" REAL DEFAULT NULL,
    "distance_min" REAL DEFAULT NULL,
    "distance_max" REAL DEFAULT NULL,
    "results_num" INTEGER DEFAULT NULL,
    "photos_show" BOOLEAN DEFAULT NULL,
    "photos_num" INTEGER DEFAULT NULL,
    "complete" BOOLEAN DEFAULT FALSE,
    PRIMARY KEY("id"),
    FOREIGN KEY("location_id") REFERENCES "locations"("destination_id") 
        ON UPDATE CASCADE 
        ON DELETE SET NULL
);

CREATE TABLE "locations"(
    "destination_id" INTEGER NOT NULL,
    "geo_id" INTEGER NOT NULL,
    "caption" VARCHAR(255) NOT NULL UNIQUE,
    "name" VARCHAR(50),
    "name_lower" VARCHAR(50),
    PRIMARY KEY ("destination_id")
);

CREATE TABLE "hotels"(
    "id" INTEGER NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    "address" VARCHAR(255) NOT NULL,
    "star_rating" INTEGER DEFAULT 0,
    "distance" REAL DEFAULT NULL,
    PRIMARY KEY("id")
);

CREATE TABLE "photos"(
    "id" INTEGER NOT NULL,
    "hotel_id" INTEGER NOT NULL,
    "url" TEXT NOT NULL,
    PRIMARY KEY("id"),
    FOREIGN KEY("hotel_id") REFERENCES "hotels"("id") 
        ON UPDATE CASCADE 
        ON DELETE CASCADE
);

CREATE TABLE "results"(
    "id" INTEGER NOT NULL,
    "session_id" INTEGER NOT NULL,
    "hotel_id" INTEGER NOT NULL,
    "url" TEXT,
    "price" REAL NOT NULL,
    PRIMARY KEY("id"),
    FOREIGN KEY("session_id") REFERENCES "sessions"("id") 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    FOREIGN KEY("hotel_id") REFERENCES "hotels"("id") 
        ON UPDATE CASCADE 
        ON DELETE CASCADE
)
