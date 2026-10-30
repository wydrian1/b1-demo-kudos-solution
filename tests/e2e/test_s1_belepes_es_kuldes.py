"""S1 – Belépés és köszönet küldése, böngészőben (EK-01…EK-07).

„Kész, ha…”: Horváth Anna belép, a keresőben megtalálja Farkas Júliát, „🤝 Deliver value together”
kategóriában emojis privát köszönetet ír, az ellenőrző nézet után elküldi, és megjelenik a toast.
"""
import re
import sys
import unittest
from datetime import datetime
from pathlib import Path

from playwright.sync_api import expect

sys.path.insert(0, str(Path(__file__).resolve().parent))
from alap import E2ETeszt  # noqa: E402

UZENET = "Köszönöm a gyors adatelemzést! 🙏🎉"
KERESO = "Keresés név, egység vagy e-mail alapján"


class TestS1(E2ETeszt):
    def kereso(self):
        return self.oldal.get_by_role("combobox", name=KERESO)

    def kategoria(self, nev):
        return self.oldal.get_by_role("radio", name=re.compile(re.escape(nev)))

    def uzenet_mezo(self):
        return self.oldal.get_by_label("Üzenet", exact=True)

    # --- EK-01, EK-02: belépés ---------------------------------------------------------------

    def test_s1_ek01_anna_belep_a_listabol(self):
        """EK-01: a lista 17 munkatársat mutat, Horváth Anna belép, a DEMO sáv a nevét mutatja."""
        self.oldal.goto(self.cim("/"))
        expect(self.oldal.get_by_role("heading", name="Belépés mint…")).to_be_visible()
        expect(self.oldal.get_by_text("DEMO – szimulált belépés")).to_be_visible()
        lista = self.oldal.get_by_role("list", name="Munkatársak")
        expect(lista.get_by_role("listitem")).to_have_count(17)

        lista.get_by_role("button", name=re.compile("Horváth Anna")).click()

        expect(self.oldal.get_by_role("heading", name="Kudos fal")).to_be_visible()
        expect(self.oldal.get_by_text("DEMO belépés: Horváth Anna · Fejlesztési Osztály")).to_be_visible()
        self.assertEqual(self.oldal.request.get(self.cim("/api/en")).json()["id"], "u05")

    def test_s1_ek01_valtas_kileptet_es_visszavisz_a_belepeshez(self):
        """EK-01: a [Váltás] gomb kiléptet, másik munkatárs léphet be."""
        self.belep("Horváth Anna")
        self.oldal.get_by_role("button", name="Váltás").click()
        expect(self.oldal.get_by_role("heading", name="Belépés mint…")).to_be_visible()
        self.assertEqual(self.oldal.request.get(self.cim("/api/en")).status, 401)

        self.oldal.get_by_role("button", name=re.compile("Varga Bence")).click()
        expect(self.oldal.get_by_text("DEMO belépés: Varga Bence · Fejlesztési Osztály")).to_be_visible()

    def test_s1_ek02_belepes_nelkul_a_belepesi_oldalra_iranyit(self):
        """EK-02: süti nélkül a Fal és az Új köszönet oldal a belépéshez irányít, az API 401."""
        self.oldal.goto(self.cim("/#/fal"))
        expect(self.oldal.get_by_role("heading", name="Belépés mint…")).to_be_visible()
        expect(self.oldal).to_have_url(re.compile(r"#/belepes$"))

        self.oldal.goto(self.cim("/#/uj"))
        expect(self.oldal.get_by_role("heading", name="Belépés mint…")).to_be_visible()

        kerelem = self.oldal.request
        self.assertEqual(kerelem.get(self.cim("/api/fal")).status, 401)
        self.assertEqual(kerelem.get(self.cim("/api/ertesitesek")).status, 401)
        self.assertEqual(kerelem.post(self.cim("/api/koszonetek"), data={}).status, 401)
        self.assertEqual(len(kerelem.get(self.cim("/api/munkatarsak")).json()), 17)

    # --- EK-03, EK-04: címzettkereső --------------------------------------------------------

    def test_s1_ek03_cimzettkereso_egyseg_email_es_sajat_nev_szerint(self):
        """EK-03: „adat” → az Adat Osztály 5 tagja, „julia.f” → Farkas Júlia, „horváth” → nincs találat."""
        self.uj_koszonet("Horváth Anna")
        kereso = self.kereso()
        opciok = self.oldal.get_by_role("option")

        kereso.fill("adat")
        expect(opciok).to_have_count(5)
        szovegek = opciok.all_inner_texts()
        for nev, beosztas in [("Szabó Katalin", "osztályvezető"), ("Farkas Júlia", "adatelemző"),
                              ("Balogh Máté", "adatmérnök"), ("Papp Zsófia", "adatmérnök"),
                              ("Takács Levente", "BI fejlesztő")]:
            sor = [s for s in szovegek if nev in s]
            self.assertEqual(len(sor), 1, nev)
            self.assertIn(beosztas, sor[0])
            self.assertIn("Adat Osztály", sor[0])

        kereso.fill("julia.f")
        expect(opciok).to_have_count(1)
        expect(opciok.first).to_contain_text("Farkas Júlia")
        expect(opciok.first).to_contain_text("adatelemző")
        expect(opciok.first).to_contain_text("Adat Osztály")

        kereso.fill("horváth")
        expect(self.oldal.get_by_text("Nincs találat")).to_be_visible()
        expect(opciok).to_have_count(0)

    def test_s1_ek04_kereso_billentyuzettel(self):
        """EK-04: „Far” + ↓ + Enter → Farkas Júlia a címzett, 2. lépés; az Esc bezárja a listát."""
        self.uj_koszonet("Horváth Anna")
        kereso = self.kereso()
        opciok = self.oldal.get_by_role("option")

        kereso.fill("Far")
        expect(opciok).to_have_count(1)
        kereso.press("Escape")
        expect(opciok).to_have_count(0)
        expect(kereso).to_have_value("Far")

        kereso.fill("Far")
        expect(opciok).to_have_count(1)
        kereso.press("ArrowDown")
        kereso.press("Enter")
        expect(self.oldal.get_by_role("heading", name="Mit?")).to_be_visible()
        expect(self.oldal.get_by_text("Farkas Júlia").first).to_be_visible()

    # --- EK-05, EK-06: varázsló, ellenőrző nézet, küldés ----------------------------------

    def test_s1_ek05_ek06_anna_privat_koszonetet_kuld_julianak(self):
        """EK-05, EK-06: a teljes „Kész, ha…” forgatókönyv, DB-ellenőrzéssel."""
        self.uj_koszonet("Horváth Anna")
        self.kereso().fill("julia.f")
        self.oldal.get_by_role("option", name=re.compile("Farkas Júlia")).click()

        expect(self.oldal.get_by_role("heading", name="Mit?")).to_be_visible()
        self.kategoria("Deliver value together").click()
        self.uzenet_mezo().fill(UZENET)
        expect(self.oldal.get_by_role("radio", name=re.compile("Privát"))).to_be_checked()
        self.oldal.get_by_role("button", name="Tovább").click()

        # 3. lépés: az ellenőrző nézet pontosan a leendő kártya
        expect(self.oldal.get_by_role("heading", name="Ellenőrzés")).to_be_visible()
        expect(self.oldal.get_by_label("Lépések").locator('[aria-current="step"]')).to_contain_text("Ellenőrzés")
        kartya = self.oldal.get_by_role("article")
        expect(kartya).to_contain_text("Horváth Anna")
        expect(kartya).to_contain_text("Farkas Júlia")
        expect(kartya).to_contain_text("Deliver value together")
        expect(kartya).to_contain_text(UZENET)
        expect(kartya.get_by_role("img", name="Privát")).to_be_visible()

        # Vissza: minden adat megmarad a 2. lépésen
        self.oldal.get_by_role("button", name="Vissza").click()
        expect(self.oldal.get_by_role("heading", name="Mit?")).to_be_visible()
        expect(self.kategoria("Deliver value together")).to_be_checked()
        expect(self.uzenet_mezo()).to_have_value(UZENET)
        expect(self.oldal.get_by_role("radio", name=re.compile("Privát"))).to_be_checked()

        self.oldal.get_by_role("button", name="Tovább").click()
        self.assertEqual(self.sorok(), [], "a Tovább még nem küld")
        self.oldal.get_by_role("button", name="Küldés").click()

        toast = self.oldal.get_by_role("status")
        expect(toast).to_contain_text("Köszönetedet elküldtük Farkas Júliának! 🎉")
        expect(toast).to_have_attribute("aria-live", "polite")

        sorok = self.sorok()
        self.assertEqual(len(sorok), 1)
        sor = sorok[0]
        self.assertEqual(
            (sor["kuldo_id"], sor["cimzett_id"], sor["kategoria"], sor["lathatosag"], sor["uzenet"]),
            ("u05", "u09", "together", "privat", UZENET),
        )
        kulonbseg = abs((datetime.now() - datetime.fromisoformat(sor["letrehozva"])).total_seconds())
        self.assertLess(kulonbseg, 5)

    # --- EK-07: arculati alapok ---------------------------------------------------------------

    def test_s1_ek07_arculati_alapok_fejlec_tokenek_nincs_kulso_keres_es_felugro_ablak(self):
        """EK-07: sötét fejléc, a tokenek betöltődnek, csak helyi kérések, nincs alert/confirm."""
        kerelmek, parbeszedek = [], []
        self.oldal.on("request", lambda k: kerelmek.append(k.url))
        self.oldal.on("dialog", lambda d: (parbeszedek.append(d.message), d.dismiss()))

        self.uj_koszonet("Horváth Anna")
        self.kereso().fill("julia.f")
        self.oldal.get_by_role("option", name=re.compile("Farkas Júlia")).click()
        self.kategoria("Deliver value together").click()
        self.uzenet_mezo().fill(UZENET)
        self.oldal.get_by_role("button", name="Tovább").click()
        expect(self.oldal.get_by_role("heading", name="Ellenőrzés")).to_be_visible()

        fejlec = self.oldal.get_by_role("banner").evaluate("e => getComputedStyle(e).backgroundColor")
        self.assertEqual(fejlec, "rgb(43, 45, 51)")
        sarga = self.oldal.evaluate(
            "() => getComputedStyle(document.documentElement).getPropertyValue('--yellow').trim()"
        )
        self.assertEqual(sarga.upper(), "#FEE600")
        self.assertTrue(any(u.endswith("/static/style.css") for u in kerelmek))
        kulso = [u for u in kerelmek if not (u.startswith(self.cim("")) or u.startswith("data:"))]
        self.assertEqual(kulso, [])
        self.assertEqual(parbeszedek, [])


if __name__ == "__main__":
    unittest.main()
