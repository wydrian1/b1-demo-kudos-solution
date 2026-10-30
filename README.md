# Kudos – spec-driven demó Claude Code-dal

> **Ez a kész mintamegoldás.** A gyakorlás kiinduló repója: [wydrian1/b1-demo-kudos](https://github.com/wydrian1/b1-demo-kudos).
> Itt a teljes folyamat eredménye látható: `SPEC.md`, storyk (`HALADAS.md`), kód, unit és böngészős tesztek, `BIZONYITEK.md` és a `dokumentacio/` mappa.

Gyakorló feladat a B-1 vezetői AI-workshop délutáni részéhez.
Egy kis belső köszönetküldő alkalmazást, a **Kudos**-t, építünk **a saját gépen, WSL-ben**, Claude Code-dal.
Nem „vibe coding”: előbb **specifikáció**, utána **tesztek**, és csak ezután **kód**, két emberi jóváhagyási ponttal.

> Az alkalmazás csak helyben fut, kitalált adatokkal. Nincs AD, e-mail, szerver vagy deploy.
> A repót csak **letöltöd**, a munkád a saját gépeden marad. Ide **nem kell visszacommitolni** semmit.

**📘 Lépésről lépésre útmutató: [Kudos lab guide](https://wydrian1.github.io/b1training/lab/)**

## Előfeltételek

- WSL (Ubuntu), benne `python3` (3.10 vagy újabb) és `git`
- Claude Code, beállítva az RBI LLM gatewayre (pl. Sonnet 5.5 modellel)

Ellenőrzés:

```bash
python3 --version
claude --version
```

## Indulás

```bash
git clone https://github.com/wydrian1/b1-demo-kudos.git kudos
cd kudos
bash scripts/setup-e2e.sh
claude
```

A `setup-e2e.sh` egyszer kell: egy helyi `.venv`-be telepíti a böngészős tesztekhez a Playwrightot és a Chromiumot (internet és `sudo` kell hozzá, pár perc). Az alkalmazás kódja ettől függetlenül csak a Python standard libraryt használja.

Az első üzenet Claude-nak:

```text
/spec
```

Claude elolvassa az üzleti leírást (`docs/uzleti-leiras.md`), feltesz néhány tisztázó kérdést, és megírja a `SPEC.md`-t. **Kódot még nem ír.**

## A folyamat

| Lépés | Ki | Mi történik |
|---|---|---|
| 1. Specifikáció | Claude (`/spec`) | `SPEC.md` készül, státusz: `TERVEZET` |
| 2. **🟡 1. kapu** | **Te** | Átnézed a specet. Ha jó, **te magad** írod át a státuszt `JÓVÁHAGYVA`-ra |
| 3. Storyk | Claude (`/build S1`, `/build S2`, …) | Storynként: előbb a story tesztjei (pirosak), aztán az építés, amíg minden zöld. Minden story után megáll, és megmondja, mit nézz meg a böngészőben |
| 4. Bizonyíték | Claude (`/verify`) | `BIZONYITEK.md`: melyik kritériumot melyik teszt igazolja, mi az eredmény |
| 5. **🟡 2. kapu** | **Te** | Elolvasod a bizonyítékot, végigkattintod a kézi ellenőrzést (lab guide 2. kapu), és elfogadod vagy visszadobod. Ha elfogadod, **te magad** írod át a `BIZONYITEK.md`-ben az `Elfogadás` sort `ELFOGADVA`-ra |
| 6. Dokumentáció | Claude (`/docs`) | Az elfogadott változatról: felhasználói útmutató képernyőképekkel, technikai leírás, nyomonkövethetőségi mátrix a `dokumentacio/` mappába |

## Futtatás (ha már elkészült)

```bash
python3 app.py
```

Majd a böngészőben: http://localhost:8000

Tesztek:

```bash
python3 -m unittest discover -s tests -v
.venv/bin/python -m unittest discover -s tests/e2e -v
```

A második sor a böngészős (E2E) teszteket futtatja. Látható böngészőablakban:

```bash
HEADED=1 .venv/bin/python -m unittest discover -s tests/e2e -v
```

## Mi van a repóban?

| Fájl | Szerep |
|---|---|
| `CLAUDE.md` | Szabályok az ágensnek (technológia, folyamat, tilalmak) |
| `docs/uzleti-leiras.md` | Az egyszerűsített üzleti igény, **ebből** indul minden |
| `docs/arculat-ui.md` | A felület kötelező útmutatója: színek, komponensek, elrendezés |
| `templates/SPEC-sablon.md` | A specifikáció kötelező szerkezete |
| `scripts/setup-e2e.sh` | A böngészős tesztek eszközeinek telepítése (Playwright + Chromium) |
| `data/munkatarsak.json` | Kitalált munkatársak és szervezeti hierarchia (az AD helyett) |
| `.claude/skills/spec/` | `/spec`: specifikáció írása vagy módosítása |
| `.claude/skills/build/` | `/build S1`: egy story tesztjei és építése, utána megállás |
| `.claude/skills/verify/` | `/verify`: tesztek futtatása és bizonyíték-összefoglaló |
| `.claude/skills/docs/` | `/docs`: dokumentáció az elfogadott változatról |
