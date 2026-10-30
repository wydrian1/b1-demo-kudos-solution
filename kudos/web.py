"""Webes réteg: `http.server` alapú JSON API és statikus fájlok. Az üzleti logika a többi modulban van."""
import json
import mimetypes
import re
from contextlib import closing
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from . import adatbazis, ertesitesek, koszonetek
from .szervezet import Szervezet

GYOKER = Path(__file__).resolve().parent.parent
SUTI_NEV = "kudos_user"
MAX_TORZS = 64 * 1024
# Belépés nélkül csak ezek érhetők el (SZ-01).
NYILVANOS_API = {("GET", "/api/munkatarsak"), ("POST", "/api/belepes")}


class Kezelo(BaseHTTPRequestHandler):
    server_version = "Kudos"

    def log_message(self, format, *args):
        if not self.server.csendes:
            super().log_message(format, *args)

    def do_GET(self):
        self._kezel("GET")

    def do_POST(self):
        self._kezel("POST")

    def _kezel(self, modszer):
        resz = urlsplit(self.path)
        utvonal = unquote(resz.path)
        self.lekerdezes = parse_qs(resz.query)
        if utvonal.startswith("/api/"):
            self._api(modszer, utvonal)
        elif modszer == "GET":
            self._statikus(utvonal)
        else:
            self._json(405, {"hiba": "A módszer nem engedélyezett."})

    # --- API -----------------------------------------------------------------------------

    def _api(self, modszer, utvonal):
        self.felhasznalo = self._bejelentkezett()
        if (modszer, utvonal) not in NYILVANOS_API and self.felhasznalo is None:
            return self._json(401, {"hiba": "Nincs bejelentkezve."})
        utvonalak = {
            ("GET", "/api/munkatarsak"): self._munkatarsak,
            ("POST", "/api/belepes"): self._belepes,
            ("POST", "/api/kilepes"): self._kilepes,
            ("GET", "/api/en"): self._en,
            ("GET", "/api/munkatarsak/kereses"): self._kereses,
            ("POST", "/api/koszonetek"): self._koszonet_kuldes,
            ("GET", "/api/koszonetek/kapott"): lambda: self._sajat("kapott"),
            ("GET", "/api/koszonetek/kuldott"): lambda: self._sajat("kuldott"),
            ("GET", "/api/fal"): self._fal,
            ("GET", "/api/ertesitesek"): self._ertesitesek,
            ("GET", "/api/csapat"): self._csapat,
            ("GET", "/api/csapat/statisztika"): self._csapat_statisztika,
            ("POST", "/api/ertesitesek/olvasott-mind"): self._mind_olvasott,
        }
        kezelo = utvonalak.get((modszer, utvonal))
        taps = re.fullmatch(r"/api/koszonetek/(\d+)/taps", utvonal)
        if kezelo is None and taps and modszer == "POST":
            kezelo = lambda: self._taps(int(taps.group(1)))  # noqa: E731
        olvasott = re.fullmatch(r"/api/ertesitesek/(\d+)/olvasott", utvonal)
        if kezelo is None and olvasott and modszer == "POST":
            kezelo = lambda: self._olvasott(int(olvasott.group(1)))  # noqa: E731
        if kezelo is None:
            return self._json(404, {"hiba": "Nincs ilyen végpont."})
        try:
            kezelo()
        except koszonetek.ValidaciosHiba as hiba:
            self._json(400, {"hiba": hiba.uzenet, "mezo": hiba.mezo})
        except koszonetek.NincsJogosultsag:
            self._json(403, {"hiba": "Ehhez vezetői jogosultság kell."})

    def _bejelentkezett(self):
        try:
            suti = cookies.SimpleCookie(self.headers.get("Cookie", ""))
        except cookies.CookieError:
            return None
        morzsa = suti.get(SUTI_NEV)
        return self.server.szervezet.get(morzsa.value) if morzsa else None

    def _torzs(self):
        hossz = int(self.headers.get("Content-Length") or 0)
        if hossz > MAX_TORZS:
            raise koszonetek.ValidaciosHiba(None, "A kérés túl nagy.")
        nyers = self.rfile.read(hossz) if hossz else b""
        if not nyers:
            return {}
        try:
            adat = json.loads(nyers)
        except ValueError:
            raise koszonetek.ValidaciosHiba(None, "Érvénytelen JSON.")
        if not isinstance(adat, dict):
            raise koszonetek.ValidaciosHiba(None, "A kérés törzse JSON-objektum legyen.")
        return adat

    def _munkatarsak(self):
        self._json(200, [
            {k: m[k] for k in ("id", "nev", "email", "egyseg", "beosztas", "szint")}
            for m in self.server.szervezet.minden()
        ])

    def _belepes(self):
        azonosito = self._torzs().get("id")
        munkatars = self.server.szervezet.get(azonosito) if isinstance(azonosito, str) else None
        if munkatars is None:
            return self._json(400, {"hiba": "Ismeretlen munkatárs.", "mezo": "id"})
        self._json(200, {"id": munkatars["id"]}, suti=f"{SUTI_NEV}={munkatars['id']}")

    def _kilepes(self):
        self._json(200, {}, suti=f"{SUTI_NEV}=; Max-Age=0")

    def _en(self):
        m = self.felhasznalo
        self._json(200, dict({k: m[k] for k in ("id", "nev", "egyseg", "beosztas")},
                             vezeto=self.server.szervezet.vezeto_e(m["id"])))

    def _kereses(self):
        szoveg = self.lekerdezes.get("q", [""])[0]
        talalatok = self.server.szervezet.kereses(szoveg, kiveve=self.felhasznalo["id"])
        self._json(200, [
            {k: m[k] for k in ("id", "nev", "beosztas", "egyseg")} for m in talalatok
        ])

    def _koszonet_kuldes(self):
        adat = self._torzs()
        szervezet = self.server.szervezet
        # A küldő mindig a bejelentkezett felhasználó, az időpontot a szerver rögzíti (SZ-16).
        with closing(adatbazis.kapcsolat(self.server.adatbazis)) as kapcs:
            azonosito = koszonetek.kuldes(
                kapcs, szervezet, self.felhasznalo["id"], adat.get("cimzett_id"),
                adat.get("kategoria"), adat.get("uzenet"), adat.get("lathatosag", "privat"),
            )
            self._json(201, koszonetek.lekeres(kapcs, szervezet, azonosito, self.felhasznalo["id"]))

    def _sajat(self, irany):
        """Kapott vagy küldött köszönetek `?q=&kategoria=&idoszak=` szűrőkkel, és a fülek darabszáma."""
        parameter = {k: self.lekerdezes.get(k, [default])[0]
                     for k, default in (("q", ""), ("kategoria", ""), ("idoszak", "osszes"))}
        with closing(adatbazis.kapcsolat(self.server.adatbazis)) as kapcs:
            lista = koszonetek.sajat(kapcs, self.server.szervezet, self.felhasznalo["id"], irany, **parameter)
            self._json(200, {"koszonetek": lista,
                             "darab": koszonetek.darabok(kapcs, self.felhasznalo["id"])})

    def _fal(self):
        with closing(adatbazis.kapcsolat(self.server.adatbazis)) as kapcs:
            kategoria = self.lekerdezes.get("kategoria", [""])[0]
            self._json(200, koszonetek.fal(kapcs, self.server.szervezet, self.felhasznalo["id"], kategoria))

    def _csapat(self):
        """Csapatköszönetek `?q=&kategoria=&idoszak=` szűrőkkel; a kört a bejelentkezett vezetőből számoljuk."""
        parameter = {k: self.lekerdezes.get(k, [default])[0]
                     for k, default in (("q", ""), ("kategoria", ""), ("idoszak", "30"))}
        with closing(adatbazis.kapcsolat(self.server.adatbazis)) as kapcs:
            self._json(200, koszonetek.csapat(kapcs, self.server.szervezet, self.felhasznalo["id"], **parameter))

    def _csapat_statisztika(self):
        """A vezető körének statisztikája `?idoszak=` időszakra (alapértelmezés: 30 nap)."""
        idoszak = self.lekerdezes.get("idoszak", ["30"])[0]
        with closing(adatbazis.kapcsolat(self.server.adatbazis)) as kapcs:
            self._json(200, koszonetek.statisztika(
                kapcs, self.server.szervezet, self.felhasznalo["id"], idoszak))

    def _ertesitesek(self):
        with closing(adatbazis.kapcsolat(self.server.adatbazis)) as kapcs:
            self._json(200, ertesitesek.lista(kapcs, self.server.szervezet, self.felhasznalo["id"]))

    def _olvasott(self, ertesites_id):
        with closing(adatbazis.kapcsolat(self.server.adatbazis)) as kapcs:
            if ertesitesek.olvasottra_allit(kapcs, self.felhasznalo["id"], ertesites_id):
                self._json(200, {"olvasott": True})
            else:
                self._json(404, {"hiba": "Nincs ilyen értesítés."})

    def _mind_olvasott(self):
        with closing(adatbazis.kapcsolat(self.server.adatbazis)) as kapcs:
            self._json(200, {"olvasott": ertesitesek.mind_olvasott(kapcs, self.felhasznalo["id"])})

    def _taps(self, koszonet_id):
        with closing(adatbazis.kapcsolat(self.server.adatbazis)) as kapcs:
            try:
                self._json(200, koszonetek.taps_valtas(
                    kapcs, self.server.szervezet, self.felhasznalo["id"], koszonet_id))
            except koszonetek.NemLathato:
                self._json(404, {"hiba": "Nincs ilyen köszönet."})

    # --- Statikus fájlok -----------------------------------------------------------------

    def _statikus(self, utvonal):
        mappa = self.server.statikus.resolve()
        if utvonal == "/":
            fajl = mappa / "index.html"
        elif utvonal.startswith("/static/"):
            fajl = (mappa / utvonal[len("/static/"):]).resolve()
        else:
            return self._json(404, {"hiba": "Nem található."})
        if not fajl.is_relative_to(mappa) or not fajl.is_file():
            return self._json(404, {"hiba": "Nem található."})
        tipus = mimetypes.guess_type(fajl.name)[0] or "application/octet-stream"
        if tipus.startswith("text/") or tipus.endswith("javascript"):
            tipus += "; charset=utf-8"
        self._valasz(200, fajl.read_bytes(), tipus)

    # --- Válaszok ------------------------------------------------------------------------

    def _json(self, allapot, tartalom, suti=None):
        torzs = json.dumps(tartalom, ensure_ascii=False).encode("utf-8")
        self._valasz(allapot, torzs, "application/json; charset=utf-8", suti)

    def _valasz(self, allapot, torzs, tipus, suti=None):
        self.send_response(allapot)
        self.send_header("Content-Type", tipus)
        self.send_header("Content-Length", str(len(torzs)))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        if suti:
            self.send_header("Set-Cookie", f"{suti}; Path=/; HttpOnly; SameSite=Lax")
        self.end_headers()
        self.wfile.write(torzs)


def szerver_letrehoz(host, port, adatbazis_utvonal, csendes=False,
                     adat_utvonal=None, statikus_mappa=None):
    adatbazis.inicializal(adatbazis_utvonal)
    szerver = ThreadingHTTPServer((host, port), Kezelo)
    szerver.adatbazis = adatbazis_utvonal
    szerver.szervezet = Szervezet.betolt(adat_utvonal or GYOKER / "data" / "munkatarsak.json")
    szerver.statikus = Path(statikus_mappa or GYOKER / "static")
    szerver.csendes = csendes
    return szerver
