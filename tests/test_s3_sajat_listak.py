"""S3 – Saját köszöneteim (EK-14…EK-21): a Kapott és Küldött lista logikája és API-ja, böngésző nélkül."""
import sys
import unittest
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from segedek import ADATOK, SzerverTeszt  # noqa: E402


class SajatListaTeszt(SzerverTeszt):
    def lekerdez(self, kliens, irany, **szuro):
        lekerdezes = urllib.parse.urlencode(szuro)
        return kliens.get(f"/api/koszonetek/{irany}" + ("?" + lekerdezes if lekerdezes else ""))

    def lista(self, kliens, irany, **szuro):
        allapot, tartalom = self.lekerdez(kliens, irany, **szuro)
        self.assertEqual(allapot, 200)
        return tartalom["koszonetek"]

    def uzenetek(self, kliens, irany, **szuro):
        return [k["uzenet"] for k in self.lista(kliens, irany, **szuro)]


class TestEK14Megjelenes(SajatListaTeszt):
    def test_ek14_a_koszonet_a_kuldo_kuldott_es_a_cimzett_kapott_listajaban_van(self):
        """EK-14 (SZ-08, SZ-15): Anna → Júlia privát köszönet; Varga Bence listái üresek."""
        anna = self.belep("u05")
        allapot, valasz = anna.post("/api/koszonetek", {
            "cimzett_id": "u09", "kategoria": "together", "uzenet": "Köszi", "lathatosag": "privat"})
        self.assertEqual(allapot, 201)
        azonosito = valasz["id"]

        allapot, kuldott = self.lekerdez(anna, "kuldott")
        self.assertEqual(allapot, 200)
        self.assertEqual([k["id"] for k in kuldott["koszonetek"]], [azonosito])
        self.assertEqual(kuldott["darab"], {"kapott": 0, "kuldott": 1})
        self.assertEqual(self.lista(anna, "kapott"), [])

        julia = self.belep("u09")
        allapot, kapott = self.lekerdez(julia, "kapott")
        self.assertEqual([k["id"] for k in kapott["koszonetek"]], [azonosito])
        self.assertEqual(kapott["darab"], {"kapott": 1, "kuldott": 0})

        varga = self.belep("u06")
        for irany in ("kapott", "kuldott"):
            allapot, tartalom = self.lekerdez(varga, irany)
            self.assertEqual(tartalom["koszonetek"], [])
            self.assertEqual(tartalom["darab"], {"kapott": 0, "kuldott": 0})

    def test_ek14_csak_a_sajat_koszonetek_szerepelnek_a_listakban(self):
        """EK-14: Kiss Réka listáiban nincs ott a köszönet, amit más küldött egymásnak."""
        self.beszur("u05", "u09")
        reka = self.belep("u07")
        self.assertEqual(self.lista(reka, "kapott"), [])
        self.assertEqual(self.lista(reka, "kuldott"), [])

    def test_ek14_belepes_nelkul_401(self):
        """EK-14 (SZ-01): a listák csak bejelentkezve érhetők el."""
        for irany in ("kapott", "kuldott"):
            self.assertEqual(self.lekerdez(self.kliens(), irany)[0], 401)


class TestEK15Kartya(SajatListaTeszt):
    def test_ek15_a_kartya_adatai(self):
        """EK-15 (SZ-16): küldő, címzett, egység, kategória, szöveg változatlanul, láthatóság, taps, idő."""
        szoveg = "Szuper! <script>alert(1)</script> 🎉"
        ketOraja = datetime.now() - timedelta(hours=2)
        azonosito = self.beszur("u05", "u09", "experiment", szoveg, "nyilvanos", ketOraja)
        self.beszur_taps(azonosito, "u06")

        julia = self.belep("u09")
        kartya = self.lista(julia, "kapott")[0]
        self.assertEqual(kartya["id"], azonosito)
        self.assertEqual((kartya["kuldo"]["nev"], kartya["kuldo"]["egyseg"]),
                         ("Horváth Anna", "Fejlesztési Osztály"))
        self.assertEqual((kartya["cimzett"]["nev"], kartya["cimzett"]["egyseg"]),
                         ("Farkas Júlia", "Adat Osztály"))
        self.assertEqual(kartya["kategoria"], "experiment")
        self.assertEqual(kartya["uzenet"], szoveg)
        self.assertEqual(kartya["lathatosag"], "nyilvanos")
        self.assertEqual(kartya["tapsok"], 1)
        self.assertEqual(kartya["letrehozva"], ketOraja.isoformat(timespec="seconds"))


class TestEK16Rendezes(SajatListaTeszt):
    def test_ek16_a_legujabb_van_elol(self):
        """EK-16 (SZ-15): Kiss Réka 12:00, Varga Bence 11:00, Horváth Anna 10:00."""
        tegnap = datetime.combine(datetime.now().date() - timedelta(days=1), datetime.min.time())
        self.beszur("u05", "u09", uzenet="Anna", letrehozva=tegnap.replace(hour=10))
        self.beszur("u06", "u09", uzenet="Bence", letrehozva=tegnap.replace(hour=11))
        self.beszur("u07", "u09", uzenet="Réka", letrehozva=tegnap.replace(hour=12))
        self.assertEqual(self.uzenetek(self.belep("u09"), "kapott"), ["Réka", "Bence", "Anna"])

    def test_ek16_azonos_idopontnal_a_nagyobb_azonosito_elol(self):
        """EK-16 (SZ-15): holtverseny esetén a később létrejött előbb."""
        ido = datetime.now() - timedelta(days=1)
        self.beszur("u05", "u09", uzenet="elso", letrehozva=ido)
        self.beszur("u06", "u09", uzenet="masodik", letrehozva=ido)
        self.assertEqual(self.uzenetek(self.belep("u09"), "kapott"), ["masodik", "elso"])


class TestEK17Kereses(SajatListaTeszt):
    def setUp(self):
        super().setUp()
        self.beszur("u05", "u09", uzenet="Köszi a riportot!", letrehozva=datetime.now() - timedelta(hours=3))
        self.beszur("u06", "u09", uzenet="Remek dashboard 💛", letrehozva=datetime.now() - timedelta(hours=2))
        self.julia = self.belep("u09")

    def test_ek17_az_uzenet_szovegeben_kis_es_nagybetutol_fuggetlenul(self):
        """EK-17 (SZ-15): „DASHBOARD” → csak Varga Bence köszönete."""
        self.assertEqual(self.uzenetek(self.julia, "kapott", q="DASHBOARD"), ["Remek dashboard 💛"])

    def test_ek17_a_kuldo_nevere_is_keres(self):
        """EK-17 (SZ-15): „horváth” → csak Horváth Anna köszönete (ékezetes, kisbetűs keresés)."""
        self.assertEqual(self.uzenetek(self.julia, "kapott", q="horváth"), ["Köszi a riportot!"])
        self.assertEqual(self.uzenetek(self.julia, "kapott", q="HORVÁTH"), ["Köszi a riportot!"])

    def test_ek17_nincs_talalat_es_a_darabszam_nem_valtozik(self):
        """EK-17 (SZ-15): „nincsilyen” → üres lista, de a fül száma továbbra is 2."""
        allapot, tartalom = self.lekerdez(self.julia, "kapott", q="nincsilyen")
        self.assertEqual(allapot, 200)
        self.assertEqual(tartalom["koszonetek"], [])
        self.assertEqual(tartalom["darab"]["kapott"], 2)

    def test_ek17_a_kuldott_listaban_a_cimzett_nevere_keres(self):
        """EK-17 (SZ-15): Annánál „farkas” → a Júliának küldött köszönet; üres keresőszó mindent mutat."""
        anna = self.belep("u05")
        self.assertEqual(self.uzenetek(anna, "kuldott", q="farkas"), ["Köszi a riportot!"])
        self.assertEqual(self.uzenetek(anna, "kuldott", q="   "), ["Köszi a riportot!"])
        self.assertEqual(self.uzenetek(anna, "kuldott", q="balogh"), [])


class TestEK18Kategoriaszuro(SajatListaTeszt):
    def test_ek18_kategoriara_szur_az_osszes_kategoria_mindent_mutat(self):
        """EK-18 (SZ-15): 🤝 és 🧪 köszönet; a 🧪 szűrő csak a másodikat adja."""
        ido = datetime.now() - timedelta(hours=1)
        self.beszur("u05", "u09", "together", "Együtt", letrehozva=ido - timedelta(minutes=5))
        self.beszur("u05", "u06", "experiment", "Kísérlet", letrehozva=ido)
        anna = self.belep("u05")
        self.assertEqual(self.uzenetek(anna, "kuldott", kategoria="experiment"), ["Kísérlet"])
        self.assertEqual(self.uzenetek(anna, "kuldott", kategoria=""), ["Kísérlet", "Együtt"])
        self.assertEqual(self.uzenetek(anna, "kuldott", kategoria="loyalty"), [])

    def test_ek18_ismeretlen_kategoria_400(self):
        """EK-18 (SZ-06): a szűrőben sem fogadunk el ismeretlen kategóriát."""
        allapot, tartalom = self.lekerdez(self.belep("u05"), "kuldott", kategoria="pizza")
        self.assertEqual((allapot, tartalom["mezo"]), (400, "kategoria"))

    def test_ek18_a_szurok_egyutt_is_mukodnek(self):
        """EK-18 (SZ-15): kategória ÉS szöveg együtt."""
        self.beszur("u05", "u09", "together", "alfa", letrehozva=datetime.now() - timedelta(hours=2))
        self.beszur("u05", "u06", "together", "béta", letrehozva=datetime.now() - timedelta(hours=1))
        self.beszur("u05", "u07", "experiment", "alfa", letrehozva=datetime.now() - timedelta(minutes=30))
        anna = self.belep("u05")
        talalatok = self.lista(anna, "kuldott", kategoria="together", q="alfa")
        self.assertEqual([(k["cimzett"]["id"], k["uzenet"]) for k in talalatok], [("u09", "alfa")])


class TestEK19Idoszakszuro(SajatListaTeszt):
    def test_ek19_7_30_nap_es_osszes(self):
        """EK-19 (SZ-15): 2, 10 és 40 napja kapott köszönet → 1 / 2 / 3; az alapértelmezés az „összes”."""
        most = datetime.now()
        for nap in (2, 10, 40):
            self.beszur("u05", "u09", uzenet=f"{nap} napos", letrehozva=most - timedelta(days=nap))
        julia = self.belep("u09")
        self.assertEqual(self.uzenetek(julia, "kapott", idoszak="7"), ["2 napos"])
        self.assertEqual(self.uzenetek(julia, "kapott", idoszak="30"), ["2 napos", "10 napos"])
        self.assertEqual(len(self.lista(julia, "kapott", idoszak="osszes")), 3)
        self.assertEqual(len(self.lista(julia, "kapott")), 3)

    def test_ek19_ismeretlen_idoszak_400(self):
        """EK-19: csak a 7, 30 és osszes értékek érvényesek."""
        allapot, tartalom = self.lekerdez(self.belep("u09"), "kapott", idoszak="5")
        self.assertEqual((allapot, tartalom["mezo"]), (400, "idoszak"))

    def test_ek19_a_hatar_pontosan_7x24_ora(self):
        """EK-19 (SZ-15): a szolgáltatás a megadott „most” időponthoz képest számol."""
        from kudos import adatbazis, koszonetek
        from kudos.szervezet import Szervezet

        most = datetime(2026, 10, 30, 12, 0, 0)
        self.beszur("u05", "u09", uzenet="pont 7 napja", letrehozva=most - timedelta(days=7))
        self.beszur("u06", "u09", uzenet="egy másodperccel korábban",
                    letrehozva=most - timedelta(days=7, seconds=1))
        kapcsolat = adatbazis.kapcsolat(self.adatbazis)
        try:
            talalatok = koszonetek.sajat(kapcsolat, Szervezet.betolt(ADATOK), "u09", "kapott",
                                         idoszak="7", most=most)
        finally:
            kapcsolat.close()
        self.assertEqual([k["uzenet"] for k in talalatok], ["pont 7 napja"])


class TestEK20UresAllapot(SajatListaTeszt):
    def test_ek20_ures_adatbazisnal_mindket_lista_ures(self):
        """EK-20: Varga Bence még semmit sem kapott és küldött."""
        varga = self.belep("u06")
        for irany in ("kapott", "kuldott"):
            allapot, tartalom = self.lekerdez(varga, irany)
            self.assertEqual((allapot, tartalom["koszonetek"]), (200, []))


class TestEK21KuldesUtan(SajatListaTeszt):
    def test_ek21_az_uj_koszonet_a_kuldott_lista_elso_eleme(self):
        """EK-21 (SZ-08): küldés után az újonnan elküldött köszönet van legelöl."""
        anna = self.belep("u05")
        elso = anna.post("/api/koszonetek", {"cimzett_id": "u06", "kategoria": "forward", "uzenet": "Első"})[1]
        masodik = anna.post("/api/koszonetek", {"cimzett_id": "u09", "kategoria": "forward", "uzenet": "Második"})[1]
        self.assertEqual([k["id"] for k in self.lista(anna, "kuldott")], [masodik["id"], elso["id"]])


if __name__ == "__main__":
    unittest.main()
