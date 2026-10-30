"""Képernyőképek a dokumentációhoz.

Futtatás: `.venv/bin/python dokumentacio/kepek_keszitese.py`

Az alkalmazást ideiglenes adatbázissal, külön porton indítja (a `kudos.db`-hez nem nyúl), minta-köszönetekkel
tölti fel a `data/munkatarsak.json` neveivel, és a `dokumentacio/kepek/` mappába menti a képeket.
"""
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

GYOKER = Path(__file__).resolve().parents[1]
KEPEK = Path(__file__).resolve().parent / "kepek"
PORT = 8791
KERESO = "Keresés név, egység vagy e-mail alapján"

# (küldő, címzett, kategória, üzenet, láthatóság, hány órája)
MINTAK = [
    ("u05", "u09", "together", "Köszönöm a gyors adatelemzést a negyedéves riporthoz!", "nyilvanos", 3),
    ("u06", "u05", "experiment", "Remek ötlet volt az új tesztkörnyezet, rengeteg időt spórolt a csapatnak.", "nyilvanos", 26),
    ("u13", "u16", "forward", "Éjszaka is felvetted a riasztást, és percek alatt megoldottad. Köszi!", "nyilvanos", 50),
    ("u07", "u06", "loyalty", "Az ügyfélbemutatón nagyon szépen levezetted a hibajavítás lépéseit.", "privat", 70),
    ("u10", "u09", "together", "Segítettél a lekérdezés optimalizálásában, így sokkal gyorsabb lett.", "privat", 5),
    ("u11", "u10", "experiment", "Kipróbáltad az új adatbetöltési megoldást, és megosztottad a tanulságokat.", "nyilvanos", 120),
    ("u12", "u11", "loyalty", "Az ügyfél külön megdicsérte a pontos jelentésedet.", "privat", 200),
    ("u03", "u12", "forward", "Átvetted a leesett BI-feladatot, pedig nem is a te dolgod volt.", "nyilvanos", 30),
]
TAPSOK = [(1, "u06"), (1, "u13"), (1, "u03"), (6, "u05"), (6, "u09")]


def betolt_munkatarsak():
    import json
    with open(GYOKER / "data" / "munkatarsak.json", encoding="utf-8") as fajl:
        return {m["id"]: m["nev"] for m in json.load(fajl)["munkatarsak"]}


def feltolt(adatbazis):
    kapcs = sqlite3.connect(adatbazis)
    most = datetime.now()
    for kuldo, cimzett, kategoria, uzenet, lathatosag, oraja in MINTAK:
        kapcs.execute(
            "INSERT INTO koszonet (kuldo_id, cimzett_id, kategoria, uzenet, lathatosag, letrehozva)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (kuldo, cimzett, kategoria, uzenet, lathatosag,
             (most - timedelta(hours=oraja)).isoformat(timespec="seconds")))
    for koszonet_id, munkatars in TAPSOK:
        kapcs.execute("INSERT INTO taps (koszonet_id, munkatars_id, letrehozva) VALUES (?, ?, ?)",
                      (koszonet_id, munkatars, most.isoformat(timespec="seconds")))
    # Értesítés: Farkas Júlia a 2 hozzá szóló köszönetről, Szabó Katalin a csapata köszönetéről.
    for munkatars, koszonet_id in (("u09", 1), ("u09", 5), ("u03", 1)):
        kapcs.execute("INSERT INTO ertesites (munkatars_id, koszonet_id, letrehozva) VALUES (?, ?, ?)",
                      (munkatars, koszonet_id, most.isoformat(timespec="seconds")))
    kapcs.commit()
    kapcs.close()


def megvar(port):
    hatarido = time.time() + 10
    while time.time() < hatarido:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/api/munkatarsak", timeout=1).close()
            return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("Az alkalmazás nem indult el.")


def main():
    KEPEK.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as mappa:
        adatbazis = os.path.join(mappa, "kepek.db")
        folyamat = subprocess.Popen(
            [sys.executable, str(GYOKER / "app.py")], cwd=GYOKER,
            env=dict(os.environ, PORT=str(PORT), KUDOS_DB=adatbazis),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            megvar(PORT)
            feltolt(adatbazis)
            kepek_keszitese(f"http://127.0.0.1:{PORT}")
        finally:
            folyamat.terminate()
            folyamat.wait(timeout=5)


def kepek_keszitese(cim):
    with sync_playwright() as pw:
        bongeszo = pw.chromium.launch()

        def uj_oldal(szelesseg=1280, magassag=800):
            kontextus = bongeszo.new_context(viewport={"width": szelesseg, "height": magassag}, locale="hu-HU")
            oldal = kontextus.new_page()
            oldal.set_default_timeout(5000)
            return kontextus, oldal

        def belep(oldal, nev):
            oldal.goto(cim + "/")
            oldal.get_by_role("button", name=re.compile(re.escape(nev))).click()
            expect(oldal.get_by_role("heading", name="Kudos fal")).to_be_visible()

        def kep(oldal, fajl, teljes=False):
            oldal.wait_for_timeout(300)
            oldal.screenshot(path=str(KEPEK / fajl), full_page=teljes)
            print("kész:", fajl)

        # 1. Belépés
        kontextus, oldal = uj_oldal()
        oldal.goto(cim + "/")
        expect(oldal.get_by_role("heading", name="Belépés mint…")).to_be_visible()
        kep(oldal, "01-belepes.png", teljes=True)

        # 2. Új köszönet: a 3 lépés (Horváth Anna → Farkas Júlia)
        oldal.get_by_role("button", name=re.compile("Horváth Anna")).click()
        expect(oldal.get_by_role("heading", name="Kudos fal")).to_be_visible()
        oldal.get_by_role("navigation", name="Főmenü").get_by_role("link", name="Új köszönet").click()
        oldal.get_by_role("combobox", name=KERESO).fill("julia.f")
        expect(oldal.get_by_role("option", name=re.compile("Farkas Júlia"))).to_be_visible()
        kep(oldal, "02-uj-koszonet-1-kinek.png")
        oldal.get_by_role("option", name=re.compile("Farkas Júlia")).click()
        expect(oldal.get_by_role("heading", name="Mit?")).to_be_visible()
        oldal.get_by_role("button", name="Tovább").click()  # üresen: hibaüzenetek a mezők alatt
        expect(oldal.get_by_text("Válassz kategóriát.")).to_be_visible()
        kep(oldal, "03-uj-koszonet-2-hibak.png", teljes=True)
        oldal.get_by_role("radio", name=re.compile("Deliver value together")).click()
        oldal.get_by_label("Üzenet", exact=True).fill("Köszönöm a gyors adatelemzést! 🙏🎉")
        oldal.get_by_role("radio", name=re.compile("Nyilvános")).click()
        kep(oldal, "04-uj-koszonet-2-mit.png", teljes=True)
        oldal.get_by_role("button", name="Tovább").click()
        expect(oldal.get_by_role("heading", name="Ellenőrzés")).to_be_visible()
        kep(oldal, "05-uj-koszonet-3-ellenorzes.png", teljes=True)
        oldal.get_by_role("button", name="Küldés").click()
        expect(oldal.get_by_role("heading", name="Saját köszönetek")).to_be_visible()
        expect(oldal.get_by_text("Köszönetedet elküldtük")).to_be_visible()
        kep(oldal, "06-kuldes-utan-toast.png")
        kontextus.close()

        # 3. Saját köszönetek (Farkas Júlia, Kapott)
        kontextus, oldal = uj_oldal()
        belep(oldal, "Farkas Júlia")
        oldal.get_by_role("navigation", name="Főmenü").get_by_role("link", name="Saját").click()
        expect(oldal.get_by_role("heading", name="Saját köszönetek")).to_be_visible()
        kep(oldal, "07-sajat-kapott.png", teljes=True)

        # 4. Értesítések (Farkas Júlia, megnyitott panel)
        oldal.get_by_role("button", name=re.compile(r"^Értesítések")).click()
        expect(oldal.get_by_role("region", name="Értesítések")).to_be_visible()
        kep(oldal, "08-ertesitesek.png")
        kontextus.close()

        # 5. Közös fal (Juhász Nóra)
        kontextus, oldal = uj_oldal()
        belep(oldal, "Juhász Nóra")
        kep(oldal, "09-fal.png", teljes=True)
        kontextus.close()

        # 6. Vezetői nézet statisztikával (Szabó Katalin)
        kontextus, oldal = uj_oldal()
        belep(oldal, "Szabó Katalin")
        oldal.get_by_role("navigation", name="Főmenü").get_by_role("link", name="Csapat").click()
        expect(oldal.get_by_role("heading", name="Csapatköszönetek")).to_be_visible()
        kep(oldal, "10-csapat-statisztika.png", teljes=True)
        kontextus.close()

        # 7. Mobilnézet (Horváth Anna, 375 px)
        kontextus, oldal = uj_oldal(375, 760)
        belep(oldal, "Horváth Anna")
        kep(oldal, "11-mobil-fal.png")
        kontextus.close()

        bongeszo.close()


if __name__ == "__main__":
    main()
