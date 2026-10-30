"""S4 – Közös fal és taps, böngészőben (EK-22…EK-28).

„Kész, ha…”: Juhász Nóra a falon látja Anna nyilvános köszönetét Júliának, a privátot nem; tapsol rá, és a
taps visszavonható. Mobilszélességen alsó tab-sáv van.
"""
import re
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from playwright.sync_api import expect

sys.path.insert(0, str(Path(__file__).resolve().parent))
from alap import E2ETeszt  # noqa: E402

SZURO_ELEMEK = ["Minden kategória", "💛 Earn customer loyalty", "🚀 Take actions to move forward",
                "🤝 Deliver value together", "🧪 Experiment, learn fast!"]
SARGA = "rgb(254, 230, 0)"


class TestS4(E2ETeszt):
    def kartyak(self):
        return self.oldal.get_by_role("article")

    def taps(self, kartya):
        return kartya.get_by_role("button", name=re.compile(r"^Taps"))

    def kategoria_szuro(self):
        return self.oldal.get_by_label("Kategória", exact=True)

    def fo_menu(self):
        return self.oldal.get_by_role("navigation", name="Főmenü")

    # --- EK-22 ----------------------------------------------------------------------------------

    def test_s4_ek22_a_falon_csak_a_nyilvanos_koszonet_latszik_mindenkinek(self):
        """EK-22: Nóra, Bence, Réka és László falán egyaránt csak a „Nyilvános köszi” kártya van."""
        self.beszur("u05", "u09", uzenet="Nyilvános köszi", lathatosag="nyilvanos")
        self.beszur("u06", "u07", uzenet="Privát köszi", lathatosag="privat")
        elso = True
        for nev in ("Juhász Nóra", "Varga Bence", "Kiss Réka", "Fehér László"):
            with self.subTest(nev=nev):
                if elso:
                    self.belep(nev)
                    elso = False
                else:
                    self.valt(nev)
                expect(self.kartyak()).to_have_count(1)
                expect(self.kartyak().first).to_contain_text("Nyilvános köszi")
                expect(self.oldal.get_by_text("Privát köszi")).to_have_count(0)
                api = self.oldal.request.get(self.cim("/api/fal")).json()
                self.assertEqual([k["uzenet"] for k in api], ["Nyilvános köszi"])

    # --- EK-23 ----------------------------------------------------------------------------------

    def test_s4_ek23_kategoriaszuro_a_falon(self):
        """EK-23: a szűrő a 4 kategóriát kínálja; 🤝 → 2 kártya, 🚀 → üres állapot; a legújabb elöl."""
        most = datetime.now()
        self.beszur("u05", "u09", "together", "elso", "nyilvanos", most - timedelta(hours=3))
        self.beszur("u06", "u09", "loyalty", "masodik", "nyilvanos", most - timedelta(hours=2))
        self.beszur("u07", "u09", "together", "harmadik", "nyilvanos", most - timedelta(hours=1))
        self.belep("Juhász Nóra")

        self.assertEqual(self.kategoria_szuro().locator("option").all_inner_texts(), SZURO_ELEMEK)
        expect(self.kartyak()).to_have_count(3)
        self.assertIn("harmadik", self.kartyak().first.inner_text())

        self.kategoria_szuro().select_option(label="🤝 Deliver value together")
        expect(self.kartyak()).to_have_count(2)
        self.kategoria_szuro().select_option(label="🚀 Take actions to move forward")
        expect(self.kartyak()).to_have_count(0)
        expect(self.oldal.get_by_text("Nincs találat")).to_be_visible()
        self.kategoria_szuro().select_option(label="Minden kategória")
        expect(self.kartyak()).to_have_count(3)

    # --- EK-24 ----------------------------------------------------------------------------------

    def test_s4_ek24_taps_es_visszavonas(self):
        """EK-24: „👏 1” sárga, aria-pressed=true; második kattintásra „👏 0”, keretes; újratöltés után is megmarad."""
        self.beszur("u05", "u09", lathatosag="nyilvanos")
        self.belep("Varga Bence")
        gomb = self.taps(self.kartyak().first)
        expect(gomb).to_have_text("👏 0")
        expect(gomb).to_have_attribute("aria-pressed", "false")
        self.assertNotEqual(gomb.evaluate("e => getComputedStyle(e).backgroundColor"), SARGA)

        gomb.click()
        expect(gomb).to_have_text("👏 1")
        expect(gomb).to_have_attribute("aria-pressed", "true")
        self.assertEqual(gomb.evaluate("e => getComputedStyle(e).backgroundColor"), SARGA)

        self.oldal.reload()
        gomb = self.taps(self.kartyak().first)
        expect(gomb).to_have_text("👏 1")
        expect(gomb).to_have_attribute("aria-pressed", "true")

        gomb.click()
        expect(gomb).to_have_text("👏 0")
        expect(gomb).to_have_attribute("aria-pressed", "false")
        self.assertNotEqual(gomb.evaluate("e => getComputedStyle(e).backgroundColor"), SARGA)
        self.assertEqual(self.sorok("taps"), [])

    # --- EK-25 ----------------------------------------------------------------------------------

    def test_s4_ek25_negy_szemely_negy_taps(self):
        """EK-25: Bence, Réka, Anna (küldő) és Júlia (címzett) tapsol egyszer-egyszer → 4."""
        self.beszur("u05", "u09", lathatosag="nyilvanos")
        elso = True
        for nev, varhato in [("Varga Bence", 1), ("Kiss Réka", 2), ("Horváth Anna", 3), ("Farkas Júlia", 4)]:
            if elso:
                self.belep(nev)
                elso = False
            else:
                self.valt(nev)
            gomb = self.taps(self.kartyak().first)
            expect(gomb).to_have_text(f"👏 {varhato - 1}")
            gomb.click()
            expect(gomb).to_have_text(f"👏 {varhato}")
            expect(gomb).to_have_attribute("aria-pressed", "true")
        sorok = self.sorok("taps")
        self.assertEqual(sorted(s["munkatars_id"] for s in sorok), ["u05", "u06", "u07", "u09"])

    # --- EK-26 ----------------------------------------------------------------------------------

    def test_s4_ek26_privat_koszonetre_csak_a_lathato_szemelyek_tapsolhatnak(self):
        """EK-26: Nóra 404-et kap; Szabó Katalin (Júlia vezetője) és Nagy Péter (Anna vezetője) tapsolhat."""
        kid = self.beszur("u05", "u09", lathatosag="privat")
        taps = self.cim(f"/api/koszonetek/{kid}/taps")

        self.belep("Juhász Nóra")
        self.assertEqual(self.oldal.request.post(taps).status, 404)
        self.assertEqual(self.sorok("taps"), [])

        self.valt("Szabó Katalin")
        valasz = self.oldal.request.post(taps)
        self.assertEqual((valasz.status, valasz.json()["tapsok"]), (200, 1))
        self.valt("Nagy Péter")
        valasz = self.oldal.request.post(taps)
        self.assertEqual((valasz.status, valasz.json()["tapsok"]), (200, 2))
        self.assertEqual(len(self.sorok("taps")), 2)

    # --- EK-27 ----------------------------------------------------------------------------------

    def test_s4_ek27_mobil_elrendezes_also_tab_sav_es_egyoszlopos_racs(self):
        """EK-27: 1280 px-en a menü a fejlécben, 3 oszlop; 375 px-en alsó tab-sáv, 1 oszlop, nincs vízszintes görgetés."""
        most = datetime.now()
        for ora in (3, 2, 1):
            self.beszur("u05", "u09", uzenet=f"Köszi {ora}", lathatosag="nyilvanos", letrehozva=most - timedelta(hours=ora))
        self.belep("Juhász Nóra")

        menu = self.fo_menu().bounding_box()
        self.assertLess(menu["y"], 80)
        kartyak = [self.kartyak().nth(i).bounding_box() for i in range(3)]
        self.assertTrue(all(abs(k["y"] - kartyak[0]["y"]) < 2 for k in kartyak), kartyak)
        self.assertTrue(kartyak[0]["x"] < kartyak[1]["x"] < kartyak[2]["x"])

        self.oldal.set_viewport_size({"width": 375, "height": 780})
        self.oldal.reload()
        expect(self.kartyak()).to_have_count(3)
        menu = self.fo_menu().bounding_box()
        self.assertGreater(menu["y"], 600)
        self.assertLess(abs(menu["y"] + menu["height"] - 780), 2)
        for felirat in ("Fal", "Új köszönet", "Saját"):
            link = self.fo_menu().get_by_role("link", name=felirat, exact=True)
            expect(link).to_be_visible()
            self.assertGreaterEqual(link.bounding_box()["height"], 44)
            self.assertRegex(link.inner_text(), r"\S\s+" + re.escape(felirat))  # ikon + rövid felirat
        kartyak = [self.kartyak().nth(i).bounding_box() for i in range(3)]
        self.assertTrue(all(abs(k["x"] - kartyak[0]["x"]) < 2 for k in kartyak), kartyak)
        self.assertTrue(kartyak[0]["y"] < kartyak[1]["y"] < kartyak[2]["y"])
        szelesseg = self.oldal.evaluate("() => [document.documentElement.scrollWidth, window.innerWidth]")
        self.assertLessEqual(szelesseg[0], szelesseg[1])

    # --- EK-28 ----------------------------------------------------------------------------------

    def test_s4_ek28_billentyuzetes_kezeles_es_latható_fokusz(self):
        """EK-28: Tab-bal elérhető a menü, a csengő, a Váltás, a szűrő és a taps gomb; látható fókuszkeret; Enter tapsol."""
        self.beszur("u05", "u09", lathatosag="nyilvanos")
        self.belep("Varga Bence")
        self.oldal.evaluate("() => document.activeElement.blur()")

        sorrend = []
        for _ in range(30):
            self.oldal.keyboard.press("Tab")
            elem = self.oldal.evaluate("""() => {
                const e = document.activeElement, s = getComputedStyle(e);
                const cimke = e.getAttribute('aria-label') || (e.labels && e.labels[0] && e.labels[0].innerText)
                              || e.innerText || e.tagName;
                return { nev: cimke.trim(), vonal: s.outlineStyle, szelesseg: s.outlineWidth };
            }""")
            self.assertNotEqual(elem["vonal"], "none", elem)
            self.assertEqual(elem["szelesseg"], "3px", elem)
            sorrend.append(elem["nev"])
            if elem["nev"].startswith("Taps"):
                break
        varhato = ["Kudos – kezdőlap", "Fal", "Új köszönet", "Saját", "Értesítések", "Váltás",
                   "+ Új köszönet", "Kategória", "Taps (0)"]
        self.assertEqual(sorrend, varhato)

        self.oldal.keyboard.press("Enter")
        gomb = self.taps(self.kartyak().first)
        expect(gomb).to_have_attribute("aria-pressed", "true")
        expect(gomb).to_have_text("👏 1")
        expect(gomb).to_have_attribute("aria-label", "Taps (1)")

        csengo = self.oldal.get_by_role("button", name="Értesítések")
        expect(csengo).to_have_attribute("aria-label", "Értesítések")
        for elem in (csengo, gomb):
            doboz = elem.bounding_box()
            self.assertGreaterEqual(doboz["width"], 44)
            self.assertGreaterEqual(doboz["height"], 44)


if __name__ == "__main__":
    unittest.main()
