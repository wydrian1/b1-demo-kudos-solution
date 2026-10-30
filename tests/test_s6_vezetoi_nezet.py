"""S6 – Vezetői nézet (EK-36…EK-41): a szervezeti kör, a jogosultság és a Csapatköszönetek API, böngésző nélkül.

Közös adatkészlet (privát, minden üzenet szövege a jele; az elmúlt 30 napban, M6 40 napja):
M1 Anna→Júlia 🤝 · M2 Júlia→Balogh Máté 🧪 · M3 Anna→Varga Bence 💛 · M4 Nóra→Simon Bálint 💛 (nyilvános) ·
M5 Nagy Péter→Szabó Katalin 🚀 · M6 Papp Zsófia→Júlia 🧪 (40 napja) · M7 Szabó Katalin→Nóra.
"""
import sys
import unittest
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from segedek import ADATOK, SzerverTeszt  # noqa: E402


class TestSzervezetiKor(unittest.TestCase):
    def setUp(self):
        from kudos.szervezet import Szervezet

        self.szervezet = Szervezet.betolt(ADATOK)

    def test_ek37_a_kor_a_vezeto_es_minden_beosztottja_barmilyen_melysegben(self):
        """EK-37, EK-38 (SZ-02): osztályvezető, főosztályvezető és board tag köre."""
        self.assertEqual(self.szervezet.kor("u03"), {"u03", "u09", "u10", "u11", "u12"})
        self.assertEqual(self.szervezet.kor("u02"), {"u02", "u05", "u06", "u07", "u08"})
        self.assertEqual(self.szervezet.kor("u04"), {"u04", "u13", "u14", "u15", "u16"})
        self.assertEqual(self.szervezet.kor("u01"), {f"u{i:02d}" for i in range(1, 17)})
        self.assertEqual(self.szervezet.kor("u00"), {f"u{i:02d}" for i in range(0, 17)})

    def test_ek36_vezeto_az_akinek_van_beosztottja(self):
        """EK-36 (SZ-13): u00–u04 vezető, a többi 12 munkatárs nem."""
        for i in range(17):
            mid = f"u{i:02d}"
            self.assertEqual(self.szervezet.vezeto_e(mid), i <= 4, mid)


class VezetoiTeszt(SzerverTeszt):
    def setUp(self):
        super().setUp()
        most = datetime.now()
        self.beszur("u05", "u09", "together", "M1", "privat", most - timedelta(days=1))
        self.beszur("u09", "u10", "experiment", "M2", "privat", most - timedelta(days=2))
        self.beszur("u05", "u06", "loyalty", "M3", "privat", most - timedelta(days=3))
        self.beszur("u13", "u16", "loyalty", "M4", "nyilvanos", most - timedelta(days=4))
        self.beszur("u02", "u03", "forward", "M5", "privat", most - timedelta(days=5))

    def m6(self):
        return self.beszur("u11", "u09", "experiment", "M6", "privat", datetime.now() - timedelta(days=40))

    def m7(self):
        return self.beszur("u03", "u13", "together", "M7", "privat", datetime.now() - timedelta(days=6))

    def csapat(self, kliens, **szuro):
        lekerdezes = urllib.parse.urlencode(szuro)
        return kliens.get("/api/csapat" + ("?" + lekerdezes if lekerdezes else ""))

    def uzenetek(self, munkatars, **szuro):
        allapot, tartalom = self.csapat(self.belep(munkatars), **szuro)
        self.assertEqual(allapot, 200)
        return [k["uzenet"] for k in tartalom]


class TestEK36Jogosultsag(VezetoiTeszt):
    def test_ek36_nem_vezeto_403_mindket_vegpontra(self):
        """EK-36 (SZ-13): Horváth Anna (alkalmazott) a Csapat- és a statisztika-API-t sem érheti el."""
        anna = self.belep("u05")
        for utvonal in ("/api/csapat", "/api/csapat/statisztika", "/api/csapat?idoszak=osszes"):
            with self.subTest(utvonal=utvonal):
                self.assertEqual(anna.get(utvonal)[0], 403)

    def test_ek36_minden_alkalmazott_403_minden_vezeto_200(self):
        """EK-36 (SZ-13): vezető, akinek van beosztottja: u00–u04; a többi 12 munkatárs nem."""
        for i in range(17):
            mid = f"u{i:02d}"
            with self.subTest(munkatars=mid):
                self.assertEqual(self.csapat(self.belep(mid))[0], 200 if i <= 4 else 403)

    def test_ek36_belepes_nelkul_401(self):
        """EK-36 (SZ-01)."""
        self.assertEqual(self.csapat(self.kliens())[0], 401)
        self.assertEqual(self.kliens().get("/api/csapat/statisztika")[0], 401)

    def test_ek36_az_en_vegpont_jelzi_hogy_vezeto_e(self):
        """EK-36 (SZ-13): a felület ebből dönti el, látszik-e a „Csapat” menüpont."""
        self.assertIs(self.belep("u05").get("/api/en")[1]["vezeto"], False)
        for mid in ("u03", "u02", "u04", "u01", "u00"):
            self.assertIs(self.belep(mid).get("/api/en")[1]["vezeto"], True, mid)

    def test_ek36_a_szolgaltatas_is_ellenorzi_a_jogosultsagot(self):
        """EK-36 (SZ-13): nem a webes réteg az egyetlen védelem."""
        from kudos import adatbazis, koszonetek
        from kudos.szervezet import Szervezet

        kapcsolat = adatbazis.kapcsolat(self.adatbazis)
        try:
            with self.assertRaises(koszonetek.NincsJogosultsag):
                koszonetek.csapat(kapcsolat, Szervezet.betolt(ADATOK), "u05")
        finally:
            kapcsolat.close()


class TestEK37EsEK38Korok(VezetoiTeszt):
    def test_ek37_osztalyvezeto_csak_a_sajat_korenek_koszonetet_latja_privatokkal_egyutt(self):
        """EK-37 (SZ-13, SZ-02): Szabó Katalin → M1, M2, M5; M3 és M4 (nyilvános is) nem."""
        self.assertEqual(self.uzenetek("u03"), ["M1", "M2", "M5"])

    def test_ek38_foosztalyvezeto_es_board_tag_az_egesz_alatta_levo_kort_latja(self):
        """EK-38 (SZ-13, SZ-02): Kovács Eszter és Fehér László mind az 5-öt."""
        self.assertEqual(self.uzenetek("u01"), ["M1", "M2", "M3", "M4", "M5"])
        self.assertEqual(self.uzenetek("u00"), ["M1", "M2", "M3", "M4", "M5"])

    def test_ek38_masik_osztalyvezeto_a_sajat_korenek_koszonetet_latja(self):
        """EK-38 (SZ-13): Nagy Péter → M1, M3, M5 (az M5 küldője ő maga); Tóth Gábor → csak M4."""
        self.assertEqual(self.uzenetek("u02"), ["M1", "M3", "M5"])
        self.assertEqual(self.uzenetek("u04"), ["M4"])

    def test_ek37_a_kartya_a_nezo_taps_allapotat_is_tartalmazza(self):
        """EK-37 (SZ-10): a Csapat kártyáin is látszik a tapsszám és a saját taps."""
        katalin = self.belep("u03")
        m1 = self.csapat(katalin)[1][0]
        self.assertEqual((m1["uzenet"], m1["tapsok"], m1["tapsolt"]), ("M1", 0, False))
        self.assertEqual(katalin.post(f"/api/koszonetek/{m1['id']}/taps")[0], 200)
        m1 = self.csapat(katalin)[1][0]
        self.assertEqual((m1["tapsok"], m1["tapsolt"]), (1, True))


class TestEK39MasKorNemSzivarog(VezetoiTeszt):
    def test_ek39_extra_parameterek_nem_valtoztatjak_a_kort(self):
        """EK-39 (SZ-13, SZ-08): `vezeto_id`, `egyseg`, `kuldo_id` paraméterrel is a bejelentkezett köre."""
        katalin = self.belep("u03")
        alap = [k["uzenet"] for k in self.csapat(katalin)[1]]
        self.assertEqual(alap, ["M1", "M2", "M5"])
        for extra in ({"vezeto_id": "u01"}, {"egyseg": "Fejlesztési Osztály"}, {"kuldo_id": "u05"},
                      {"kor": "u00"}, {"munkatars": "u13"}):
            with self.subTest(extra=extra):
                allapot, tartalom = self.csapat(katalin, **extra)
                self.assertEqual((allapot, [k["uzenet"] for k in tartalom]), (200, alap))

    def test_ek39_idegen_kor_privat_koszonetere_nem_lehet_tapsolni(self):
        """EK-39 (SZ-10, SZ-08): Szabó Katalin az M3-ra (Fejlesztési Osztály belső) 404-et kap."""
        m3 = next(s["id"] for s in self.sorok() if s["uzenet"] == "M3")
        self.assertEqual(self.belep("u03").post(f"/api/koszonetek/{m3}/taps")[0], 404)
        self.assertEqual(self.sorok("taps"), [])


class TestEK40KeresesEsSzures(VezetoiTeszt):
    def test_ek40_az_alapertelmezett_idoszak_30_nap(self):
        """EK-40 (SZ-15): a 40 napos M6 alapból nem látszik, „összes” időszakra igen."""
        self.m6()
        self.assertEqual(self.uzenetek("u03"), ["M1", "M2", "M5"])
        self.assertEqual(self.uzenetek("u03", idoszak="osszes"), ["M1", "M2", "M5", "M6"])
        self.assertEqual(self.uzenetek("u03", idoszak="7"), ["M1", "M2", "M5"])

    def test_ek40_kereses_a_kuldo_es_a_cimzett_nevere(self):
        """EK-40 (SZ-15): „júlia” → M1 (címzett) és M2 (küldő)."""
        self.m6()
        self.assertEqual(self.uzenetek("u03", q="júlia"), ["M1", "M2"])
        self.assertEqual(self.uzenetek("u03", q="JÚLIA", idoszak="osszes"), ["M1", "M2", "M6"])

    def test_ek40_kategoriaszuro_es_a_szurok_egyutt(self):
        """EK-40 (SZ-15): 🧪 → M2; összes időszak + 🧪 → M2 és M6 ebben a sorrendben."""
        self.m6()
        self.assertEqual(self.uzenetek("u03", kategoria="experiment"), ["M2"])
        self.assertEqual(self.uzenetek("u03", kategoria="experiment", idoszak="osszes"), ["M2", "M6"])
        self.assertEqual(self.uzenetek("u03", kategoria="experiment", idoszak="osszes", q="papp"), ["M6"])

    def test_ek40_ismeretlen_szuroertek_400(self):
        """EK-40 (SZ-06): ismeretlen kategória vagy időszak."""
        katalin = self.belep("u03")
        self.assertEqual(self.csapat(katalin, kategoria="pizza")[0], 400)
        self.assertEqual(self.csapat(katalin, idoszak="5")[0], 400)


class TestEK41VezetoMagaIsAKorBan(VezetoiTeszt):
    def test_ek41_a_vezeto_sajat_koszonetei_is_a_koreben_vannak(self):
        """EK-41 (SZ-13, SZ-02): Szabó Katalin → M1, M2, M5, M7 (M7-nek ő a küldője)."""
        self.m7()
        self.assertEqual(self.uzenetek("u03"), ["M1", "M2", "M5", "M7"])

    def test_ek41_a_beosztott_vezetoje_latja_a_beosztott_kapott_koszonetet(self):
        """EK-41 (SZ-13): Tóth Gábor → M4 és M7 (Juhász Nóra a címzett)."""
        self.m7()
        self.assertEqual(self.uzenetek("u04"), ["M4", "M7"])


if __name__ == "__main__":
    unittest.main()
