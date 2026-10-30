"""Közös segédek a unit tesztekhez: tesztszerver külön szálban és egyszerű HTTP-kliens (csak standard library)."""
import json
import os
import sqlite3
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

GYOKER = Path(__file__).resolve().parent.parent
if str(GYOKER) not in sys.path:
    sys.path.insert(0, str(GYOKER))

ADATOK = GYOKER / "data" / "munkatarsak.json"


class Kliens:
    """Egyetlen felhasználó böngészőjét utánzó HTTP-kliens: a `kudos_user` sütit megjegyzi."""

    def __init__(self, port, suti=None):
        self.port = port
        self.suti = suti
        self.utolso_set_cookie = []

    def keres(self, modszer, utvonal, adat=None):
        torzs = json.dumps(adat).encode("utf-8") if adat is not None else None
        kerelem = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{utvonal}", data=torzs, method=modszer
        )
        if torzs is not None:
            kerelem.add_header("Content-Type", "application/json")
        if self.suti:
            kerelem.add_header("Cookie", f"kudos_user={self.suti}")
        try:
            valasz = urllib.request.urlopen(kerelem)
        except urllib.error.HTTPError as hiba:
            valasz = hiba
        with valasz:
            nyers = valasz.read()
            allapot = valasz.getcode()
            self.utolso_set_cookie = valasz.headers.get_all("Set-Cookie") or []
        for sor in self.utolso_set_cookie:
            nev, _, ertek = sor.split(";")[0].partition("=")
            if nev == "kudos_user":
                self.suti = ertek or None
        return allapot, (json.loads(nyers) if nyers else None)

    def get(self, utvonal):
        return self.keres("GET", utvonal)

    def post(self, utvonal, adat=None):
        return self.keres("POST", utvonal, adat)


class SzerverTeszt(unittest.TestCase):
    """Minden teszt saját, ideiglenes adatbázissal és szabad porton futó szervert kap."""

    def setUp(self):
        from kudos.web import szerver_letrehoz

        self.mappa = tempfile.TemporaryDirectory()
        self.addCleanup(self.mappa.cleanup)
        self.adatbazis = os.path.join(self.mappa.name, "teszt.db")
        self.szerver = szerver_letrehoz("127.0.0.1", 0, self.adatbazis, csendes=True)
        self.port = self.szerver.server_address[1]
        szal = threading.Thread(target=self.szerver.serve_forever, daemon=True)
        szal.start()
        self.addCleanup(self._leallit)

    def _leallit(self):
        self.szerver.shutdown()
        self.szerver.server_close()

    def kliens(self, suti=None):
        return Kliens(self.port, suti)

    def belep(self, munkatars_id):
        kliens = self.kliens()
        allapot, _ = kliens.post("/api/belepes", {"id": munkatars_id})
        self.assertEqual(allapot, 200)
        return kliens

    def beszur(self, kuldo, cimzett, kategoria="together", uzenet="Köszönöm!", lathatosag="privat",
               letrehozva=None):
        """Közvetlenül az adatbázisba ír egy köszönetet (előfeltétel-adat); az azonosítóját adja vissza."""
        letrehozva = (letrehozva or datetime.now()).isoformat(timespec="seconds")
        kapcsolat = sqlite3.connect(self.adatbazis)
        try:
            kurzor = kapcsolat.execute(
                "INSERT INTO koszonet (kuldo_id, cimzett_id, kategoria, uzenet, lathatosag, letrehozva)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (kuldo, cimzett, kategoria, uzenet, lathatosag, letrehozva))
            kapcsolat.commit()
            return kurzor.lastrowid
        finally:
            kapcsolat.close()

    def beszur_taps(self, koszonet_id, munkatars_id):
        kapcsolat = sqlite3.connect(self.adatbazis)
        try:
            kapcsolat.execute("INSERT INTO taps (koszonet_id, munkatars_id, letrehozva) VALUES (?, ?, ?)",
                              (koszonet_id, munkatars_id, datetime.now().isoformat(timespec="seconds")))
            kapcsolat.commit()
        finally:
            kapcsolat.close()

    def sorok(self, tabla="koszonet"):
        kapcsolat = sqlite3.connect(self.adatbazis)
        kapcsolat.row_factory = sqlite3.Row
        try:
            return [dict(sor) for sor in kapcsolat.execute(f"SELECT * FROM {tabla} ORDER BY rowid")]
        finally:
            kapcsolat.close()
