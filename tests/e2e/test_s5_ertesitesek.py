"""S5 – Értesítések, böngészőben (EK-29…EK-35).

„Kész, ha…”: Anna köszönete után Farkas Júlia, Szabó Katalin és Kovács Eszter csengőjén „1” látszik, Fehér
Lászlónál nem. Júlia megnyitja, és a számláló eltűnik.
"""
import re
import sys
import unittest
from datetime import datetime
from pathlib import Path

from playwright.sync_api import expect

sys.path.insert(0, str(Path(__file__).resolve().parent))
from alap import E2ETeszt  # noqa: E402

KERESO = "Keresés név, egység vagy e-mail alapján"
SARGA_HALVANY = "rgb(255, 240, 166)"  # --yellow-soft


class TestS5(E2ETeszt):
    def csengo(self):
        return self.oldal.get_by_role("button", name=re.compile(r"^Értesítések"))

    def panel(self):
        return self.oldal.get_by_role("region", name="Értesítések")

    def elemek(self):
        return self.panel().get_by_role("listitem")

    def varhato_szamlalo(self, darab):
        """A csengőn a megadott olvasatlan-szám látszik (0 = nincs buborék, a felirat egyszerű)."""
        if darab:
            expect(self.csengo()).to_have_attribute("aria-label", f"Értesítések, {darab} olvasatlan")
            expect(self.csengo().get_by_text(str(darab), exact=True)).to_be_visible()
        else:
            expect(self.csengo()).to_have_attribute("aria-label", "Értesítések")
            expect(self.csengo().get_by_text(re.compile(r"^\d+$"))).to_be_hidden()

    def koszonet_api(self, cimzett_id, uzenet, kategoria="together"):
        valasz = self.oldal.request.post(self.cim("/api/koszonetek"), data={
            "cimzett_id": cimzett_id, "kategoria": kategoria, "uzenet": uzenet, "lathatosag": "privat"})
        self.assertEqual(valasz.status, 201)

    # --- EK-29 és a „Kész, ha…” ----------------------------------------------------------------

    def test_s5_ek29_anna_koszonete_utan_julia_katalin_es_eszter_ertesitest_kap_laszlo_nem(self):
        """EK-29: Anna a varázslóval küld Júliának; Júlia, Katalin, Eszter csengőjén „1”, másokén nincs."""
        self.uj_koszonet("Horváth Anna")
        self.oldal.get_by_role("combobox", name=KERESO).fill("julia.f")
        self.oldal.get_by_role("option", name=re.compile("Farkas Júlia")).click()
        self.oldal.get_by_role("radio", name=re.compile("Deliver value together")).click()
        self.oldal.get_by_label("Üzenet", exact=True).fill("Köszönöm a gyors adatelemzést! 🙏🎉")
        self.oldal.get_by_role("button", name="Tovább").click()
        self.oldal.get_by_role("button", name="Küldés").click()
        expect(self.oldal.get_by_role("heading", name="Saját köszönetek")).to_be_visible()
        self.varhato_szamlalo(0)  # a küldő nem kap értesítést

        for nev, darab in [("Farkas Júlia", 1), ("Szabó Katalin", 1), ("Kovács Eszter", 1),
                           ("Fehér László", 0), ("Nagy Péter", 0)]:
            with self.subTest(nev=nev):
                self.valt(nev)
                self.varhato_szamlalo(darab)

        # Júlia megnyitja az értesítést, és a számláló eltűnik
        self.valt("Farkas Júlia")
        self.csengo().click()
        expect(self.elemek()).to_have_count(1)
        expect(self.elemek().first).to_contain_text("Horváth Anna → Farkas Júlia")
        self.elemek().first.get_by_role("button").click()
        self.varhato_szamlalo(0)

    # --- EK-34 ------------------------------------------------------------------------------------

    def test_s5_ek34_csengo_szamlalo_es_az_ertesites_tartalma(self):
        """EK-34: Júlián a „2” számláló; a panelen 2 olvasatlan (halványsárga) elem, a legújabb elöl; Nóránál üres."""
        elotag = "Köszönöm a gyors adatelemzést! 🙏 "
        hosszu = elotag + "x" * (120 - len(elotag))
        self.belep("Horváth Anna")
        self.koszonet_api("u09", hosszu)
        self.valt("Varga Bence")
        self.koszonet_api("u09", "Rövid köszönet")
        self.valt("Farkas Júlia")

        self.varhato_szamlalo(2)
        expect(self.csengo()).to_have_attribute("aria-label", "Értesítések, 2 olvasatlan")
        self.csengo().click()
        expect(self.elemek()).to_have_count(2)
        for i in range(2):
            self.assertEqual(self.elemek().nth(i).evaluate("e => getComputedStyle(e).backgroundColor"), SARGA_HALVANY)
            expect(self.elemek().nth(i)).to_contain_text("Olvasatlan")

        expect(self.elemek().first).to_contain_text("Varga Bence → Farkas Júlia")
        expect(self.elemek().first).to_contain_text("Rövid köszönet")
        anna = self.elemek().nth(1)
        expect(anna).to_contain_text("Horváth Anna → Farkas Júlia")
        expect(anna).to_contain_text("🤝 Deliver value together")
        expect(anna).to_contain_text(hosszu[:80] + "…")
        expect(anna).not_to_contain_text("x" * 81)
        kuldve = datetime.fromisoformat(self.sorok()[0]["letrehozva"])
        szoveg = anna.inner_text()
        self.assertIn(str(kuldve.year), szoveg)
        self.assertIn(f"{kuldve.minute:02d}:{kuldve.second:02d}", szoveg)

        self.valt("Juhász Nóra")
        self.varhato_szamlalo(0)
        self.assertEqual(self.oldal.request.get(self.cim("/api/ertesitesek")).json(), [])
        self.csengo().click()
        expect(self.panel().get_by_text("Nincs új értesítés.")).to_be_visible()

    # --- EK-35 ------------------------------------------------------------------------------------

    def test_s5_ek35_megnyitas_es_mind_olvasott(self):
        """EK-35: egy értesítés megnyitása után „1”, a [Mind olvasott] után nincs számláló; Katalinnál továbbra is „2”."""
        self.belep("Horváth Anna")
        self.koszonet_api("u09", "Anna köszönete")
        self.valt("Varga Bence")
        self.koszonet_api("u09", "Bence köszönete")
        self.valt("Farkas Júlia")
        self.varhato_szamlalo(2)

        self.csengo().click()
        self.elemek().first.get_by_role("button").click()
        self.varhato_szamlalo(1)
        expect(self.elemek().first).not_to_contain_text("Olvasatlan")
        self.assertNotEqual(self.elemek().first.evaluate("e => getComputedStyle(e).backgroundColor"), SARGA_HALVANY)
        self.assertEqual(self.elemek().nth(1).evaluate("e => getComputedStyle(e).backgroundColor"), SARGA_HALVANY)

        self.panel().get_by_role("button", name="Mind olvasott").click()
        self.varhato_szamlalo(0)
        for i in range(2):
            self.assertNotEqual(self.elemek().nth(i).evaluate("e => getComputedStyle(e).backgroundColor"), SARGA_HALVANY)

        # idegen értesítést nem lehet olvasottra állítani, Katalin értesítései érintetlenek
        julia_ertesitese = self.sorok("ertesites")[0]
        self.assertEqual(julia_ertesitese["munkatars_id"], "u09")
        self.valt("Juhász Nóra")
        valasz = self.oldal.request.post(self.cim(f"/api/ertesitesek/{julia_ertesitese['id']}/olvasott"))
        self.assertEqual(valasz.status, 404)
        self.valt("Szabó Katalin")
        self.varhato_szamlalo(2)

    def test_s5_ek35_billentyuzettel_is_megnyithato_az_ertesites(self):
        """EK-35: az értesítés Tab-bal elérhető, Enterrel olvasottá válik."""
        self.belep("Horváth Anna")
        self.koszonet_api("u09", "Köszönet billentyűzethez")
        self.valt("Farkas Júlia")
        self.varhato_szamlalo(1)
        self.csengo().focus()
        self.oldal.keyboard.press("Enter")
        expect(self.elemek()).to_have_count(1)
        self.oldal.keyboard.press("Tab")  # [Mind olvasott]
        self.oldal.keyboard.press("Tab")  # az értesítés
        self.oldal.keyboard.press("Enter")
        self.varhato_szamlalo(0)


if __name__ == "__main__":
    unittest.main()
