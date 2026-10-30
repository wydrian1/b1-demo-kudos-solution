"use strict";

// A felhasználói szöveget mindig szövegcsomópontként (append / textContent) jelenítjük meg, így escape-elt.

const KATEGORIAK = [
  { kod: "loyalty", emoji: "💛", nev: "Earn customer loyalty",
    leiras: "az ügyfélért, az ügyfélelégedettségért tett erőfeszítés" },
  { kod: "forward", emoji: "🚀", nev: "Take actions to move forward",
    leiras: "nem várt, cselekedett: elakadást oldott fel, felvette a leesett feladatot" },
  { kod: "together", emoji: "🤝", nev: "Deliver value together",
    leiras: "közös munka, együtt teremtett érték az ügyfélnek" },
  { kod: "experiment", emoji: "🧪", nev: "Experiment, learn fast!",
    leiras: "kipróbált valami újat, tanult a hibából, jobbá tette a folyamatot" },
];

const MAX_HOSSZ = 500;
const gyoker = document.getElementById("alkalmazas");
const allapot = { en: null };
let varazslo = null;
let utvonalSzamlalo = 0;

// --- Segédek -------------------------------------------------------------------------------

function el(tag, attrs, ...gyerekek) {
  const elem = document.createElement(tag);
  for (const [kulcs, ertek] of Object.entries(attrs || {})) {
    if (ertek === false || ertek == null) continue;
    if (kulcs === "class") elem.className = ertek;
    else if (kulcs.startsWith("on")) elem.addEventListener(kulcs.slice(2), ertek);
    else elem.setAttribute(kulcs, ertek === true ? "" : ertek);
  }
  for (const gyerek of gyerekek.flat()) {
    if (gyerek != null && gyerek !== false) elem.append(gyerek);
  }
  return elem;
}

async function api(modszer, utvonal, adat) {
  const valasz = await fetch(utvonal, {
    method: modszer,
    headers: adat ? { "Content-Type": "application/json" } : {},
    body: adat ? JSON.stringify(adat) : undefined,
    credentials: "same-origin",
  });
  let tartalom = null;
  try { tartalom = await valasz.json(); } catch (_) { /* üres válasz */ }
  return { allapot: valasz.status, tartalom };
}

function ugrik(hash) {
  if (location.hash === hash) utvonalvalaszto();
  else location.hash = hash;
}

function kategoriaAdat(kod) {
  return KATEGORIAK.find((k) => k.kod === kod);
}

// Magyar részeshatározó (-nak/-nek) a névben szereplő utolsó szóhoz: „Farkas Júlia” → „Farkas Júliának”.
function nakNek(nev) {
  const szavak = nev.split(" ");
  const szo = szavak.pop();
  const alacsony = szo.toLowerCase();
  const magánhangzók = [...alacsony].filter((c) => "aáeéiíoóöőuúüű".includes(c));
  const semleges = "iíé";
  const hatarozo = [...magánhangzók].reverse().find((c) => !semleges.includes(c)) || "e";
  const hatulso = "aáoóuú".includes(hatarozo);
  let toldalek = hatulso ? "nak" : "nek";
  let tovek = szo;
  if (alacsony.endsWith("a")) tovek = szo.slice(0, -1) + "á";
  else if (alacsony.endsWith("e")) tovek = szo.slice(0, -1) + "é";
  return [...szavak, tovek + toldalek].join(" ");
}

function relativIdo(iso) {
  const masodperc = (Date.now() - new Date(iso).getTime()) / 1000;
  if (masodperc < 60) return "most";
  if (masodperc < 3600) return `${Math.floor(masodperc / 60)} perce`;
  if (masodperc < 86400) return `${Math.floor(masodperc / 3600)} órája`;
  if (masodperc < 7 * 86400) return `${Math.floor(masodperc / 86400)} napja`;
  return new Date(iso).toLocaleDateString("hu-HU");
}

let toastIdozito = null;
function toast(szoveg) {
  const tarolo = document.getElementById("toast");
  tarolo.replaceChildren(el("div", { class: "toast" }, szoveg));
  clearTimeout(toastIdozito);
  toastIdozito = setTimeout(() => tarolo.replaceChildren(), 4000);
}

// --- Komponensek ---------------------------------------------------------------------------

function monogram(nev) {
  return nev.split(" ").slice(0, 2).map((resz) => resz[0]).join("").toUpperCase();
}

function avatarSzin(azonosito) {
  let osszeg = 0;
  for (const c of azonosito) osszeg += c.charCodeAt(0);
  return osszeg % 6;
}

function avatar(szemely, extra) {
  return el("span", Object.assign(
    { class: `avatar avatar-${avatarSzin(szemely.id)}`, "aria-hidden": "true" }, extra || {},
  ), monogram(szemely.nev));
}

function szemely(m) {
  return el("div", { class: "szemely" },
    avatar(m),
    el("div", { class: "szemely-adatok" },
      el("span", { class: "szemely-nev" }, m.nev),
      el("span", { class: "masodlagos-szoveg" }, m.egyseg)));
}

function kartya(k) {
  const kat = kategoriaAdat(k.kategoria);
  const nyilvanos = k.lathatosag === "nyilvanos";
  const felirat = nyilvanos ? "Nyilvános" : "Privát";
  return el("article", { class: `kartya kat-${k.kategoria}` },
    el("div", { class: "kartya-szemelyek" },
      szemely(k.kuldo), el("span", { "aria-hidden": "true" }, "→"), szemely(k.cimzett)),
    el("div", { class: "kartya-kozep" },
      el("span", { class: "chip" }, `${kat.emoji} ${kat.nev}`),
      el("span", { role: "img", "aria-label": felirat, title: felirat }, nyilvanos ? "🌐" : "🔒")),
    el("p", { class: "uzenet" }, `„${k.uzenet}”`),
    el("div", { class: "kartya-lab" },
      k.letrehozva
        ? el("time", { class: "masodlagos-szoveg", datetime: k.letrehozva,
                       title: new Date(k.letrehozva).toLocaleString("hu-HU") }, relativIdo(k.letrehozva))
        : el("span", { class: "masodlagos-szoveg" }, "most"),
      k.tapsok === undefined ? null : tapsGomb(k)));
}

// 👏 taps (SZ-10): egy kattintás tapsol, a következő visszavon; a szerver dönti el, láthatja-e a köszönetet.
function tapsGomb(k) {
  const gomb = el("button", { type: "button", class: "taps", onclick: async () => {
    const valasz = await api("POST", `/api/koszonetek/${k.id}/taps`);
    if (valasz.allapot === 200) {
      k.tapsolt = valasz.tartalom.tapsolt;
      k.tapsok = valasz.tartalom.tapsok;
      frissit();
      gomb.classList.remove("pop");
      void gomb.offsetWidth;
      gomb.classList.add("pop");
    } else if (valasz.allapot === 401) {
      ugrik("#/belepes");
    } else {
      toast("Erre a köszönetre nem tapsolhatsz.");
    }
  } });
  function frissit() {
    gomb.setAttribute("aria-pressed", String(Boolean(k.tapsolt)));
    gomb.setAttribute("aria-label", `Taps (${k.tapsok})`);
    gomb.textContent = `👏 ${k.tapsok}`;
  }
  frissit();
  return gomb;
}

// Ha a link az éppen megnyitott oldalra mutat, a hash nem változik; ilyenkor az oldal újratöltődik
// (pl. az „Új köszönet” menüpont újraindítja a varázslót).
function ujratolt(hash) {
  return (esemeny) => {
    if (location.hash === hash) { esemeny.preventDefault(); utvonalvalaszto(); }
  };
}

// Űrlaphiba a mező alatt: ikon + szöveg, piros; a `mutat("")` elrejti.
function hibaSor(azonosito) {
  const szoveg = el("span", {});
  const sor = el("p", { class: "hiba", id: azonosito, role: "alert", hidden: true },
    el("span", { "aria-hidden": "true" }, "⚠️"), szoveg);
  sor.mutat = (uzenet) => { szoveg.textContent = uzenet; sor.hidden = !uzenet; };
  return sor;
}

function ujKoszonetGomb() {
  return el("a", { class: "gomb gomb-elsodleges", href: "#/uj", onclick: ujratolt("#/uj") }, "+ Új köszönet");
}

function uresAllapot(emoji, szoveg, gomb) {
  return el("div", { class: "ures" },
    el("div", { class: "ures-emoji", "aria-hidden": "true" }, emoji),
    el("p", {}, szoveg),
    gomb || ujKoszonetGomb());
}

// Az ikon csak a mobil alsó tab-sávban látszik (ikon + rövid felirat).
function menupont(hash, felirat, aktiv, ikon) {
  return el("a", { href: hash, onclick: ujratolt(hash), "aria-current": hash === aktiv ? "page" : null },
    el("span", { class: "menu-ikon", "aria-hidden": "true" }, ikon), el("span", {}, felirat));
}

// Csengő a fejlécben (SZ-12): olvasatlan-számláló, legördülő panel, olvasottnak jelölés.
function ertesitesek() {
  let lista = [];
  const szamlalo = el("span", { class: "ertesites-szamlalo", "aria-hidden": "true", hidden: true });
  const gomb = el("button", { type: "button", class: "ikon-gomb ertesites-gomb", "aria-label": "Értesítések",
    "aria-expanded": "false", "aria-controls": "ertesites-panel", onclick: () => {
      panel.hidden = !panel.hidden;
      gomb.setAttribute("aria-expanded", String(!panel.hidden));
      if (!panel.hidden) betolt();
    } }, el("span", { "aria-hidden": "true" }, "🔔"), szamlalo);
  const mindOlvasott = el("button", { type: "button", class: "gomb gomb-szoveges", hidden: true,
    onclick: async () => {
      const valasz = await api("POST", "/api/ertesitesek/olvasott-mind");
      if (valasz.allapot === 200) { lista.forEach((n) => { n.olvasott = true; }); kirajzol(); }
    } }, "Mind olvasott");
  const uresSor = el("p", { class: "ertesites-ures" }, "Nincs új értesítés.");
  const elemek = el("ul", { class: "ertesites-lista" });
  const panel = el("div", { class: "ertesites-panel", id: "ertesites-panel", role: "region",
    "aria-label": "Értesítések", hidden: true },
    el("div", { class: "ertesites-fej" }, el("h2", {}, "Értesítések"), mindOlvasott), uresSor, elemek);

  function elem(n) {
    const kat = kategoriaAdat(n.kategoria);
    return el("li", { class: "ertesites-sor" + (n.olvasott ? "" : " olvasatlan") },
      el("button", { type: "button", class: "ertesites-elem", onclick: () => megnyit(n) },
        n.olvasott ? null : el("span", { class: "rejtett-szoveg" }, "Olvasatlan: "),
        el("span", { class: "szemely-nev" }, `${n.kuldo.nev} → ${n.cimzett.nev}`),
        el("span", { class: "masodlagos-szoveg" },
          `${kat.emoji} ${kat.nev} · ${new Date(n.koszonet_letrehozva).toLocaleString("hu-HU")}`),
        el("span", { class: "ertesites-elonezet" }, `„${n.elonezet}”`)));
  }

  function kirajzol() {
    const olvasatlan = lista.filter((n) => !n.olvasott).length;
    szamlalo.textContent = String(olvasatlan);
    szamlalo.hidden = olvasatlan === 0;
    gomb.setAttribute("aria-label", olvasatlan ? `Értesítések, ${olvasatlan} olvasatlan` : "Értesítések");
    uresSor.hidden = lista.length > 0;
    mindOlvasott.hidden = olvasatlan === 0;
    elemek.replaceChildren(...lista.map(elem));
  }

  async function megnyit(n) {
    if (n.olvasott) return;
    const valasz = await api("POST", `/api/ertesitesek/${n.id}/olvasott`);
    if (valasz.allapot === 200) { n.olvasott = true; kirajzol(); }
  }

  async function betolt() {
    const valasz = await api("GET", "/api/ertesitesek");
    if (valasz.allapot === 200) { lista = valasz.tartalom; kirajzol(); }
  }

  panel.addEventListener("keydown", (esemeny) => {
    if (esemeny.key === "Escape") { panel.hidden = true; gomb.setAttribute("aria-expanded", "false"); gomb.focus(); }
  });
  kirajzol();
  betolt();
  return el("div", { class: "ertesites" }, gomb, panel);
}

// A panelen belüli kattintás (akkor is, ha a célelem közben újrarajzolódott) nem zárja be a panelt.
document.addEventListener("click", (esemeny) => {
  for (const panel of document.querySelectorAll(".ertesites-panel")) {
    if (!panel.hidden && !esemeny.composedPath().includes(panel.parentElement)) {
      panel.hidden = true;
      panel.parentElement.querySelector("button").setAttribute("aria-expanded", "false");
    }
  }
});

function keret(aktiv, ...tartalom) {
  const en = allapot.en;
  return [
    el("header", { class: "fejlec" },
      el("div", { class: "fejlec-belso" },
        el("a", { class: "jel", href: "#/fal", onclick: ujratolt("#/fal"), "aria-label": "Kudos – kezdőlap" },
          el("span", { class: "jel-ek", "aria-hidden": "true" }), "Kudos"),
        el("nav", { class: "fomenu", "aria-label": "Főmenü" },
          menupont("#/fal", "Fal", aktiv, "🏠"), menupont("#/uj", "Új köszönet", aktiv, "✍️"),
          menupont("#/sajat", "Saját", aktiv, "👤"),
          en.vezeto ? menupont("#/csapat", "Csapat", aktiv, "👥") : null),
        ertesitesek(),
        avatar(en, { class: `avatar avatar-${avatarSzin(en.id)} fejlec-avatar`, "aria-hidden": null, role: "img",
                     "aria-label": `Bejelentkezve: ${en.nev}`, title: en.nev }))),
    el("div", { class: "demo-sav" },
      el("div", { class: "demo-sav-belso" },
        el("p", {}, `DEMO belépés: ${en.nev} · ${en.egyseg}`),
        el("button", { type: "button", class: "gomb gomb-szoveges", onclick: kilepes }, "Váltás"))),
    el("main", { class: "tartalom" }, ...tartalom),
  ];
}

// --- Oldalak -------------------------------------------------------------------------------

async function belepesOldal() {
  document.title = "Belépés – Kudos (DEMO)";
  const { tartalom: munkatarsak } = await api("GET", "/api/munkatarsak");
  gyoker.replaceChildren(
    el("header", { class: "fejlec" },
      el("div", { class: "fejlec-belso" },
        el("span", { class: "jel" }, el("span", { class: "jel-ek", "aria-hidden": "true" }), "Kudos"))),
    el("main", { class: "tartalom" },
      el("div", { class: "belepes-fej" },
        el("p", { class: "demo-jelveny" }, "DEMO – szimulált belépés, jelszó nincs"),
        el("h1", {}, "Belépés mint…")),
      el("ul", { class: "belepes-lista", "aria-label": "Munkatársak" },
        munkatarsak.map((m) => el("li", {},
          el("button", { type: "button", class: "belepes-gomb", onclick: () => belepes(m.id) },
            avatar(m),
            el("span", { class: "szemely-adatok" },
              el("span", { class: "szemely-nev" }, m.nev),
              el("span", { class: "masodlagos-szoveg" }, `${m.beosztas} · ${m.egyseg}`))))))));
}

async function belepes(azonosito) {
  const valasz = await api("POST", "/api/belepes", { id: azonosito });
  if (valasz.allapot === 200) ugrik("#/fal");
}

async function kilepes() {
  await api("POST", "/api/kilepes");
  allapot.en = null;
  ugrik("#/belepes");
}

async function falOldal() {
  document.title = "Kudos fal – Kudos (DEMO)";
  let kategoria = "";
  let sorszam = 0;
  const valaszto = kategoriaSzuro("fal-kategoria");
  const lista = el("div", {});

  function szuroTorlese() {
    return el("button", { type: "button", class: "gomb gomb-elsodleges", onclick: () => {
      valaszto.value = "";
      kategoria = "";
      frissit();
    } }, "Szűrő törlése");
  }

  function kirajzol(koszonetek) {
    if (koszonetek.length) lista.replaceChildren(el("div", { class: "racs" }, koszonetek.map(kartya)));
    else if (kategoria) lista.replaceChildren(uresAllapot("🔍", "Nincs találat ebben a kategóriában.", szuroTorlese()));
    else lista.replaceChildren(uresAllapot("🌱", "Még nincs nyilvános köszönet a falon. Légy te az első!"));
  }

  async function frissit() {
    const szam = ++sorszam;
    const valasz = await api("GET", `/api/fal?${new URLSearchParams({ kategoria })}`);
    if (szam !== sorszam) return;
    if (valasz.allapot === 401) { ugrik("#/belepes"); return; }
    if (valasz.allapot === 200) kirajzol(valasz.tartalom);
  }

  valaszto.addEventListener("change", () => { kategoria = valaszto.value; frissit(); });
  gyoker.replaceChildren(...keret("#/fal",
    el("div", { class: "oldalcim" }, el("h1", {}, "Kudos fal"), ujKoszonetGomb()),
    el("div", { class: "szurosor szurosor-egy" }, szuroMezo("Kategória", "fal-kategoria", valaszto)),
    lista));
  await frissit();
}

// --- Saját köszöneteim ------------------------------------------------------------------------

const IDOSZAKOK = [["7", "Elmúlt 7 nap"], ["30", "Elmúlt 30 nap"], ["osszes", "Összes"]];

function kategoriaSzuro(azonosito) {
  return el("select", { class: "beviteli", id: azonosito },
    el("option", { value: "" }, "Minden kategória"),
    KATEGORIAK.map((k) => el("option", { value: k.kod }, `${k.emoji} ${k.nev}`)));
}

function szuroMezo(felirat, azonosito, vezerlo) {
  return el("div", { class: "szuro" }, el("label", { for: azonosito }, felirat), vezerlo);
}

async function sajatOldal(irany) {
  document.title = "Saját köszönetek – Kudos (DEMO)";
  const szurok = { q: "", kategoria: "", idoszak: "osszes" };
  let sorszam = 0;

  const kereso = el("input", { class: "beviteli", id: "sajat-kereso", type: "text", autocomplete: "off" });
  const kategoriaValaszto = kategoriaSzuro("sajat-kategoria");
  const idoszakValaszto = el("select", { class: "beviteli", id: "sajat-idoszak" },
    IDOSZAKOK.map(([kod, felirat]) => el("option", { value: kod }, felirat)));
  idoszakValaszto.value = szurok.idoszak;

  const fulek = el("nav", { class: "fulek", "aria-label": "Saját köszönetek" });
  const lista = el("div", {});

  function szurokTorlese() {
    return el("button", { type: "button", class: "gomb gomb-elsodleges", onclick: () => {
      kereso.value = ""; kategoriaValaszto.value = ""; idoszakValaszto.value = "osszes";
      Object.assign(szurok, { q: "", kategoria: "", idoszak: "osszes" });
      frissit();
    } }, "Szűrők törlése");
  }

  function kirajzol({ koszonetek, darab }) {
    fulek.replaceChildren(...[["kapott", "Kapott"], ["kuldott", "Küldött"]].map(([kod, felirat]) =>
      el("a", { href: `#/sajat/${kod}`, "aria-current": kod === irany ? "page" : null },
        `${felirat} (${darab[kod]})`)));
    if (koszonetek.length) {
      lista.replaceChildren(el("div", { class: "racs" }, koszonetek.map(kartya)));
    } else if (darab[irany] === 0) {
      lista.replaceChildren(irany === "kapott"
        ? uresAllapot("🌱", "Még nem kaptál köszönetet. Te már küldtél ma valakinek?")
        : uresAllapot("✉️", "Még nem küldtél köszönetet. Kezdd el most!"));
    } else {
      lista.replaceChildren(uresAllapot("🔍", "Nincs találat a megadott szűrőkkel.", szurokTorlese()));
    }
  }

  async function frissit() {
    const szam = ++sorszam;
    const valasz = await api("GET", `/api/koszonetek/${irany}?${new URLSearchParams(szurok)}`);
    if (szam !== sorszam) return;
    if (valasz.allapot === 401) { ugrik("#/belepes"); return; }
    if (valasz.allapot === 200) kirajzol(valasz.tartalom);
  }

  kereso.addEventListener("input", () => { szurok.q = kereso.value; frissit(); });
  kategoriaValaszto.addEventListener("change", () => { szurok.kategoria = kategoriaValaszto.value; frissit(); });
  idoszakValaszto.addEventListener("change", () => { szurok.idoszak = idoszakValaszto.value; frissit(); });

  gyoker.replaceChildren(...keret("#/sajat",
    el("div", { class: "oldalcim" }, el("h1", {}, "Saját köszönetek")),
    fulek,
    el("div", { class: "szurosor" },
      szuroMezo("Keresés a köszönetekben", "sajat-kereso", kereso),
      szuroMezo("Kategória", "sajat-kategoria", kategoriaValaszto),
      szuroMezo("Időszak", "sajat-idoszak", idoszakValaszto)),
    lista));
  await frissit();
}

// --- Csapatköszönetek (csak vezetőknek) ---------------------------------------------------------

// Mutató-kártya: nagy szám és címke; a csoport neve a képernyőolvasónak szól.
function mutatoKartya(csoportNev, szam, cimke) {
  return el("div", { class: "mutato", role: "group", "aria-label": csoportNev },
    el("span", { class: "mutato-szam" }, String(szam)), " ", el("span", { class: "mutato-cimke" }, cimke));
}

// A vezetői statisztika (SZ-14): mutatók, kategória-megoszlás tisztán CSS-sávokkal, Top 3.
function statisztikaDobozok(adat) {
  const legtobb = Math.max(1, ...adat.kategoriak.map((k) => k.darab));
  const savok = el("ul", { class: "savok", "aria-label": "Köszönetek kategóriák szerint" },
    adat.kategoriak.map((k) => {
      const kat = kategoriaAdat(k.kategoria);
      const kitoltes = el("span", { class: "sav-kitoltes" });
      kitoltes.style.width = `${(k.darab / legtobb) * 100}%`;
      return el("li", { class: `sav-sor kat-${k.kategoria}` },
        el("span", { class: "sav-cimke" }, `${kat.emoji} ${kat.nev}`),
        el("span", { class: "sav" }, kitoltes),
        el("span", { class: "sav-darab" }, String(k.darab)));
    }));
  const helyezesek = ["🥇", "🥈", "🥉"];
  const top3 = adat.top3.length
    ? el("ol", { class: "top3", "aria-label": "Legtöbb köszönetet kapott" }, adat.top3.map((t, i) =>
      el("li", { class: "top3-sor" },
        el("span", { class: "top3-helyezes", "aria-hidden": "true" }, helyezesek[i]),
        el("span", { class: "rejtett-szoveg" }, `${i + 1}. hely: `),
        avatar(t),
        el("span", { class: "szemely-adatok" },
          el("span", { class: "szemely-nev" }, t.nev),
          el("span", { class: "masodlagos-szoveg" }, t.egyseg)),
        el("span", { class: "top3-darab" }, `${t.darab} köszönet`))))
    : el("p", { class: "stat-ures" }, "Ebben az időszakban még senki nem kapott köszönetet a körödben.");
  return [
    el("div", { class: "mutatok" },
      mutatoKartya("Kapott köszönet", adat.kapott, "kapott köszönet"),
      mutatoKartya("Küldött köszönet", adat.kuldott, "küldött köszönet"),
      mutatoKartya("Aktív küldő", adat.aktiv_kuldok, "aktív küldő"),
      mutatoKartya("Összes köszönet", adat.osszes, "összes köszönet")),
    el("div", { class: "stat-racs" },
      el("section", { class: "stat-doboz" }, el("h2", {}, "Köszönetek kategóriák szerint"), savok),
      el("section", { class: "stat-doboz" }, el("h2", {}, "Legtöbb köszönetet kapott"), top3)),
  ];
}

async function csapatOldal() {
  document.title = "Csapatköszönetek – Kudos (DEMO)";
  const cim = el("div", { class: "oldalcim" }, el("h1", {}, "Csapatköszönetek"));
  if (!allapot.en.vezeto) {
    gyoker.replaceChildren(...keret("#/csapat", cim,
      el("p", { class: "hiba", role: "alert" },
        el("span", { "aria-hidden": "true" }, "⚠️"), el("span", {}, "Ehhez a nézethez vezetői jogosultság kell."))));
    return;
  }

  const alap = { q: "", kategoria: "", idoszak: "30" };
  const szurok = { ...alap };
  let sorszam = 0;

  const kereso = el("input", { class: "beviteli", id: "csapat-kereso", type: "text", autocomplete: "off" });
  const kategoriaValaszto = kategoriaSzuro("csapat-kategoria");
  const idoszakValaszto = el("select", { class: "beviteli", id: "csapat-idoszak" },
    IDOSZAKOK.map(([kod, felirat]) => el("option", { value: kod }, felirat)));
  idoszakValaszto.value = alap.idoszak;
  const lista = el("div", {});
  const statisztika = el("div", { class: "statisztika" });

  function szurokTorlese() {
    return el("button", { type: "button", class: "gomb gomb-elsodleges", onclick: () => {
      kereso.value = ""; kategoriaValaszto.value = ""; idoszakValaszto.value = alap.idoszak;
      Object.assign(szurok, alap);
      frissit();
      statFrissit();
    } }, "Szűrők törlése");
  }

  function kirajzol(koszonetek) {
    lista.replaceChildren(koszonetek.length
      ? el("div", { class: "racs" }, koszonetek.map(kartya))
      : uresAllapot("🔍", "Nincs találat a megadott szűrőkkel.", szurokTorlese()));
  }

  async function frissit() {
    const szam = ++sorszam;
    const valasz = await api("GET", `/api/csapat?${new URLSearchParams(szurok)}`);
    if (szam !== sorszam) return;
    if (valasz.allapot === 401) { ugrik("#/belepes"); return; }
    if (valasz.allapot === 200) kirajzol(valasz.tartalom);
  }

  // Az időszak a statisztikára is hat, a keresőszó és a kategória csak a listára.
  let statSorszam = 0;
  async function statFrissit() {
    const szam = ++statSorszam;
    const valasz = await api("GET", `/api/csapat/statisztika?${new URLSearchParams({ idoszak: szurok.idoszak })}`);
    if (szam !== statSorszam) return;
    if (valasz.allapot === 200) statisztika.replaceChildren(...statisztikaDobozok(valasz.tartalom));
  }

  kereso.addEventListener("input", () => { szurok.q = kereso.value; frissit(); });
  kategoriaValaszto.addEventListener("change", () => { szurok.kategoria = kategoriaValaszto.value; frissit(); });
  idoszakValaszto.addEventListener("change", () => { szurok.idoszak = idoszakValaszto.value; frissit(); statFrissit(); });

  gyoker.replaceChildren(...keret("#/csapat", cim, statisztika,
    el("div", { class: "szurosor" },
      szuroMezo("Keresés a köszönetekben", "csapat-kereso", kereso),
      szuroMezo("Kategória", "csapat-kategoria", kategoriaValaszto),
      szuroMezo("Időszak", "csapat-idoszak", idoszakValaszto)),
    lista));
  await Promise.all([frissit(), statFrissit()]);
}

// --- Új köszönet: 3 lépéses varázsló --------------------------------------------------------

function varazsloKezdoAllapot() {
  return { lepes: 1, cimzett: null, keresoSzoveg: "", kategoria: null, uzenet: "",
           lathatosag: "privat", hiba: null, kuldes: false };
}

function ujOldal() {
  document.title = "Új köszönet – Kudos (DEMO)";
  varazslo = varazsloKezdoAllapot();
  rajzolVarazslo();
}

function rajzolVarazslo() {
  const v = varazslo;
  const lepesek = ["Kinek?", "Mit?", "Ellenőrzés"];
  const tartalom = v.lepes === 1 ? lepes1() : v.lepes === 2 ? lepes2() : lepes3();
  gyoker.replaceChildren(...keret("#/uj",
    el("div", { class: "varazslo" },
      el("h1", {}, "Új köszönet"),
      el("ol", { class: "lepesek", "aria-label": "Lépések" },
        lepesek.map((nev, i) => el("li", { class: "lepes", "aria-current": v.lepes === i + 1 ? "step" : null },
          el("span", { class: "lepes-szam" }, String(i + 1)), nev))),
      tartalom.elem)));
  tartalom.fokusz();
}

function lepes1() {
  const v = varazslo;
  let talalatok = [];
  let aktiv = -1;
  let nyitva = false;
  let keresesSzam = 0;

  const mezo = el("input", {
    class: "beviteli", id: "kereso", type: "text", role: "combobox", autocomplete: "off",
    "aria-autocomplete": "list", "aria-expanded": "false", "aria-controls": "talalatok",
  });
  mezo.value = v.keresoSzoveg;
  const lista = el("ul", { class: "talalatok", id: "talalatok", role: "listbox", "aria-label": "Találatok", hidden: true });
  const nincs = el("p", { class: "nincs-talalat", hidden: true }, "Nincs találat");

  function frissit() {
    const vanTalalat = nyitva && talalatok.length > 0;
    lista.hidden = !vanTalalat;
    nincs.hidden = !(nyitva && talalatok.length === 0);
    mezo.setAttribute("aria-expanded", String(vanTalalat));
    if (vanTalalat && aktiv >= 0) mezo.setAttribute("aria-activedescendant", `talalat-${aktiv}`);
    else mezo.removeAttribute("aria-activedescendant");
    lista.replaceChildren(...talalatok.map((m, i) => el("li", {
      class: "talalat", id: `talalat-${i}`, role: "option", "aria-selected": String(i === aktiv),
      onclick: () => kivalaszt(m),
    }, avatar(m),
      el("span", { class: "szemely-adatok" },
        el("span", { class: "szemely-nev" }, m.nev),
        el("span", { class: "masodlagos-szoveg" }, `${m.beosztas} · ${m.egyseg}`)))));
  }

  async function keres() {
    const szam = ++keresesSzam;
    const szoveg = mezo.value.trim();
    if (!szoveg) { talalatok = []; nyitva = false; frissit(); return; }
    const valasz = await api("GET", "/api/munkatarsak/kereses?q=" + encodeURIComponent(szoveg));
    if (szam !== keresesSzam) return;
    talalatok = valasz.allapot === 200 ? valasz.tartalom : [];
    aktiv = -1;
    nyitva = true;
    frissit();
  }

  function kivalaszt(munkatars) {
    v.cimzett = munkatars;
    v.lepes = 2;
    rajzolVarazslo();
  }

  mezo.addEventListener("input", () => { v.keresoSzoveg = mezo.value; keres(); });
  mezo.addEventListener("keydown", (esemeny) => {
    if (esemeny.key === "ArrowDown") {
      esemeny.preventDefault();
      if (!nyitva) { keres(); return; }
      if (talalatok.length) { aktiv = (aktiv + 1) % talalatok.length; frissit(); }
    } else if (esemeny.key === "ArrowUp") {
      esemeny.preventDefault();
      if (nyitva && talalatok.length) { aktiv = (aktiv - 1 + talalatok.length) % talalatok.length; frissit(); }
    } else if (esemeny.key === "Enter") {
      if (nyitva && aktiv >= 0) { esemeny.preventDefault(); kivalaszt(talalatok[aktiv]); }
    } else if (esemeny.key === "Escape") {
      // Az Esc csak a találati listát zárja be, a mező tartalma megmarad.
      esemeny.preventDefault();
      if (nyitva) { nyitva = false; frissit(); }
    }
  });

  if (v.keresoSzoveg.trim()) keres();

  return {
    elem: el("section", {},
      el("h2", {}, "Kinek?"),
      el("div", { class: "mezo" },
        el("label", { for: "kereso" }, KERESO_FELIRAT),
        mezo, lista, nincs)),
    fokusz: () => mezo.focus(),
  };
}

const KERESO_FELIRAT = "Keresés név, egység vagy e-mail alapján";

function lepes2() {
  const v = varazslo;
  const valaszto = (csoportNev, csoportKod, elemek, kivalasztott, valasztas, extraOsztaly) => {
    const gombok = elemek.map((elem) => el("button", {
      type: "button", role: "radio",
      class: `${extraOsztaly(elem)}`,
      "aria-checked": String(elem.kod === kivalasztott),
      onclick: () => {
        valasztas(elem.kod);
        gombok.forEach((g, i) => g.setAttribute("aria-checked", String(elemek[i].kod === elem.kod)));
      },
    }, ...elem.tartalom));
    return el("div", { role: "radiogroup", "aria-label": csoportNev, class: csoportKod }, gombok);
  };

  const kategoriaHiba = hibaSor("kategoria-hiba");
  const uzenetHiba = hibaSor("uzenet-hiba");

  const kategoriak = valaszto("Kategória", "kategoriak",
    KATEGORIAK.map((k) => ({ kod: k.kod, kat: k, tartalom: [
      el("span", { class: "kategoria-nev" }, `${k.emoji} ${k.nev}`),
      el("span", { class: "masodlagos-szoveg" }, k.leiras)] })),
    v.kategoria, (kod) => { v.kategoria = kod; kategoriaHiba.mutat(""); },
    (elem) => `kategoria-kartya kat-${elem.kod}`);

  const lathatosag = valaszto("Láthatóság", "kapcsolo", [
    { kod: "privat", tartalom: ["🔒 Privát"] },
    { kod: "nyilvanos", tartalom: ["🌐 Nyilvános"] }],
    v.lathatosag, (kod) => { v.lathatosag = kod; }, () => "kapcsolo-gomb");

  const szoveg = el("textarea", { class: "beviteli", id: "uzenet", rows: "5",
                                   "aria-describedby": "uzenet-hiba szamlalo" });
  szoveg.value = v.uzenet;
  const szamlalo = el("p", { class: "szamlalo", id: "szamlalo" });
  function szamol() {
    const hossz = [...szoveg.value].length;
    szamlalo.textContent = `${hossz} / ${MAX_HOSSZ}`;
    szamlalo.className = "szamlalo" + (hossz > MAX_HOSSZ ? " tul" : hossz > 450 ? " figyelmeztet" : "");
  }
  szoveg.addEventListener("input", () => {
    v.uzenet = szoveg.value;
    szamol();
    uzenetHiba.mutat("");
    szoveg.removeAttribute("aria-invalid");
  });
  szamol();

  // A szerver ugyanezeket a szabályokat ellenőrzi (SZ-05, SZ-06); itt a hiba a mező alatt jelenik meg.
  function tovabb() {
    const tiszta = v.uzenet.trim();
    const kategoriaUzenet = v.kategoria ? "" : "Válassz kategóriát.";
    const uzenetUzenet = !tiszta ? "Az üzenet nem lehet üres."
      : [...tiszta].length > MAX_HOSSZ ? `Az üzenet legfeljebb ${MAX_HOSSZ} karakter lehet.` : "";
    kategoriaHiba.mutat(kategoriaUzenet);
    uzenetHiba.mutat(uzenetUzenet);
    if (uzenetUzenet) szoveg.setAttribute("aria-invalid", "true");
    else szoveg.removeAttribute("aria-invalid");
    if (kategoriaUzenet) { kategoriak.querySelector("button").focus(); return; }
    if (uzenetUzenet) { szoveg.focus(); return; }
    v.hiba = null;
    v.lepes = 3;
    rajzolVarazslo();
  }

  return {
    elem: el("section", {},
      el("h2", { tabindex: "-1" }, "Mit?"),
      el("p", { class: "kinek-chip" }, avatar(v.cimzett), el("span", {}, "Kinek: ", el("strong", {}, v.cimzett.nev))),
      el("div", { class: "mezo" }, el("span", { class: "mezo-cim" }, "Kategória"), kategoriak, kategoriaHiba),
      el("div", { class: "mezo" },
        el("label", { for: "uzenet" }, "Üzenet"), szoveg, uzenetHiba, szamlalo),
      el("div", { class: "mezo" }, el("span", { class: "mezo-cim" }, "Láthatóság"), lathatosag),
      el("div", { class: "muveletek" },
        el("button", { type: "button", class: "gomb", onclick: () => { v.lepes = 1; rajzolVarazslo(); } }, "Vissza"),
        el("button", { type: "button", class: "gomb gomb-elsodleges", onclick: tovabb }, "Tovább"))),
    fokusz: () => document.querySelector(".varazslo h2").focus(),
  };
}

function lepes3() {
  const v = varazslo;
  const kuldesGomb = el("button", { type: "button", class: "gomb gomb-elsodleges", onclick: kuldes }, "Küldés");
  kuldesGomb.disabled = v.kuldes;
  const hiba = hibaSor("kuldes-hiba");
  hiba.mutat(v.hiba || "");

  async function kuldes() {
    v.kuldes = true;
    kuldesGomb.disabled = true;
    const valasz = await api("POST", "/api/koszonetek", {
      cimzett_id: v.cimzett.id, kategoria: v.kategoria, uzenet: v.uzenet, lathatosag: v.lathatosag,
    });
    v.kuldes = false;
    if (valasz.allapot === 201) {
      toast(`Köszönetedet elküldtük ${nakNek(v.cimzett.nev)}! 🎉`);
      varazslo = null;
      ugrik("#/sajat/kuldott");
    } else if (valasz.allapot === 401) {
      ugrik("#/belepes");
    } else {
      v.hiba = (valasz.tartalom && valasz.tartalom.hiba) || "A küldés nem sikerült. Próbáld újra.";
      rajzolVarazslo();
    }
  }

  return {
    elem: el("section", {},
      el("h2", { tabindex: "-1" }, "Ellenőrzés"),
      kartya({ kuldo: allapot.en, cimzett: v.cimzett, kategoria: v.kategoria, uzenet: v.uzenet.trim(),
               lathatosag: v.lathatosag, letrehozva: null }),
      hiba,
      el("div", { class: "muveletek" },
        el("button", { type: "button", class: "gomb", onclick: () => { v.lepes = 2; rajzolVarazslo(); } }, "Vissza"),
        kuldesGomb)),
    fokusz: () => document.querySelector(".varazslo h2").focus(),
  };
}

// --- Útvonalválasztó -----------------------------------------------------------------------

async function utvonalvalaszto() {
  const szam = ++utvonalSzamlalo;
  const hash = location.hash || "#/fal";
  const en = await api("GET", "/api/en");
  if (szam !== utvonalSzamlalo) return;
  allapot.en = en.allapot === 200 ? en.tartalom : null;

  if (!allapot.en) {
    if (hash !== "#/belepes") { location.replace("#/belepes"); return; }
    await belepesOldal();
  } else if (hash === "#/belepes") {
    location.replace("#/fal");
  } else if (hash === "#/uj") {
    ujOldal();
  } else if (hash === "#/csapat") {
    await csapatOldal();
  } else if (hash === "#/sajat" || hash.startsWith("#/sajat/")) {
    await sajatOldal(hash === "#/sajat/kuldott" ? "kuldott" : "kapott");
  } else {
    await falOldal();
  }
}

window.addEventListener("hashchange", utvonalvalaszto);
utvonalvalaszto();
