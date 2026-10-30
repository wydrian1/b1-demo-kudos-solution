# Kudos – dokumentáció

Az elfogadott változat (SPEC 1.1, `BIZONYITEK.md`: `Elfogadás: ELFOGADVA`) dokumentációja.

| Dokumentum | Kinek | Miről szól |
|---|---|---|
| [felhasznaloi-utmutato.md](felhasznaloi-utmutato.md) | munkatársaknak és vezetőknek | Belépés, köszönet küldése képernyőképekkel, saját lista, közös fal, értesítések, vezetői nézet, „ki mit lát” táblázat, szabályok, GYIK. |
| [technikai-leiras.md](technikai-leiras.md) | fejlesztőknek, üzemeltetőknek | Architektúra, adatmodell, HTTP végpontok, jogosultsági logika, futtatás és tesztek, biztonság, ismert korlátok. |
| [nyomonkovethetoseg.md](nyomonkovethetoseg.md) | auditálóknak, elfogadóknak | Mind a 47 EK: story, teszt(ek), megvalósító kód, eredmény; összesítés. |
| [kepek/](kepek/) | – | A felhasználói útmutató 11 képernyőképe. |
| [kepek_keszitese.py](kepek_keszitese.py) | fejlesztőknek | A képeket előállító szkript: `.venv/bin/python dokumentacio/kepek_keszitese.py` (ideiglenes adatbázis, a `kudos.db`-hez nem nyúl). |

A dokumentumok csak azt írják le, ami a kódban megvan, és amit a `BIZONYITEK.md` elfogadott. A forrás a `SPEC.md`,
a `BIZONYITEK.md` és a kód.
