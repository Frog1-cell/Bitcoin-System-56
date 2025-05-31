DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS bitcoin_price;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    euro REAL,
    bitcoin REAL,
    is_admin INTEGER
);

CREATE TABLE bitcoin_price (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    price REAL,
    time TEXT
);

INSERT INTO bitcoin_price (price, time) VALUES (20000, datetime('now'));
