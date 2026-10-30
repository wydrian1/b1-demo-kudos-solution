"""S2 – Küldési szabályok (EK-08…EK-13, EK-47): az üzleti logika és a HTTP API, böngésző nélkül."""
import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from segedek import ADATOK, SzerverTeszt  # noqa: E402

LIMIT_HIBA = "Ugyanannak a munkatársnak ma már 3 köszönetet küldtél."


class TestKuldesiSzabalyok(SzerverTeszt):
    @staticmethod
    def adat(**felulir):
        alap = {"cimzett_id": "u09", "kategoria": "together", "uzenet": "Köszönöm!", "lathatosag": "privat"}
        alap.update(felulir)
        return alap

    def hibas(self, kliens, bemenet, mezo, uzenet=None):
        allapot, tartalom = kliens.post("/api/koszonetek", bemenet)
        self.assertEqual(allapot, 400, bemenet)
        self.assertEqual(tartalom["mezo"], mezo)
        if uzenet is not None:
            self.assertEqual(tartalom["hiba"], uzenet)

    def test_ek08_onmagnak_es_nem_letezo_cimzettnek_nem_kuldhet(self):
        """EK-08 (SZ-04): u05 → u05 és u05 → u99 egyaránt 400, `mezo` = cimzett, nincs mentés."""
        anna = self.belep("u05")
        self.hibas(anna, self.adat(cimzett_id="u05"), "cimzett", "Magadnak nem küldhetsz köszönetet.")
        self.hibas(anna, self.adat(cimzett_id="u99"), "cimzett")
        self.assertEqual(self.sorok(), [])

    def test_ek08_a_szolgaltatas_is_visszautasitja_az_onmagnak_kuldest(self):
        """EK-08 (SZ-04): nem csak a webes réteg ellenőriz."""
        from kudos import adatbazis, koszonetek
        from kudos.szervezet import Szervezet

        kapcsolat = adatbazis.kapcsolat(self.adatbazis)
        try:
            with self.assertRaises(koszonetek.ValidaciosHiba) as kivetel:
                koszonetek.kuldes(kapcsolat, Szervezet.betolt(ADATOK), "u05", "u05", "together", "Köszi")
        finally:
            kapcsolat.close()
        self.assertEqual(kivetel.exception.mezo, "cimzett")
        self.assertEqual(self.sorok(), [])

    def test_ek09_ures_es_csak_szokozbol_allo_uzenet_nem_kuldheto(self):
        """EK-09 (SZ-05): "", "   ", sortörés/tab, hiányzó és nem szöveges üzenet → 400, `mezo` = uzenet."""
        anna = self.belep("u05")
        for uzenet in ("", "   ", "\n\t ", None, 123):
            with self.subTest(uzenet=uzenet):
                self.hibas(anna, self.adat(uzenet=uzenet), "uzenet", "Az üzenet nem lehet üres." if isinstance(uzenet, (str, type(None))) else None)
        bemenet = self.adat()
        del bemenet["uzenet"]
        self.hibas(anna, bemenet, "uzenet")
        self.assertEqual(self.sorok(), [])

    def test_ek10_500_karakter_elfogadott_501_nem(self):
        """EK-10 (SZ-05): 499 „a” + 🙏 = 500 karakter még jó (az emoji 1 karakter), 501 már nem."""
        anna = self.belep("u05")
        hatar = "a" * 499 + "🙏"
        self.assertEqual(anna.post("/api/koszonetek", self.adat(uzenet=hatar))[0], 201)
        self.hibas(anna, self.adat(uzenet=hatar + "a"), "uzenet", "Az üzenet legfeljebb 500 karakter lehet.")
        self.assertEqual(len(self.sorok()), 1)
        self.assertEqual(self.sorok()[0]["uzenet"], hatar)

    def test_ek10_a_hosszt_a_levagott_szoveg_alapjan_szamoljuk(self):
        """EK-10 (SZ-05): a szélén lévő szóközök nem számítanak bele az 500-ba."""
        anna = self.belep("u05")
        self.assertEqual(anna.post("/api/koszonetek", self.adat(uzenet="  " + "a" * 500 + "   "))[0], 201)
        self.assertEqual(self.sorok()[0]["uzenet"], "a" * 500)

    def test_ek11_kategoria_nelkul_es_ismeretlen_kategoriaval_nem_kuldheto(self):
        """EK-11 (SZ-06): hiányzó, üres, null és `pizza` kategória → 400, `mezo` = kategoria."""
        anna = self.belep("u05")
        bemenet = self.adat()
        del bemenet["kategoria"]
        self.hibas(anna, bemenet, "kategoria", "Válassz kategóriát.")
        self.hibas(anna, self.adat(kategoria=None), "kategoria", "Válassz kategóriát.")
        self.hibas(anna, self.adat(kategoria=""), "kategoria", "Válassz kategóriát.")
        self.hibas(anna, self.adat(kategoria="pizza"), "kategoria")
        self.assertEqual(self.sorok(), [])

    def test_ek12_a_negyedik_aznapi_koszonet_nem_kuldheto_ugyanannak(self):
        """EK-12 (SZ-07): Anna → Júlia 3×, a 4. 400, de Varga Bencének továbbra is küldhet."""
        anna = self.belep("u05")
        for _ in range(3):
            self.assertEqual(anna.post("/api/koszonetek", self.adat())[0], 201)
        self.hibas(anna, self.adat(), "cimzett", LIMIT_HIBA)
        julianak = [s for s in self.sorok() if (s["kuldo_id"], s["cimzett_id"]) == ("u05", "u09")]
        self.assertEqual(len(julianak), 3)
        self.assertEqual(anna.post("/api/koszonetek", self.adat(cimzett_id="u06"))[0], 201)


class TestNaptariNap(SzerverTeszt):
    def kuldes(self, kuldo, cimzett, most):
        from kudos import adatbazis, koszonetek
        from kudos.szervezet import Szervezet

        kapcsolat = adatbazis.kapcsolat(self.adatbazis)
        try:
            return koszonetek.kuldes(kapcsolat, Szervezet.betolt(ADATOK), kuldo, cimzett,
                                     "together", "Köszi", most=most)
        finally:
            kapcsolat.close()

    def test_ek13_a_napi_limit_naptari_napra_vonatkozik(self):
        """EK-13 (SZ-07): tegnap 23:50-kor 3 köszönet, ma 00:10-től újra 3 mehet, a 4. nem; más küldő nem számít."""
        from kudos.koszonetek import ValidaciosHiba

        tegnap = datetime(2026, 10, 29, 23, 50)
        for perc in range(3):
            self.kuldes("u05", "u09", tegnap.replace(minute=50 + perc))
        # Varga Bence ma szintén 3-at küldött Júliának: ez Anna limitjébe nem számít bele.
        for perc in range(3):
            self.kuldes("u06", "u09", datetime(2026, 10, 30, 0, 5 + perc))

        for perc in range(3):
            self.kuldes("u05", "u09", datetime(2026, 10, 30, 0, 10 + perc))
        with self.assertRaises(ValidaciosHiba) as kivetel:
            self.kuldes("u05", "u09", datetime(2026, 10, 30, 0, 13))
        self.assertEqual(kivetel.exception.uzenet, LIMIT_HIBA)
        self.assertEqual(kivetel.exception.mezo, "cimzett")

        anna_juliának = [s for s in self.sorok() if (s["kuldo_id"], s["cimzett_id"]) == ("u05", "u09")]
        self.assertEqual(len(anna_juliának), 6)

    def test_ek13_ejfel_ket_kulon_nap_es_mas_cimzett_limitje_fuggetlen(self):
        """EK-13 (SZ-07): 23:59 és 00:00 két külön nap; más címzett limitje független."""
        for perc in range(3):
            self.kuldes("u05", "u09", datetime(2026, 10, 29, 23, 57 + perc))
        self.kuldes("u05", "u06", datetime(2026, 10, 29, 23, 59))
        self.kuldes("u05", "u09", datetime(2026, 10, 30, 0, 0))
        self.assertEqual(len(self.sorok()), 5)


class TestEK47Kategoriak(SzerverTeszt):
    def test_ek47_a_negy_behavioral_anchor_kuldheto_a_regiek_nem(self):
        """EK-47 (SZ-06): `experiment` megy, az üzleti leírás régi kategóriái 400-at kapnak."""
        from kudos.koszonetek import KATEGORIAK

        self.assertEqual(KATEGORIAK, ("loyalty", "forward", "together", "experiment"))
        anna = self.belep("u05")
        adat = {"cimzett_id": "u09", "uzenet": "Köszi", "lathatosag": "privat"}
        self.assertEqual(anna.post("/api/koszonetek", dict(adat, kategoria="experiment"))[0], 201)
        for regi in ("egyuttmukodes", "kiemelkedo", "ugyfel", "segitseg", "otlet"):
            with self.subTest(kategoria=regi):
                allapot, tartalom = anna.post("/api/koszonetek", dict(adat, kategoria=regi))
                self.assertEqual(allapot, 400)
                self.assertEqual(tartalom["mezo"], "kategoria")
        self.assertEqual(len(self.sorok()), 1)


if __name__ == "__main__":
    unittest.main()
