"""A munkatársak és a keresés. Az adatok a `data/munkatarsak.json` fájlból jönnek (csak olvassuk)."""
import json


class Szervezet:
    def __init__(self, munkatarsak):
        self._munkatarsak = list(munkatarsak)
        self._azonosito_szerint = {m["id"]: m for m in self._munkatarsak}
        self._beosztottak = {}
        for m in self._munkatarsak:
            if m["vezeto_id"]:
                self._beosztottak.setdefault(m["vezeto_id"], []).append(m["id"])

    @classmethod
    def betolt(cls, utvonal):
        with open(utvonal, encoding="utf-8") as fajl:
            return cls(json.load(fajl)["munkatarsak"])

    def minden(self):
        return list(self._munkatarsak)

    def get(self, munkatars_id):
        return self._azonosito_szerint.get(munkatars_id)

    def vezeto_e(self, munkatars_id):
        """Vezető az, akinek van legalább egy beosztottja."""
        return bool(self._beosztottak.get(munkatars_id))

    def kor(self, munkatars_id):
        """Szervezeti kör: maga a munkatárs és minden alatta lévő, bármilyen mélységben (SZ-02)."""
        kor, sor = {munkatars_id}, [munkatars_id]
        while sor:
            for beosztott in self._beosztottak.get(sor.pop(), []):
                if beosztott not in kor:
                    kor.add(beosztott)
                    sor.append(beosztott)
        return kor

    def felettesek(self, munkatars_id):
        """A munkatárs feletti vezetői lánc a legközelebbitől felfelé (közvetlen vezető, B-1, B)."""
        lanc, lathatott = [], {munkatars_id}
        vezeto_id = (self.get(munkatars_id) or {}).get("vezeto_id")
        while vezeto_id and vezeto_id not in lathatott and self.get(vezeto_id):
            lanc.append(vezeto_id)
            lathatott.add(vezeto_id)
            vezeto_id = self.get(vezeto_id)["vezeto_id"]
        return lanc

    def kereses(self, szoveg, kiveve=None):
        """Név, szervezeti egység vagy e-mail részszöveg szerint (kis- és nagybetűtől függetlenül).

        Üres keresőszóra nincs találat. A `kiveve` azonosítójú munkatárs nem szerepel az eredményben.
        """
        szoveg = (szoveg or "").strip().casefold()
        if not szoveg:
            return []
        return [
            m for m in self._munkatarsak
            if m["id"] != kiveve
            and any(szoveg in m[mezo].casefold() for mezo in ("nev", "egyseg", "email"))
        ]
