"""S5 – Értesítések (EK-29…EK-35): kinek jár értesítés, a lista tartalma és az olvasottság, böngésző nélkül."""
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from segedek import ADATOK, SzerverTeszt  # noqa: E402


class ErtesitesTeszt(SzerverTeszt):
    def kuld(self, kuldo, cimzett, uzenet="Köszi", kategoria="together"):
        allapot, valasz = self.belep(kuldo).post("/api/koszonetek", {
            "cimzett_id": cimzett, "kategoria": kategoria, "uzenet": uzenet, "lathatosag": "privat"})
        self.assertEqual(allapot, 201)
        return valasz["id"]

    def ertesitettek(self, koszonet_id):
        """Az értesítést kapók azonosítói, minden előfordulás külön (a duplikátum így látszik)."""
        return sorted(s["munkatars_id"] for s in self.sorok("ertesites") if s["koszonet_id"] == koszonet_id)

    def lista(self, kliens):
        allapot, tartalom = kliens.get("/api/ertesitesek")
        self.assertEqual(allapot, 200)
        return tartalom


class TestKinekJarErtesites(ErtesitesTeszt):
    def test_ek29_cimzett_kozvetlen_vezeto_es_b1_vezeto(self):
        """EK-29 (SZ-11, SZ-02): Anna → Júlia: Farkas Júlia, Szabó Katalin (közvetlen), Kovács Eszter (B-1)."""
        kid = self.kuld("u05", "u09")
        self.assertEqual(self.ertesitettek(kid), ["u01", "u03", "u09"])
        # nem kap: Anna (küldő), Nagy Péter (Anna vezetője), Fehér László (board tag)
        self.assertEqual(len(self.sorok("ertesites")), 3)

    def test_ek30_aki_tobb_szerepben_erintett_egy_ertesitest_kap(self):
        """EK-30 (SZ-11): Anna → Nagy Péter: Kovács Eszter közvetlen vezetőként és B-1-ként is érintett, mégis egy."""
        kid = self.kuld("u05", "u02")
        self.assertEqual(self.ertesitettek(kid), ["u01", "u02"])

    def test_ek31_b1_cimzettnek_nincs_b1_vezetoje_a_board_tag_kozvetlen_vezetokent_kap(self):
        """EK-31 (SZ-11, SZ-02): Anna → Kovács Eszter: Eszter és Fehér László (közvetlen vezető), Nagy Péter nem."""
        kid = self.kuld("u05", "u01")
        self.assertEqual(self.ertesitettek(kid), ["u00", "u01"])

    def test_ek32_vezeto_nelkuli_cimzett_csak_maga_kap(self):
        """EK-32 (SZ-11): Varga Bence → Fehér László (board tag, nincs vezetője)."""
        kid = self.kuld("u06", "u00")
        self.assertEqual(self.ertesitettek(kid), ["u00"])

    def test_ek33_a_kuldo_nem_kap_ertesitest_a_sajat_koszonetererol(self):
        """EK-33 (SZ-11): Nagy Péter → Horváth Anna: Anna és Kovács Eszter kap, Péter (Anna vezetője) nem."""
        kid = self.kuld("u02", "u05")
        self.assertEqual(self.ertesitettek(kid), ["u01", "u05"])

    def test_ek33_tovabbi_esetek_a_szabalyok_kombinacioja(self):
        """EK-33 (SZ-11): Fehér László (a címzett vezetője) küld Kovács Eszternek; Adat és Üzemeltetési Osztály."""
        eredmeny = {}
        for kuldo, cimzett in [("u00", "u01"), ("u05", "u10"), ("u05", "u13"), ("u06", "u03"), ("u05", "u04")]:
            eredmeny[(kuldo, cimzett)] = self.ertesitettek(self.kuld(kuldo, cimzett))
        self.assertEqual(eredmeny, {
            ("u00", "u01"): ["u01"],                  # a közvetlen vezető a küldő, B-1 címzettnek nincs B-1 vezetője
            ("u05", "u10"): ["u01", "u03", "u10"],    # Balogh Máté, Szabó Katalin, Kovács Eszter
            ("u05", "u13"): ["u01", "u04", "u13"],    # Juhász Nóra, Tóth Gábor, Kovács Eszter
            ("u06", "u03"): ["u01", "u03"],           # B-2 címzett: Szabó Katalin és Kovács Eszter
            ("u05", "u04"): ["u01", "u04"],
        })

    def test_ek29_a_sikertelen_kuldes_nem_hagy_ertesitest(self):
        """EK-29 (SZ-11): a köszönet és az értesítések egy tranzakcióban jönnek létre."""
        for _ in range(3):
            self.kuld("u05", "u09")
        self.assertEqual(len(self.sorok("ertesites")), 9)
        anna = self.belep("u05")
        self.assertEqual(anna.post("/api/koszonetek", {"cimzett_id": "u09", "kategoria": "together", "uzenet": "4."})[0], 400)
        self.assertEqual(anna.post("/api/koszonetek", {"cimzett_id": "u09", "kategoria": "pizza", "uzenet": "x"})[0], 400)
        self.assertEqual(len(self.sorok("koszonet")), 3)
        self.assertEqual(len(self.sorok("ertesites")), 9)

    def test_ek29_az_adatbazis_sem_enged_ketszeres_ertesitest(self):
        """EK-29 (SZ-11): (munkatárs, köszönet) páronként egyedi."""
        kid = self.kuld("u05", "u09")
        kapcsolat = sqlite3.connect(self.adatbazis)
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                kapcsolat.execute(
                    "INSERT INTO ertesites (munkatars_id, koszonet_id, letrehozva) VALUES ('u09', ?, 'x')", (kid,))
        finally:
            kapcsolat.close()

    def test_ek29_a_cimzettek_fuggveny_a_szervezetbol_szamol(self):
        """EK-29 (SZ-11, SZ-02): az értesítendők listája a címzett, a közvetlen vezető, a B-1 sorrendjében."""
        from kudos import ertesitesek
        from kudos.szervezet import Szervezet

        szervezet = Szervezet.betolt(ADATOK)
        self.assertEqual(ertesitesek.cimzettek(szervezet, "u05", "u09"), ["u09", "u03", "u01"])
        self.assertEqual(ertesitesek.cimzettek(szervezet, "u05", "u02"), ["u02", "u01"])
        self.assertEqual(ertesitesek.cimzettek(szervezet, "u05", "u01"), ["u01", "u00"])
        self.assertEqual(ertesitesek.cimzettek(szervezet, "u06", "u00"), ["u00"])
        self.assertEqual(ertesitesek.cimzettek(szervezet, "u02", "u05"), ["u05", "u01"])


class TestEK34Lista(ErtesitesTeszt):
    def test_ek34_a_lista_tartalma_legujabb_elol_es_az_elonezet(self):
        """EK-34 (SZ-12): küldő, címzett, kategória, dátum, az üzenet első 80 karaktere „…”-tal."""
        hosszu = "Köszönöm a gyors adatelemzést! 🙏 " + "x" * 87
        self.assertEqual(len(hosszu), 120)
        anna_id = self.kuld("u05", "u09", hosszu)
        bence_id = self.kuld("u06", "u09", "Rövid köszönet")

        lista = self.lista(self.belep("u09"))
        self.assertEqual([n["koszonet_id"] for n in lista], [bence_id, anna_id])
        self.assertTrue(all(n["olvasott"] is False for n in lista))

        anna = lista[1]
        self.assertEqual((anna["kuldo"]["nev"], anna["cimzett"]["nev"]), ("Horváth Anna", "Farkas Júlia"))
        self.assertEqual(anna["kategoria"], "together")
        self.assertEqual(anna["elonezet"], hosszu[:80] + "…")
        self.assertEqual(len(anna["elonezet"]), 81)
        self.assertEqual(anna["koszonet_letrehozva"], self.sorok("koszonet")[0]["letrehozva"])
        self.assertEqual(lista[0]["elonezet"], "Rövid köszönet")

    def test_ek34_az_elonezet_a_karaktereket_nem_a_bajtokat_szamolja(self):
        """EK-34 (SZ-12): pontosan 80 karakter (az emoji 1) nem kap „…”-t, 81 igen."""
        pontosan = "a" * 79 + "🙏"
        self.kuld("u05", "u09", pontosan)
        self.kuld("u06", "u09", pontosan + "b")
        elonezetek = sorted(n["elonezet"] for n in self.lista(self.belep("u09")))
        self.assertEqual(elonezetek, sorted([pontosan, pontosan + "…"]))

    def test_ek34_mas_munkatars_ertesitesi_listaja_ures(self):
        """EK-34 (SZ-12): Juhász Nóra listája üres, belépés nélkül 401."""
        self.kuld("u05", "u09")
        self.assertEqual(self.lista(self.belep("u13")), [])
        self.assertEqual(self.kliens().get("/api/ertesitesek")[0], 401)


class TestEK35Olvasottsag(ErtesitesTeszt):
    def setUp(self):
        super().setUp()
        self.kuld("u05", "u09", "Anna köszönete")
        self.kuld("u06", "u09", "Bence köszönete")
        self.julia = self.belep("u09")
        self.katalin = self.belep("u03")

    def olvasatlan(self, kliens):
        return sum(1 for n in self.lista(kliens) if not n["olvasott"])

    def test_ek35_egy_ertesites_megnyitasa_olvasottra_allitja(self):
        """EK-35 (SZ-12): 2 olvasatlan → az egyik megnyitása után 1."""
        self.assertEqual(self.olvasatlan(self.julia), 2)
        elso = self.lista(self.julia)[0]
        allapot, _ = self.julia.post(f"/api/ertesitesek/{elso['id']}/olvasott")
        self.assertEqual(allapot, 200)
        self.assertEqual(self.olvasatlan(self.julia), 1)
        self.assertTrue(self.lista(self.julia)[0]["olvasott"])
        # ismételt megnyitás sem hiba
        self.assertEqual(self.julia.post(f"/api/ertesitesek/{elso['id']}/olvasott")[0], 200)

    def test_ek35_mind_olvasott_csak_a_sajat_ertesiteseket_erinti(self):
        """EK-35 (SZ-12): Júlia „Mind olvasott” gombja után Szabó Katalin értesítései olvasatlanok maradnak (2)."""
        self.assertEqual(self.olvasatlan(self.katalin), 2)
        self.assertEqual(self.julia.post("/api/ertesitesek/olvasott-mind")[0], 200)
        self.assertEqual(self.olvasatlan(self.julia), 0)
        self.assertEqual(len(self.lista(self.julia)), 2)
        self.assertEqual(self.olvasatlan(self.katalin), 2)

    def test_ek35_mas_ertesiteset_nem_lehet_olvasottra_allitani(self):
        """EK-35 (SZ-12): Juhász Nóra Júlia értesítésére 404-et kap, és az nem változik; nem létező azonosító is 404."""
        julia_ertesitese = self.lista(self.julia)[0]["id"]
        nora = self.belep("u13")
        self.assertEqual(nora.post(f"/api/ertesitesek/{julia_ertesitese}/olvasott")[0], 404)
        self.assertEqual(nora.post("/api/ertesitesek/9999/olvasott")[0], 404)
        self.assertEqual(self.olvasatlan(self.julia), 2)

    def test_ek35_belepes_nelkul_401(self):
        """EK-35 (SZ-01)."""
        kliens = self.kliens()
        self.assertEqual(kliens.post("/api/ertesitesek/1/olvasott")[0], 401)
        self.assertEqual(kliens.post("/api/ertesitesek/olvasott-mind")[0], 401)


if __name__ == "__main__":
    unittest.main()
