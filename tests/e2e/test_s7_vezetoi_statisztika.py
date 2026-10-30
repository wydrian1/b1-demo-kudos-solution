"""S7 – Vezetői statisztika, böngészőben (EK-42…EK-46).

„Kész, ha…”: Szabó Katalin a Csapat nézet tetején látja a 4 mutatót, a kategória-sávdiagramot és a Top 3-at, és az
időszak váltásával a számok változnak.

Adatkészlet (privát): K1 Anna→Farkas Júlia 🤝 (1 napja) · K2 Júlia→Balogh Máté 🧪 (2) · K3 Papp Zsófia→Júlia 🤝 (3) ·
K4 Takács Levente→Balogh Máté 🤝 (5) · K5 Nagy Péter→Szabó Katalin 🚀 (10) · K6 Anna→Varga Bence 💛 (1) ·
K7 Júlia→Papp Zsófia 🧪 (40).
"""
import re
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from playwright.sync_api import expect

sys.path.insert(0, str(Path(__file__).resolve().parent))
from alap import E2ETeszt  # noqa: E402

# --cat-ugyfel, --cat-segitseg, --cat-egyuttmukodes, --cat-otlet
SZINEK = {"Earn customer loyalty": "rgb(255, 139, 107)", "Take actions to move forward": "rgb(81, 194, 242)",
          "Deliver value together": "rgb(103, 208, 171)", "Experiment, learn fast!": "rgb(157, 136, 217)"}
KATEGORIA_SORREND = ["Earn customer loyalty", "Take actions to move forward", "Deliver value together",
                     "Experiment, learn fast!"]


class TestS7(E2ETeszt):
    def adatok(self):
        most = datetime.now()
        for kuldo, cimzett, kategoria, nap in [
            ("u05", "u09", "together", 1), ("u09", "u10", "experiment", 2), ("u11", "u09", "together", 3),
            ("u12", "u10", "together", 5), ("u02", "u03", "forward", 10), ("u05", "u06", "loyalty", 1),
            ("u09", "u11", "experiment", 40),
        ]:
            self.beszur(kuldo, cimzett, kategoria, "Köszi", "privat", most - timedelta(days=nap))

    def csapat(self, nev, elso=False):
        if elso:
            self.belep(nev)
        else:
            self.valt(nev)
        self.oldal.get_by_role("navigation", name="Főmenü").get_by_role("link", name="Csapat", exact=True).click()
        expect(self.oldal.get_by_role("heading", name="Csapatköszönetek")).to_be_visible()

    def mutato(self, cimke):
        return self.oldal.get_by_role("group", name=cimke, exact=True)

    def varhato_mutatok(self, kapott, kuldott, aktiv, osszes):
        expect(self.mutato("Kapott köszönet")).to_have_text(f"{kapott} kapott köszönet")
        expect(self.mutato("Küldött köszönet")).to_have_text(f"{kuldott} küldött köszönet")
        expect(self.mutato("Aktív küldő")).to_have_text(f"{aktiv} aktív küldő")
        expect(self.mutato("Összes köszönet")).to_have_text(f"{osszes} összes köszönet")

    def savok(self):
        return self.oldal.get_by_role("list", name="Köszönetek kategóriák szerint").get_by_role("listitem")

    def top3(self):
        return self.oldal.get_by_role("list", name="Legtöbb köszönetet kapott").get_by_role("listitem")

    def idoszak(self, felirat):
        self.oldal.get_by_label("Időszak", exact=True).select_option(label=felirat)

    # --- EK-42 ------------------------------------------------------------------------------------

    def test_s7_ek42_a_negy_mutato_az_alapertelmezett_30_napra(self):
        """EK-42: 5 kapott, 3 küldött, 3 aktív küldő, 5 összes köszönet."""
        self.adatok()
        self.csapat("Szabó Katalin", elso=True)
        expect(self.oldal.get_by_label("Időszak", exact=True)).to_have_value("30")
        self.varhato_mutatok(5, 3, 3, 5)
        # a mutatók a statisztika tetején, a szűrők és a kártyalista felett vannak
        mutato = self.mutato("Kapott köszönet").bounding_box()
        szuro = self.oldal.get_by_label("Keresés a köszönetekben").bounding_box()
        self.assertLess(mutato["y"], szuro["y"])
        expect(self.oldal.get_by_role("article")).to_have_count(5)

    # --- EK-43 ------------------------------------------------------------------------------------

    def test_s7_ek43_kategoria_megoszlas_savdiagram(self):
        """EK-43: 4 sáv a megadott sorrendben: 💛 0, 🚀 1, 🤝 3, 🧪 1; saját színnel, a leghosszabb a 🤝."""
        self.adatok()
        self.csapat("Szabó Katalin", elso=True)
        expect(self.savok()).to_have_count(4)
        szelessegek = {}
        for i, (nev, darab) in enumerate(zip(KATEGORIA_SORREND, (0, 1, 3, 1))):
            sav = self.savok().nth(i)
            expect(sav).to_contain_text(nev)
            expect(sav.get_by_text(str(darab), exact=True)).to_be_visible()  # a sáv végén a darabszám
            kitoltes = sav.locator(".sav-kitoltes")
            self.assertEqual(kitoltes.evaluate("e => getComputedStyle(e).backgroundColor"), SZINEK[nev])
            szelessegek[nev] = kitoltes.evaluate("e => e.getBoundingClientRect().width")
        self.assertEqual(szelessegek["Earn customer loyalty"], 0)
        self.assertEqual(max(szelessegek, key=szelessegek.get), "Deliver value together")
        self.assertAlmostEqual(szelessegek["Take actions to move forward"], szelessegek["Experiment, learn fast!"], delta=1)
        self.assertAlmostEqual(szelessegek["Deliver value together"] / 3, szelessegek["Take actions to move forward"], delta=2)

    # --- EK-44 ------------------------------------------------------------------------------------

    def test_s7_ek44_top3_holtversenyben_abecerendben(self):
        """EK-44: 30 napra Balogh Máté, Farkas Júlia, Szabó Katalin; Összesre a harmadik Papp Zsófia."""
        self.adatok()
        self.csapat("Szabó Katalin", elso=True)
        expect(self.top3()).to_have_count(3)
        for i, (jelzes, nev, darab) in enumerate([("🥇", "Balogh Máté", 2), ("🥈", "Farkas Júlia", 2),
                                                  ("🥉", "Szabó Katalin", 1)]):
            expect(self.top3().nth(i)).to_contain_text(jelzes)
            expect(self.top3().nth(i)).to_contain_text(nev)
            expect(self.top3().nth(i)).to_contain_text(f"{darab} köszönet")

        self.idoszak("Összes")
        expect(self.top3().nth(2)).to_contain_text("Papp Zsófia")
        expect(self.top3().nth(2)).not_to_contain_text("Szabó Katalin")
        expect(self.top3().nth(0)).to_contain_text("Balogh Máté")
        expect(self.top3().nth(1)).to_contain_text("Farkas Júlia")

    # --- EK-45 ------------------------------------------------------------------------------------

    def test_s7_ek45_az_idoszak_valtasa_megvaltoztatja_a_szamokat_es_a_listat(self):
        """EK-45: 7 nap → 4/3/3/4; Összes → 6/4/3/6, a 🧪 értéke 2; a kártyalista is követi."""
        self.adatok()
        self.csapat("Szabó Katalin", elso=True)
        self.varhato_mutatok(5, 3, 3, 5)

        self.idoszak("Elmúlt 7 nap")
        self.varhato_mutatok(4, 3, 3, 4)
        expect(self.oldal.get_by_role("article")).to_have_count(4)

        self.idoszak("Összes")
        self.varhato_mutatok(6, 4, 3, 6)
        expect(self.savok().nth(3)).to_contain_text("Experiment, learn fast!")
        expect(self.savok().nth(3).get_by_text("2", exact=True)).to_be_visible()
        expect(self.oldal.get_by_role("article")).to_have_count(6)

    def test_s7_ek45_a_keresoszo_es_a_kategoria_nem_valtoztatja_a_statisztikat(self):
        """EK-45: a kereső és a kategóriaszűrő csak a listára hat."""
        self.adatok()
        self.csapat("Szabó Katalin", elso=True)
        self.oldal.get_by_label("Keresés a köszönetekben").fill("júlia")
        expect(self.oldal.get_by_role("article")).to_have_count(3)
        self.varhato_mutatok(5, 3, 3, 5)
        self.oldal.get_by_label("Kategória", exact=True).select_option(label="🚀 Take actions to move forward")
        expect(self.oldal.get_by_role("article")).to_have_count(0)
        self.varhato_mutatok(5, 3, 3, 5)

    # --- EK-46 ------------------------------------------------------------------------------------

    def test_s7_ek46_mas_kor_adata_nem_szivarog_be(self):
        """EK-46: Tóth Gábor „Összes” statisztikája csupa 0, a Top 3 üres; Katalin a saját értékeit kapja."""
        self.adatok()
        self.csapat("Tóth Gábor", elso=True)
        self.idoszak("Összes")
        self.varhato_mutatok(0, 0, 0, 0)
        for i in range(4):
            expect(self.savok().nth(i).get_by_text("0", exact=True)).to_be_visible()
            self.assertEqual(self.savok().nth(i).locator(".sav-kitoltes").evaluate("e => e.getBoundingClientRect().width"), 0)
        expect(self.top3()).to_have_count(0)
        expect(self.oldal.get_by_text("még senki nem kapott köszönetet")).to_be_visible()

        self.csapat("Szabó Katalin")
        self.idoszak("Összes")
        self.varhato_mutatok(6, 4, 3, 6)
        valasz = self.oldal.request.get(self.cim("/api/csapat/statisztika?idoszak=osszes&vezeto_id=u01"))
        self.assertEqual(valasz.status, 200)
        adat = valasz.json()
        self.assertEqual((adat["kapott"], adat["kuldott"], adat["aktiv_kuldok"], adat["osszes"]), (6, 4, 3, 6))
        self.assertEqual({k["kategoria"]: k["darab"] for k in adat["kategoriak"]}["loyalty"], 0)  # a K6 nem számít

    def test_s7_ek46_reszponziv_2x2_mutatok_mobilon(self):
        """EK-46 (NF-02): 375 px-en a 4 mutató-kártya 2×2 rácsban áll, nincs vízszintes görgetés."""
        self.adatok()
        self.csapat("Szabó Katalin", elso=True)
        sor = [self.mutato(c).bounding_box() for c in ("Kapott köszönet", "Küldött köszönet", "Aktív küldő", "Összes köszönet")]
        self.assertTrue(all(abs(d["y"] - sor[0]["y"]) < 2 for d in sor), sor)  # asztali nézeten egy sorban

        self.oldal.set_viewport_size({"width": 375, "height": 780})
        self.oldal.reload()
        expect(self.mutato("Kapott köszönet")).to_be_visible()
        d = [self.mutato(c).bounding_box() for c in ("Kapott köszönet", "Küldött köszönet", "Aktív küldő", "Összes köszönet")]
        self.assertAlmostEqual(d[0]["y"], d[1]["y"], delta=2)
        self.assertAlmostEqual(d[2]["y"], d[3]["y"], delta=2)
        self.assertGreater(d[2]["y"], d[0]["y"] + d[0]["height"] - 2)
        self.assertAlmostEqual(d[0]["x"], d[2]["x"], delta=2)
        szelesseg = self.oldal.evaluate("() => [document.documentElement.scrollWidth, window.innerWidth]")
        self.assertLessEqual(szelesseg[0], szelesseg[1])


if __name__ == "__main__":
    unittest.main()
