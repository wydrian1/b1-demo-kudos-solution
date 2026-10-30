"""Köszönetek: küldés és lekérdezés."""
import unicodedata
from collections import Counter
from datetime import datetime, timedelta

from . import ertesitesek

# Az IT-BSO négy Behavioral Anchorja (SPEC 4.2.). A sorrend a felületen is ez.
KATEGORIAK = ("loyalty", "forward", "together", "experiment")
LATHATOSAGOK = ("privat", "nyilvanos")


class ValidaciosHiba(Exception):
    def __init__(self, mezo, uzenet):
        super().__init__(uzenet)
        self.mezo = mezo
        self.uzenet = uzenet


MAX_HOSSZ = 500
NAPI_LIMIT = 3


def _ellenoriz(szervezet, kuldo_id, cimzett_id, kategoria, uzenet, lathatosag):
    """A bemenet szabályai (SZ-04, SZ-05, SZ-06, SZ-08). Visszaadja a levágott üzenetet."""
    if not isinstance(cimzett_id, str) or szervezet.get(cimzett_id) is None:
        raise ValidaciosHiba("cimzett", "A címzett nem létezik.")
    if cimzett_id == kuldo_id:
        raise ValidaciosHiba("cimzett", "Magadnak nem küldhetsz köszönetet.")
    if uzenet is not None and not isinstance(uzenet, str):
        raise ValidaciosHiba("uzenet", "Az üzenet szöveg legyen.")
    uzenet = (uzenet or "").strip()
    if not uzenet:
        raise ValidaciosHiba("uzenet", "Az üzenet nem lehet üres.")
    if len(uzenet) > MAX_HOSSZ:  # Unicode-kódpontok: egy egyszerű emoji 1 karakter
        raise ValidaciosHiba("uzenet", f"Az üzenet legfeljebb {MAX_HOSSZ} karakter lehet.")
    if kategoria is None or kategoria == "":
        raise ValidaciosHiba("kategoria", "Válassz kategóriát.")
    if kategoria not in KATEGORIAK:
        raise ValidaciosHiba("kategoria", "Ismeretlen kategória.")
    if lathatosag not in LATHATOSAGOK:
        raise ValidaciosHiba("lathatosag", "Ismeretlen láthatóság.")
    return uzenet


def kuldes(kapcsolat, szervezet, kuldo_id, cimzett_id, kategoria, uzenet,
           lathatosag="privat", most=None):
    """Elmenti a köszönetet, és visszaadja az azonosítóját. Az időpontot a szerver rögzíti."""
    uzenet = _ellenoriz(szervezet, kuldo_id, cimzett_id, kategoria, uzenet, lathatosag)
    most = most or datetime.now()
    # A napi limit (SZ-07) ellenőrzése és a mentés egy zárolt tranzakcióban, hogy két párhuzamos
    # kérés együtt se léphesse át a határt.
    kapcsolat.execute("BEGIN IMMEDIATE")
    try:
        aznapi = kapcsolat.execute(
            "SELECT COUNT(*) FROM koszonet WHERE kuldo_id = ? AND cimzett_id = ?"
            " AND substr(letrehozva, 1, 10) = ?",
            (kuldo_id, cimzett_id, most.date().isoformat()),
        ).fetchone()[0]
        if aznapi >= NAPI_LIMIT:
            raise ValidaciosHiba(
                "cimzett", f"Ugyanannak a munkatársnak ma már {NAPI_LIMIT} köszönetet küldtél.")
        kurzor = kapcsolat.execute(
            "INSERT INTO koszonet (kuldo_id, cimzett_id, kategoria, uzenet, lathatosag, letrehozva)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (kuldo_id, cimzett_id, kategoria, uzenet, lathatosag, most.isoformat(timespec="seconds")),
        )
        ertesitesek.letrehoz(kapcsolat, szervezet, kurzor.lastrowid, kuldo_id, cimzett_id, most)
        kapcsolat.commit()
    except BaseException:
        kapcsolat.rollback()
        raise
    return kurzor.lastrowid


def _szemely(szervezet, munkatars_id):
    m = szervezet.get(munkatars_id)
    return {"id": m["id"], "nev": m["nev"], "egyseg": m["egyseg"], "beosztas": m["beosztas"]}


def _kartyak(kapcsolat, szervezet, sorok, felhasznalo_id):
    """A köszönetek megjelenítési adatai (küldő, címzett, tapsok), a sorok sorrendjében.

    A `tapsolt` azt mutatja, hogy a `felhasznalo_id` munkatárs tapsolt-e már a köszönetre.
    """
    tapsok, sajat_tapsok = {}, set()
    if sorok:
        azonositok = [sor["id"] for sor in sorok]
        helyorzok = ",".join("?" * len(azonositok))
        for tap in kapcsolat.execute(
            f"SELECT koszonet_id, COUNT(*) AS db FROM taps WHERE koszonet_id IN ({helyorzok})"
            " GROUP BY koszonet_id", azonositok,
        ):
            tapsok[tap["koszonet_id"]] = tap["db"]
        for tap in kapcsolat.execute(
            f"SELECT koszonet_id FROM taps WHERE munkatars_id = ? AND koszonet_id IN ({helyorzok})",
            [felhasznalo_id, *azonositok],
        ):
            sajat_tapsok.add(tap["koszonet_id"])
    return [{
        "id": sor["id"],
        "kuldo": _szemely(szervezet, sor["kuldo_id"]),
        "cimzett": _szemely(szervezet, sor["cimzett_id"]),
        "kategoria": sor["kategoria"],
        "uzenet": sor["uzenet"],
        "lathatosag": sor["lathatosag"],
        "letrehozva": sor["letrehozva"],
        "tapsok": tapsok.get(sor["id"], 0),
        "tapsolt": sor["id"] in sajat_tapsok,
    } for sor in sorok]


def lekeres(kapcsolat, szervezet, koszonet_id, felhasznalo_id=None):
    sor = kapcsolat.execute("SELECT * FROM koszonet WHERE id = ?", (koszonet_id,)).fetchone()
    return _kartyak(kapcsolat, szervezet, [sor], felhasznalo_id)[0] if sor else None


def fal(kapcsolat, szervezet, felhasznalo_id, kategoria=""):
    """A nyilvános köszönetek (SZ-09), a legújabbal kezdve, kategóriára szűrhetően."""
    if kategoria and kategoria not in KATEGORIAK:
        raise ValidaciosHiba("kategoria", "Ismeretlen kategória.")
    feltetel, parameterek = "lathatosag = 'nyilvanos'", []
    if kategoria:
        feltetel += " AND kategoria = ?"
        parameterek.append(kategoria)
    sorok = kapcsolat.execute(
        f"SELECT * FROM koszonet WHERE {feltetel} ORDER BY letrehozva DESC, id DESC", parameterek
    ).fetchall()
    return _kartyak(kapcsolat, szervezet, sorok, felhasznalo_id)


def lathato(szervezet, felhasznalo_id, sor):
    """Láthatja-e a felhasználó a köszönetet (SZ-08)?

    Nyilvánosat mindenki; privátat a küldő, a címzett és azok (bármilyen mélységű) vezetői.
    """
    if sor["lathatosag"] == "nyilvanos" or felhasznalo_id in (sor["kuldo_id"], sor["cimzett_id"]):
        return True
    return (felhasznalo_id in szervezet.felettesek(sor["kuldo_id"])
            or felhasznalo_id in szervezet.felettesek(sor["cimzett_id"]))


class NemLathato(Exception):
    """A köszönet nem létezik, vagy a felhasználó nem láthatja (a kettőt nem különböztetjük meg)."""


def taps_valtas(kapcsolat, szervezet, felhasznalo_id, koszonet_id, most=None):
    """Tapsot ad vagy visszavon (SZ-10); egy személy egy köszönetre legfeljebb egy tapsot adhat."""
    most = most or datetime.now()
    kapcsolat.execute("BEGIN IMMEDIATE")  # a vizsgálat és a váltás egyben, párhuzamos kérésnél is
    try:
        sor = kapcsolat.execute("SELECT * FROM koszonet WHERE id = ?", (koszonet_id,)).fetchone()
        if sor is None or not lathato(szervezet, felhasznalo_id, sor):
            raise NemLathato()
        van = kapcsolat.execute(
            "SELECT 1 FROM taps WHERE koszonet_id = ? AND munkatars_id = ?", (koszonet_id, felhasznalo_id)
        ).fetchone()
        if van:
            kapcsolat.execute("DELETE FROM taps WHERE koszonet_id = ? AND munkatars_id = ?",
                              (koszonet_id, felhasznalo_id))
        else:
            kapcsolat.execute(
                "INSERT INTO taps (koszonet_id, munkatars_id, letrehozva) VALUES (?, ?, ?)",
                (koszonet_id, felhasznalo_id, most.isoformat(timespec="seconds")))
        darab = kapcsolat.execute("SELECT COUNT(*) FROM taps WHERE koszonet_id = ?", (koszonet_id,)).fetchone()[0]
        kapcsolat.commit()
    except BaseException:
        kapcsolat.rollback()
        raise
    return {"tapsolt": not van, "tapsok": darab}


# Az időszakszűrő értékei és a hozzájuk tartozó napok száma (SZ-15); `None` = nincs korlát.
IDOSZAKOK = {"7": 7, "30": 30, "osszes": None}
IRANYOK = {"kapott": "cimzett_id", "kuldott": "kuldo_id"}


def _szurt(kapcsolat, szervezet, felhasznalo_id, alap_feltetel, alap_parameterek, q, kategoria, idoszak, most):
    """Közös szűrés (SZ-15): kategória, időszak és szabad szavas keresés; a legújabbal kezdve.

    `q`: kis- és nagybetűtől függetlenül az üzenet szövegében, a küldő és a címzett nevében keres.
    A `felhasznalo_id` a nézőé: neki számolja a `tapsolt` jelzést.
    """
    if kategoria and kategoria not in KATEGORIAK:
        raise ValidaciosHiba("kategoria", "Ismeretlen kategória.")
    if idoszak not in IDOSZAKOK:
        raise ValidaciosHiba("idoszak", "Ismeretlen időszak.")
    feltetel, parameterek = alap_feltetel, list(alap_parameterek)
    if kategoria:
        feltetel += " AND kategoria = ?"
        parameterek.append(kategoria)
    napok = IDOSZAKOK[idoszak]
    if napok is not None:
        feltetel += " AND letrehozva >= ?"
        parameterek.append(((most or datetime.now()) - timedelta(days=napok)).isoformat(timespec="seconds"))
    sorok = kapcsolat.execute(
        f"SELECT * FROM koszonet WHERE {feltetel} ORDER BY letrehozva DESC, id DESC", parameterek
    ).fetchall()
    kartyak = _kartyak(kapcsolat, szervezet, sorok, felhasznalo_id)
    keresett = (q or "").strip().casefold()
    if keresett:
        kartyak = [
            k for k in kartyak
            if keresett in " ".join((k["uzenet"], k["kuldo"]["nev"], k["cimzett"]["nev"])).casefold()
        ]
    return kartyak


def sajat(kapcsolat, szervezet, felhasznalo_id, irany, q="", kategoria="", idoszak="osszes", most=None):
    """A felhasználó kapott vagy küldött köszönetei (SZ-15)."""
    return _szurt(kapcsolat, szervezet, felhasznalo_id, f"{IRANYOK[irany]} = ?", [felhasznalo_id],
                  q, kategoria, idoszak, most)


class NincsJogosultsag(Exception):
    """A felhasználó nem vezető, ezért nem érheti el a vezetői nézetet."""


def csapat(kapcsolat, szervezet, vezeto_id, q="", kategoria="", idoszak="30", most=None):
    """A vezető szervezeti köréhez kapcsolódó köszönetek (SZ-13): privátok és nyilvánosak is.

    Egy köszönet akkor tartozik ide, ha a küldője vagy a címzettje a vezető körében van (maga a vezető is).
    A kört mindig a bejelentkezett vezető azonosítójából számoljuk, a kérés nem választhat másikat.
    """
    if not szervezet.vezeto_e(vezeto_id):
        raise NincsJogosultsag()
    kor = sorted(szervezet.kor(vezeto_id))
    helyorzok = ",".join("?" * len(kor))
    return _szurt(kapcsolat, szervezet, vezeto_id,
                  f"(kuldo_id IN ({helyorzok}) OR cimzett_id IN ({helyorzok}))", kor + kor,
                  q, kategoria, idoszak, most)


def _abc_kulcs(nev):
    """Ábécé-rendezési kulcs: kis- és nagybetűtől, ékezettől függetlenül."""
    return unicodedata.normalize("NFD", nev).encode("ascii", "ignore").decode().casefold()


def statisztika(kapcsolat, szervezet, vezeto_id, idoszak="30", most=None):
    """A vezető szervezeti körének statisztikája a megadott időszakra (SZ-14).

    Kizárólag a Csapatköszönetek listában szereplő (SZ-13) köszönetekből számol, így más kör adata nem
    szivároghat bele. Az időszak a statisztikára is hat, a szöveg- és kategóriaszűrő nem.
    """
    kartyak = csapat(kapcsolat, szervezet, vezeto_id, idoszak=idoszak, most=most)
    kor = szervezet.kor(vezeto_id)
    kuldok = {k["kuldo"]["id"] for k in kartyak if k["kuldo"]["id"] in kor}
    kapottak = Counter(k["cimzett"]["id"] for k in kartyak if k["cimzett"]["id"] in kor)
    megoszlas = Counter(k["kategoria"] for k in kartyak)
    rangsor = sorted(kapottak.items(), key=lambda p: (
        -p[1], _abc_kulcs(szervezet.get(p[0])["nev"]), szervezet.get(p[0])["nev"]))
    return {
        "kapott": sum(kapottak.values()),
        "kuldott": sum(1 for k in kartyak if k["kuldo"]["id"] in kor),
        "aktiv_kuldok": len(kuldok),
        "osszes": len(kartyak),
        "kategoriak": [{"kategoria": kod, "darab": megoszlas.get(kod, 0)} for kod in KATEGORIAK],
        "top3": [{"id": mid, "nev": szervezet.get(mid)["nev"], "egyseg": szervezet.get(mid)["egyseg"],
                  "darab": darab} for mid, darab in rangsor[:3]],
    }


def darabok(kapcsolat, felhasznalo_id):
    """A kapott és a küldött köszönetek száma szűrés nélkül (a fülek felirata)."""
    return {
        irany: kapcsolat.execute(
            f"SELECT COUNT(*) FROM koszonet WHERE {mezo} = ?", (felhasznalo_id,)).fetchone()[0]
        for irany, mezo in IRANYOK.items()
    }
