# SPEC – Kudos

Státusz: JÓVÁHAGYVA
Verzió: 1.1
Utolsó módosítás: 2026-10-30

> A `Státusz` sort **csak az ember** állíthatja `JÓVÁHAGYVA`-ra (1. kapu). Amíg `TERVEZET`, kód nem készülhet.

## 1. Cél
A Kudos egy helyben futó demó-webalkalmazás. A munkatársak kategóriával ellátott köszönő üzenetet küldhetnek egymásnak, privát vagy nyilvános láthatósággal. A vezetők látják a szervezeti körükhöz kapcsolódó köszöneteket és azok statisztikáit. Így az elismerés látható, visszakereshető és mérhető lesz.

## 2. Hatókör

### 2.1. Benne van
- Szimulált belépés a munkatárslistából („Belépés mint…”), jól látható DEMO jelzéssel.
- Köszönet küldése 3 lépéses varázslóval: címzettkereső, kategória (az IT-BSO négy Behavioral Anchorja, lásd 2.3.), üzenet (emojival), láthatóság, ellenőrző nézet, visszaigazolás.
- Küldési szabályok: egy címzett, önmagának nem küldhető, nem lehet üres, legfeljebb 500 karakter, kötelező a kategória, ugyanannak a címzettnek naponta legfeljebb 3.
- Saját köszöneteim: Kapott és Küldött lista darabszámmal, kereséssel, kategória- és időszakszűrővel.
- Közös fal (kezdőoldal): csak a nyilvános köszönetek, kategóriaszűrővel.
- Reakció: 👏 taps, személyenként és köszönetenként legfeljebb egy, visszavonható.
- Alkalmazáson belüli értesítések (csengő, olvasatlan-számláló, olvasottnak jelölés), a címzettnek, a közvetlen vezetőjének és a B-1 vezetőjének.
- Vezetői nézet („Csapatköszönetek”) a szervezeti körre szűrve, kereséssel és szűrőkkel.
- Vezetői statisztika: küldött és kapott köszönetek száma, kategória-megoszlás, Top 3 címzett, aktív küldők.
- Felület a `docs/arculat-ui.md` szerint (Raiffeisen színek, kártyák, reszponzív elrendezés, billentyűzetes kezelés).

### 2.2. Kimarad
| Kimarad | Helyettesítés a demóban |
|---|---|
| Valódi Active Directory és SSO | `data/munkatarsak.json` és „Belépés mint…” |
| E-mail és Teams értesítés | alkalmazáson belüli értesítés (csengő ikon) |
| Képfeltöltés és vírusellenőrzés | – (csak szöveg és emoji) |
| Adminisztrátori szerepkör, moderáció, riportok | – |
| Megőrzési és archiválási szabályok | – (minden adat a helyi `kudos.db`-ben marad) |
| Szerveres üzemeltetés és deploy | csak helyi futtatás (`python3 app.py`, `localhost`) |
| Teljes WCAG-audit | az alapokra figyelünk: billentyűzetes használat, látható fókusz, kontraszt, `aria` címkék |
| Köszönet szerkesztése vagy törlése küldés után | – (az üzleti leírás nem kéri) |

### 2.3. Eltérés a forrásdokumentumoktól (1.1-ben új)
Változáskérés alapján a köszönet kategóriái **nem** az üzleti leírás 3.2. pontjában felsorolt 5 kategória, hanem az IT-BSO négy Behavioral Anchorja (a pontos lista a 4.2. pontban). A `docs/uzleti-leiras.md` és a `docs/arculat-ui.md` változatlan marad, ahol ellentmondanak, ez a spec az irányadó:

| Forrás | Ott ez áll | A specben |
|---|---|---|
| `docs/uzleti-leiras.md` 3.2. | 5 kategória: 🤝 Együttműködés, 🚀 Gyors segítség, 💡 Jó ötlet, 🎯 Ügyfélfókusz, ⭐ Kiemelkedő munka | 4 kategória: 💛 Earn customer loyalty, 🚀 Take actions to move forward, 🤝 Deliver value together, 🧪 Experiment, learn fast! |
| `docs/arculat-ui.md` 3.3. | kategória-választó „5 nagy kártyagombként” | 4 nagy kártyagomb |
| `docs/arculat-ui.md` 1. | 5 kategóriaszín-token (`--cat-…`) | a tokenek neve és értéke változatlan, a 4 kategória közülük 4-et használ (4.2. pont). A `--cat-kiemelkedo` a CSS-ben megmarad (EK-07), de kategóriához nem tartozik. |
## 3. Szereplők és jogosultságok

### 3.1. Szervezeti szintek
A szintet a `data/munkatarsak.json` `szint` mezője adja meg: `B` = board tag, `B-1` = főosztályvezető, `B-2` = osztályvezető, `null` = alkalmazott. A hierarchiát a `vezeto_id` mező írja le.

| Szint | Személy (a JSON-ból) |
|---|---|
| B | Fehér László (u00) |
| B-1 | Kovács Eszter (u01) |
| B-2 | Nagy Péter (u02, Fejlesztési Oszt.), Szabó Katalin (u03, Adat Oszt.), Tóth Gábor (u04, Üzemeltetési Oszt.) |
| alkalmazott | u05–u16 |

### 3.2. Fogalmak
- **Vezető:** akinek legalább egy beosztottja van (akinek az azonosítójára legalább egy munkatárs `vezeto_id`-ja mutat). A mostani adatokban: u00–u04.
- **Szervezeti kör** (a vezetőé): **maga a vezető**, és minden alatta lévő munkatárs, bármilyen mélységben. Például Szabó Katalin köre: u03, u09, u10, u11, u12. Kovács Eszter köre: u01–u16. Fehér László köre: u00–u16.
- **Közvetlen vezető:** a címzett `vezeto_id`-ja szerinti személy (ha van).
- **A címzett B-1 vezetője:** a címzett **feletti** vezetői láncban lévő, `B-1` szintű személy. Ha a címzett maga B-1 vagy B szintű, nincs B-1 vezetője. Ha a közvetlen vezető maga a B-1, ugyanaz a személy mindkét szerepben érintett.

### 3.3. Ki mit lát és tehet
| Szereplő | Mit lát | Mit tehet |
|---|---|---|
| Munkatárs (bárki) | a közös falat (nyilvános köszönetek), a saját Kapott és Küldött köszöneteit, a saját értesítéseit | köszönetet küld, tapsol a számára látható köszönetekre, olvasottnak jelöli az értesítéseit |
| Vezető (B-2, B-1, B) | mint egy munkatárs, és **a Csapatköszönetek nézetben** minden olyan köszönetet (privátot is), amelynek a küldője vagy a címzettje a szervezeti körébe tartozik, valamint ezek statisztikáját | mint egy munkatárs |

Egy köszönetet **láthat** egy felhasználó, ha a köszönet nyilvános, vagy ő a küldője, vagy ő a címzettje, vagy vezető, és a küldő vagy a címzett a szervezeti körébe tartozik (SZ-08).

## 4. Adatmodell

### 4.1. Munkatárs (csak olvasható, `data/munkatarsak.json`)
| Mező | Típus | Megjegyzés |
|---|---|---|
| `id` | szöveg | kulcs, pl. `u05` |
| `nev` | szöveg | |
| `email` | szöveg | |
| `egyseg` | szöveg | szervezeti egység |
| `beosztas` | szöveg | |
| `szint` | `B` / `B-1` / `B-2` / `null` | |
| `vezeto_id` | szöveg / `null` | közvetlen vezető |

Az alkalmazás indításkor beolvassa, és soha nem írja. Az adatbázisban nem tárolja másolatban.

### 4.2. Köszönet (`koszonet` tábla)
| Mező | Típus | Korlát |
|---|---|---|
| `id` | egész | elsődleges kulcs, automatikus |
| `kuldo_id` | szöveg | kötelező, létező munkatárs, a bejelentkezett felhasználó |
| `cimzett_id` | szöveg | kötelező, létező munkatárs, ≠ `kuldo_id` |
| `kategoria` | szöveg | kötelező, ezek egyike: `loyalty`, `forward`, `together`, `experiment` (1.1-ben módosult) |
| `uzenet` | szöveg | kötelező; az elején és a végén lévő szóközöket levágva tároljuk; 1–500 karakter |
| `lathatosag` | szöveg | `privat` (alapértelmezés) vagy `nyilvanos` |
| `letrehozva` | időbélyeg | a szerver rögzíti, helyi idő, ISO 8601 (`ÉÉÉÉ-HH-NNTóó:pp:mm`) |

Kategóriák megjelenítése (1.1-ben módosult: az IT-BSO Behavioral Anchorjai, ebben a sorrendben):

| Kód | Felirat | Leírás | Szín-token |
|---|---|---|---|
| `loyalty` | 💛 Earn customer loyalty | az ügyfélért, az ügyfélelégedettségért tett erőfeszítés | `--cat-ugyfel` (korall) |
| `forward` | 🚀 Take actions to move forward | nem várt, cselekedett: elakadást oldott fel, felvette a leesett feladatot | `--cat-segitseg` (kék) |
| `together` | 🤝 Deliver value together | közös munka, együtt teremtett érték az ügyfélnek | `--cat-egyuttmukodes` (zöld) |
| `experiment` | 🧪 Experiment, learn fast! | kipróbált valami újat, tanult a hibából, jobbá tette a folyamatot | `--cat-otlet` (lila) |

A felirat (az angol név) mindenhol változatlanul, fordítás nélkül jelenik meg: a varázslóban, a kártya chipjén, a szűrőkben, az értesítésben és a statisztikában.

**Karakterszám:** az üzenet hosszát Unicode-kódpontokban mérjük (Pythonban `len(s)`, JavaScriptben `[...s].length`), így egy egyszerű emoji (pl. 🙏) 1 karakternek számít.

### 4.3. Taps (`taps` tábla)
| Mező | Típus | Korlát |
|---|---|---|
| `koszonet_id` | egész | idegen kulcs |
| `munkatars_id` | szöveg | aki tapsolt |
| `letrehozva` | időbélyeg | |

Kulcs: (`koszonet_id`, `munkatars_id`), ezért egy személy egy köszönetre legfeljebb egy tapsot adhat.

### 4.4. Értesítés (`ertesites` tábla)
| Mező | Típus | Korlát |
|---|---|---|
| `id` | egész | elsődleges kulcs |
| `munkatars_id` | szöveg | akinek szól |
| `koszonet_id` | egész | idegen kulcs |
| `olvasott` | logikai | alapértelmezés: hamis |
| `letrehozva` | időbélyeg | |

Egyedi: (`munkatars_id`, `koszonet_id`), ezért egy személy egy köszönetről legfeljebb egy értesítést kap. Az értesítés tartalmát (küldő, címzett, kategória, dátum, előnézet) a köszönetből állítjuk elő.

### 4.5. Munkamenet
A szimulált belépés egy `kudos_user` sütiben tárolja a munkatárs azonosítóját (`HttpOnly`, `SameSite=Lax`). A szerver minden kérésnél ellenőrzi, hogy létező munkatárs-e. Ha nem, a kérés `401`-et kap.

## 5. Képernyők és folyamatok

Közös keret minden belépés utáni oldalon (`docs/arculat-ui.md` 2. pont): sötét, sticky fejléc a „Kudos” jellel és a menüvel (Fal · Új köszönet · Saját · Csapat), mellette a csengő és a monogram-avatar. Alatta vékony sárga sáv: „DEMO belépés: ‹név› · ‹egység›” és egy [Váltás] gomb. A „Csapat” menüpont csak vezetőknek látszik. 640 px alatt a menü alsó tab-sávba kerül.

### 5.1. Belépés
- Lista az összes munkatársról (név, beosztás, egység), egy „DEMO – szimulált belépés, jelszó nincs” felirattal.
- Kiválasztás után átirányít a Falra. A [Váltás] gomb kiléptet, és visszavisz ide.
- Belépés nélkül bármelyik oldal ide irányít.

### 5.2. Kudos fal (kezdőoldal)
- Kártyarács az összes nyilvános köszönetről, a legújabbal kezdve. Fölötte kategóriaszűrő („Minden kategória” + a 4 kategória).
- Minden kártyán taps gomb. Ha nincs találat, üres állapot jelenik meg.

### 5.3. Új köszönet (3 lépéses varázsló)
A lépésjelző (1 — 2 — 3) mindig mutatja az aktuális lépést.
1. **Kinek?** Kereső mező („Keresés név, egység vagy e-mail alapján”). Gépelés közben élő találati lista (avatar, név, beosztás, egység), amely ↑ ↓ Enter Esc billentyűkkel is kezelhető. Saját magát nem mutatja. Választás után a 2. lépésre lép.
2. **Mit?** 4 kategória-kártyagomb (emoji, angol név, egysoros magyar leírás; 1.1-ben módosult). Üzenet szövegmező karakterszámlálóval (`n / 500`; 450 felett narancs, 500 felett piros). Láthatóság-kapcsoló: 🔒 Privát (alapértelmezett) / 🌐 Nyilvános. [Vissza] és [Tovább] gomb. A [Tovább] ellenőrzi a mezőket, a hibát a mező alatt jelzi.
3. **Ellenőrzés:** a köszönet kártyaként, pontosan úgy, ahogy a listákban fog megjelenni. Alatta [Vissza] (a 2. lépésre, a beírt adatok megmaradnak) és [Küldés]. A szerver által visszautasított küldés hibaüzenete is itt, a kártya alatt jelenik meg.

Sikeres küldés után toast jelenik meg („Köszönetedet elküldtük Farkas Júliának! 🎉”, 4 mp, `aria-live="polite"`), majd az alkalmazás átvisz a Saját → Küldött listára.

### 5.4. Saját köszöneteim
- Két fül: **Kapott (n)** és **Küldött (n)**, a darabszámmal. A szám a szűrés nélküli összes darabot mutatja.
- Szűrősor: szabad szavas kereső, kategóriaszűrő, időszakszűrő (Elmúlt 7 nap / Elmúlt 30 nap / Összes; alapértelmezés: Összes).
- Kártyarács, a legújabbal kezdve. Üres listánál üres állapot.

### 5.5. Csapatköszönetek (csak vezetőknek)
- Felül a statisztika (5.6), alatta szűrősor (kereső, kategória, időszak; az időszak alapértelmezése: Elmúlt 30 nap), majd a kártyarács a vezető szervezeti köréhez kapcsolódó köszönetekről.
- Az időszakszűrő a statisztikára és a listára is vonatkozik. A kereső és a kategóriaszűrő csak a listára.
- Nem vezető felhasználónál (ha közvetlenül nyitja meg az oldalt) csak ez az üzenet jelenik meg: „Ehhez a nézethez vezetői jogosultság kell.”

### 5.6. Vezetői statisztika
- 4 mutató-kártya: **kapott köszönet**, **küldött köszönet**, **aktív küldő**, **összes köszönet** (mobilon 2×2).
- Kategória-megoszlás vízszintes CSS-sávdiagramként, a kategória színével, a sáv végén a darabszámmal.
- Top 3 lista (🥇 🥈 🥉) avatarral, névvel és a kapott köszönetek számával.

### 5.7. Értesítések
- Csengő a fejlécben, sárga buborékban az olvasatlanok száma (0-nál nincs buborék).
- Kattintásra legördülő panel: legújabb elöl, az olvasatlanok halványsárga háttérrel. Fent [Mind olvasott] gomb.
- Egy értesítés: „‹küldő› → ‹címzett›”, kategória, dátum, és az üzenet első legfeljebb 80 karaktere (ha hosszabb, „…”-tal). Megnyitásra (kattintás vagy Enter) olvasottá válik, és a számláló csökken.

### 5.8. Szerver API (a felület ezeket hívja)
| Metódus és útvonal | Mit csinál |
|---|---|
| `GET /api/munkatarsak` | a belépési lista (belépés nélkül is elérhető) |
| `POST /api/belepes` · `POST /api/kilepes` · `GET /api/en` | szimulált belépés, kilépés, a bejelentkezett felhasználó (és hogy vezető-e) |
| `GET /api/munkatarsak/kereses?q=` | címzettkereső |
| `POST /api/koszonetek` | köszönet küldése; hibánál `400` és `{"hiba": "...", "mezo": "..."}` |
| `GET /api/koszonetek/kapott` · `/kuldott` `?q=&kategoria=&idoszak=` | saját listák |
| `GET /api/fal?kategoria=` | közös fal |
| `POST /api/koszonetek/{id}/taps` | taps be/ki (váltás); nem látható köszönetnél `404` |
| `GET /api/ertesitesek` · `POST /api/ertesitesek/{id}/olvasott` · `POST /api/ertesitesek/olvasott-mind` | értesítések |
| `GET /api/csapat?q=&kategoria=&idoszak=` · `GET /api/csapat/statisztika?idoszak=` | vezetői nézet; nem vezetőnek `403` |

`idoszak` értékei: `7`, `30`, `osszes`. Belépés nélkül minden API (a munkatárslistán és a belépésen kívül) `401`-et ad.

## 6. Üzleti szabályok

- **SZ-01 – Szimulált belépés.** Bármelyik munkatárs beléphet a `data/munkatarsak.json` listájából, jelszó nélkül. A belépett felhasználó neve és egysége, valamint a „DEMO” jelzés minden oldalon látszik. Belépés nélkül csak a belépési oldal és a munkatárslista érhető el.
- **SZ-02 – Szervezeti kör és vezetői lánc.** A szervezeti kör, a közvetlen vezető és a B-1 vezető a 3.2. pont szerint számolódik, a `vezeto_id` láncból, tetszőleges mélységig.
- **SZ-03 – Címzettkereső.** A kereső a név, az egység és az e-mail-cím részszövegére keres, kis- és nagybetűtől függetlenül (ékezetet nem alakít át). Üres keresőszóra nincs találat. A találatban látszik a név, a beosztás és az egység. A bejelentkezett felhasználó nem szerepel a találatok között.
- **SZ-04 – Egy címzett, önmagának nem.** Egy köszönetnek pontosan egy, létező munkatárs a címzettje. A címzett nem lehet maga a küldő. A szerver ezt akkor is visszautasítja, ha a kérés nem a felületről jön.
- **SZ-05 – Üzenet.** Az üzenet a levágott szóközök után nem lehet üres, és legfeljebb 500 karakter (Unicode-kódpont) lehet. Emoji használható. Írás közben a felület mutatja a karakterszámot (`n / 500`).
- **SZ-06 – Kategória (1.1-ben módosult).** Pontosan egy kategória kötelező, a 4.2. pontban felsorolt 4 Behavioral Anchor közül (`loyalty`, `forward`, `together`, `experiment`). Ismeretlen kategóriakódot, köztük az üzleti leírás régi kategóriáit (pl. `egyuttmukodes`, `kiemelkedo`), a szerver visszautasítja.
- **SZ-07 – Napi limit.** Ugyanaz a küldő ugyanannak a címzettnek egy naptári napon (helyi idő, 00:00–23:59) legfeljebb 3 köszönetet küldhet. A 4. próbálkozást a szerver visszautasítja ezzel az üzenettel: „Ugyanannak a munkatársnak ma már 3 köszönetet küldtél.” Más címzettnek ugyanaznap továbbra is lehet küldeni.
- **SZ-08 – Láthatóság.** A láthatóság alapértelmezése a **Privát**. Egy köszönetet az láthat, aki a küldője vagy a címzettje, vagy olyan vezető, akinek a szervezeti körébe a küldő vagy a címzett tartozik. Nyilvános köszönetet ezen felül mindenki láthat. Ezt minden API szerveroldalon érvényesíti.
- **SZ-09 – Közös fal.** A falon kizárólag a nyilvános köszönetek jelennek meg, mindenkinek ugyanazok, a legújabbal kezdve, kategória szerint szűrhetően. Privát köszönet a falon soha nem jelenik meg, a küldőnek, a címzettnek és a vezetőknek sem.
- **SZ-10 – Taps.** Egy felhasználó egy általa látható köszönetre (SZ-08) legfeljebb egy tapsot adhat. Az újabb kattintás visszavonja. A küldő és a címzett is tapsolhat. A kártyán látszik a tapsok száma, és hogy a felhasználó tapsolt-e már. Nem látható köszönetre a taps kérést a szerver `404`-gyel utasítja vissza, és a tapsszám nem változik.
- **SZ-11 – Értesítendők köre.** Köszönet küldésekor értesítést kap a címzett, a címzett közvetlen vezetője (ha van) és a címzett B-1 vezetője (ha van). Más nem kap értesítést. A board tag (B) csak akkor kap értesítést, ha ő a címzett közvetlen vezetője. Egy személy egy köszönetről legfeljebb egy értesítést kap. **A küldő a saját köszönetéről nem kap értesítést**, akkor sem, ha ő a címzett vezetője (1.1-ben eldöntve, lásd 10. pont).
- **SZ-12 – Értesítés megjelenése és olvasottsága.** Az értesítés tartalmazza a küldő és a címzett nevét, a kategóriát, a dátumot és az üzenet első legfeljebb 80 karakterét. A csengőn az olvasatlanok száma látszik. Megnyitáskor az értesítés olvasottá válik. A [Mind olvasott] a felhasználó összes értesítését olvasottá teszi. Mindenki csak a saját értesítéseit látja és módosíthatja.
- **SZ-13 – Vezetői nézet.** A Csapatköszönetek nézet és API-ja csak vezetőknek érhető el, nem vezetőnek a menüpont nem látszik, az API pedig `403`-at ad. A nézet pontosan azokat a köszönetet listázza (privátot és nyilvánosat is), amelyeknek a küldője vagy a címzettje a vezető szervezeti körébe tartozik. A szűrést a szerver végzi a bejelentkezett felhasználó alapján, a böngészőtől kapott adatokra nem hagyatkozik.
- **SZ-14 – Vezetői statisztika.** A kiválasztott időszakban (alapértelmezés: elmúlt 30 nap), kizárólag az SZ-13 szerinti köszönetekből számol:
  - **kapott köszönet:** azok száma, amelyeknek a címzettje a körbe tartozik,
  - **küldött köszönet:** azok száma, amelyeknek a küldője a körbe tartozik,
  - **összes köszönet:** az SZ-13 szerinti köszönetek száma (mindegyik egyszer),
  - **kategória-megoszlás:** az SZ-13 szerinti köszönetek darabszáma kategóriánként (mindegyik egyszer),
  - **Top 3:** a körből a legtöbb köszönetet kapott legfeljebb 3 munkatárs (csak akik legalább 1-et kaptak), holtversenyben név szerinti ábécérendben,
  - **aktív küldő:** a kör hány különböző tagja küldött legalább egy köszönetet.
- **SZ-15 – Rendezés, keresés, szűrés.** Minden lista a legújabbal kezdődik (azonos időpontnál a nagyobb azonosító előbb). A szabad szavas keresés kis- és nagybetűtől függetlenül az üzenet szövegében, a küldő nevében és a címzett nevében keres. A kategóriaszűrő egy kategóriára szűkít. Az időszakszűrő: `7` = az utolsó 7×24 óra, `30` = az utolsó 30×24 óra, `osszes` = nincs korlát. A szűrők együtt is használhatók (ÉS kapcsolat).
- **SZ-16 – Időbélyeg.** A küldés dátumát és időpontját a szerver rögzíti, a kliens nem adhatja meg. A kártyán relatív idő látszik („2 órája”), az egér alatt vagy a `title` attribútumban a pontos időpont.

## 7. Elfogadási kritériumok

A kritériumok a `data/munkatarsak.json` neveit használják. Ahol „üres adatbázis” szerepel, ott a tesztet új, ideiglenes `KUDOS_DB`-vel kell indítani. Az időfüggő kritériumokhoz a logika a „most” időpontot paraméterként is megkaphatja (unit teszt), vagy a teszt közvetlenül az adatbázisba ír régebbi köszönetet.

### 7.1. Belépés és köszönet küldése

- **EK-01 (SZ-01) – Belépés a listából.**
  Adott: üres adatbázis, a belépési oldal.
  Amikor: a lista mind a 17 munkatársat mutatja, és a felhasználó a „Horváth Anna” elemet választja.
  Akkor: a Kudos fal jelenik meg, a sárga sávban ez áll: „DEMO belépés: Horváth Anna · Fejlesztési Osztály”, és a `GET /api/en` válasza `u05`.

- **EK-02 (SZ-01) – Belépés nélkül nincs hozzáférés.**
  Adott: nincs `kudos_user` süti (vagy nem létező azonosító van benne, pl. `u99`).
  Amikor: a kliens meghívja a `GET /api/fal`, `POST /api/koszonetek` vagy `GET /api/ertesitesek` végpontot, illetve megnyitja a Fal oldalt.
  Akkor: az API `401`-et ad, az oldal pedig a belépési oldalra irányít. A `GET /api/munkatarsak` belépés nélkül is 17 elemet ad vissza.

- **EK-03 (SZ-03) – Címzettkereső.**
  Adott: Horváth Anna (u05) belépett, az Új köszönet 1. lépésén van.
  Amikor: beírja, hogy „adat”, majd „julia.f”, majd „horváth”.
  Akkor: „adat”-ra pontosan az Adat Osztály 5 tagja jelenik meg (Szabó Katalin, Farkas Júlia, Balogh Máté, Papp Zsófia, Takács Levente), mindegyiknél a név, a beosztás és az egység. „julia.f”-re egyetlen találat: Farkas Júlia · adatelemző · Adat Osztály. „horváth”-ra nincs találat, mert Horváth Anna saját magát nem látja.

- **EK-04 (SZ-03, NF-04) – Kereső billentyűzettel.**
  Adott: Horváth Anna az 1. lépésen beírja, hogy „Far”.
  Amikor: lenyomja a ↓, majd az Enter billentyűt.
  Akkor: Farkas Júlia lesz a kiválasztott címzett, és a varázsló a 2. lépésre lép. Az Esc a találati listát bezárja, a kereső tartalma megmarad.

- **EK-05 (SZ-05, SZ-06, NF-02) – Varázsló és ellenőrző nézet (1.1-ben módosult).**
  Adott: Horváth Anna kiválasztotta Farkas Júliát.
  Amikor: a 2. lépésen a „🤝 Deliver value together” kategóriát választja, beírja: „Köszönöm a gyors adatelemzést! 🙏🎉”, a láthatóságot nem módosítja, és a [Tovább] gombra kattint.
  Akkor: a lépésjelzőn a 3. lépés aktív, és az ellenőrző kártyán ez látszik: Horváth Anna → Farkas Júlia, 🤝 Deliver value together, a beírt szöveg emojikkal, 🔒 Privát. A [Vissza] gombra a 2. lépés jelenik meg, és a kategória, a szöveg és a láthatóság változatlanul ki van töltve.

- **EK-06 (SZ-04, SZ-08, SZ-16) – Sikeres küldés (1.1-ben módosult).**
  Adott: az EK-05 ellenőrző nézete.
  Amikor: Horváth Anna a [Küldés] gombra kattint.
  Akkor: megjelenik egy `aria-live="polite"` toast: „Köszönetedet elküldtük Farkas Júliának! 🎉”. Az adatbázisban egy új köszönet van: `kuldo_id` = u05, `cimzett_id` = u09, `kategoria` = `together`, `lathatosag` = `privat`, a szöveg emojikkal együtt változatlan, a `letrehozva` pedig a szerver aktuális ideje (±5 mp). Ha a kérés `letrehozva` mezőt is küld, a szerver figyelmen kívül hagyja.

- **EK-07 (NF-01, NF-02) – Arculati alapok.**
  Adott: az alkalmazás fut.
  Amikor: a teszt betölti a `static/` CSS-fájlját és a Fal oldalt.
  Akkor: a CSS-fájl a `:root` blokkal kezdődik, benne a `docs/arculat-ui.md` 1. pontjának összes tokenjével (`--yellow` … `--font`). A fejléc háttérszíne `rgb(43, 45, 51)` (`--offblack`). Az oldal egyetlen kérést sem indít a `localhost`-on kívülre, és nem használ `alert()`-et vagy `confirm()`-ot.

### 7.2. Küldési szabályok (negatív esetek)

- **EK-08 (SZ-04) – Önmagának nem küldhet.**
  Adott: Horváth Anna (u05) belépett.
  Amikor: közvetlenül meghívja a `POST /api/koszonetek` végpontot `cimzett_id` = `u05` értékkel (érvényes kategóriával és szöveggel), illetve nem létező címzettel (`u99`).
  Akkor: mindkét esetben `400` a válasz, a `mezo` értéke `cimzett`, az első esetben a hibaüzenet: „Magadnak nem küldhetsz köszönetet.”. Új köszönet és értesítés nem jön létre.

- **EK-09 (SZ-05, NF-03) – Üres üzenet (1.1-ben módosult).**
  Adott: Horváth Anna kiválasztotta Farkas Júliát és a „🚀 Take actions to move forward” kategóriát.
  Amikor: az üzenetmezőt üresen hagyja, majd csak szóközöket ír bele, és a [Tovább] gombra kattint. A teszt ugyanezt közvetlenül az API-n is megpróbálja (`"uzenet": "   "`).
  Akkor: a felület a 2. lépésen marad, és az üzenetmező alatt piros szöveggel, ikonnal ez jelenik meg: „Az üzenet nem lehet üres.”. Felugró ablak nincs. Az API `400`-at ad (`mezo` = `uzenet`), köszönet nem jön létre.

- **EK-10 (SZ-05) – Üzenet hossza és karakterszámláló.**
  Adott: Horváth Anna a 2. lépésen van, a címzett Farkas Júlia.
  Amikor: 499 „a” betűt és egy 🙏 emojit ír be (500 karakter), majd egy újabb „a” betűvel 501 karakterre bővíti, és a [Tovább] gombra kattint.
  Akkor: 500 karakternél a számláló „500 / 500”, és nincs hibaüzenet. 501 karakternél a számláló „501 / 500” és piros, a [Tovább] után a mező alatt ez látszik: „Az üzenet legfeljebb 500 karakter lehet.”, és a varázsló nem lép tovább. Az API az 500 karakteres üzenetet elfogadja, az 501 karakteresre `400`-at ad (`mezo` = `uzenet`).

- **EK-11 (SZ-06, NF-03) – Kategória nélkül nem küldhető.**
  Adott: Horváth Anna kiválasztotta Farkas Júliát, és beírt egy érvényes üzenetet.
  Amikor: kategória kiválasztása nélkül a [Tovább] gombra kattint. Az API-n pedig kategória nélkül, majd `"kategoria": "pizza"` értékkel próbál küldeni.
  Akkor: a felület a 2. lépésen marad, a kategóriák alatt ez áll: „Válassz kategóriát.”. Az API mindkét esetben `400`-at ad (`mezo` = `kategoria`).

- **EK-12 (SZ-07, NF-03) – Napi limit: a 4. köszönet.**
  Adott: Horváth Anna ma már 3 köszönetet küldött Farkas Júliának.
  Amikor: a varázslóban egy 4. köszönetet próbál küldeni neki, majd ugyanaznap Varga Bencének (u06) küld egyet.
  Akkor: a 4. küldésnél az ellenőrző nézetben, a kártya alatt piros szöveggel ez jelenik meg: „Ugyanannak a munkatársnak ma már 3 köszönetet küldtél.”. Az API `400`-at ad, Farkas Júliának továbbra is 3 mai köszönete van Annától. A Varga Bencének küldött köszönet sikeres.

- **EK-13 (SZ-07) – A napi limit naptári napra vonatkozik.**
  Adott: Horváth Anna tegnap 23:50-kor 3 köszönetet küldött Farkas Júliának (a teszt az adatbázisba írja, vagy a logikának megadja a „most” időpontot).
  Amikor: ma 00:10-kor újabb köszönetet küld neki, majd ma még kettőt, végül egy negyediket.
  Akkor: a három mai köszönet sikeres, a negyedik mai próbálkozást a szerver visszautasítja. Más küldő (pl. Varga Bence) Farkas Júliának küldött köszönetei Anna limitjébe nem számítanak bele.

- **EK-47 (SZ-06, NF-02) – A négy Behavioral Anchor kategória (1.1-ben új).**
  Adott: Horváth Anna kiválasztotta Farkas Júliát, és a varázsló 2. lépésén van.
  Amikor: megnézi a kategória-választót, majd a teszt közvetlenül az API-n próbál küldeni sorban `"kategoria": "experiment"`, `"egyuttmukodes"` és `"kiemelkedo"` értékkel.
  Akkor: pontosan 4 kategória-kártyagomb látszik, ebben a sorrendben: „💛 Earn customer loyalty”, „🚀 Take actions to move forward”, „🤝 Deliver value together”, „🧪 Experiment, learn fast!”, mindegyik alatt a 4.2. pont szerinti magyar leírás (pl. „kipróbált valami újat, tanult a hibából, jobbá tette a folyamatot”). Az üzleti leírás régi kategóriái közül egyik sem jelenik meg. Az `experiment` kóddal a küldés sikeres, az `egyuttmukodes` és a `kiemelkedo` kódra az API `400`-at ad (`mezo` = `kategoria`).

### 7.3. Saját köszöneteim

- **EK-14 (SZ-08, SZ-15) – Megjelenés a Küldött és a Kapott listában.**
  Adott: Horváth Anna privát köszönetet küldött Farkas Júliának (EK-06).
  Amikor: Anna megnyitja a Saját → Küldött fület, majd Farkas Júlia belép, és megnyitja a Saját → Kapott fület.
  Akkor: Annánál a fül felirata „Küldött (1)”, Júliánál „Kapott (1)”, és mindkettejüknél megjelenik a köszönet kártyája. Varga Bence (u06) Kapott és Küldött listája üres („Kapott (0)”, „Küldött (0)”).

- **EK-15 (SZ-16, NF-05) – A kártya tartalma és a szöveg escape-elése (1.1-ben módosult).**
  Adott: Horváth Anna nyilvános köszönetet küldött Farkas Júliának „🧪 Experiment, learn fast!” kategóriában, ezzel a szöveggel: `Szuper! <script>alert(1)</script> 🎉`. Varga Bence már tapsolt rá.
  Amikor: Farkas Júlia megnyitja a Kapott listát.
  Akkor: a kártyán látszik a küldő neve (Horváth Anna) és egysége, a címzett neve (Farkas Júlia) és egysége, a „🧪 Experiment, learn fast!” chip, a kártya bal szélén a `--cat-otlet` színű csík, a 🌐 láthatóság-ikon, a szöveg pontosan betű szerint (a `<script>` szövegként jelenik meg, nem fut le), a tapsszám (1) és a relatív idő, amelynek `title` attribútumában a pontos időpont áll.

- **EK-16 (SZ-15) – Rendezés: a legújabb elöl.**
  Adott: Farkas Júlia 3 köszönetet kapott ebben a sorrendben: Horváth Anna 10:00-kor, Varga Bence 11:00-kor, Kiss Réka 12:00-kor.
  Amikor: Júlia megnyitja a Kapott listát.
  Akkor: a kártyák sorrendje: Kiss Réka, Varga Bence, Horváth Anna.

- **EK-17 (SZ-15) – Szabad szavas keresés.**
  Adott: Farkas Júlia kapott egy köszönetet Horváth Annától („Köszi a riportot!”) és egyet Varga Bencétől („Remek dashboard 💛”).
  Amikor: a Kapott listában rákeres arra, hogy „DASHBOARD”, majd arra, hogy „horváth”, majd arra, hogy „nincsilyen”.
  Akkor: „DASHBOARD”-ra csak Varga Bence köszönete, „horváth”-ra csak Horváth Annáé látszik. „nincsilyen”-re a „nincs találat” üres állapot jelenik meg. A fül darabszáma közben végig „Kapott (2)”.

- **EK-18 (SZ-15) – Kategóriaszűrő a saját nézetben (1.1-ben módosult).**
  Adott: Horváth Anna küldött egy 🤝 Deliver value together és egy 🧪 Experiment, learn fast! kategóriájú köszönetet.
  Amikor: a Küldött listában a „🧪 Experiment, learn fast!” szűrőt választja.
  Akkor: csak a 🧪 kategóriájú köszönet látszik. A „Minden kategória” választásra újra mindkettő.

- **EK-19 (SZ-15) – Időszakszűrő.**
  Adott: Farkas Júlia kapott köszönetet 2 napja, 10 napja és 40 napja (a teszt az adatbázisba írja).
  Amikor: a Kapott listában az „Elmúlt 7 nap”, az „Elmúlt 30 nap” és az „Összes” időszakot választja.
  Akkor: 7 napra 1, 30 napra 2, „Összes”-re 3 köszönet látszik. Az alapértelmezett szűrő az „Összes”.

- **EK-20 (NF-03) – Üres állapot.**
  Adott: üres adatbázis, Varga Bence belépett.
  Amikor: megnyitja a Saját → Kapott fület.
  Akkor: nagy emoji, ez a mondat: „Még nem kaptál köszönetet. Te már küldtél ma valakinek?”, és egy [+ Új köszönet] elsődleges gomb látszik, amely a varázslóba visz.

- **EK-21 (SZ-08) – Küldés után a Küldött lista.**
  Adott: Horváth Anna az EK-06 szerint elküldi a köszönetet.
  Amikor: a toast megjelenik.
  Akkor: az alkalmazás a Saját → Küldött fülre visz, ahol az új köszönet az első kártya.

### 7.4. Közös fal és taps

- **EK-22 (SZ-09, SZ-08) – A falon csak a nyilvános köszönet jelenik meg.**
  Adott: Horváth Anna nyilvános köszönetet küldött Farkas Júliának („Nyilvános köszi”), Varga Bence pedig privátot Kiss Rékának („Privát köszi”).
  Amikor: sorban belép Juhász Nóra (u13), Varga Bence, Kiss Réka és Fehér László (u00), és mindegyikük megnyitja a Falat (és lekéri a `GET /api/fal`-t).
  Akkor: mind a négyüknél pontosan egy kártya van a falon, a „Nyilvános köszi”. A „Privát köszi” egyiküknél sem jelenik meg a falon, a küldőnél, a címzettnél és a board tagnál sem.

- **EK-23 (SZ-09, SZ-15) – Kategóriaszűrő a falon, sorrend (1.1-ben módosult).**
  Adott: a falon 3 nyilvános köszönet van, egymás után küldve: 🤝 Deliver value together, 💛 Earn customer loyalty, 🤝 Deliver value together.
  Amikor: Juhász Nóra megnyitja a Falat, és megnézi a kategóriaszűrő elemeit, majd a „🤝 Deliver value together” szűrőt választja, végül a „🚀 Take actions to move forward” szűrőt.
  Akkor: a szűrő elemei pontosan: „Minden kategória”, „💛 Earn customer loyalty”, „🚀 Take actions to move forward”, „🤝 Deliver value together”, „🧪 Experiment, learn fast!”. Szűrés nélkül 3 kártya van, a legutóbb küldött az első. A 🤝 szűrővel 2, a 🚀 szűrővel 0 kártya és üres állapot látszik.

- **EK-24 (SZ-10) – Taps és visszavonás.**
  Adott: a falon Horváth Anna Farkas Júliának küldött nyilvános köszönete, 0 tapssal.
  Amikor: Varga Bence a kártya „👏” gombjára kattint, majd újra rákattint.
  Akkor: első kattintásra a gomb „👏 1”, kitöltött sárga állapotú, és `aria-pressed="true"`. A második kattintásra „👏 0”, keretes állapotú, és `aria-pressed="false"`. Az oldal újratöltése után is a mentett állapot látszik.

- **EK-25 (SZ-10) – Egy személy egy tapsa, a küldő és a címzett is tapsolhat.**
  Adott: ugyanaz a nyilvános köszönet.
  Amikor: Varga Bence, Kiss Réka, Horváth Anna (a küldő) és Farkas Júlia (a címzett) egyszer-egyszer tapsol, majd a logikai réteg Varga Bence nevében még egy tapsot próbál rögzíteni úgy, hogy a meglévőt nem vonja vissza (pl. egyidejű dupla kérés).
  Akkor: a tapsszám 4, az adatbázisban Varga Bencétől erre a köszönetre legfeljebb egy taps van.

- **EK-26 (SZ-10, SZ-08) – Nem látható köszönetre nem lehet tapsolni.**
  Adott: Horváth Anna privát köszönetet küldött Farkas Júliának, ennek ismert az azonosítója.
  Amikor: Juhász Nóra (u13, Üzemeltetési Osztály) közvetlenül meghívja a `POST /api/koszonetek/{id}/taps` végpontot. Utána Szabó Katalin (Júlia vezetője) és Nagy Péter (Anna vezetője) is tapsol rá ugyanígy.
  Akkor: Juhász Nóra `404`-et kap, és a tapsszám nem változik. Szabó Katalin és Nagy Péter tapsa sikeres (a köszönet látható számukra), a tapsszám 2.

- **EK-27 (NF-02) – Mobil elrendezés: alsó tab-sáv, egyoszlopos rács.**
  Adott: a falon 3 nyilvános köszönet, Juhász Nóra belépett.
  Amikor: a böngészőablak szélessége 1280 px, majd 375 px.
  Akkor: 1280 px-nél a menü a fejlécben van, és a kártyák 3 oszlopban állnak (az első három kártya egy sorban). 375 px-nél a menü a képernyő alján lévő tab-sávban van (Fal, Új köszönet, Saját, ikonnal és felirattal), a kártyák egymás alatt állnak, és nincs vízszintes görgetősáv.

- **EK-28 (NF-04) – Billentyűzetes kezelés és látható fókusz.**
  Adott: a falon egy nyilvános köszönet, Varga Bence belépett.
  Amikor: csak Tab billentyűvel lépked az oldalon, majd a taps gombon Entert nyom.
  Akkor: a menüpontok, a csengő, a [Váltás] gomb, a kategóriaszűrő és a taps gomb Tab-bal elérhető, a fókuszált elemen látható fókuszkeret van (`outline` nem `none`). Az Enter tapsol, a csengő és a taps gomb rendelkezik `aria-label`-lel.

### 7.5. Értesítések

- **EK-29 (SZ-11, SZ-02) – Alapeset: címzett, közvetlen vezető, B-1.**
  Adott: üres adatbázis.
  Amikor: Horváth Anna (u05) köszönetet küld Farkas Júliának (u09).
  Akkor: pontosan hárman kapnak egy-egy értesítést: Farkas Júlia (címzett), Szabó Katalin (u03, közvetlen vezető) és Kovács Eszter (u01, B-1 vezető). Nem kap értesítést Horváth Anna, Nagy Péter (Anna vezetője), Fehér László (u00, board tag) és senki más.

- **EK-30 (SZ-11) – Aki több szerepben érintett, egy értesítést kap.**
  Adott: üres adatbázis.
  Amikor: Horváth Anna köszönetet küld Nagy Péternek (u02, B-2), akinek a közvetlen vezetője Kovács Eszter (B-1).
  Akkor: pontosan két értesítés jön létre: Nagy Péternek és Kovács Eszternek. Kovács Eszter, aki közvetlen vezetőként és B-1-ként is érintett, csak egyet kap. Fehér László nem kap.

- **EK-31 (SZ-11, SZ-02) – B-1 címzett: nincs B-1 vezető, a board tag közvetlen vezetőként értesül.**
  Adott: üres adatbázis.
  Amikor: Horváth Anna köszönetet küld Kovács Eszternek (u01, B-1).
  Akkor: pontosan két értesítés jön létre: Kovács Eszternek (címzett) és Fehér Lászlónak (közvetlen vezető, B). Nagy Péter nem kap értesítést.

- **EK-32 (SZ-11) – Vezető nélküli címzett.**
  Adott: üres adatbázis.
  Amikor: Varga Bence (u06) köszönetet küld Fehér Lászlónak (u00, B, nincs vezetője).
  Akkor: pontosan egy értesítés jön létre, Fehér Lászlónak.

- **EK-33 (SZ-11) – A küldő nem kap értesítést a saját köszönetéről.**
  Adott: üres adatbázis.
  Amikor: Nagy Péter (u02) köszönetet küld a beosztottjának, Horváth Annának (u05).
  Akkor: pontosan két értesítés jön létre: Horváth Annának és Kovács Eszternek (B-1). Nagy Péter, bár ő Anna közvetlen vezetője, nem kap értesítést.

- **EK-34 (SZ-12, NF-05) – Csengő, számláló és az értesítés tartalma (1.1-ben módosult).**
  Adott: Horváth Anna ezzel a szöveggel küldött köszönetet Farkas Júliának a „🤝 Deliver value together” kategóriában: egy 120 karakteres szöveg, amely így kezdődik: „Köszönöm a gyors adatelemzést! 🙏”. Varga Bence pedig egy rövid köszönetet küldött Júliának.
  Amikor: Farkas Júlia belép, és rákattint a csengőre.
  Akkor: a csengőn a „2” számláló látszik, az ikonnak `aria-label`-je van. A panelen 2 olvasatlan (halványsárga hátterű) értesítés van, a legújabb (Varga Bencéé) elöl. Anna értesítésében ez áll: „Horváth Anna → Farkas Júlia”, „🤝 Deliver value together”, a küldés dátuma, és a szöveg első 80 karaktere „…”-tal. Juhász Nóra csengőjén nincs számláló, és a `GET /api/ertesitesek` neki üres listát ad.

- **EK-35 (SZ-12) – Olvasottnak jelölés.**
  Adott: az EK-34 állapota, Farkas Júliának 2 olvasatlan értesítése van, Szabó Katalinnak szintén 2.
  Amikor: Júlia megnyitja (rákattint) az egyik értesítést, majd a [Mind olvasott] gombra kattint. Juhász Nóra közvetlenül meghívja a `POST /api/ertesitesek/{id}/olvasott` végpontot Júlia egyik értesítésének azonosítójával.
  Akkor: a megnyitás után a számláló „1”, a [Mind olvasott] után nincs számláló, és a panelen egyik értesítés sincs kiemelve. Szabó Katalin értesítései olvasatlanok maradnak (2). Juhász Nóra kérése `404`-et kap.

### 7.6. Vezetői nézet

Az EK-36…EK-41 közös adatkészlete (mind az elmúlt 30 napban, privát, ha nincs más jelölve; minden üzenet szövege: „Köszönöm!”; a kategóriák 1.1-ben módosultak):

| Jel | Küldő → címzett | Kategória |
|---|---|---|
| M1 | Horváth Anna (u05) → Farkas Júlia (u09) | 🤝 `together` |
| M2 | Farkas Júlia (u09) → Balogh Máté (u10) | 🧪 `experiment` |
| M3 | Horváth Anna (u05) → Varga Bence (u06) | 💛 `loyalty` |
| M4 | Juhász Nóra (u13) → Simon Bálint (u16), **nyilvános** | 💛 `loyalty` |
| M5 | Nagy Péter (u02) → Szabó Katalin (u03) | 🚀 `forward` |

- **EK-36 (SZ-13) – Nem vezető nem éri el.**
  Adott: az M1–M5 adatkészlet, Horváth Anna (alkalmazott) belépett.
  Amikor: megnézi a menüt, közvetlenül megnyitja a Csapat oldal címét, és meghívja a `GET /api/csapat` és a `GET /api/csapat/statisztika` végpontot.
  Akkor: a menüben nincs „Csapat” pont. Az oldal a „Ehhez a nézethez vezetői jogosultság kell.” üzenetet mutatja, köszönetadatok nélkül, mindkét API pedig `403`-at ad. Szabó Katalin (B-2) belépve látja a „Csapat” menüpontot.

- **EK-37 (SZ-13, SZ-02) – B-2 vezető: csak a saját köre, privátokkal együtt.**
  Adott: az M1–M5 adatkészlet.
  Amikor: Szabó Katalin (u03) megnyitja a Csapatköszönetek nézetet.
  Akkor: pontosan M1, M2 és M5 látszik (M1: a címzett a körében van; M2: mindkét fél; M5: ő maga a címzett). Az M3 (Fejlesztési Osztály belső) és az M4 (Üzemeltetési Osztály belső, bár nyilvános) nem jelenik meg.

- **EK-38 (SZ-13, SZ-02) – Mélyebb kör: B-1 és B vezető.**
  Adott: az M1–M5 adatkészlet.
  Amikor: Kovács Eszter (u01), majd Fehér László (u00), majd Nagy Péter (u02), majd Tóth Gábor (u04) megnyitja a Csapatköszönetek nézetet.
  Akkor: Kovács Eszternél és Fehér Lászlónál mind az 5 köszönet látszik. Nagy Péternél M1, M3 és M5 (az M5-nek ő maga a küldője). Tóth Gábornál csak az M4.

- **EK-39 (SZ-13, SZ-08) – Más kör adata közvetlen kéréssel sem érhető el.**
  Adott: az M1–M5 adatkészlet, Szabó Katalin belépett.
  Amikor: meghívja a `GET /api/csapat` végpontot olyan extra paraméterekkel, amelyek egy másik kört kérnének (pl. `?vezeto_id=u01`, `?egyseg=Fejlesztési Osztály`), valamint tapsolni próbál az M3-ra (`POST /api/koszonetek/{M3 id}/taps`).
  Akkor: a `GET /api/csapat` ugyanazt adja vissza, mint paraméter nélkül (M1, M2, M5), vagyis a szerver a bejelentkezett felhasználó körét használja. A taps `404`-et kap.

- **EK-40 (SZ-15, SZ-13) – Keresés és szűrés a vezetői nézetben (1.1-ben módosult).**
  Adott: az M1–M5 adatkészlet, továbbá egy M6: Papp Zsófia (u11) → Farkas Júlia, 🧪 `experiment`, 40 napja.
  Amikor: Szabó Katalin a Csapatköszönetek nézetben (alapértelmezett időszak) rákeres arra, hogy „júlia”, majd a keresőt törli, és a „🧪 Experiment, learn fast!” kategóriát választja, végül az időszakot „Összes”-re állítja.
  Akkor: az alapértelmezett időszak „Elmúlt 30 nap”, ezért M6 kezdetben nem látszik. „júlia”-ra M1 és M2 látszik (Júlia a címzett, illetve a küldő). A 🧪 szűrővel M2. Az „Összes” időszakkal és a 🧪 szűrővel M2 és M6, ebben a sorrendben.

- **EK-41 (SZ-13, SZ-02) – A vezető maga is a köre része.**
  Adott: az M1–M5 adatkészlet, továbbá egy M7: Szabó Katalin (u03) → Juhász Nóra (u13).
  Amikor: Szabó Katalin, majd Tóth Gábor (Nóra vezetője) megnyitja a Csapatköszönetek nézetet.
  Akkor: Szabó Katalinnál M1, M2, M5 és M7 látszik (M7-nek ő a küldője). Tóth Gábornál M4 és M7 (Nóra a címzett).

### 7.7. Vezetői statisztika

Az EK-42…EK-46 közös adatkészlete (Szabó Katalin köre: u03, u09, u10, u11, u12; a kategóriák 1.1-ben módosultak):

| Jel | Küldő → címzett | Kategória | Mikor |
|---|---|---|---|
| K1 | Horváth Anna (u05) → Farkas Júlia (u09) | 🤝 `together` | 1 napja |
| K2 | Farkas Júlia (u09) → Balogh Máté (u10) | 🧪 `experiment` | 2 napja |
| K3 | Papp Zsófia (u11) → Farkas Júlia (u09) | 🤝 `together` | 3 napja |
| K4 | Takács Levente (u12) → Balogh Máté (u10) | 🤝 `together` | 5 napja |
| K5 | Nagy Péter (u02) → Szabó Katalin (u03) | 🚀 `forward` | 10 napja |
| K6 | Horváth Anna (u05) → Varga Bence (u06) | 💛 `loyalty` | 1 napja |
| K7 | Farkas Júlia (u09) → Papp Zsófia (u11) | 🧪 `experiment` | 40 napja |

- **EK-42 (SZ-14) – Mutatók az alapértelmezett 30 napra.**
  Adott: a K1–K7 adatkészlet.
  Amikor: Szabó Katalin megnyitja a Csapatköszönetek nézetet.
  Akkor: az időszak „Elmúlt 30 nap”, és a 4 mutató-kártyán ez áll: **5** kapott köszönet (K1–K5), **3** küldött köszönet (K2, K3, K4), **3** aktív küldő (Farkas Júlia, Papp Zsófia, Takács Levente), **5** összes köszönet.

- **EK-43 (SZ-14, NF-02) – Kategória-megoszlás (1.1-ben módosult).**
  Adott: a K1–K7 adatkészlet, alapértelmezett időszak.
  Amikor: Szabó Katalin a statisztikát nézi.
  Akkor: a sávdiagramon pontosan 4 sáv van, ebben a sorrendben és ezekkel az értékekkel: 💛 Earn customer loyalty 0 (a K6 nem az ő köréhez tartozik), 🚀 Take actions to move forward 1, 🤝 Deliver value together 3, 🧪 Experiment, learn fast! 1. Minden sáv a 4.2. pont szerinti szín-tokent használja, és a sáv végén a darabszám látszik. A leghosszabb sáv a 🤝.

- **EK-44 (SZ-14) – Top 3, holtversenyben ábécérendben.**
  Adott: a K1–K7 adatkészlet.
  Amikor: Szabó Katalin a statisztikát nézi az „Elmúlt 30 nap”, majd az „Összes” időszakra.
  Akkor: 30 napra: 🥇 Balogh Máté (2), 🥈 Farkas Júlia (2), 🥉 Szabó Katalin (1). „Összes”-re: 🥇 Balogh Máté (2), 🥈 Farkas Júlia (2), 🥉 Papp Zsófia (1), mert Papp Zsófia és Szabó Katalin holtversenyben van, és ábécérendben Papp Zsófia következik.

- **EK-45 (SZ-14, SZ-15) – Időszakváltás a statisztikában (1.1-ben módosult).**
  Adott: a K1–K7 adatkészlet.
  Amikor: Szabó Katalin az időszakot „Elmúlt 7 nap”-ra, majd „Összes”-re állítja.
  Akkor: 7 napra: 4 kapott (K1–K4), 3 küldött, 3 aktív küldő, 4 összes. „Összes”-re: 6 kapott, 4 küldött, 3 aktív küldő, 6 összes, és a 🧪 Experiment, learn fast! értéke 2.

- **EK-46 (SZ-14, SZ-13) – A statisztikába nem szivárog más kör adata.**
  Adott: a K1–K7 adatkészlet.
  Amikor: Tóth Gábor (u04, Üzemeltetési Osztály) megnyitja a statisztikát „Összes” időszakra, és Szabó Katalin meghívja a `GET /api/csapat/statisztika?idoszak=osszes&vezeto_id=u01` végpontot.
  Akkor: Tóth Gábornál minden mutató 0, minden kategória 0, a Top 3 helyén üres állapot jelenik meg. Szabó Katalin a saját köre szerinti „Összes” értékeket kapja (EK-45), a K6 egyik számba sem kerül bele.

## 8. Storyk és szállítási sorrend

Minden story vertikális szelet (felület + logika + adat), és a végén böngészőben kipróbálható. Az S1–S4 együtt adja a minimálisan használható változatot (MVP).

Az 1.1-ben új EK-47 az S2-be került, nem új storyba, mert még egyik story sincs megvalósítva, és tartalmilag a kategóriaszabályhoz (EK-11) tartozik.

| Story | Felhasználói történet | EK-k | Kész, ha (böngészőben ellenőrizhető) | MVP |
|---|---|---|---|---|
| S1 | Munkatársként be akarok lépni, és egy kollégámnak köszönetet akarok küldeni, hogy lássa, értékelem a munkáját. | EK-01, EK-02, EK-03, EK-04, EK-05, EK-06, EK-07 | Horváth Anna belép, a keresőben megtalálja Farkas Júliát, „🤝 Deliver value together” kategóriában emojis privát köszönetet ír, az ellenőrző nézet után elküldi, és megjelenik a toast. | igen |
| S2 | Munkatársként érthető hibaüzenetet akarok kapni, ha szabálytalan köszönetet küldenék, hogy tudjam, mit javítsak. | EK-08, EK-09, EK-10, EK-11, EK-12, EK-13, EK-47 | Horváth Anna üres, 501 karakteres vagy kategória nélküli üzenetnél a mező alatt hibát lát, és Farkas Júliának a 4. mai köszönetet nem tudja elküldeni. A kategória-választóban pontosan a 4 Behavioral Anchor látszik. | igen |
| S3 | Munkatársként látni akarom a kapott és küldött köszöneteimet, és keresni akarok bennük, hogy visszanézhessem őket. | EK-14, EK-15, EK-16, EK-17, EK-18, EK-19, EK-20, EK-21 | Anna küldés után a „Küldött (1)” listán látja a köszönetet, Farkas Júlia a „Kapott (1)” listán, és mindketten kereshetnek és szűrhetnek. Varga Bence üres állapotot lát. | igen |
| S4 | Munkatársként látni akarom a nyilvános köszöneteket a közös falon, és tapsolni akarok rájuk, hogy én is elismerjem a kollégákat. | EK-22, EK-23, EK-24, EK-25, EK-26, EK-27, EK-28 | Juhász Nóra a falon látja Anna nyilvános köszönetét Júliának, a privátot nem; tapsol rá, és a taps visszavonható. Mobilszélességen alsó tab-sáv van. | igen |
| S5 | Címzettként és vezetőként értesítést akarok kapni a köszönetekről, hogy azonnal tudjak róluk. | EK-29, EK-30, EK-31, EK-32, EK-33, EK-34, EK-35 | Anna köszönete után Farkas Júlia, Szabó Katalin és Kovács Eszter csengőjén „1” látszik, Fehér Lászlónál nem. Júlia megnyitja, és a számláló eltűnik. | nem |
| S6 | Vezetőként látni akarom a szervezeti köröm köszöneteit, hogy képet kapjak a csapatom elismeréseiről. | EK-36, EK-37, EK-38, EK-39, EK-40, EK-41 | Szabó Katalin a Csapat nézetben látja az Adat Osztályhoz kapcsolódó (privát) köszöneteket, a Fejlesztési Osztály belsőit nem. Horváth Annának nincs Csapat menüpontja. | nem |
| S7 | Vezetőként statisztikát akarok látni a köröm köszöneteiről, hogy mérhető legyen az elismerés. | EK-42, EK-43, EK-44, EK-45, EK-46 | Szabó Katalin a Csapat nézet tetején látja a 4 mutatót, a kategória-sávdiagramot és a Top 3-at, és az időszak váltásával a számok változnak. | nem |

## 9. Nem funkcionális elvárások

- **NF-01 – Technológiai keret** (`CLAUDE.md` szerint): Python 3.10+ standard library (`http.server`, `sqlite3`, `json`, `html`, `urllib`, `unittest`). Az alkalmazás nem használ külső csomagot, hálózati hívást vagy CDN-t. A felület sima HTML, CSS és vanilla JS a `static/` mappában. Az adatok SQLite-ban (`kudos.db`, nem kerül a gitbe). Indítás: `python3 app.py` → http://localhost:8000. Környezeti változók: `PORT` (alapértelmezés: 8000), `KUDOS_DB` (alapértelmezés: `kudos.db`). Az üzleti logika (szervezet, köszönetek, láthatóság, értesítések, statisztika) a webes rétegtől független `kudos/` modulban van, böngésző nélkül tesztelhető.
- **NF-02 – Arculat:** a felület kötelező útmutatója a `docs/arculat-ui.md`. A CSS külön fájlban van, a design tokenekkel kezdődik, a komponensek a tokenekre épülnek, és nincsenek szétszórt, beégetett színek. Köszönetkártyák (nem táblázat), 3 lépéses varázsló lépésjelzővel, toast, üres állapotok, reszponzív rács (3 / 2 / 1 oszlop), 640 px alatt alsó tab-sáv, sticky fejléc, szöveges „Kudos” jel (nem a hivatalos logó). Az 5. pont („Amit kerülj”) tételei nem fordulnak elő.
- **NF-03 – Hibák és üres állapotok:** űrlaphiba a mező alatt, piros szöveggel és ikonnal, soha nem `alert()` vagy `confirm()`. Minden listának van üres állapota (emoji, egy mondat, elsődleges gomb).
- **NF-04 – Akadálymentesség (alapszint):** minden interaktív elem Tab-bal elérhető, a fókusz jól látható. Az ikon-gomboknak `aria-label`-je van, a toastnak `aria-live`-ja. A szöveg kontrasztja legalább 4.5:1, a kattintható felületek legalább 44×44 px-esek. `prefers-reduced-motion` esetén nincs animáció. A kereső billentyűzettel kezelhető (↑ ↓ Enter Esc).
- **NF-05 – Biztonság:** minden felhasználói szöveg escape-elve jelenik meg (a felületen `textContent`, szerveroldali HTML-nél `html.escape`). Az SQL-ben csak paraméterezett lekérdezés van. Minden jogosultságot (láthatóság, taps, értesítések, vezetői nézet) a szerver ellenőriz a bejelentkezett felhasználó alapján. A belépés szimulált, és ezt a felület jól láthatóan jelzi (DEMO).
- **NF-06 – Tesztelés:** unit tesztek a `tests/` mappában, E2E tesztek a `tests/e2e/` mappában (Playwright, `unittest`, szinkron API). Minden EK-hoz legalább egy teszt tartozik, amelynek a neve vagy docstringje hivatkozik az EK-azonosítóra. Minden storyhoz legalább egy E2E teszt tartozik, amely a „Kész, ha…” forgatókönyvet kattintja végig. Az E2E tesztek maguk indítják az alkalmazást szabad porton, ideiglenes `KUDOS_DB`-vel. Alapból headless módban futnak, `HEADED=1` esetén látható ablakkal és `slow_mo`-val.

## 10. Nyitott kérdések

Nincs nyitott kérdés.

Eldöntött kérdések:
- (1.1) A küldő akkor sem kap értesítést a saját köszönetéről, ha ő a címzett közvetlen vagy B-1 vezetője (pl. Nagy Péter → Horváth Anna). A felhasználó döntése: „ne kapjon” (SZ-11, EK-33).
- (1.1) A kategóriák az IT-BSO négy Behavioral Anchorja, angol felirattal és magyar leírással (2.3., 4.2., SZ-06).
- A napi limit **naptári napra** (helyi idő) vonatkozik (SZ-07).
- A vezető szervezeti körébe **maga a vezető is** beletartozik (3.2. pont, SZ-13, EK-41).
- A kategória-megoszlás **a vezető által látott összes köszönetből** számol, mindegyiket egyszer számolva (SZ-14).
- A küldő és a címzett is tapsolhat a saját köszönetére (SZ-10).

## 11. Változásnapló
| Verzió | Dátum | Változás | Érintett EK-k |
|---|---|---|---|
| 1.0 | 2026-10-30 | Első változat | – |
| 1.1 | 2026-10-30 | Változáskérés: az üzleti leírás 5 kategóriája helyett az IT-BSO négy Behavioral Anchorja (💛 Earn customer loyalty, 🚀 Take actions to move forward, 🤝 Deliver value together, 🧪 Experiment, learn fast!). Új 2.3. pont az eltérésről, módosult a 4.2. pont, az 5.2., az 5.3. és az SZ-06. Az M- és K-adatkészlet kategóriái és az EK-43 elvárt értékei átszámolva. Új EK-47 (S2). Lezárult az 1. nyitott kérdés (SZ-11: a küldő nem kap értesítést). | EK-05, EK-06, EK-09, EK-15, EK-18, EK-23, EK-34, EK-40, EK-43, EK-45, EK-47 (új); adatkészlet: EK-36…EK-46 |
