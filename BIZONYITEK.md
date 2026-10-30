# Bizonyíték – Kudos

Elfogadás: ELFOGADVA

Spec verzió: 1.1 · Dátum: 2026-10-30 · Unit: 117 db, ebből zöld: 117 · E2E: 45 db, ebből zöld: 45

## Kritériumok lefedettsége
Jelmagyarázat: **[U]** = unit teszt (`tests/`), **[E]** = böngészős E2E teszt (`tests/e2e/`). Egy EK-t több teszt is igazolhat; az eredmény ✅, ha mindegyik zöld.

| EK | Rövid leírás | Teszt(ek) | Eredmény |
|---|---|---|---|
| EK-01 | Belépés a listából | [U] `test_ek01_a_munkatarslista_belepes_nelkul_is_17_elem`<br>[U] `test_ek01_belepes_utan_az_en_vegpont_u05_t_ad_es_a_suti_vedett`<br>[U] `test_ek01_ismeretlen_azonosito_nem_lephet_be`<br>[U] `test_ek01_kilepes_utan_nincs_munkamenet`<br>[E] `test_s1_ek01_anna_belep_a_listabol`<br>[E] `test_s1_ek01_valtas_kileptet_es_visszavisz_a_belepeshez` | ✅ |
| EK-02 | Belépés nélkül nincs hozzáférés | [U] `test_ek01_a_munkatarslista_belepes_nelkul_is_17_elem`<br>[U] `test_ek02_belepes_nelkul_es_ismeretlen_sutivel_401`<br>[E] `test_s1_ek02_belepes_nelkul_a_belepesi_oldalra_iranyit` | ✅ |
| EK-03 | Címzettkereső | [U] `test_ek03_egyseg_szerint_az_adat_osztaly_5_tagja`<br>[U] `test_ek03_email_reszlet_szerint`<br>[U] `test_ek03_a_bejelentkezett_felhasznalo_nem_szerepel_a_talalatok_kozott`<br>[U] `test_ek03_kis_es_nagybetutol_fuggetlen`<br>[U] `test_ek03_ures_keresoszora_nincs_talalat`<br>[U] `test_ek03_a_beosztas_nem_kereso_mezo`<br>[U] `test_ek03_a_talalatban_latszik_a_nev_a_beosztas_es_az_egyseg`<br>[U] `test_ek03_api_a_bejelentkezett_felhasznalo_nem_szerepel_a_talalatok_kozott`<br>[E] `test_s1_ek03_cimzettkereso_egyseg_email_es_sajat_nev_szerint` | ✅ |
| EK-04 | Kereső billentyűzettel | [E] `test_s1_ek04_kereso_billentyuzettel` | ✅ |
| EK-05 | Varázsló és ellenőrző nézet (1.1-ben módosult) | [E] `test_s1_ek05_ek06_anna_privat_koszonetet_kuld_julianak` | ✅ |
| EK-06 | Sikeres küldés (1.1-ben módosult) | [U] `test_ek06_a_koszonet_az_adatbazisba_kerul`<br>[U] `test_ek06_a_kliens_nem_adhatja_meg_az_idopontot_es_a_kuldot`<br>[U] `test_ek06_alapertelmezett_lathatosag_a_privat`<br>[U] `test_ek06_a_valasz_a_koszonet_adatait_tartalmazza`<br>[U] `test_ek06_ervenytelen_cimzett_kategoria_vagy_lathatosag_nem_mentodik`<br>[U] `test_ek06_a_szolgaltatas_kozvetlenul_is_ment_es_az_idot_a_szerver_adja`<br>[E] `test_s1_ek05_ek06_anna_privat_koszonetet_kuld_julianak` | ✅ |
| EK-07 | Arculati alapok | [U] `test_ek07_a_css_a_root_blokkal_kezdodik`<br>[U] `test_ek07_az_utmutato_osszes_tokenje_definialva_van`<br>[U] `test_ek07_a_root_blokkon_kivul_nincs_beegetett_szin`<br>[U] `test_ek07_nincs_kulso_hivatkozas_es_felugro_ablak_a_felulet_fajljaiban`<br>[E] `test_s1_ek07_arculati_alapok_fejlec_tokenek_nincs_kulso_keres_es_felugro_ablak` | ✅ |
| EK-08 | Önmagának nem küldhet | [U] `test_ek08_onmagnak_es_nem_letezo_cimzettnek_nem_kuldhet`<br>[U] `test_ek08_a_szolgaltatas_is_visszautasitja_az_onmagnak_kuldest`<br>[E] `test_s2_ek08_onmagnak_nem_kuldhet_az_api_sem_engedi` | ✅ |
| EK-09 | Üres üzenet (1.1-ben módosult) | [U] `test_ek09_ures_es_csak_szokozbol_allo_uzenet_nem_kuldheto`<br>[E] `test_s2_ek09_ures_uzenet_hiba_a_mezo_alatt` | ✅ |
| EK-10 | Üzenet hossza és karakterszámláló | [U] `test_ek10_500_karakter_elfogadott_501_nem`<br>[U] `test_ek10_a_hosszt_a_levagott_szoveg_alapjan_szamoljuk`<br>[E] `test_s2_ek10_karakterszamlalo_500_es_501_karakter` | ✅ |
| EK-11 | Kategória nélkül nem küldhető | [U] `test_ek11_kategoria_nelkul_es_ismeretlen_kategoriaval_nem_kuldheto`<br>[E] `test_s2_ek11_kategoria_nelkul_nem_lep_tovabb` | ✅ |
| EK-12 | Napi limit: a 4. köszönet | [U] `test_ek12_a_negyedik_aznapi_koszonet_nem_kuldheto_ugyanannak`<br>[E] `test_s2_ek12_a_negyedik_mai_koszonet_nem_megy_el_de_mas_cimzettnek_igen` | ✅ |
| EK-13 | A napi limit naptári napra vonatkozik | [U] `test_ek13_a_napi_limit_naptari_napra_vonatkozik`<br>[U] `test_ek13_ejfel_ket_kulon_nap_es_mas_cimzett_limitje_fuggetlen`<br>[E] `test_s2_ek13_a_tegnapi_koszonetek_nem_szamitanak_a_mai_limitbe` | ✅ |
| EK-14 | Megjelenés a Küldött és a Kapott listában | [U] `test_ek14_a_koszonet_a_kuldo_kuldott_es_a_cimzett_kapott_listajaban_van`<br>[U] `test_ek14_csak_a_sajat_koszonetek_szerepelnek_a_listakban`<br>[U] `test_ek14_belepes_nelkul_401`<br>[E] `test_s3_ek14_ek21_anna_kuld_es_a_kuldott_listara_erkezik_julia_a_kapottat_latja` | ✅ |
| EK-15 | A kártya tartalma és a szöveg escape-elése (1.1-ben módosult) | [U] `test_ek15_a_kartya_adatai`<br>[E] `test_s3_ek15_a_kartya_tartalma_es_a_szoveg_escape_elese` | ✅ |
| EK-16 | Rendezés: a legújabb elöl | [U] `test_ek16_a_legujabb_van_elol`<br>[U] `test_ek16_azonos_idopontnal_a_nagyobb_azonosito_elol`<br>[E] `test_s3_ek16_a_legujabb_kartya_van_elol` | ✅ |
| EK-17 | Szabad szavas keresés | [U] `test_ek17_az_uzenet_szovegeben_kis_es_nagybetutol_fuggetlenul`<br>[U] `test_ek17_a_kuldo_nevere_is_keres`<br>[U] `test_ek17_nincs_talalat_es_a_darabszam_nem_valtozik`<br>[U] `test_ek17_a_kuldott_listaban_a_cimzett_nevere_keres`<br>[E] `test_s3_ek17_szabad_szavas_kereses` | ✅ |
| EK-18 | Kategóriaszűrő a saját nézetben (1.1-ben módosult) | [U] `test_ek18_kategoriara_szur_az_osszes_kategoria_mindent_mutat`<br>[U] `test_ek18_ismeretlen_kategoria_400`<br>[U] `test_ek18_a_szurok_egyutt_is_mukodnek`<br>[E] `test_s3_ek18_kategoriaszuro_a_sajat_nezetben` | ✅ |
| EK-19 | Időszakszűrő | [U] `test_ek19_7_30_nap_es_osszes`<br>[U] `test_ek19_ismeretlen_idoszak_400`<br>[U] `test_ek19_a_hatar_pontosan_7x24_ora`<br>[E] `test_s3_ek19_idoszakszuro` | ✅ |
| EK-20 | Üres állapot | [U] `test_ek20_ures_adatbazisnal_mindket_lista_ures`<br>[E] `test_s3_ek20_ures_allapot_uj_koszonet_gombbal` | ✅ |
| EK-21 | Küldés után a Küldött lista | [U] `test_ek21_az_uj_koszonet_a_kuldott_lista_elso_eleme`<br>[E] `test_s3_ek14_ek21_anna_kuld_es_a_kuldott_listara_erkezik_julia_a_kapottat_latja` | ✅ |
| EK-22 | A falon csak a nyilvános köszönet jelenik meg | [U] `test_ek22_a_falon_csak_a_nyilvanos_koszonet_jelenik_meg_mindenkinek`<br>[E] `test_s4_ek22_a_falon_csak_a_nyilvanos_koszonet_latszik_mindenkinek` | ✅ |
| EK-23 | Kategóriaszűrő a falon, sorrend (1.1-ben módosult) | [U] `test_ek23_a_legujabb_van_elol_szures_nelkul`<br>[U] `test_ek23_kategoriara_szur`<br>[U] `test_ek23_ismeretlen_kategoria_400`<br>[E] `test_s4_ek23_kategoriaszuro_a_falon` | ✅ |
| EK-24 | Taps és visszavonás | [U] `test_ek24_taps_be_majd_ki`<br>[U] `test_ek24_a_sajat_listakon_is_latszik_a_taps_allapota`<br>[U] `test_ek24_belepes_nelkul_401`<br>[E] `test_s4_ek24_taps_es_visszavonas` | ✅ |
| EK-25 | Egy személy egy tapsa, a küldő és a címzett is tapsolhat | [U] `test_ek25_a_kuldo_a_cimzett_es_masok_is_tapsolhatnak_egyszer`<br>[U] `test_ek25_az_adatbazis_nem_enged_ketszeres_tapsot`<br>[U] `test_ek25_parhuzamos_kerések_sem_hagynak_duplikatumot`<br>[E] `test_s4_ek25_negy_szemely_negy_taps` | ✅ |
| EK-26 | Nem látható köszönetre nem lehet tapsolni | [U] `test_ek26_illetektelen_nem_tapsolhat_a_privat_koszonetre`<br>[U] `test_ek26_a_jogosult_vezetok_a_kuldo_es_a_cimzett_tapsolhat`<br>[U] `test_ek26_nem_letezo_koszonetre_404`<br>[U] `test_ek26_a_felettesek_lancat_a_vezeto_id_adja`<br>[U] `test_ek26_lathatosagi_szabaly`<br>[E] `test_s4_ek26_privat_koszonetre_csak_a_lathato_szemelyek_tapsolhatnak` | ✅ |
| EK-27 | Mobil elrendezés: alsó tab-sáv, egyoszlopos rács | [E] `test_s4_ek27_mobil_elrendezes_also_tab_sav_es_egyoszlopos_racs` | ✅ |
| EK-28 | Billentyűzetes kezelés és látható fókusz | [E] `test_s4_ek28_billentyuzetes_kezeles_es_latható_fokusz` | ✅ |
| EK-29 | Alapeset: címzett, közvetlen vezető, B-1 | [U] `test_ek29_cimzett_kozvetlen_vezeto_es_b1_vezeto`<br>[U] `test_ek29_a_sikertelen_kuldes_nem_hagy_ertesitest`<br>[U] `test_ek29_az_adatbazis_sem_enged_ketszeres_ertesitest`<br>[U] `test_ek29_a_cimzettek_fuggveny_a_szervezetbol_szamol`<br>[E] `test_s5_ek29_anna_koszonete_utan_julia_katalin_es_eszter_ertesitest_kap_laszlo_nem` | ✅ |
| EK-30 | Aki több szerepben érintett, egy értesítést kap | [U] `test_ek30_aki_tobb_szerepben_erintett_egy_ertesitest_kap` | ✅ |
| EK-31 | B-1 címzett: nincs B-1 vezető, a board tag közvetlen vezetőként értesül | [U] `test_ek31_b1_cimzettnek_nincs_b1_vezetoje_a_board_tag_kozvetlen_vezetokent_kap` | ✅ |
| EK-32 | Vezető nélküli címzett | [U] `test_ek32_vezeto_nelkuli_cimzett_csak_maga_kap` | ✅ |
| EK-33 | A küldő nem kap értesítést a saját köszönetéről | [U] `test_ek33_a_kuldo_nem_kap_ertesitest_a_sajat_koszonetererol`<br>[U] `test_ek33_tovabbi_esetek_a_szabalyok_kombinacioja` | ✅ |
| EK-34 | Csengő, számláló és az értesítés tartalma (1.1-ben módosult) | [U] `test_ek34_a_lista_tartalma_legujabb_elol_es_az_elonezet`<br>[U] `test_ek34_az_elonezet_a_karaktereket_nem_a_bajtokat_szamolja`<br>[U] `test_ek34_mas_munkatars_ertesitesi_listaja_ures`<br>[E] `test_s5_ek34_csengo_szamlalo_es_az_ertesites_tartalma` | ✅ |
| EK-35 | Olvasottnak jelölés | [U] `test_ek35_egy_ertesites_megnyitasa_olvasottra_allitja`<br>[U] `test_ek35_mind_olvasott_csak_a_sajat_ertesiteseket_erinti`<br>[U] `test_ek35_mas_ertesiteset_nem_lehet_olvasottra_allitani`<br>[U] `test_ek35_belepes_nelkul_401`<br>[E] `test_s5_ek35_megnyitas_es_mind_olvasott`<br>[E] `test_s5_ek35_billentyuzettel_is_megnyithato_az_ertesites` | ✅ |
| EK-36 | Nem vezető nem éri el | [U] `test_ek36_vezeto_az_akinek_van_beosztottja`<br>[U] `test_ek36_nem_vezeto_403_mindket_vegpontra`<br>[U] `test_ek36_minden_alkalmazott_403_minden_vezeto_200`<br>[U] `test_ek36_belepes_nelkul_401`<br>[U] `test_ek36_az_en_vegpont_jelzi_hogy_vezeto_e`<br>[U] `test_ek36_a_szolgaltatas_is_ellenorzi_a_jogosultsagot`<br>[E] `test_s6_ek36_nem_vezeto_nem_ereti_el_a_csapat_nezetet` | ✅ |
| EK-37 | B-2 vezető: csak a saját köre, privátokkal együtt | [U] `test_ek37_a_kor_a_vezeto_es_minden_beosztottja_barmilyen_melysegben`<br>[U] `test_ek37_osztalyvezeto_csak_a_sajat_korenek_koszonetet_latja_privatokkal_egyutt`<br>[U] `test_ek37_a_kartya_a_nezo_taps_allapotat_is_tartalmazza`<br>[E] `test_s6_ek37_katalin_az_adat_osztaly_koszonetet_latja_a_fejlesztesi_osztaly_beloleit_nem` | ✅ |
| EK-38 | Mélyebb kör: B-1 és B vezető | [U] `test_ek37_a_kor_a_vezeto_es_minden_beosztottja_barmilyen_melysegben`<br>[U] `test_ek38_foosztalyvezeto_es_board_tag_az_egesz_alatta_levo_kort_latja`<br>[U] `test_ek38_masik_osztalyvezeto_a_sajat_korenek_koszonetet_latja`<br>[E] `test_s6_ek38_foosztalyvezeto_board_tag_es_a_masik_osztalyvezetok` | ✅ |
| EK-39 | Más kör adata közvetlen kéréssel sem érhető el | [U] `test_ek39_extra_parameterek_nem_valtoztatjak_a_kort`<br>[U] `test_ek39_idegen_kor_privat_koszonetere_nem_lehet_tapsolni`<br>[E] `test_s6_ek39_mas_kor_adata_kozvetlen_keressel_sem_erheto_el` | ✅ |
| EK-40 | Keresés és szűrés a vezetői nézetben (1.1-ben módosult) | [U] `test_ek40_az_alapertelmezett_idoszak_30_nap`<br>[U] `test_ek40_kereses_a_kuldo_es_a_cimzett_nevere`<br>[U] `test_ek40_kategoriaszuro_es_a_szurok_egyutt`<br>[U] `test_ek40_ismeretlen_szuroertek_400`<br>[E] `test_s6_ek40_kereses_es_szurok_a_vezetoi_nezetben` | ✅ |
| EK-41 | A vezető maga is a köre része | [U] `test_ek41_a_vezeto_sajat_koszonetei_is_a_koreben_vannak`<br>[U] `test_ek41_a_beosztott_vezetoje_latja_a_beosztott_kapott_koszonetet`<br>[E] `test_s6_ek41_a_vezeto_maga_is_a_koreben_van` | ✅ |
| EK-42 | Mutatók az alapértelmezett 30 napra | [U] `test_ek42_mutatok_az_alapertelmezett_30_napra`<br>[U] `test_ek42_az_alapertelmezes_a_30_nap`<br>[U] `test_ek42_az_aktiv_kuldok_kulonbozo_szemelyek`<br>[E] `test_s7_ek42_a_negy_mutato_az_alapertelmezett_30_napra` | ✅ |
| EK-43 | Kategória-megoszlás (1.1-ben módosult) | [U] `test_ek43_a_megoszlas_a_negy_kategoria_rogzitett_sorrendjeben`<br>[E] `test_s7_ek43_kategoria_megoszlas_savdiagram` | ✅ |
| EK-44 | Top 3, holtversenyben ábécérendben | [U] `test_ek44_top3_30_napra_holtversenyben_abecerendben`<br>[U] `test_ek44_top3_az_osszes_idoszakra_a_harmadik_helyen_papp_zsofia`<br>[U] `test_ek44_a_top3_elemei_a_korbol_valok_es_legalabb_egy_koszonetet_kaptak`<br>[E] `test_s7_ek44_top3_holtversenyben_abecerendben` | ✅ |
| EK-45 | Időszakváltás a statisztikában (1.1-ben módosult) | [U] `test_ek45_7_napra`<br>[U] `test_ek45_osszes_idoszakra`<br>[U] `test_ek45_ismeretlen_idoszak_400`<br>[U] `test_ek45_a_keresoszo_es_a_kategoria_nem_hat_a_statisztikara`<br>[E] `test_s7_ek45_az_idoszak_valtasa_megvaltoztatja_a_szamokat_es_a_listat`<br>[E] `test_s7_ek45_a_keresoszo_es_a_kategoria_nem_valtoztatja_a_statisztikat` | ✅ |
| EK-46 | A statisztikába nem szivárog más kör adata | [U] `test_ek46_mas_kor_vezetoje_csupa_nullat_kap`<br>[U] `test_ek46_extra_parameterek_nem_valtoztatjak_a_kort`<br>[U] `test_ek46_a_fobb_vezetok_nagyobb_korbol_szamolnak`<br>[U] `test_ek46_nem_vezeto_403_belepes_nelkul_401`<br>[U] `test_ek46_a_mutatok_egyeznek_a_lista_tartalmaval`<br>[E] `test_s7_ek46_mas_kor_adata_nem_szivarog_be`<br>[E] `test_s7_ek46_reszponziv_2x2_mutatok_mobilon` | ✅ |
| EK-47 | A négy Behavioral Anchor kategória (1.1-ben új) | [U] `test_ek47_a_negy_behavioral_anchor_kuldheto_a_regiek_nem`<br>[E] `test_s2_ek47_pontosan_a_negy_behavioral_anchor_latszik` | ✅ |

## Böngészős (E2E) tesztek storynként
Minden teszt új, ideiglenes adatbázissal indított alkalmazást vezérel valódi (Chromium) böngészőben, a `data/munkatarsak.json` neveivel.

| Story | E2E teszt | Mit kattint végig | Eredmény |
|---|---|---|---|
| S1 | `test_s1_ek01_anna_belep_a_listabol` | a lista 17 munkatársat mutat, Horváth Anna belép, a DEMO sáv a nevét mutatja. | ✅ |
| S1 | `test_s1_ek01_valtas_kileptet_es_visszavisz_a_belepeshez` | a [Váltás] gomb kiléptet, másik munkatárs léphet be. | ✅ |
| S1 | `test_s1_ek02_belepes_nelkul_a_belepesi_oldalra_iranyit` | süti nélkül a Fal és az Új köszönet oldal a belépéshez irányít, az API 401. | ✅ |
| S1 | `test_s1_ek03_cimzettkereso_egyseg_email_es_sajat_nev_szerint` | „adat” → az Adat Osztály 5 tagja, „julia.f” → Farkas Júlia, „horváth” → nincs találat. | ✅ |
| S1 | `test_s1_ek04_kereso_billentyuzettel` | „Far” + ↓ + Enter → Farkas Júlia a címzett, 2. lépés; az Esc bezárja a listát. | ✅ |
| S1 | `test_s1_ek05_ek06_anna_privat_koszonetet_kuld_julianak` | a teljes „Kész, ha…” forgatókönyv, DB-ellenőrzéssel. | ✅ |
| S1 | `test_s1_ek07_arculati_alapok_fejlec_tokenek_nincs_kulso_keres_es_felugro_ablak` | sötét fejléc, a tokenek betöltődnek, csak helyi kérések, nincs alert/confirm. | ✅ |
| S2 | `test_s2_ek08_onmagnak_nem_kuldhet_az_api_sem_engedi` | Horváth Anna közvetlenül sem küldhet magának, sem nem létező címzettnek. | ✅ |
| S2 | `test_s2_ek09_ures_uzenet_hiba_a_mezo_alatt` | üres és szóközös üzenetnél a 2. lépésen marad, a mező alatt hiba van, felugró ablak nincs. | ✅ |
| S2 | `test_s2_ek10_karakterszamlalo_500_es_501_karakter` | 500 karakternél nincs hiba, 501-nél piros a számláló, hiba jelenik meg, nincs továbblépés. | ✅ |
| S2 | `test_s2_ek11_kategoria_nelkul_nem_lep_tovabb` | kategória nélkül a kategóriák alatt „Válassz kategóriát.” látszik; az API is visszautasít. | ✅ |
| S2 | `test_s2_ek12_a_negyedik_mai_koszonet_nem_megy_el_de_mas_cimzettnek_igen` | Anna ma 3-at küldött Júliának; a 4. hibát ad a kártya alatt, Varga Bencének küldhet. | ✅ |
| S2 | `test_s2_ek13_a_tegnapi_koszonetek_nem_szamitanak_a_mai_limitbe` | tegnap este 3 köszönet ment Júliának, ma újra küldhet neki. | ✅ |
| S2 | `test_s2_ek47_pontosan_a_negy_behavioral_anchor_latszik` | 4 kategória-kártyagomb a megadott sorrendben, leírással; a régi kategóriák nincsenek ott. | ✅ |
| S3 | `test_s3_ek14_ek21_anna_kuld_es_a_kuldott_listara_erkezik_julia_a_kapottat_latja` | küldés után a Küldött lista nyílik; Júlia Kapott (1), Varga Bence mindkettő (0). | ✅ |
| S3 | `test_s3_ek15_a_kartya_tartalma_es_a_szoveg_escape_elese` | küldő, címzett, egység, chip, kategóriacsík, 🌐, szöveg betű szerint, taps, pontos idő. | ✅ |
| S3 | `test_s3_ek16_a_legujabb_kartya_van_elol` | Kiss Réka (12:00), Varga Bence (11:00), Horváth Anna (10:00) sorrendben. | ✅ |
| S3 | `test_s3_ek17_szabad_szavas_kereses` | „DASHBOARD” → Varga Bence, „horváth” → Horváth Anna, „nincsilyen” → üres állapot. | ✅ |
| S3 | `test_s3_ek18_kategoriaszuro_a_sajat_nezetben` | a „🧪 Experiment, learn fast!” szűrővel csak a 🧪 köszönet, a „Minden kategória”-val mindkettő. | ✅ |
| S3 | `test_s3_ek19_idoszakszuro` | 2, 10 és 40 napja kapott köszönet → Elmúlt 7 nap: 1, Elmúlt 30 nap: 2, Összes: 3. | ✅ |
| S3 | `test_s3_ek20_ures_allapot_uj_koszonet_gombbal` | Varga Bence üres Kapott listáján emoji, mondat és [+ Új köszönet] gomb van, ami a varázslóba visz. | ✅ |
| S4 | `test_s4_ek22_a_falon_csak_a_nyilvanos_koszonet_latszik_mindenkinek` | Nóra, Bence, Réka és László falán egyaránt csak a „Nyilvános köszi” kártya van. | ✅ |
| S4 | `test_s4_ek23_kategoriaszuro_a_falon` | a szűrő a 4 kategóriát kínálja; 🤝 → 2 kártya, 🚀 → üres állapot; a legújabb elöl. | ✅ |
| S4 | `test_s4_ek24_taps_es_visszavonas` | „👏 1” sárga, aria-pressed=true; második kattintásra „👏 0”, keretes; újratöltés után is megmarad. | ✅ |
| S4 | `test_s4_ek25_negy_szemely_negy_taps` | Bence, Réka, Anna (küldő) és Júlia (címzett) tapsol egyszer-egyszer → 4. | ✅ |
| S4 | `test_s4_ek26_privat_koszonetre_csak_a_lathato_szemelyek_tapsolhatnak` | Nóra 404-et kap; Szabó Katalin (Júlia vezetője) és Nagy Péter (Anna vezetője) tapsolhat. | ✅ |
| S4 | `test_s4_ek27_mobil_elrendezes_also_tab_sav_es_egyoszlopos_racs` | 1280 px-en a menü a fejlécben, 3 oszlop; 375 px-en alsó tab-sáv, 1 oszlop, nincs vízszintes görgetés. | ✅ |
| S4 | `test_s4_ek28_billentyuzetes_kezeles_es_latható_fokusz` | Tab-bal elérhető a menü, a csengő, a Váltás, a szűrő és a taps gomb; látható fókuszkeret; Enter tapsol. | ✅ |
| S5 | `test_s5_ek29_anna_koszonete_utan_julia_katalin_es_eszter_ertesitest_kap_laszlo_nem` | Anna a varázslóval küld Júliának; Júlia, Katalin, Eszter csengőjén „1”, másokén nincs. | ✅ |
| S5 | `test_s5_ek34_csengo_szamlalo_es_az_ertesites_tartalma` | Júlián a „2” számláló; a panelen 2 olvasatlan (halványsárga) elem, a legújabb elöl; Nóránál üres. | ✅ |
| S5 | `test_s5_ek35_megnyitas_es_mind_olvasott` | egy értesítés megnyitása után „1”, a [Mind olvasott] után nincs számláló; Katalinnál továbbra is „2”. | ✅ |
| S5 | `test_s5_ek35_billentyuzettel_is_megnyithato_az_ertesites` | az értesítés Tab-bal elérhető, Enterrel olvasottá válik. | ✅ |
| S6 | `test_s6_ek36_nem_vezeto_nem_ereti_el_a_csapat_nezetet` | Annának nincs Csapat menüpontja, a címet megnyitva üzenetet kap, az API 403; Katalinnak van menüpontja. | ✅ |
| S6 | `test_s6_ek37_katalin_az_adat_osztaly_koszonetet_latja_a_fejlesztesi_osztaly_beloleit_nem` | Szabó Katalin → M1, M2, M5 (privátok is); az M3 és a nyilvános M4 nem. | ✅ |
| S6 | `test_s6_ek38_foosztalyvezeto_board_tag_es_a_masik_osztalyvezetok` | Eszter és László mind az 5-öt; Nagy Péter M1, M3, M5; Tóth Gábor csak M4. | ✅ |
| S6 | `test_s6_ek41_a_vezeto_maga_is_a_koreben_van` | Katalin → M1, M2, M5, M7 (M7-nek ő a küldője); Tóth Gábor → M4 és M7. | ✅ |
| S6 | `test_s6_ek39_mas_kor_adata_kozvetlen_keressel_sem_erheto_el` | extra paraméterekkel is Katalin köre jön vissza; az M3-ra tapsolni nem lehet (404). | ✅ |
| S6 | `test_s6_ek40_kereses_es_szurok_a_vezetoi_nezetben` | alapból 30 nap (M6 nincs); „júlia” → M1, M2; 🧪 → M2; Összes + 🧪 → M2, M6. | ✅ |
| S7 | `test_s7_ek42_a_negy_mutato_az_alapertelmezett_30_napra` | 5 kapott, 3 küldött, 3 aktív küldő, 5 összes köszönet. | ✅ |
| S7 | `test_s7_ek43_kategoria_megoszlas_savdiagram` | 4 sáv a megadott sorrendben: 💛 0, 🚀 1, 🤝 3, 🧪 1; saját színnel, a leghosszabb a 🤝. | ✅ |
| S7 | `test_s7_ek44_top3_holtversenyben_abecerendben` | 30 napra Balogh Máté, Farkas Júlia, Szabó Katalin; Összesre a harmadik Papp Zsófia. | ✅ |
| S7 | `test_s7_ek45_az_idoszak_valtasa_megvaltoztatja_a_szamokat_es_a_listat` | 7 nap → 4/3/3/4; Összes → 6/4/3/6, a 🧪 értéke 2; a kártyalista is követi. | ✅ |
| S7 | `test_s7_ek45_a_keresoszo_es_a_kategoria_nem_valtoztatja_a_statisztikat` | a kereső és a kategóriaszűrő csak a listára hat. | ✅ |
| S7 | `test_s7_ek46_mas_kor_adata_nem_szivarog_be` | Tóth Gábor „Összes” statisztikája csupa 0, a Top 3 üres; Katalin a saját értékeit kapja. | ✅ |
| S7 | `test_s7_ek46_reszponziv_2x2_mutatok_mobilon` | EK-46 (NF-02): 375 px-en a 4 mutató-kártya 2×2 rácsban áll, nincs vízszintes görgetés. | ✅ |

## Lefedetlen kritériumok
Nincs. Mind a 47 EK-hoz (EK-01…EK-47) tartozik legalább egy teszt, és mind a 7 storyhoz legalább egy E2E teszt.

## Kézi ellenőrzés az elfogadóknak
Az elfogadáshoz érdemes **tiszta adatbázissal** indítani, hogy a korábbi próbálkozások ne zavarjanak (a `kudos.db`-t ez nem érinti):

```bash
KUDOS_DB=/tmp/kudos-elfogadas.db PORT=8001 python3 app.py
```

Majd nyisd meg: http://localhost:8001. (A megszokott `python3 app.py` a http://localhost:8000 címen a `kudos.db`-vel fut.) A **Váltás** gombbal bármikor másik munkatársként léphetsz be.

1. **Belépés (S1).** A belépési oldalon sárga „DEMO – szimulált belépés, jelszó nincs” jelzés és 17 név látszik. Kattints a **Horváth Anna** névre: a sárga sávban ez áll: „DEMO belépés: Horváth Anna · Fejlesztési Osztály”, és a Kudos fal nyílik meg (még üres, 🌱 üres állapot).
2. **Köszönet küldése (S1).** **Új köszönet** → írd a keresőbe, hogy `adat`: 5 találat (Szabó Katalin, Farkas Júlia, Balogh Máté, Papp Zsófia, Takács Levente). Írj `julia.f`-et, és válaszd a **Farkas Júliát** (vagy `Far`, ↓, Enter). A 2. lépésen válaszd a „🤝 Deliver value together” kategóriát, írd be: `Köszönöm a gyors adatelemzést! 🙏🎉`, a láthatóság maradjon 🔒 Privát, majd **Tovább**. Az ellenőrző kártyán minden adat látszik; a **Vissza** gombbal az adatok megmaradnak; **Tovább**, majd **Küldés**. Toast: „Köszönetedet elküldtük Farkas Júliának! 🎉”, utána a **Saját → Küldött (1)** lista nyílik, rajta a kártya.
3. **Szabályok (S2).** Új köszönetnél (Farkas Júliának) kattints a **Tovább** gombra mindent üresen hagyva: a kategóriák alatt „Válassz kategóriát.”, az üzenet alatt „Az üzenet nem lehet üres.” (piros, a mező alatt). Írj csak szóközöket: ugyanez. Másolj be 501 karaktert: a számláló „501 / 500” és piros, a **Tovább** után hiba jön. Küldj Júliának összesen 3 köszönetet, majd egy 4.-et: az ellenőrző nézetben „Ugyanannak a munkatársnak ma már 3 köszönetet küldtél.” látszik. Az **Új köszönet** menüpont újraindítja a varázslót, és **Varga Bencének** már mehet köszönet.
4. **Értesítések (S5).** Az 1–2. lépés köszönete (Anna → Júlia) után lépj be sorban **Farkas Júliaként**, **Szabó Katalinként** és **Kovács Eszterként**: a 🔔 mindegyiknél „1”-et mutat. **Fehér Lászlónál**, **Nagy Péternél** és **Horváth Annánál** nincs számláló. Júliánál kattints a 🔔-ra: a panelen „Horváth Anna → Farkas Júlia”, kategória, dátum, előnézet látszik, halványsárga háttérrel; kattints az elemre: a számláló eltűnik. A **Mind olvasott** gomb az összeset olvasottá teszi (csak a sajátodat).
5. **Saját köszöneteim (S3).** **Farkas Júliaként**: **Saját → Kapott (n)**, rajta Anna kártyája, legújabb elöl. Próbáld a keresőt (`horváth`, majd `nincsilyen` → „Nincs találat”), a kategória- és az időszakszűrőt; a fül száma közben nem változik. **Varga Bencével** (ha még semmit nem kapott) a Kapott lista üres állapotot mutat és [+ Új köszönet] gombot.
6. **Közös fal és taps (S4).** **Horváth Annaként** küldj Júliának egy **🌐 Nyilvános** köszönetet (más kategóriával is). **Juhász Nóraként**: a Falon csak a nyilvános kártya látszik, az Annától Júliának küldött privát nem. Kattints a **👏** gombra („👏 1”, sárga), frissíts (Ctrl+F5, megmarad), kattints újra (visszavonódik). A kategóriaszűrő működik (🚀 → „Nincs találat”).
7. **Billentyűzet és mobil (S4).** A Falon nyomj Tab-ot: sorban a „Kudos” jel, a menüpontok, a 🔔, a Váltás, a + Új köszönet, a Kategória szűrő és a 👏 kap fókuszt (sárga-fekete keret), az Enter tapsol. Szűkítsd az ablakot 640 px alá (F12, mobil nézet): a menü alulra kerül ikonnal és felirattal, a kártyák egymás alatt állnak.
8. **Vezetői nézet (S6).** **Horváth Annánál** nincs „Csapat” menüpont; a `http://localhost:8001/#/csapat` címet megnyitva ez az üzenet látszik: „Ehhez a nézethez vezetői jogosultság kell.”, köszönetek nélkül. **Szabó Katalinnál** van „Csapat” menüpont: az Annától Júliának küldött privát köszönet látszik (Júlia az Adat Osztályon van), az Annától Varga Bencének küldött nem. **Nagy Péternél** az utóbbi látszik, az előbbi nem. **Kovács Eszter** és **Fehér László** mindkettőt látja. **Tóth Gábornál** (Üzemeltetési Osztály) egyik sem. Próbáld a keresőt, a kategória- és az időszakszűrőt (alapértelmezés: Elmúlt 30 nap).
9. **Vezetői statisztika (S7).** **Szabó Katalinként** a Csapat oldal tetején 4 mutató (kapott, küldött, aktív küldő, összes), a kategória-sávdiagram (a kategóriák saját színével, a sáv végén a darabszám) és a Top 3 (🥇🥈🥉) látszik. Váltsd az **Időszakot** „Elmúlt 7 nap”-ra, majd „Összes”-re: a számok, a sávok és a Top 3 is változnak. A kereső és a kategóriaszűrő csak a kártyalistát szűkíti, a mutatókat nem. **Tóth Gábornál** minden mutató 0, a Top 3 helyén üres állapot áll.
10. **Szöveg-escape (biztonság).** Küldj egy köszönetet ezzel a szöveggel: `<b>nem félkövér</b> <script>alert(1)</script>`. A kártyán betű szerint, szövegként jelenik meg, felugró ablak nincs.
11. **Arculat.** Nézd át a felületet: sötét fejléc, sárga DEMO-sáv, kártyák (nem táblázat), kategóriák saját színe, a hibák a mező alatt, a visszajelzés toast (nem `alert`), üres állapotok emojival és gombbal.

## Ismert korlátok
**A „Kimarad” rész szerint (szándékosan nincs benne):**
- Valódi Active Directory és SSO (helyette: `data/munkatarsak.json` és szimulált „Belépés mint…”, DEMO jelzéssel).
- E-mail és Teams értesítés (helyette: alkalmazáson belüli értesítés, csengő).
- Képfeltöltés és vírusellenőrzés.
- Adminisztrátori szerepkör, moderáció, riportok.
- Megőrzési és archiválási szabályok (minden adat a helyi `kudos.db`-ben marad).
- Szerveres üzemeltetés és deploy (csak `localhost`, a szerver a `127.0.0.1` címen hallgat).
- Teljes WCAG-audit (csak az alapok: billentyűzet, látható fókusz, kontraszt, `aria` címkék).
- Köszönet szerkesztése vagy törlése küldés után.

**Eltérés a forrásdokumentumoktól (a spec 2.3. pontja rögzíti, jóváhagyva):**
- A kategóriák az üzleti leírás 5 kategóriája helyett az IT-BSO négy Behavioral Anchorja; ezért a kategória-választó az `arculat-ui.md` „5 nagy kártyagombja” helyett 4 kártyagomb. A `--cat-kiemelkedo` szín-token a CSS-ben megmaradt (az EK-07 az összes tokent elvárja), de egyik kategória sem használja.

**Menet közben észrevett korlátok, amelyek nem EK-k:**
- **Az értesítések csak az új köszönetekről jönnek létre.** A funkció előtt elküldött köszönetekhez (pl. a kézi próbák a `kudos.db`-ben) utólag nem keletkezik értesítés.
- **A csengő nem frissül magától:** az értesítések az oldal (újra)rajzolásakor és a panel megnyitásakor töltődnek be, élő frissítés (polling) nincs. Az értesítésre kattintás olvasottá teszi, de nem visz a köszönethez.
- **A keresők ékezetérzékenyek** (a spec szerint a címzettkereső „ékezetet nem alakít át”; ugyanez igaz a Saját és Csapat keresőre is): a „julia” nem találja a „Júlia” nevet, az e-mail-címben viszont igen (`julia.f`). A Top 3 holtverseny-rendezése ékezetfüggetlen ábécérendet használ, ezt adat híján nem fedi külön teszt.
- **Idő:** a szerver a helyi időt használja (nincs időzóna-kezelés); a napi limit a szerver naptári napjára számol. A pontos idő a böngésző `hu-HU` formátumában jelenik meg.
- **Éjfél körül** az „aznapi” adatokat „most”-hoz képest előállító tesztek (pl. EK-12, EK-13 E2E) elvileg hamis hibát adhatnak, ha a futás átível az éjféli határon.
- **A „-nak/-nek” toldalék** a visszaigazoló toastban szabályalapú (mind a 17 névre átgondolva), automata teszt csak a „Farkas Júliának” és a „Varga Bencének” esetet ellenőrzi.
- **Böngészők:** a tesztek kizárólag Chromiumban futnak; a mobil nézet emulált képernyőméret, nem valódi eszköz.
- **Akadálymentesség (alapszint):** automatikus kontrasztvizsgálat nincs, a 4,5:1-es kontrasztot a tokenek megválasztása (`--text-2`, `--error-text`, `--warn`) biztosítja. A Tab-sorrendet automata teszt csak a Fal oldalon ellenőrzi. A kategória- és láthatóság-választó (ARIA radiogroup) elemei külön-külön Tab-bal érhetők el, nyílbillentyűs léptetés nincs.
- **Teljesítmény:** a listák lapozás nélkül mutatják az összes elemet; a demóadatmennyiséghez ez elég, nagy adatnál lapozás kellene.
- **A `/api/koszonetek/{id}/taps` 404-et ad** a nem létező és a nem látható köszönetre is (szándékosan nem különbözteti meg a kettőt).
- **Az EK-07 „csak helyi kérés” ellenőrzése** böngészőben a belépési, a Fal és a varázsló oldalakat járja végig; az összes `static/` fájlra külön statikus vizsgálat fut (nincs külső URL, `alert`, `confirm`).

## Teszt-kimenet (összefoglaló)
Futtatás: 2026-10-30, a `python3 -m unittest discover -s tests -v` és a `.venv/bin/python -m unittest discover -s tests/e2e -v` parancsokkal (a teljes kimenet a gitből kizárt `test-results/` mappában van).

```text
Unit:  Ran 117 tests in 57.822s   OK
E2E:   Ran 45 tests in 29.299s    OK
```

| Szint | Teszt | Zöld | Piros |
|---|---|---|---|
| Unit | 117 | 117 | 0 |
| E2E | 45 | 45 | 0 |
| **Összesen** | **162** | **162** | **0** |

Storynként (unit / E2E): S1 23 / 7 · S2 10 / 7 · S3 18 / 7 · S4 15 / 7 · S5 16 / 4 · S6 19 / 6 · S7 16 / 7.
