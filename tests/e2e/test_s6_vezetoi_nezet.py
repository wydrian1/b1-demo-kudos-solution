"""S6 – Vezetői nézet, böngészőben (EK-36…EK-41).

„Kész, ha…”: Szabó Katalin a Csapat nézetben látja az Adat Osztályhoz kapcsolódó (privát) köszönetekeket, a
Fejlesztési Osztály belsőit nem. Horváth Annának nincs Csapat menüpontja.

Adatkészlet (privát, az üzenet szövege a jele): M1 Anna→Júlia · M2 Júlia→Balogh Máté · M3 Anna→Varga Bence ·
M4 Nóra→Simon Bálint (nyilvános) · M5 Nagy Péter→Szabó Katalin · M6 Papp Zsófia→Júlia (40 napja) ·
M7 Szabó Katalin→Nóra.
"""
import re
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from playwright.sync_api import expect

sys.path.insert(0, str(Path(__file__).resolve().parent))
from alap import E2ETeszt  # noqa: E402

VEZETOI_UZENET = "Ehhez a nézethez vezetői jogosultság kell."


class TestS6(E2ETeszt):
    def adatok(self, m6=False, m7=False):
        most = datetime.now()
        self.beszur("u05", "u09", "together", "M1", "privat", most - timedelta(days=1))
        self.beszur("u09", "u10", "experiment", "M2", "privat", most - timedelta(days=2))
        self.beszur("u05", "u06", "loyalty", "M3", "privat", most - timedelta(days=3))
        self.beszur("u13", "u16", "loyalty", "M4", "nyilvanos", most - timedelta(days=4))
        self.beszur("u02", "u03", "forward", "M5", "privat", most - timedelta(days=5))
        if m7:
            self.beszur("u03", "u13", "together", "M7", "privat", most - timedelta(days=6))
        if m6:
            self.beszur("u11", "u09", "experiment", "M6", "privat", most - timedelta(days=40))

    def fo_menu(self):
        return self.oldal.get_by_role("navigation", name="Főmenü")

    def kartyak(self):
        return self.oldal.get_by_role("article")

    def csapat(self, nev, elso=False):
        """Belépés (vagy váltás), majd a Csapat oldal megnyitása a menüből."""
        if elso:
            self.belep(nev)
        else:
            self.valt(nev)
        self.fo_menu().get_by_role("link", name="Csapat", exact=True).click()
        expect(self.oldal.get_by_role("heading", name="Csapatköszönetek")).to_be_visible()

    def jelek(self):
        """A látható kártyák üzenet-jelei (M1, M2, …) a megjelenés sorrendjében."""
        self.oldal.wait_for_load_state()
        return re.findall(r"„(M\d)”", " ".join(t.replace("\n", " ") for t in self.kartyak().all_inner_texts()))

    def varhato(self, *jelek):
        """Megvárja, amíg a lista pontosan a megadott kártyákat mutatja."""
        expect(self.kartyak()).to_have_count(len(jelek))
        self.assertEqual(self.jelek(), list(jelek))

    def kategoria_szuro(self):
        return self.oldal.get_by_label("Kategória", exact=True)

    def idoszak_szuro(self):
        return self.oldal.get_by_label("Időszak", exact=True)

    def kereso(self):
        return self.oldal.get_by_label("Keresés a köszönetekben")

    # --- EK-36 ------------------------------------------------------------------------------------

    def test_s6_ek36_nem_vezeto_nem_ereti_el_a_csapat_nezetet(self):
        """EK-36: Annának nincs Csapat menüpontja, a címet megnyitva üzenetet kap, az API 403; Katalinnak van menüpontja."""
        self.adatok()
        self.belep("Horváth Anna")
        expect(self.fo_menu().get_by_role("link", name="Saját", exact=True)).to_be_visible()
        expect(self.fo_menu().get_by_role("link", name="Csapat")).to_have_count(0)

        self.oldal.goto(self.cim("/#/csapat"))
        expect(self.oldal.get_by_text(VEZETOI_UZENET)).to_be_visible()
        expect(self.kartyak()).to_have_count(0)
        self.assertEqual(self.oldal.request.get(self.cim("/api/csapat")).status, 403)
        self.assertEqual(self.oldal.request.get(self.cim("/api/csapat/statisztika")).status, 403)

        self.valt("Szabó Katalin")
        expect(self.fo_menu().get_by_role("link", name="Csapat", exact=True)).to_be_visible()

    # --- EK-37, EK-38, EK-41 ------------------------------------------------------------------------

    def test_s6_ek37_katalin_az_adat_osztaly_koszonetet_latja_a_fejlesztesi_osztaly_beloleit_nem(self):
        """EK-37: Szabó Katalin → M1, M2, M5 (privátok is); az M3 és a nyilvános M4 nem."""
        self.adatok()
        self.csapat("Szabó Katalin", elso=True)
        self.varhato("M1", "M2", "M5")
        expect(self.oldal.get_by_text("„M3”")).to_have_count(0)
        expect(self.oldal.get_by_text("„M4”")).to_have_count(0)
        # a privát köszönetek ikonja is látszik: a vezető a privátot is látja
        expect(self.kartyak().first.get_by_role("img", name="Privát")).to_be_visible()

    def test_s6_ek38_foosztalyvezeto_board_tag_es_a_masik_osztalyvezetok(self):
        """EK-38: Eszter és László mind az 5-öt; Nagy Péter M1, M3, M5; Tóth Gábor csak M4."""
        self.adatok()
        self.csapat("Kovács Eszter", elso=True)
        self.varhato("M1", "M2", "M3", "M4", "M5")
        self.csapat("Fehér László")
        self.varhato("M1", "M2", "M3", "M4", "M5")
        self.csapat("Nagy Péter")
        self.varhato("M1", "M3", "M5")
        self.csapat("Tóth Gábor")
        self.varhato("M4")

    def test_s6_ek41_a_vezeto_maga_is_a_koreben_van(self):
        """EK-41: Katalin → M1, M2, M5, M7 (M7-nek ő a küldője); Tóth Gábor → M4 és M7."""
        self.adatok(m7=True)
        self.csapat("Szabó Katalin", elso=True)
        self.varhato("M1", "M2", "M5", "M7")
        self.csapat("Tóth Gábor")
        self.varhato("M4", "M7")

    # --- EK-39 ------------------------------------------------------------------------------------

    def test_s6_ek39_mas_kor_adata_kozvetlen_keressel_sem_erheto_el(self):
        """EK-39: extra paraméterekkel is Katalin köre jön vissza; az M3-ra tapsolni nem lehet (404)."""
        self.adatok()
        self.belep("Szabó Katalin")
        alap = [k["uzenet"] for k in self.oldal.request.get(self.cim("/api/csapat")).json()]
        self.assertEqual(alap, ["M1", "M2", "M5"])
        for extra in ("?vezeto_id=u01", "?egyseg=Fejleszt%C3%A9si%20Oszt%C3%A1ly", "?vezeto_id=u01&kuldo_id=u05"):
            valasz = self.oldal.request.get(self.cim("/api/csapat" + extra))
            self.assertEqual(valasz.status, 200)
            self.assertEqual([k["uzenet"] for k in valasz.json()], alap, extra)
        m3 = next(s["id"] for s in self.sorok() if s["uzenet"] == "M3")
        self.assertEqual(self.oldal.request.post(self.cim(f"/api/koszonetek/{m3}/taps")).status, 404)
        self.assertEqual(self.sorok("taps"), [])

    # --- EK-40 ------------------------------------------------------------------------------------

    def test_s6_ek40_kereses_es_szurok_a_vezetoi_nezetben(self):
        """EK-40: alapból 30 nap (M6 nincs); „júlia” → M1, M2; 🧪 → M2; Összes + 🧪 → M2, M6."""
        self.adatok(m6=True)
        self.csapat("Szabó Katalin", elso=True)
        expect(self.idoszak_szuro()).to_have_value("30")
        self.varhato("M1", "M2", "M5")

        self.kereso().fill("júlia")
        self.varhato("M1", "M2")

        self.kereso().fill("")
        self.varhato("M1", "M2", "M5")
        self.kategoria_szuro().select_option(label="🧪 Experiment, learn fast!")
        self.varhato("M2")

        self.idoszak_szuro().select_option(label="Összes")
        self.varhato("M2", "M6")

        self.kategoria_szuro().select_option(label="🚀 Take actions to move forward")
        self.varhato("M5")
        self.kategoria_szuro().select_option(label="💛 Earn customer loyalty")
        expect(self.kartyak()).to_have_count(0)
        expect(self.oldal.get_by_text("Nincs találat")).to_be_visible()


if __name__ == "__main__":
    unittest.main()
