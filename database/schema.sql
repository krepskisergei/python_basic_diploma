PRAGMA foreing_keys=on;

CREATE TABLE "history"(
    "id" INTEGER NOT NULL,
    "chatId" INTEGER NOT NULL,
    "queryTime" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "command" VARCHAR(10) NOT NULL,
    "locationId" INTEGER,
    "checkIn" DATE,
    "checkOut" DATE,
    "priceMin" REAL DEFAULT 0,
    "priceMax" REAL
    "distanceMin" REAL DEFAULT 0,
    "distanceMax" REAL,
    "resultsNum" INTEGER,
    "photosNum" INTEGER DEFAULT 0,
    "complete" BOOLEAN DEFAULT FALSE,
    PRIMARY KEY("id"),
    FOREIGN KEY("locationId") REFERENCES "locations"("destinationId") 
        ON UPDATE CASCADE 
        ON DELETE SET NULL
);

CREATE TABLE "locations"(
    "destinationId" INTEGER NOT NULL,
    "geoId" INTEGER NOT NULL,
    "caption" VARCHAR(255) NOT NULL UNIQUE,
    "name" VARCHAR(50),
    PRIMARY KEY ("destinationId")
);

CREATE TABLE "hotels"(
    "id" INTEGER NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    "fullAddress" VARCHAR(255) NOT NULL,
    "url" VARCHAR(255),
    "starRating" INTEGER DEFAULT 0,
    "distance" VARCHAR(20),
    PRIMARY KEY("id")
);

CREATE TABLE "photos"(
    "imageId" INTEGER NOT NULL,
    "hotelId" INTEGER NOT NULL,
    "baseUrl" TEXT NOT NULL,
    PRIMARY KEY("imageId"),
    FOREIGN KEY("hotelId") REFERENCES "hotels"("id") 
        ON UPDATE CASCADE 
        ON DELETE CASCADE
);

CREATE TABLE "results"(
    "id" INTEGER NOT NULL,
    "historyId" INTEGER NOT NULL,
    "hotelId" INTEGER NOT NULL,
    "price" REAL NOT NULL,
    PRIMARY KEY("id"),
    FOREIGN KEY("historyId") REFERENCES "history"("id") 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    FOREIGN KEY("hotelId") REFERENCES "hotels"("id") 
        ON UPDATE CASCADE 
        ON DELETE CASCADE
)
