"""S3 – Saját köszöneteim, böngészőben (EK-14…EK-21).

„Kész, ha…”: Anna küldés után a „Küldött (1)” listán látja a köszönetet, Farkas Júlia a „Kapott (1)” listán,
és mindketten kereshetnek és szűrhetnek. Varga Bence üres állapotot lát.
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
UZENET = "Köszönöm a gyors adatelemzést! 🙏🎉"


class TestS3(E2ETeszt):
    def kartyak(self):
        return self.oldal.get_by_role("article")

    def sajat(self, nev, ful="Kapott"):
        """Belépés, majd a Saját oldal megnyitása a menüből, a kért füllel."""
        self.belep(nev)
        self.oldal.get_by_role("navigation", name="Főmenü").get_by_role("link", name="Saját", exact=True).click()
        expect(self.oldal.get_by_role("heading", name="Saját köszönetek")).to_be_visible()
        if ful == "Küldött":
            self.oldal.get_by_role("link", name=re.compile(r"^Küldött")).click()
        self.ful_aktiv(ful)

    def ful_aktiv(self, ful):
        expect(self.oldal.get_by_role("link", name=re.compile(rf"^{ful}"))).to_have_attribute("aria-current", "page")

    def ful(self, felirat):
        return self.oldal.get_by_role("link", name=felirat, exact=True)

    def kereso(self):
        return self.oldal.get_by_label("Keresés a köszönetekben")

    def kategoria_szuro(self):
        return self.oldal.get_by_label("Kategória", exact=True)

    def idoszak_szuro(self):
        return self.oldal.get_by_label("Időszak", exact=True)

    def kuldes_a_varazslovel(self, keres, nev, kategoria, uzenet):
        self.oldal.get_by_role("combobox", name=KERESO).fill(keres)
        self.oldal.get_by_role("option", name=re.compile(nev)).click()
        self.oldal.get_by_role("radio", name=re.compile(re.escape(kategoria))).click()
        self.oldal.get_by_label("Üzenet", exact=True).fill(uzenet)
        self.oldal.get_by_role("button", name="Tovább").click()
        self.oldal.get_by_role("button", name="Küldés").click()

    # --- EK-14, EK-21 -----------------------------------------------------------------------------

    def test_s3_ek14_ek21_anna_kuld_es_a_kuldott_listara_erkezik_julia_a_kapottat_latja(self):
        """EK-14, EK-21: küldés után a Küldött lista nyílik; Júlia Kapott (1), Varga Bence mindkettő (0)."""
        self.uj_koszonet("Horváth Anna")
        self.kuldes_a_varazslovel("julia.f", "Farkas Júlia", "Deliver value together", UZENET)

        expect(self.oldal.get_by_role("status")).to_contain_text("Köszönetedet elküldtük Farkas Júliának!")
        expect(self.oldal.get_by_role("heading", name="Saját köszönetek")).to_be_visible()
        self.ful_aktiv("Küldött")
        expect(self.ful("Küldött (1)")).to_be_visible()
        expect(self.ful("Kapott (0)")).to_be_visible()
        expect(self.kartyak()).to_have_count(1)
        expect(self.kartyak().first).to_contain_text("Farkas Júlia")
        expect(self.kartyak().first).to_contain_text(UZENET)

        self.valt("Farkas Júlia")
        self.oldal.get_by_role("navigation", name="Főmenü").get_by_role("link", name="Saját", exact=True).click()
        self.ful_aktiv("Kapott")
        expect(self.ful("Kapott (1)")).to_be_visible()
        expect(self.ful("Küldött (0)")).to_be_visible()
        expect(self.kartyak()).to_have_count(1)
        expect(self.kartyak().first).to_contain_text("Horváth Anna")

        self.valt("Varga Bence")
        self.oldal.get_by_role("navigation", name="Főmenü").get_by_role("link", name="Saját", exact=True).click()
        expect(self.ful("Kapott (0)")).to_be_visible()
        expect(self.ful("Küldött (0)")).to_be_visible()
        expect(self.kartyak()).to_have_count(0)

    # --- EK-15 ------------------------------------------------------------------------------------

    def test_s3_ek15_a_kartya_tartalma_es_a_szoveg_escape_elese(self):
        """EK-15: küldő, címzett, egység, chip, kategóriacsík, 🌐, szöveg betű szerint, taps, pontos idő."""
        parbeszedek = []
        self.oldal.on("dialog", lambda d: (parbeszedek.append(d.message), d.dismiss()))
        szoveg = "Szuper! <script>alert(1)</script> 🎉"
        ketOraja = (datetime.now() - timedelta(hours=2)).replace(microsecond=0)
        azonosito = self.beszur("u05", "u09", "experiment", szoveg, "nyilvanos", ketOraja)
        self.beszur_taps(azonosito, "u06")

        self.sajat("Farkas Júlia")
        kartya = self.kartyak().first
        expect(kartya).to_contain_text("Horváth Anna")
        expect(kartya).to_contain_text("Fejlesztési Osztály")
        expect(kartya).to_contain_text("Farkas Júlia")
        expect(kartya).to_contain_text("Adat Osztály")
        expect(kartya).to_contain_text("🧪 Experiment, learn fast!")
        expect(kartya.get_by_role("img", name="Nyilvános")).to_be_visible()
        expect(kartya).to_contain_text(szoveg)
        expect(kartya.locator("script")).to_have_count(0)
        expect(kartya).to_contain_text("👏 1")
        self.assertEqual(
            kartya.evaluate("e => getComputedStyle(e).borderLeftColor"), "rgb(157, 136, 217)")  # --cat-otlet

        ido = kartya.locator("time")
        expect(ido).to_have_text("2 órája")
        expect(ido).to_have_attribute("datetime", ketOraja.isoformat(timespec="seconds"))
        cim = ido.get_attribute("title")
        self.assertIn(str(ketOraja.year), cim)
        self.assertIn(f"{ketOraja.minute:02d}:{ketOraja.second:02d}", cim)
        self.assertEqual(parbeszedek, [])

    # --- EK-16 ------------------------------------------------------------------------------------

    def test_s3_ek16_a_legujabb_kartya_van_elol(self):
        """EK-16: Kiss Réka (12:00), Varga Bence (11:00), Horváth Anna (10:00) sorrendben."""
        tegnap = datetime.combine(datetime.now().date() - timedelta(days=1), datetime.min.time())
        self.beszur("u05", "u09", letrehozva=tegnap.replace(hour=10))
        self.beszur("u06", "u09", letrehozva=tegnap.replace(hour=11))
        self.beszur("u07", "u09", letrehozva=tegnap.replace(hour=12))
        self.sajat("Farkas Júlia")
        expect(self.kartyak()).to_have_count(3)
        szovegek = [t.replace("\n", " ") for t in self.kartyak().all_inner_texts()]
        self.assertIn("Kiss Réka", szovegek[0])
        self.assertIn("Varga Bence", szovegek[1])
        self.assertIn("Horváth Anna", szovegek[2])

    # --- EK-17 ------------------------------------------------------------------------------------

    def test_s3_ek17_szabad_szavas_kereses(self):
        """EK-17: „DASHBOARD” → Varga Bence, „horváth” → Horváth Anna, „nincsilyen” → üres állapot."""
        self.beszur("u05", "u09", uzenet="Köszi a riportot!", letrehozva=datetime.now() - timedelta(hours=3))
        self.beszur("u06", "u09", uzenet="Remek dashboard 💛", letrehozva=datetime.now() - timedelta(hours=2))
        self.sajat("Farkas Júlia")
        expect(self.kartyak()).to_have_count(2)

        self.kereso().fill("DASHBOARD")
        expect(self.kartyak()).to_have_count(1)
        expect(self.kartyak().first).to_contain_text("Varga Bence")

        self.kereso().fill("horváth")
        expect(self.kartyak()).to_have_count(1)
        expect(self.kartyak().first).to_contain_text("Horváth Anna")

        self.kereso().fill("nincsilyen")
        expect(self.kartyak()).to_have_count(0)
        expect(self.oldal.get_by_text("Nincs találat")).to_be_visible()
        expect(self.ful("Kapott (2)")).to_be_visible()

        self.kereso().fill("")
        expect(self.kartyak()).to_have_count(2)

    # --- EK-18 ------------------------------------------------------------------------------------

    def test_s3_ek18_kategoriaszuro_a_sajat_nezetben(self):
        """EK-18: a „🧪 Experiment, learn fast!” szűrővel csak a 🧪 köszönet, a „Minden kategória”-val mindkettő."""
        self.beszur("u05", "u06", "together", "Együtt", letrehozva=datetime.now() - timedelta(hours=2))
        self.beszur("u05", "u09", "experiment", "Kísérlet", letrehozva=datetime.now() - timedelta(hours=1))
        self.sajat("Horváth Anna", "Küldött")
        expect(self.kartyak()).to_have_count(2)

        self.kategoria_szuro().select_option(label="🧪 Experiment, learn fast!")
        expect(self.kartyak()).to_have_count(1)
        expect(self.kartyak().first).to_contain_text("Kísérlet")
        expect(self.ful("Küldött (2)")).to_be_visible()

        self.kategoria_szuro().select_option(label="Minden kategória")
        expect(self.kartyak()).to_have_count(2)

    # --- EK-19 ------------------------------------------------------------------------------------

    def test_s3_ek19_idoszakszuro(self):
        """EK-19: 2, 10 és 40 napja kapott köszönet → Elmúlt 7 nap: 1, Elmúlt 30 nap: 2, Összes: 3."""
        most = datetime.now()
        for nap in (2, 10, 40):
            self.beszur("u05", "u09", letrehozva=most - timedelta(days=nap))
        self.sajat("Farkas Júlia")
        expect(self.idoszak_szuro()).to_have_value("osszes")
        expect(self.kartyak()).to_have_count(3)

        self.idoszak_szuro().select_option(label="Elmúlt 7 nap")
        expect(self.kartyak()).to_have_count(1)
        self.idoszak_szuro().select_option(label="Elmúlt 30 nap")
        expect(self.kartyak()).to_have_count(2)
        self.idoszak_szuro().select_option(label="Összes")
        expect(self.kartyak()).to_have_count(3)
        expect(self.ful("Kapott (3)")).to_be_visible()

    # --- EK-20 ------------------------------------------------------------------------------------

    def test_s3_ek20_ures_allapot_uj_koszonet_gombbal(self):
        """EK-20: Varga Bence üres Kapott listáján emoji, mondat és [+ Új köszönet] gomb van, ami a varázslóba visz."""
        self.sajat("Varga Bence")
        expect(self.oldal.get_by_text("Még nem kaptál köszönetet. Te már küldtél ma valakinek?")).to_be_visible()
        gomb = self.oldal.get_by_role("link", name="+ Új köszönet")
        expect(gomb).to_be_visible()
        gomb.click()
        expect(self.oldal.get_by_role("heading", name="Kinek?")).to_be_visible()


if __name__ == "__main__":
    unittest.main()
