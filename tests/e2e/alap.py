"""Közös alap a böngészős (E2E) tesztekhez.

Minden teszt maga indítja az alkalmazást alfolyamatként (szabad porton, ideiglenes adatbázissal),
megvárja, amíg válaszol, és a végén leállítja. A böngésző (Chromium, Playwright) osztályonként egyszer indul.
`HEADED=1` esetén látható ablakkal és lassítással fut.
"""
import os
import re
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
from datetime import datetime
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

GYOKER = Path(__file__).resolve().parents[2]


def szabad_port(kezdo=8765):
    for port in range(kezdo, kezdo + 200):
        with socket.socket() as foglalo:
            try:
                foglalo.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("Nincs szabad port a teszteléshez.")


class E2ETeszt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        lathato = os.environ.get("HEADED") == "1"
        cls.bongeszo = cls.playwright.chromium.launch(headless=not lathato, slow_mo=400 if lathato else 0)

    @classmethod
    def tearDownClass(cls):
        cls.bongeszo.close()
        cls.playwright.stop()

    def setUp(self):
        self.mappa = tempfile.TemporaryDirectory()
        self.addCleanup(self.mappa.cleanup)
        self.adatbazis = os.path.join(self.mappa.name, "teszt.db")
        self.port = szabad_port()
        self.naplo = Path(self.mappa.name) / "app.log"
        kornyezet = dict(os.environ, PORT=str(self.port), KUDOS_DB=self.adatbazis)
        with open(self.naplo, "w") as naplo:
            self.folyamat = subprocess.Popen(
                [sys.executable, str(GYOKER / "app.py")],
                cwd=GYOKER, env=kornyezet, stdout=naplo, stderr=subprocess.STDOUT,
            )
        self.addCleanup(self._leallit)
        self._megvar()

        self.kontextus = self.bongeszo.new_context(viewport={"width": 1280, "height": 800}, locale="hu-HU")
        self.addCleanup(self.kontextus.close)
        self.oldal = self.kontextus.new_page()
        self.oldal.set_default_timeout(5000)
        expect.set_options(timeout=5000)

    def _megvar(self):
        hatarido = time.time() + 10
        while time.time() < hatarido:
            if self.folyamat.poll() is not None:
                break
            try:
                urllib.request.urlopen(self.cim("/api/munkatarsak"), timeout=1).close()
                return
            except OSError:
                time.sleep(0.1)
        self.fail("Az alkalmazás nem indult el:\n" + self.naplo.read_text(errors="replace"))

    def _leallit(self):
        if self.folyamat.poll() is None:
            self.folyamat.terminate()
            try:
                self.folyamat.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.folyamat.kill()

    def cim(self, utvonal="/"):
        return f"http://127.0.0.1:{self.port}{utvonal}"

    def belep(self, nev):
        """Belépés a listából; a Kudos falon áll meg."""
        self.oldal.goto(self.cim("/"))
        self.oldal.get_by_role("button", name=re.compile(re.escape(nev))).click()
        expect(self.oldal.get_by_role("heading", name="Kudos fal")).to_be_visible()

    def uj_koszonet(self, nev):
        """Belépés után az Új köszönet varázsló 1. lépéséig."""
        self.belep(nev)
        self.oldal.get_by_role("navigation", name="Főmenü").get_by_role("link", name="Új köszönet").click()
        expect(self.oldal.get_by_role("heading", name="Kinek?")).to_be_visible()

    def valt(self, nev):
        """A [Váltás] gombbal másik munkatársként lép be."""
        self.oldal.get_by_role("button", name="Váltás").click()
        self.oldal.get_by_role("button", name=re.compile(re.escape(nev))).click()
        expect(self.oldal.get_by_role("heading", name="Kudos fal")).to_be_visible()

    def beszur(self, kuldo, cimzett, kategoria="together", uzenet="Köszönöm!", lathatosag="privat",
               letrehozva=None):
        """Közvetlenül az adatbázisba ír egy köszönetet (előfeltétel-adat a tesztekhez)."""
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
