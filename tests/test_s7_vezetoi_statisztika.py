"""S7 – Vezetői statisztika (EK-42…EK-46): a számítás és az API, böngésző nélkül.

Adatkészlet (privát; Szabó Katalin köre: u03, u09, u10, u11, u12):
K1 Anna→Farkas Júlia 🤝 (1 napja) · K2 Júlia→Balogh Máté 🧪 (2) · K3 Papp Zsófia→Júlia 🤝 (3) ·
K4 Takács Levente→Balogh Máté 🤝 (5) · K5 Nagy Péter→Szabó Katalin 🚀 (10) · K6 Anna→Varga Bence 💛 (1) ·
K7 Júlia→Papp Zsófia 🧪 (40).
"""
import sys
import unittest
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from segedek import SzerverTeszt  # noqa: E402

KATEGORIAK = ["loyalty", "forward", "together", "experiment"]


class StatisztikaTeszt(SzerverTeszt):
    def setUp(self):
        super().setUp()
        most = datetime.now()
        for kuldo, cimzett, kategoria, nap in [
            ("u05", "u09", "together", 1), ("u09", "u10", "experiment", 2), ("u11", "u09", "together", 3),
            ("u12", "u10", "together", 5), ("u02", "u03", "forward", 10), ("u05", "u06", "loyalty", 1),
            ("u09", "u11", "experiment", 40),
        ]:
            self.beszur(kuldo, cimzett, kategoria, "Köszi", "privat", most - timedelta(days=nap))

    def statisztika(self, munkatars, **parameter):
        lekerdezes = urllib.parse.urlencode(parameter)
        allapot, tartalom = self.belep(munkatars).get(
            "/api/csapat/statisztika" + ("?" + lekerdezes if lekerdezes else ""))
        self.assertEqual(allapot, 200)
        return tartalom

    def mutatok(self, statisztika):
        return (statisztika["kapott"], statisztika["kuldott"], statisztika["aktiv_kuldok"], statisztika["osszes"])

    def megoszlas(self, statisztika):
        return {k["kategoria"]: k["darab"] for k in statisztika["kategoriak"]}

    def top3(self, statisztika):
        return [(t["nev"], t["darab"]) for t in statisztika["top3"]]


class TestEK42Mutatok(StatisztikaTeszt):
    def test_ek42_mutatok_az_alapertelmezett_30_napra(self):
        """EK-42 (SZ-14): 5 kapott (K1–K5), 3 küldött (K2, K3, K4), 3 aktív küldő, 5 összes."""
        statisztika = self.statisztika("u03")
        self.assertEqual(self.mutatok(statisztika), (5, 3, 3, 5))

    def test_ek42_az_alapertelmezes_a_30_nap(self):
        """EK-42 (SZ-14): paraméter nélkül ugyanaz, mint `idoszak=30`."""
        self.assertEqual(self.statisztika("u03"), self.statisztika("u03", idoszak="30"))

    def test_ek42_az_aktiv_kuldok_kulonbozo_szemelyek(self):
        """EK-42 (SZ-14): Farkas Júlia két köszönetet küldött (K2 és K7), de egy aktív küldőnek számít."""
        statisztika = self.statisztika("u03", idoszak="osszes")
        self.assertEqual(statisztika["kuldott"], 4)
        self.assertEqual(statisztika["aktiv_kuldok"], 3)


class TestEK43Kategoriak(StatisztikaTeszt):
    def test_ek43_a_megoszlas_a_negy_kategoria_rogzitett_sorrendjeben(self):
        """EK-43 (SZ-14): 💛 0 · 🚀 1 · 🤝 3 · 🧪 1; a K6 (💛, más kör) nem számít bele."""
        statisztika = self.statisztika("u03")
        self.assertEqual([k["kategoria"] for k in statisztika["kategoriak"]], KATEGORIAK)
        self.assertEqual(self.megoszlas(statisztika), {"loyalty": 0, "forward": 1, "together": 3, "experiment": 1})


class TestEK44Top3(StatisztikaTeszt):
    def test_ek44_top3_30_napra_holtversenyben_abecerendben(self):
        """EK-44 (SZ-14): Balogh Máté (2), Farkas Júlia (2), Szabó Katalin (1)."""
        self.assertEqual(self.top3(self.statisztika("u03")),
                         [("Balogh Máté", 2), ("Farkas Júlia", 2), ("Szabó Katalin", 1)])

    def test_ek44_top3_az_osszes_idoszakra_a_harmadik_helyen_papp_zsofia(self):
        """EK-44 (SZ-14): Papp Zsófia és Szabó Katalin holtversenyben (1–1), ábécérendben Papp Zsófia jön."""
        self.assertEqual(self.top3(self.statisztika("u03", idoszak="osszes")),
                         [("Balogh Máté", 2), ("Farkas Júlia", 2), ("Papp Zsófia", 1)])

    def test_ek44_a_top3_elemei_a_korbol_valok_es_legalabb_egy_koszonetet_kaptak(self):
        """EK-44 (SZ-14): Varga Bence (K6 címzettje) nincs a körben, ezért nincs a listán; legfeljebb 3 elem."""
        statisztika = self.statisztika("u03", idoszak="osszes")
        self.assertLessEqual(len(statisztika["top3"]), 3)
        self.assertNotIn("Varga Bence", [t["nev"] for t in statisztika["top3"]])
        self.assertEqual(statisztika["top3"][0]["id"], "u10")
        self.assertEqual(set(statisztika["top3"][0]), {"id", "nev", "egyseg", "darab"})


class TestEK45Idoszakvaltas(StatisztikaTeszt):
    def test_ek45_7_napra(self):
        """EK-45 (SZ-14, SZ-15): 4 kapott (K1–K4), 3 küldött, 3 aktív küldő, 4 összes."""
        self.assertEqual(self.mutatok(self.statisztika("u03", idoszak="7")), (4, 3, 3, 4))

    def test_ek45_osszes_idoszakra(self):
        """EK-45 (SZ-14, SZ-15): 6 kapott, 4 küldött, 3 aktív küldő, 6 összes; a 🧪 értéke 2."""
        statisztika = self.statisztika("u03", idoszak="osszes")
        self.assertEqual(self.mutatok(statisztika), (6, 4, 3, 6))
        self.assertEqual(self.megoszlas(statisztika)["experiment"], 2)

    def test_ek45_ismeretlen_idoszak_400(self):
        """EK-45 (SZ-15)."""
        allapot, tartalom = self.belep("u03").get("/api/csapat/statisztika?idoszak=5")
        self.assertEqual((allapot, tartalom["mezo"]), (400, "idoszak"))

    def test_ek45_a_keresoszo_es_a_kategoria_nem_hat_a_statisztikara(self):
        """EK-45 (SZ-15, 5.5. pont): az időszak a statisztikára is hat, a szöveg- és kategóriaszűrő csak a listára."""
        self.assertEqual(self.statisztika("u03", q="nincsilyen", kategoria="forward"), self.statisztika("u03"))


class TestEK46NemSzivarogMasKorAdata(StatisztikaTeszt):
    def test_ek46_mas_kor_vezetoje_csupa_nullat_kap(self):
        """EK-46 (SZ-14, SZ-13): Tóth Gábor (Üzemeltetési Osztály) körében nincs köszönet."""
        statisztika = self.statisztika("u04", idoszak="osszes")
        self.assertEqual(self.mutatok(statisztika), (0, 0, 0, 0))
        self.assertEqual(self.megoszlas(statisztika), {k: 0 for k in KATEGORIAK})
        self.assertEqual(statisztika["top3"], [])

    def test_ek46_extra_parameterek_nem_valtoztatjak_a_kort(self):
        """EK-46 (SZ-13): Szabó Katalin `vezeto_id=u01` paraméterrel is a saját „Összes” értékeit kapja (K6 nélkül)."""
        sajat = self.statisztika("u03", idoszak="osszes")
        self.assertEqual(self.mutatok(sajat), (6, 4, 3, 6))
        for extra in ({"vezeto_id": "u01"}, {"egyseg": "Fejlesztési Osztály"}, {"kor": "u00"}):
            with self.subTest(extra=extra):
                self.assertEqual(self.statisztika("u03", idoszak="osszes", **extra), sajat)

    def test_ek46_a_fobb_vezetok_nagyobb_korbol_szamolnak(self):
        """EK-46 (SZ-13): Kovács Eszter köre az egész főosztály, ott a K6 is benne van (💛 1)."""
        statisztika = self.statisztika("u01", idoszak="osszes")
        self.assertEqual(self.mutatok(statisztika), (7, 7, 5, 7))
        self.assertEqual(self.megoszlas(statisztika)["loyalty"], 1)

    def test_ek46_nem_vezeto_403_belepes_nelkul_401(self):
        """EK-46 (SZ-13, SZ-01)."""
        self.assertEqual(self.belep("u05").get("/api/csapat/statisztika")[0], 403)
        self.assertEqual(self.kliens().get("/api/csapat/statisztika")[0], 401)

    def test_ek46_a_mutatok_egyeznek_a_lista_tartalmaval(self):
        """EK-46 (SZ-14, SZ-13): az „összes” mutató mindig a Csapat lista elemeinek száma (minden vezető, minden időszak)."""
        for vezeto in ("u00", "u01", "u02", "u03", "u04"):
            kliens = self.belep(vezeto)
            for idoszak in ("7", "30", "osszes"):
                with self.subTest(vezeto=vezeto, idoszak=idoszak):
                    lista = kliens.get(f"/api/csapat?idoszak={idoszak}")[1]
                    statisztika = kliens.get(f"/api/csapat/statisztika?idoszak={idoszak}")[1]
                    self.assertEqual(statisztika["osszes"], len(lista))
                    self.assertEqual(sum(self.megoszlas(statisztika).values()), len(lista))


if __name__ == "__main__":
    unittest.main()
