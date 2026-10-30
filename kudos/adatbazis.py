"""SQLite-kapcsolat és séma."""
import sqlite3

SEMA = """
CREATE TABLE IF NOT EXISTS koszonet (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    kuldo_id    TEXT NOT NULL,
    cimzett_id  TEXT NOT NULL,
    kategoria   TEXT NOT NULL,
    uzenet      TEXT NOT NULL,
    lathatosag  TEXT NOT NULL DEFAULT 'privat',
    letrehozva  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS taps (
    koszonet_id  INTEGER NOT NULL REFERENCES koszonet(id),
    munkatars_id TEXT NOT NULL,
    letrehozva   TEXT NOT NULL,
    PRIMARY KEY (koszonet_id, munkatars_id)
);

CREATE TABLE IF NOT EXISTS ertesites (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    munkatars_id TEXT NOT NULL,
    koszonet_id  INTEGER NOT NULL REFERENCES koszonet(id),
    olvasott     INTEGER NOT NULL DEFAULT 0,
    letrehozva   TEXT NOT NULL,
    UNIQUE (munkatars_id, koszonet_id)
);
"""


def kapcsolat(utvonal):
    kapcs = sqlite3.connect(utvonal)
    kapcs.row_factory = sqlite3.Row
    kapcs.execute("PRAGMA foreign_keys = ON")
    return kapcs


def inicializal(utvonal):
    kapcs = kapcsolat(utvonal)
    try:
        kapcs.executescript(SEMA)
        kapcs.commit()
    finally:
        kapcs.close()
