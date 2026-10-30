"""S1 – Belépés és köszönet küldése (EK-01…EK-07): az üzleti logika és a HTTP API, böngésző nélkül."""
import re
import sys
import unittest
import urllib.parse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from segedek import ADATOK, GYOKER, SzerverTeszt  # noqa: E402

UZENET = "Köszönöm a gyors adatelemzést! 🙏🎉"


class TestEK01Belepes(SzerverTeszt):
    def test_ek01_a_munkatarslista_belepes_nelkul_is_17_elem(self):
        """EK-01 (SZ-01), EK-02: a munkatárslista belépés nélkül is elérhető."""
        allapot, lista = self.kliens().get("/api/munkatarsak")
        self.assertEqual(allapot, 200)
        self.assertEqual(len(lista), 17)
        anna = next(m for m in lista if m["id"] == "u05")
        self.assertEqual(anna["nev"], "Horváth Anna")
        self.assertEqual(anna["egyseg"], "Fejlesztési Osztály")

    def test_ek01_belepes_utan_az_en_vegpont_u05_t_ad_es_a_suti_vedett(self):
        """EK-01 (SZ-01): a süti HttpOnly és SameSite=Lax (4.5. pont)."""
        kliens = self.kliens()
        allapot, _ = kliens.post("/api/belepes", {"id": "u05"})
        self.assertEqual(allapot, 200)
        suti = " ".join(kliens.utolso_set_cookie)
        self.assertIn("kudos_user=u05", suti)
        self.assertIn("HttpOnly", suti)
        self.assertIn("SameSite=Lax", suti)
        allapot, en = kliens.get("/api/en")
        self.assertEqual(allapot, 200)
        self.assertEqual(en["id"], "u05")
        self.assertEqual(en["nev"], "Horváth Anna")
        self.assertEqual(en["egyseg"], "Fejlesztési Osztály")

    def test_ek01_ismeretlen_azonosito_nem_lephet_be(self):
        """EK-01 (SZ-01): csak a listában szereplő munkatárs léphet be."""
        kliens = self.kliens()
        allapot, tartalom = kliens.post("/api/belepes", {"id": "u99"})
        self.assertEqual(allapot, 400)
        self.assertIn("hiba", tartalom)
        self.assertIsNone(kliens.suti)
        self.assertEqual(kliens.get("/api/en")[0], 401)

    def test_ek01_kilepes_utan_nincs_munkamenet(self):
        """EK-01 (SZ-01): a [Váltás] gomb kiléptet."""
        kliens = self.belep("u05")
        allapot, _ = kliens.post("/api/kilepes")
        self.assertEqual(allapot, 200)
        self.assertEqual(kliens.get("/api/en")[0], 401)


class TestEK02BelepesNelkulNincsHozzaferes(SzerverTeszt):
    VEDETT = [
        ("GET", "/api/fal"),
        ("POST", "/api/koszonetek"),
        ("GET", "/api/ertesitesek"),
        ("GET", "/api/en"),
        ("GET", "/api/munkatarsak/kereses?q=adat"),
    ]

    def test_ek02_belepes_nelkul_es_ismeretlen_sutivel_401(self):
        """EK-02 (SZ-01): sütivel sem létező munkatárs (u99) nem fér hozzá semmihez."""
        for suti in (None, "u99"):
            kliens = self.kliens(suti)
            for modszer, utvonal in self.VEDETT:
                with self.subTest(suti=suti, kerelem=f"{modszer} {utvonal}"):
                    allapot, _ = kliens.keres(modszer, utvonal, {} if modszer == "POST" else None)
                    self.assertEqual(allapot, 401)


class TestEK03Kereso(unittest.TestCase):
    def setUp(self):
        from kudos.szervezet import Szervezet

        self.szervezet = Szervezet.betolt(ADATOK)

    def azonositok(self, szoveg, kiveve=None):
        return [m["id"] for m in self.szervezet.kereses(szoveg, kiveve=kiveve)]

    def test_ek03_egyseg_szerint_az_adat_osztaly_5_tagja(self):
        """EK-03 (SZ-03): „adat” → Szabó Katalin, Farkas Júlia, Balogh Máté, Papp Zsófia, Takács Levente."""
        self.assertEqual(set(self.azonositok("adat", kiveve="u05")), {"u03", "u09", "u10", "u11", "u12"})

    def test_ek03_email_reszlet_szerint(self):
        """EK-03 (SZ-03): „julia.f” egyetlen találat: Farkas Júlia."""
        self.assertEqual(self.azonositok("julia.f", kiveve="u05"), ["u09"])

    def test_ek03_a_bejelentkezett_felhasznalo_nem_szerepel_a_talalatok_kozott(self):
        """EK-03 (SZ-03): Horváth Anna saját magát nem találja meg."""
        self.assertEqual(self.azonositok("horváth", kiveve="u05"), [])
        self.assertEqual(self.azonositok("horváth"), ["u05"])

    def test_ek03_kis_es_nagybetutol_fuggetlen(self):
        """EK-03 (SZ-03)."""
        self.assertEqual(set(self.azonositok("ADAT", kiveve="u05")), {"u03", "u09", "u10", "u11", "u12"})
        self.assertEqual(self.azonositok("FARKAS", kiveve="u05"), ["u09"])

    def test_ek03_ures_keresoszora_nincs_talalat(self):
        """EK-03 (SZ-03): üres és csak szóközből álló keresőszó."""
        self.assertEqual(self.azonositok(""), [])
        self.assertEqual(self.azonositok("   "), [])

    def test_ek03_a_beosztas_nem_kereso_mezo(self):
        """EK-03 (SZ-03): név, egység és e-mail alapján keres, beosztás alapján nem."""
        self.assertEqual(self.azonositok("szoftverfejlesztő"), [])

    def test_ek03_a_talalatban_latszik_a_nev_a_beosztas_es_az_egyseg(self):
        """EK-03 (SZ-03)."""
        julia = self.szervezet.kereses("julia.f")[0]
        self.assertEqual((julia["nev"], julia["beosztas"], julia["egyseg"]),
                         ("Farkas Júlia", "adatelemző", "Adat Osztály"))


class TestEK03KeresoApi(SzerverTeszt):
    def kereses(self, kliens, szoveg):
        allapot, talalatok = kliens.get("/api/munkatarsak/kereses?q=" + urllib.parse.quote(szoveg))
        self.assertEqual(allapot, 200)
        return talalatok

    def test_ek03_api_a_bejelentkezett_felhasznalo_nem_szerepel_a_talalatok_kozott(self):
        """EK-03 (SZ-03): a szerver a munkamenetből tudja, kit kell kihagyni."""
        anna = self.belep("u05")
        adat = self.kereses(anna, "adat")
        self.assertEqual({m["id"] for m in adat}, {"u03", "u09", "u10", "u11", "u12"})
        for m in adat:
            self.assertTrue(m["nev"] and m["beosztas"] and m["egyseg"])
        self.assertEqual(self.kereses(anna, "horváth"), [])
        self.assertEqual([m["id"] for m in self.kereses(anna, "julia.f")], ["u09"])


class TestEK06Kuldes(SzerverTeszt):
    @staticmethod
    def adat(**felulir):
        alap = {"cimzett_id": "u09", "kategoria": "together", "uzenet": UZENET, "lathatosag": "privat"}
        alap.update(felulir)
        return alap

    def test_ek06_a_koszonet_az_adatbazisba_kerul(self):
        """EK-06 (SZ-04, SZ-08, SZ-16): Horváth Anna → Farkas Júlia, privát, az idő ±5 mp."""
        anna = self.belep("u05")
        allapot, valasz = anna.post("/api/koszonetek", self.adat())
        self.assertEqual(allapot, 201)
        sorok = self.sorok()
        self.assertEqual(len(sorok), 1)
        sor = sorok[0]
        self.assertEqual(
            (sor["kuldo_id"], sor["cimzett_id"], sor["kategoria"], sor["lathatosag"], sor["uzenet"]),
            ("u05", "u09", "together", "privat", UZENET),
        )
        kulonbseg = abs((datetime.now() - datetime.fromisoformat(sor["letrehozva"])).total_seconds())
        self.assertLess(kulonbseg, 5)
        self.assertEqual(valasz["id"], sor["id"])

    def test_ek06_a_kliens_nem_adhatja_meg_az_idopontot_es_a_kuldot(self):
        """EK-06 (SZ-16): a `letrehozva` és a `kuldo_id` mezőt a szerver figyelmen kívül hagyja."""
        anna = self.belep("u05")
        allapot, _ = anna.post(
            "/api/koszonetek", self.adat(letrehozva="2000-01-01T00:00:00", kuldo_id="u06")
        )
        self.assertEqual(allapot, 201)
        sor = self.sorok()[0]
        self.assertEqual(sor["kuldo_id"], "u05")
        self.assertNotEqual(sor["letrehozva"][:4], "2000")

    def test_ek06_alapertelmezett_lathatosag_a_privat(self):
        """EK-06 (SZ-08): láthatóság megadása nélkül a köszönet privát."""
        anna = self.belep("u05")
        bemenet = self.adat()
        del bemenet["lathatosag"]
        self.assertEqual(anna.post("/api/koszonetek", bemenet)[0], 201)
        self.assertEqual(self.sorok()[0]["lathatosag"], "privat")

    def test_ek06_a_valasz_a_koszonet_adatait_tartalmazza(self):
        """EK-06 (SZ-04): a válaszban a küldő és a címzett neve is szerepel."""
        anna = self.belep("u05")
        _, valasz = anna.post("/api/koszonetek", self.adat(lathatosag="nyilvanos"))
        self.assertEqual(valasz["kuldo"]["nev"], "Horváth Anna")
        self.assertEqual(valasz["cimzett"]["nev"], "Farkas Júlia")
        self.assertEqual(valasz["cimzett"]["egyseg"], "Adat Osztály")
        self.assertEqual(valasz["kategoria"], "together")
        self.assertEqual(valasz["uzenet"], UZENET)
        self.assertEqual(valasz["lathatosag"], "nyilvanos")

    def test_ek06_ervenytelen_cimzett_kategoria_vagy_lathatosag_nem_mentodik(self):
        """EK-06 (SZ-04, SZ-06, SZ-08): nem létező címzett, ismeretlen kategória vagy láthatóság."""
        anna = self.belep("u05")
        esetek = [
            (self.adat(cimzett_id="u99"), "cimzett"),
            (self.adat(kategoria="pizza"), "kategoria"),
            (self.adat(lathatosag="titkos"), "lathatosag"),
        ]
        for bemenet, mezo in esetek:
            with self.subTest(mezo=mezo):
                allapot, tartalom = anna.post("/api/koszonetek", bemenet)
                self.assertEqual(allapot, 400)
                self.assertEqual(tartalom["mezo"], mezo)
        self.assertEqual(self.sorok(), [])

    def test_ek06_a_szolgaltatas_kozvetlenul_is_ment_es_az_idot_a_szerver_adja(self):
        """EK-06 (SZ-16): `kuldes()` a megadott „most” időpontot rögzíti."""
        from kudos import adatbazis, koszonetek
        from kudos.szervezet import Szervezet

        kapcsolat = adatbazis.kapcsolat(self.adatbazis)
        try:
            azonosito = koszonetek.kuldes(
                kapcsolat, Szervezet.betolt(ADATOK), "u05", "u09", "together", UZENET,
                most=datetime(2026, 10, 30, 10, 0, 0),
            )
        finally:
            kapcsolat.close()
        sor = self.sorok()[0]
        self.assertEqual(sor["id"], azonosito)
        self.assertEqual(sor["letrehozva"], "2026-10-30T10:00:00")


class TestEK07Arculat(unittest.TestCase):
    TOKENEK = [
        "--yellow", "--yellow-2", "--yellow-soft", "--offblack",
        "--grey-1", "--grey-2", "--grey-3", "--grey-4", "--white",
        "--cat-egyuttmukodes", "--cat-segitseg", "--cat-otlet", "--cat-ugyfel", "--cat-kiemelkedo",
        "--ok", "--error", "--radius", "--radius-sm", "--shadow", "--shadow-hover", "--font",
    ]

    def setUp(self):
        self.css = (GYOKER / "static" / "style.css").read_text(encoding="utf-8")
        self.torzs = re.sub(r"^\s*(/\*.*?\*/\s*)*", "", self.css, flags=re.S)

    def root_blokk(self):
        self.assertTrue(self.torzs.startswith(":root"))
        return self.torzs[: self.torzs.index("}") + 1]

    def test_ek07_a_css_a_root_blokkal_kezdodik(self):
        """EK-07 (NF-02): a stíluslap a design tokenekkel kezdődik."""
        self.root_blokk()

    def test_ek07_az_utmutato_osszes_tokenje_definialva_van(self):
        """EK-07 (NF-02): `--yellow` … `--font`, az útmutató értékeivel."""
        blokk = self.root_blokk()
        for token in self.TOKENEK:
            with self.subTest(token=token):
                self.assertRegex(blokk, re.escape(token) + r"\s*:")
        self.assertRegex(blokk, r"--yellow\s*:\s*#FEE600", )
        self.assertRegex(blokk, r"--offblack\s*:\s*#2B2D33")

    def test_ek07_a_root_blokkon_kivul_nincs_beegetett_szin(self):
        """EK-07 (NF-02): a komponensek a tokenekre épülnek."""
        maradek = self.torzs[self.torzs.index("}") + 1:]
        self.assertNotRegex(maradek, r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")

    def test_ek07_nincs_kulso_hivatkozas_es_felugro_ablak_a_felulet_fajljaiban(self):
        """EK-07 (NF-01, NF-03): nincs CDN/külső URL, `alert()`, `confirm()`, `prompt()`."""
        fajlok = [f for f in (GYOKER / "static").rglob("*") if f.is_file()]
        self.assertTrue(fajlok)
        for fajl in fajlok:
            szoveg = fajl.read_text(encoding="utf-8")
            with self.subTest(fajl=fajl.name):
                self.assertNotRegex(szoveg, r"https?://")
                self.assertNotRegex(szoveg, r"\b(alert|confirm|prompt)\s*\(")


if __name__ == "__main__":
    unittest.main()
