"""S4 – Közös fal és taps (EK-22…EK-28): a fal, a láthatóság és a taps logikája, böngésző nélkül."""
import sqlite3
import sys
import threading
import unittest
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from segedek import ADATOK, SzerverTeszt  # noqa: E402


class FalTeszt(SzerverTeszt):
    def fal(self, kliens, **szuro):
        lekerdezes = urllib.parse.urlencode(szuro)
        allapot, tartalom = kliens.get("/api/fal" + ("?" + lekerdezes if lekerdezes else ""))
        self.assertEqual(allapot, 200)
        return tartalom

    def uzenetek(self, kliens, **szuro):
        return [k["uzenet"] for k in self.fal(kliens, **szuro)]

    def tap(self, kliens, koszonet_id):
        return kliens.post(f"/api/koszonetek/{koszonet_id}/taps")


class TestEK22CsakNyilvanos(FalTeszt):
    def test_ek22_a_falon_csak_a_nyilvanos_koszonet_jelenik_meg_mindenkinek(self):
        """EK-22 (SZ-09, SZ-08): a privát köszönet a küldőnek, a címzettnek és a vezetőknek sem jelenik meg."""
        self.beszur("u05", "u09", uzenet="Nyilvános köszi", lathatosag="nyilvanos")
        self.beszur("u06", "u07", uzenet="Privát köszi", lathatosag="privat")
        for munkatars in ("u13", "u06", "u07", "u00", "u05", "u09", "u03", "u01"):
            with self.subTest(munkatars=munkatars):
                self.assertEqual(self.uzenetek(self.belep(munkatars)), ["Nyilvános köszi"])


class TestEK23Szuro(FalTeszt):
    def setUp(self):
        super().setUp()
        most = datetime.now()
        self.beszur("u05", "u09", "together", "elso", "nyilvanos", most - timedelta(hours=3))
        self.beszur("u06", "u09", "loyalty", "masodik", "nyilvanos", most - timedelta(hours=2))
        self.beszur("u07", "u09", "together", "harmadik", "nyilvanos", most - timedelta(hours=1))
        self.nora = self.belep("u13")

    def test_ek23_a_legujabb_van_elol_szures_nelkul(self):
        """EK-23 (SZ-09, SZ-15): 3 nyilvános köszönet, a legutóbb küldött az első."""
        self.assertEqual(self.uzenetek(self.nora), ["harmadik", "masodik", "elso"])

    def test_ek23_kategoriara_szur(self):
        """EK-23 (SZ-15): 🤝 → 2, 🚀 → 0, üres kategória = mind."""
        self.assertEqual(self.uzenetek(self.nora, kategoria="together"), ["harmadik", "elso"])
        self.assertEqual(self.uzenetek(self.nora, kategoria="forward"), [])
        self.assertEqual(self.uzenetek(self.nora, kategoria=""), ["harmadik", "masodik", "elso"])

    def test_ek23_ismeretlen_kategoria_400(self):
        """EK-23 (SZ-06): a szűrőben sem fogadunk el ismeretlen kategóriát."""
        allapot, tartalom = self.nora.get("/api/fal?kategoria=pizza")
        self.assertEqual((allapot, tartalom["mezo"]), (400, "kategoria"))


class TestEK24TapsEsVisszavonas(FalTeszt):
    def test_ek24_taps_be_majd_ki(self):
        """EK-24 (SZ-10): az első kattintás tapsol, a második visszavon; a kártyán látszik az állapot."""
        kid = self.beszur("u05", "u09", lathatosag="nyilvanos")
        varga = self.belep("u06")

        self.assertEqual(self.tap(varga, kid), (200, {"tapsolt": True, "tapsok": 1}))
        sajat = self.fal(varga)[0]
        self.assertEqual((sajat["tapsolt"], sajat["tapsok"]), (True, 1))
        masik = self.fal(self.belep("u13"))[0]
        self.assertEqual((masik["tapsolt"], masik["tapsok"]), (False, 1))
        self.assertEqual([(s["koszonet_id"], s["munkatars_id"]) for s in self.sorok("taps")], [(kid, "u06")])

        self.assertEqual(self.tap(varga, kid), (200, {"tapsolt": False, "tapsok": 0}))
        self.assertEqual(self.sorok("taps"), [])
        self.assertEqual((self.fal(varga)[0]["tapsolt"], self.fal(varga)[0]["tapsok"]), (False, 0))

    def test_ek24_a_sajat_listakon_is_latszik_a_taps_allapota(self):
        """EK-24 (SZ-10): a Kapott lista kártyáján is ott a tapsszám és a saját taps."""
        kid = self.beszur("u05", "u09")
        julia = self.belep("u09")
        self.tap(julia, kid)
        kartya = julia.get("/api/koszonetek/kapott")[1]["koszonetek"][0]
        self.assertEqual((kartya["tapsolt"], kartya["tapsok"]), (True, 1))

    def test_ek24_belepes_nelkul_401(self):
        """EK-24 (SZ-01)."""
        self.assertEqual(self.tap(self.kliens(), 1)[0], 401)


class TestEK25EgySzemelyEgyTaps(FalTeszt):
    def test_ek25_a_kuldo_a_cimzett_es_masok_is_tapsolhatnak_egyszer(self):
        """EK-25 (SZ-10): Varga Bence, Kiss Réka, Horváth Anna (küldő), Farkas Júlia (címzett) → 4 taps."""
        kid = self.beszur("u05", "u09", lathatosag="nyilvanos")
        for varhato, munkatars in enumerate(("u06", "u07", "u05", "u09"), start=1):
            self.assertEqual(self.tap(self.belep(munkatars), kid), (200, {"tapsolt": True, "tapsok": varhato}))
        self.assertEqual(self.fal(self.belep("u13"))[0]["tapsok"], 4)

    def test_ek25_az_adatbazis_nem_enged_ketszeres_tapsot(self):
        """EK-25 (SZ-10): ugyanattól a személytől második taps rögzítése nem sikerül, a meglévő megmarad."""
        kid = self.beszur("u05", "u09", lathatosag="nyilvanos")
        self.tap(self.belep("u06"), kid)
        kapcsolat = sqlite3.connect(self.adatbazis)
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                kapcsolat.execute("INSERT INTO taps (koszonet_id, munkatars_id, letrehozva) VALUES (?, 'u06', 'x')", (kid,))
        finally:
            kapcsolat.close()
        self.assertEqual(len(self.sorok("taps")), 1)

    def test_ek25_parhuzamos_kerések_sem_hagynak_duplikatumot(self):
        """EK-25 (SZ-10): 8 egyidejű váltás ugyanattól a személytől → páros szám, tehát nincs taps, nincs hiba."""
        kid = self.beszur("u05", "u09", lathatosag="nyilvanos")
        allapotok = []

        def valtas():
            allapotok.append(self.tap(self.kliens("u13"), kid)[0])

        szalak = [threading.Thread(target=valtas) for _ in range(8)]
        for szal in szalak:
            szal.start()
        for szal in szalak:
            szal.join()
        self.assertEqual(allapotok, [200] * 8)
        self.assertEqual(self.sorok("taps"), [])


class TestEK26NemLathatoKoszonet(FalTeszt):
    def test_ek26_illetektelen_nem_tapsolhat_a_privat_koszonetre(self):
        """EK-26 (SZ-10, SZ-08): Juhász Nóra, Tóth Gábor és Varga Bence 404-et kap, a tapsszám nem változik."""
        kid = self.beszur("u05", "u09", lathatosag="privat")
        for munkatars in ("u13", "u04", "u06"):
            with self.subTest(munkatars=munkatars):
                self.assertEqual(self.tap(self.belep(munkatars), kid)[0], 404)
        self.assertEqual(self.sorok("taps"), [])

    def test_ek26_a_jogosult_vezetok_a_kuldo_es_a_cimzett_tapsolhat(self):
        """EK-26 (SZ-10, SZ-08): Szabó Katalin, Nagy Péter, Kovács Eszter, Fehér László, Anna és Júlia is."""
        kid = self.beszur("u05", "u09", lathatosag="privat")
        for varhato, munkatars in enumerate(("u03", "u02", "u01", "u00", "u05", "u09"), start=1):
            with self.subTest(munkatars=munkatars):
                self.assertEqual(self.tap(self.belep(munkatars), kid), (200, {"tapsolt": True, "tapsok": varhato}))

    def test_ek26_nem_letezo_koszonetre_404(self):
        """EK-26 (SZ-10): nem létező azonosító ugyanúgy 404, mint a nem látható."""
        self.assertEqual(self.tap(self.belep("u05"), 9999)[0], 404)

    def test_ek26_a_felettesek_lancat_a_vezeto_id_adja(self):
        """EK-26 (SZ-02, SZ-08): közvetlen vezető, B-1, B – a legalsóból felfelé."""
        from kudos.szervezet import Szervezet

        szervezet = Szervezet.betolt(ADATOK)
        self.assertEqual(szervezet.felettesek("u05"), ["u02", "u01", "u00"])
        self.assertEqual(szervezet.felettesek("u09"), ["u03", "u01", "u00"])
        self.assertEqual(szervezet.felettesek("u01"), ["u00"])
        self.assertEqual(szervezet.felettesek("u00"), [])

    def test_ek26_lathatosagi_szabaly(self):
        """EK-26 (SZ-08): nyilvános → mindenki; privát → küldő, címzett és azok vezetői."""
        from kudos import koszonetek
        from kudos.szervezet import Szervezet

        szervezet = Szervezet.betolt(ADATOK)
        privat = {"lathatosag": "privat", "kuldo_id": "u05", "cimzett_id": "u09"}
        nyilvanos = dict(privat, lathatosag="nyilvanos")
        for munkatars, varhato in [("u05", True), ("u09", True), ("u02", True), ("u03", True), ("u01", True),
                                   ("u00", True), ("u04", False), ("u06", False), ("u13", False)]:
            with self.subTest(munkatars=munkatars):
                self.assertEqual(koszonetek.lathato(szervezet, munkatars, privat), varhato)
                self.assertTrue(koszonetek.lathato(szervezet, munkatars, nyilvanos))


if __name__ == "__main__":
    unittest.main()
