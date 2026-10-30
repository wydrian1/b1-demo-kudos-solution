"""S2 – Küldési szabályok, böngészőben (EK-08…EK-13, EK-47).

„Kész, ha…”: Horváth Anna üres, 501 karakteres vagy kategória nélküli üzenetnél a mező alatt hibát lát,
és Farkas Júliának a 4. mai köszönetet nem tudja elküldeni. A kategória-választóban pontosan a 4 Behavioral
Anchor látszik.
"""
import re
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from playwright.sync_api import expect

sys.path.insert(0, str(Path(__file__).resolve().parent))
from alap import E2ETeszt  # noqa: E402

KERESO = "Keresés név, egység vagy e-mail alapján"
LIMIT_HIBA = "Ugyanannak a munkatársnak ma már 3 köszönetet küldtél."
HIRDETETT_KATEGORIAK = [
    ("💛 Earn customer loyalty", "az ügyfélért, az ügyfélelégedettségért tett erőfeszítés"),
    ("🚀 Take actions to move forward", "nem várt, cselekedett: elakadást oldott fel, felvette a leesett feladatot"),
    ("🤝 Deliver value together", "közös munka, együtt teremtett érték az ügyfélnek"),
    ("🧪 Experiment, learn fast!", "kipróbált valami újat, tanult a hibából, jobbá tette a folyamatot"),
]


class TestS2(E2ETeszt):
    def kategoria(self, nev):
        return self.oldal.get_by_role("radio", name=re.compile(re.escape(nev)))

    def uzenet_mezo(self):
        return self.oldal.get_by_label("Üzenet", exact=True)

    def tovabb(self):
        self.oldal.get_by_role("button", name="Tovább").click()

    def cimzett_valasztasa(self, keres, nev):
        self.oldal.get_by_role("combobox", name=KERESO).fill(keres)
        self.oldal.get_by_role("option", name=re.compile(nev)).click()
        expect(self.oldal.get_by_role("heading", name="Mit?")).to_be_visible()

    def mit_lepes(self, felhasznalo="Horváth Anna", keres="julia.f", cimzett="Farkas Júlia"):
        self.uj_koszonet(felhasznalo)
        self.cimzett_valasztasa(keres, cimzett)

    def api_kuldes(self, **mezok):
        adat = {"cimzett_id": "u09", "kategoria": "together", "uzenet": "Köszi", "lathatosag": "privat"}
        adat.update(mezok)
        return self.oldal.request.post(self.cim("/api/koszonetek"), data=adat)

    # --- EK-08 ----------------------------------------------------------------------------------

    def test_s2_ek08_onmagnak_nem_kuldhet_az_api_sem_engedi(self):
        """EK-08: Horváth Anna közvetlenül sem küldhet magának, sem nem létező címzettnek."""
        self.belep("Horváth Anna")
        onmagnak = self.api_kuldes(cimzett_id="u05")
        self.assertEqual(onmagnak.status, 400)
        self.assertEqual(onmagnak.json()["mezo"], "cimzett")
        self.assertEqual(onmagnak.json()["hiba"], "Magadnak nem küldhetsz köszönetet.")
        self.assertEqual(self.api_kuldes(cimzett_id="u99").status, 400)
        self.assertEqual(self.sorok(), [])

    # --- EK-09, EK-10, EK-11: hibák a mező alatt -------------------------------------------------

    def test_s2_ek09_ures_uzenet_hiba_a_mezo_alatt(self):
        """EK-09: üres és szóközös üzenetnél a 2. lépésen marad, a mező alatt hiba van, felugró ablak nincs."""
        parbeszedek = []
        self.oldal.on("dialog", lambda d: (parbeszedek.append(d.message), d.dismiss()))
        self.mit_lepes()
        self.kategoria("Take actions to move forward").click()

        self.tovabb()
        hiba = self.oldal.get_by_text("Az üzenet nem lehet üres.")
        expect(hiba).to_be_visible()
        expect(self.oldal.get_by_role("heading", name="Mit?")).to_be_visible()
        # a hiba a szövegmező alatt van, és a mező hibásként van jelölve
        mezo = self.uzenet_mezo().bounding_box()
        self.assertGreaterEqual(hiba.bounding_box()["y"], mezo["y"] + mezo["height"])
        expect(self.uzenet_mezo()).to_have_attribute("aria-invalid", "true")

        self.uzenet_mezo().fill("   ")
        self.tovabb()
        expect(hiba).to_be_visible()
        expect(self.oldal.get_by_role("heading", name="Mit?")).to_be_visible()

        self.uzenet_mezo().fill("Köszi!")
        expect(hiba).to_be_hidden()

        self.assertEqual(parbeszedek, [])
        valasz = self.api_kuldes(uzenet="   ")
        self.assertEqual(valasz.status, 400)
        self.assertEqual(valasz.json()["mezo"], "uzenet")
        self.assertEqual(self.sorok(), [])

    def test_s2_ek10_karakterszamlalo_500_es_501_karakter(self):
        """EK-10: 500 karakternél nincs hiba, 501-nél piros a számláló, hiba jelenik meg, nincs továbblépés."""
        self.mit_lepes()
        self.kategoria("Deliver value together").click()
        hatar = "a" * 499 + "🙏"

        self.uzenet_mezo().fill(hatar)
        expect(self.oldal.get_by_text("500 / 500")).to_be_visible()
        expect(self.oldal.get_by_text("Az üzenet legfeljebb 500 karakter lehet.")).to_be_hidden()

        self.uzenet_mezo().fill(hatar + "a")
        szamlalo = self.oldal.get_by_text("501 / 500")
        expect(szamlalo).to_be_visible()
        self.assertEqual(szamlalo.evaluate("e => getComputedStyle(e).color"), "rgb(168, 65, 47)")
        self.tovabb()
        expect(self.oldal.get_by_text("Az üzenet legfeljebb 500 karakter lehet.")).to_be_visible()
        expect(self.oldal.get_by_role("heading", name="Mit?")).to_be_visible()

        valasz = self.api_kuldes(uzenet=hatar + "a")
        self.assertEqual(valasz.status, 400)
        self.assertEqual(valasz.json()["mezo"], "uzenet")
        self.assertEqual(self.sorok(), [])

    def test_s2_ek11_kategoria_nelkul_nem_lep_tovabb(self):
        """EK-11: kategória nélkül a kategóriák alatt „Válassz kategóriát.” látszik; az API is visszautasít."""
        self.mit_lepes()
        self.uzenet_mezo().fill("Köszi a segítséget!")
        self.tovabb()
        hiba = self.oldal.get_by_text("Válassz kategóriát.")
        expect(hiba).to_be_visible()
        expect(self.oldal.get_by_role("heading", name="Mit?")).to_be_visible()
        csoport = self.oldal.get_by_role("radiogroup", name="Kategória").bounding_box()
        self.assertGreaterEqual(hiba.bounding_box()["y"], csoport["y"] + csoport["height"])

        self.kategoria("Earn customer loyalty").click()
        expect(hiba).to_be_hidden()
        self.tovabb()
        expect(self.oldal.get_by_role("heading", name="Ellenőrzés")).to_be_visible()

        hianyzo = self.oldal.request.post(self.cim("/api/koszonetek"), data={
            "cimzett_id": "u09", "uzenet": "Köszi", "lathatosag": "privat"})
        self.assertEqual((hianyzo.status, hianyzo.json()["mezo"]), (400, "kategoria"))
        ismeretlen = self.api_kuldes(kategoria="pizza")
        self.assertEqual((ismeretlen.status, ismeretlen.json()["mezo"]), (400, "kategoria"))
        self.assertEqual(self.sorok(), [])

    # --- EK-12, EK-13: napi limit -------------------------------------------------------------------

    def test_s2_ek12_a_negyedik_mai_koszonet_nem_megy_el_de_mas_cimzettnek_igen(self):
        """EK-12: Anna ma 3-at küldött Júliának; a 4. hibát ad a kártya alatt, Varga Bencének küldhet."""
        for _ in range(3):
            self.beszur("u05", "u09")
        self.mit_lepes()
        self.kategoria("Deliver value together").click()
        self.uzenet_mezo().fill("Negyedik köszönet")
        self.tovabb()
        expect(self.oldal.get_by_role("heading", name="Ellenőrzés")).to_be_visible()
        self.oldal.get_by_role("button", name="Küldés").click()

        hiba = self.oldal.get_by_text(LIMIT_HIBA)
        expect(hiba).to_be_visible()
        expect(self.oldal.get_by_role("heading", name="Ellenőrzés")).to_be_visible()
        kartya = self.oldal.get_by_role("article").bounding_box()
        self.assertGreaterEqual(hiba.bounding_box()["y"], kartya["y"] + kartya["height"])
        julianak = [s for s in self.sorok() if (s["kuldo_id"], s["cimzett_id"]) == ("u05", "u09")]
        self.assertEqual(len(julianak), 3)
        valasz = self.api_kuldes()
        self.assertEqual((valasz.status, valasz.json()["hiba"]), (400, LIMIT_HIBA))

        # a menüpontra kattintva a varázsló újraindul, és más címzettnek mehet köszönet
        self.oldal.get_by_role("navigation").get_by_role("link", name="Új köszönet").click()
        expect(self.oldal.get_by_role("heading", name="Kinek?")).to_be_visible()
        self.cimzett_valasztasa("varga", "Varga Bence")
        self.kategoria("Deliver value together").click()
        self.uzenet_mezo().fill("Köszi, Bence!")
        self.tovabb()
        self.oldal.get_by_role("button", name="Küldés").click()
        expect(self.oldal.get_by_role("status")).to_contain_text("Köszönetedet elküldtük Varga Bencének! 🎉")
        self.assertEqual(self.sorok()[-1]["cimzett_id"], "u06")
        self.assertEqual(len(self.sorok()), 4)

    def test_s2_ek13_a_tegnapi_koszonetek_nem_szamitanak_a_mai_limitbe(self):
        """EK-13: tegnap este 3 köszönet ment Júliának, ma újra küldhet neki."""
        tegnap = datetime.combine(datetime.now().date() - timedelta(days=1), datetime.min.time())
        for perc in range(3):
            self.beszur("u05", "u09", letrehozva=tegnap.replace(hour=23, minute=50 + perc))
        self.mit_lepes()
        self.kategoria("Deliver value together").click()
        self.uzenet_mezo().fill("Mai köszönet")
        self.tovabb()
        self.oldal.get_by_role("button", name="Küldés").click()
        expect(self.oldal.get_by_role("status")).to_contain_text("Köszönetedet elküldtük Farkas Júliának!")
        self.assertEqual(len(self.sorok()), 4)
        self.assertEqual(self.sorok()[-1]["letrehozva"][:10], datetime.now().date().isoformat())

    # --- EK-47 ---------------------------------------------------------------------------------------

    def test_s2_ek47_pontosan_a_negy_behavioral_anchor_latszik(self):
        """EK-47: 4 kategória-kártyagomb a megadott sorrendben, leírással; a régi kategóriák nincsenek ott."""
        self.mit_lepes()
        gombok = self.oldal.get_by_role("radiogroup", name="Kategória").get_by_role("radio")
        expect(gombok).to_have_count(4)
        szovegek = gombok.all_inner_texts()
        for szoveg, (nev, leiras) in zip(szovegek, HIRDETETT_KATEGORIAK):
            self.assertIn(nev, szoveg)
            self.assertIn(leiras, szoveg)
        for regi in ("Együttműködés", "Gyors segítség", "Jó ötlet", "Ügyfélfókusz", "Kiemelkedő munka"):
            expect(self.oldal.get_by_text(regi)).to_have_count(0)

        kategoria = self.api_kuldes(kategoria="experiment")
        self.assertEqual(kategoria.status, 201)
        for regi in ("egyuttmukodes", "kiemelkedo"):
            valasz = self.api_kuldes(kategoria=regi)
            self.assertEqual((valasz.status, valasz.json()["mezo"]), (400, "kategoria"))


if __name__ == "__main__":
    unittest.main()
