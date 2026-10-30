"""Alkalmazáson belüli értesítések (SZ-11, SZ-12)."""
ELONEZET_HOSSZ = 80


def cimzettek(szervezet, kuldo_id, cimzett_id):
    """Kik kapnak értesítést egy köszönetről: a címzett, a közvetlen vezetője és a B-1 vezetője.

    Egy személy legfeljebb egyszer szerepel, a küldő a saját köszönetéről nem kap értesítést. A board tag (B)
    csak akkor szerepel, ha ő a címzett közvetlen vezetője. A B-1 vezető a címzett feletti láncban lévő,
    B-1 szintű személy; B-1 vagy B szintű címzettnek nincs.
    """
    cimzett = szervezet.get(cimzett_id)
    jeloltek = [cimzett_id]
    if cimzett["vezeto_id"]:
        jeloltek.append(cimzett["vezeto_id"])
    if cimzett["szint"] not in ("B-1", "B"):
        b1 = next((m for m in szervezet.felettesek(cimzett_id) if szervezet.get(m)["szint"] == "B-1"), None)
        if b1:
            jeloltek.append(b1)
    ertesitendok = []
    for munkatars_id in jeloltek:
        if munkatars_id != kuldo_id and munkatars_id not in ertesitendok:
            ertesitendok.append(munkatars_id)
    return ertesitendok


def letrehoz(kapcsolat, szervezet, koszonet_id, kuldo_id, cimzett_id, most):
    """Létrehozza az értesítéseket; a köszönet mentésével egy tranzakcióban kell hívni (nem commitál)."""
    for munkatars_id in cimzettek(szervezet, kuldo_id, cimzett_id):
        kapcsolat.execute(
            "INSERT INTO ertesites (munkatars_id, koszonet_id, letrehozva) VALUES (?, ?, ?)",
            (munkatars_id, koszonet_id, most.isoformat(timespec="seconds")))


def _elonezet(uzenet):
    # Unicode-kódpontokat számolunk: az egyszerű emoji 1 karakter.
    return uzenet if len(uzenet) <= ELONEZET_HOSSZ else uzenet[:ELONEZET_HOSSZ] + "…"


def lista(kapcsolat, szervezet, felhasznalo_id):
    """A felhasználó értesítései, a legújabbal kezdve."""
    sorok = kapcsolat.execute(
        "SELECT e.id, e.olvasott, e.letrehozva, k.id AS koszonet_id, k.kuldo_id, k.cimzett_id, k.kategoria,"
        " k.uzenet, k.letrehozva AS koszonet_letrehozva"
        " FROM ertesites e JOIN koszonet k ON k.id = e.koszonet_id WHERE e.munkatars_id = ?"
        " ORDER BY e.letrehozva DESC, e.id DESC", (felhasznalo_id,)).fetchall()
    return [{
        "id": sor["id"],
        "koszonet_id": sor["koszonet_id"],
        "olvasott": bool(sor["olvasott"]),
        "kuldo": {"id": sor["kuldo_id"], "nev": szervezet.get(sor["kuldo_id"])["nev"]},
        "cimzett": {"id": sor["cimzett_id"], "nev": szervezet.get(sor["cimzett_id"])["nev"]},
        "kategoria": sor["kategoria"],
        "elonezet": _elonezet(sor["uzenet"]),
        "koszonet_letrehozva": sor["koszonet_letrehozva"],
        "letrehozva": sor["letrehozva"],
    } for sor in sorok]


def olvasottra_allit(kapcsolat, felhasznalo_id, ertesites_id):
    """Olvasottnak jelöl egy értesítést; csak a sajátját. Igaz, ha van ilyen saját értesítés."""
    kurzor = kapcsolat.execute(
        "UPDATE ertesites SET olvasott = 1 WHERE id = ? AND munkatars_id = ?", (ertesites_id, felhasznalo_id))
    kapcsolat.commit()
    return kurzor.rowcount > 0


def mind_olvasott(kapcsolat, felhasznalo_id):
    """A felhasználó összes értesítését olvasottnak jelöli; a módosított darabszámot adja vissza."""
    kurzor = kapcsolat.execute(
        "UPDATE ertesites SET olvasott = 1 WHERE munkatars_id = ? AND olvasott = 0", (felhasznalo_id,))
    kapcsolat.commit()
    return kurzor.rowcount
