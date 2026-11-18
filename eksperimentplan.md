# Eksperimentplan – Prosjekt 3: slider vs tallfelt (mobil)

> Planleggingsnotater for gruppa. Bevisst stikkord, ikke rapporttekst. Rapporten skriver hver av dere selv, med egne ord (krav i emnet).
> Testverktøyet (`index.html`) og analyseskriptet (`analyse.py`) er laget med KI-hjelp. Sjekk emnets/OsloMets regler for KI-bruk og oppgi det i rapporten (f.eks. under Utstyr).

## 1. Problemstilling
- Interaksjonsproblem: stille inn en eksakt tallverdi (0–100) på mobil.
- Grensesnitt: **slider** (dra) vs **tallfelt** (skrive tallet med numerisk skjermtastatur).
- Forskningsspørsmål (utkast): Er tallfelt eller slider raskest og mest nøyaktig når brukeren skal stille inn en eksakt verdi på mobil, og hva foretrekker brukerne?
- Hvorfor interessant: slider brukes mye (volum, pris-filtre, spørreskjema), men på en liten skjerm er ett verdisteg bare ca. 3 px (≈ 1 mm). Fitts' lov peker mot små, vanskelige mål.

## 2. Hypoteser (LÅST 18.11.2026, før datainnsamling)
Hypotesene under er bestemt og skal ikke endres etter at første deltaker er testet. Begge testes **tosidig** (α = .05).

| | Nullhypotese (H0) | Alternativ hypotese (H1/H2) | Avhengig variabel | Test |
|---|---|---|---|---|
| **H1 Tid** | Det er ingen forskjell i tid mellom slider og tallfelt. | **Det er forskjell i tid mellom slider og tallfelt** (tosidig). | median tid per forsøk (ms) per deltaker og betingelse | paret t-test, eller Wilcoxon signed-rank hvis differansene ikke er normalfordelte |
| **H2 Feilrate** | Det er ingen forskjell i feilrate mellom slider og tallfelt. | **Det er forskjell i feilrate mellom slider og tallfelt** (tosidig). | feilrate = andel ikke-eksakte svar per deltaker og betingelse | Wilcoxon signed-rank (feilrate har ofte mange nuller), paret t-test som kontroll |

- Hvorfor tosidig: Fitts' lov peker mot at slider er tregere og mindre nøyaktig (lite mål, ca. 1 verdisteg). Men tallfeltet krever et ekstra trykk for fokus og at tastaturet kommer opp, så retningen er ikke sikker. En tosidig test er det forsiktige valget, og den oppdager en forskjell uansett retning.
- Bare hovedforsøk (practice = 0) brukes.
- Bare H1 og H2 er bekreftende hypoteser. Alt annet under er **utforskende** og rapporteres som det.

### Utforskende analyser (ikke låste hypoteser)
- Absolutt avvik (slider vs tallfelt).
- SEQ og de to Likert-leddene (opplevd presisjon og behagelig).
- Preferanse: binomialtest (slider vs tallfelt, «ingen preferanse» utelatt).
- Fitts: tid med slider mot log2(D+1). Tid med tallfelt mot antall siffer.

## 3. Design
- **Innad i grupper** (within-subjects): alle prøver begge grensesnitt. Det gir færre deltakere og kontrollerer for individuelle forskjeller.
- **Uavhengig variabel:** grensesnitt, med 2 nivåer (slider, tallfelt). Valgfritt et 3. nivå (stepper, se pkt. 10).
- **Avhengige variabler:**
  - tid fra forsøket vises til Bekreft (ms, `performance.now()`)
  - feilrate (0/1 per forsøk)
  - absolutt avvik
  - SEQ (1–7) etter hver betingelse
  - 2 Likert-ledd (opplevd presisjon og behagelig, 1–7)
  - preferanse til slutt
- **Ekstra logget (til diskusjon):** tid til første interaksjon, antall interaksjoner (drag eller tastetrykk), antall backspace, startverdi, avstand og antall siffer.
- **Motbalansering:** rekkefølge A (slider først) eller B (tallfelt først). Oddetalls-ID får A og partalls-ID får B, og appen foreslår dette automatisk. Med et partall deltakere blir det like mange i hver rekkefølge.
- **Målverdier:**
  - Fast pool på 20 heltall, spredt over skalaen med 4 per femtedel: 3, 8, 14, 17, 22, 27, 33, 38, 41, 46, 53, 58, 62, 67, 73, 79, 84, 88, 92, 97.
  - 0, 50, 100 og 5-gangere er utelatt med vilje. Ytterpunktene er trivielle på slider, og «runde» tall er lettere å treffe.
  - Samme pool i begge betingelser, men stokket i ulik rekkefølge med et seed per deltaker og betingelse. Dermed er stokkingen reproduserbar.
  - Øving bruker 12, 64 og 89, som ikke er med i hovedpoolen.
- **Slider:**
  - native `input type=range`, 0–100, steg 1, med stor «tommel» (44 px)
  - verdien vises stort over slideren, så det er mulig å treffe eksakt
  - **startverdi konstant 0**, slik at alle starter likt. Ulempe: avstand = målverdi, så avstand og posisjon på skalaen er sammenblandet. Med `SLIDER_START: 'tilfeldig'` får dere seedet tilfeldig start (minst 10 unna målet). Velg én løsning og hold den fast.
- **Tallfelt:**
  - `inputmode="numeric"` gir et numerisk skjermtastatur, og feltet tar maks 3 siffer
  - **på mobil trykker deltakeren på feltet for å få fokus (ingen autofokus)**, fordi iOS ikke åpner tastaturet automatisk. Det gjør også at hvert forsøk starter likt. Trykket teller med i tiden, og det er realistisk.
  - Enter/«Ferdig» på tastaturet sender **ikke** svaret. Bare Bekreft gjør det, likt i begge betingelser.
- **Bekreft:** samme størrelse og posisjon i begge betingelser (verifisert i test: x=18, y=286, 354×68 px på en 390 px bred skjerm). Den ligger høyt nok til ikke å dekkes av tastaturet.
- **Start-knapp før hvert forsøk:**
  - Start ligger på samme sted som Bekreft, så fingeren starter på samme sted i hvert forsøk.
  - Tiden måles fra målet vises.
  - Bekreft ignoreres de første 250 ms, for å hindre dobbelttrykk.
- **Feil svar er lov:** de blokkeres ikke, men logges. Tomt tallfelt blokkeres, og forsøket logges som `n_empty_submits`.
- **Tilbakemelding:** etter øvingsforsøk vises riktig/feil. Etter hovedforsøk vises bare «Registrert», så deltakeren ikke endrer strategi.

## 4. Konfunderende variabler og kontroll
- **Én felles telefon til alle (sterkt anbefalt).**
  - Skjermbredden bestemmer px per verdisteg på slideren, og dermed vanskeligheten (Fitts).
  - Ulike telefoner har ulike tastaturer, ulik responstid og ulik størrelse.
- **Bruker deltakerne hver sin telefon, er det en konfunderende variabel:**
  - Appen logger `screen_w`, `screen_h`, `dpr`, `slider_track_px` og `user_agent`, og `analyse.py` advarer hvis disse varierer.
  - Nevn det som en begrensning i rapporten.
  - Innad-design demper problemet noe, siden hver deltaker bruker samme telefon i begge betingelser. Slider-vanskeligheten varierer likevel mellom deltakerne.
- Samme grep for alle: f.eks. telefonen i én hånd og tommelen på dominant hånd, eller telefonen i venstre hånd og pekefinger på høyre. Bestem én variant og vis den.
- Samme stilling (sittende ved bord), samme rom/lys, samme lysstyrke, og lys/mørk modus fast (sett telefonen til én av dem).
- Telefon i flymodus/forstyrr ikke, ingen varsler. Lukk andre apper. Batterisparing av (den kan strupe ytelse).
- Stående (portrett). Appen viser en advarsel ved liggende.
- Øvingsforsøk (3 per betingelse) reduserer læringseffekt, og motbalanseringen fordeler resten.
- Samme muntlige instruksjon ordrett (se pkt. 6). Ikke hjelp under forsøkene.

## 5. Deltakere og tid
- Minimum 10, mål **14–16** (partall).
- Styrke (paret t-test, α = .05 tosidig, 80 %): n = 10 oppdager dz ≈ 1,0. n = 14 oppdager dz ≈ 0,81. n = 16 oppdager dz ≈ 0,75. n = 20 oppdager dz ≈ 0,66.
- Rekruttering: medstudenter og venner (bekvemmelighetsutvalg, som nevnes som begrensning). Ikke de som kjenner hypotesene.
- Kriterier: vant smarttelefonbruker, 18 år eller eldre.
- Øktlengde: ca. 10–15 min. 2 × (3 øving + 20 forsøk) à 3–5 s, i tillegg samtykke, instruksjoner og spørsmål. For nærmere 15–20 min kan `N_MAIN` settes til 30 (gir bedre data).
- Bytt roller mellom dere: én leser instruksjon og noterer avvik, én passer på utstyret.

## 6. Prosedyre (manus for eksperimentator)
1. Før økten: telefonen er ladet og i flymodus etter at siden er lastet, lysstyrken er fast og `index.html` er åpen i samme nettleser hver gang.
2. Ønsk velkommen og les samtykketeksten (pkt. 7). Fortsett bare ved muntlig ja.
3. Eksperimentator skriver inn ID (P01, P02, …), sjekker foreslått rekkefølge og trykker *Start økt*.
4. Gi telefonen til deltakeren, vis grepet og les instruksjonen høyt:
   > «Du skal stille inn tall mellom 0 og 100 på to ulike måter. Øverst på skjermen står tallet du skal stille inn. Trykk *Start*, still inn tallet så raskt og nøyaktig du kan, og trykk *Bekreft*. Du får noen øvingsforsøk først. Det er grensesnittet vi tester, ikke deg. Hold telefonen slik jeg viste deg hele tiden.»
5. Deltakeren gjør del 1: øving, forsøk og 3 spørsmål. Deretter del 2 på samme måte, og til slutt preferanse, kommentar og demografi.
6. Når sluttskjermen kommer, tar eksperimentator telefonen og sjekker at de to CSV-filene ble lastet ned automatisk. Mangler en, trykk *Last ned forsøk* / *Last ned spørreskjema* (eller *Kopier*).
7. Noter avvik (forstyrrelser, feil grep, avbrudd) i en egen logg med ID og klokkeslett, uten navn.
8. Takk deltakeren og be dem ikke fortelle hypotesene til andre deltakere.
- Etter hver testdag: åpne `index.html#eksperimentator` (eller trykk 5 ganger raskt på tittelen) og eksporter **alle** økter som backup.

## 7. Etikk og personvern
- Bare anonym ID (P01 …). Ingen navn, e-post eller IP-adresse lagres av appen. Alder lagres som intervall, og kjønn har alternativet «vil ikke oppgi».
- Ikke lag en navneliste som kan kobles til ID. Ingen bilde eller video.
- Dataene lagres bare lokalt i nettleseren (localStorage) og i CSV-filer hos dere. Ingenting sendes til en server.
- Fritekst-kommentar: be deltakeren om ikke å skrive navn eller annet som identifiserer. Sjekk feltene før deling.
- `user_agent` og skjermstørrelse logges, og det er tekniske data om telefonen, ikke om personen.
- Rett til å trekke seg når som helst uten begrunnelse. Avbrutte økter slettes, eller utelates med `--exclude P07`.
- **Sikt-meldeplikt:** trolig ikke nødvendig, siden dataene er anonyme og det ikke samles inn personopplysninger. **Sjekk med foreleser før dere starter.**
- Samtykketekst (les høyt eller vis):
  > «Dette er et studentprosjekt i emnet Menneske-maskin interaksjon ved OsloMet. Vi sammenlikner to måter å stille inn tall på mobil. Det tar ca. 10–15 minutter. Vi lagrer bare tid, svar og noen spørsmål om alder (intervall), kjønn og hvilken hånd du bruker. Vi lagrer ikke navnet ditt, og resultatene kan ikke spores tilbake til deg. Deltakelse er frivillig, og du kan avbryte når som helst uten å oppgi grunn. Er det greit for deg å delta?»

## 8. Analyse: valg av tester
- Bare hovedforsøk (practice=0). Per deltaker og betingelse beregnes **median tid** (robust mot enkeltstående trege forsøk; `--time mean` er alternativet), feilrate, gjennomsnittlig absolutt avvik og SEQ.
- To betingelser med repeated measures (samme person i begge) gir en paret test:
  - Shapiro-Wilk på **differansene**. Er de normalfordelte, brukes paret t-test (effektstørrelse Cohens dz). Hvis ikke, brukes Wilcoxon signed-rank (effektstørrelse rank-biserial r).
  - Feilrate og Likert/SEQ er ofte ikke normalfordelt (ordinale data, mange nuller), og da er Wilcoxon mest forsvarlig.
- Rekkefølgeeffekt: sammenlikn tid i del 1 og del 2, og differansen slider − tallfelt i gruppe A og B. I JASP: RM-ANOVA med `order` som between-faktor, der interaksjonen er det dere ser på.
- Preferanse:
  - binomialtest (slider vs tallfelt, «ingen preferanse» utelatt, p = 0,5)
  - eventuelt kji-kvadrat goodness-of-fit over 3 kategorier. Med n ≈ 16 blir forventet frekvens < 5, så binomialtesten er tryggere.
- Fitts-inspirert:
  - lineær regresjon av tid mot log2(D+1) for slider, med D = |mål − start| og W = 1 steg
  - stigning per deltaker testes mot 0 med en ettutvalgs t-test
  - tallfelt: tid per antall siffer
- Ved flere tester (H1–H4 og flere DV-er) bør dere vurdere Holm/Bonferroni, eller nevne økt risiko for type I-feil.
- Kjør `analyse.py` for å sjekke at JASP-tallene stemmer.

### Kjøre analyse.py
```
pip install pandas numpy scipy statsmodels
python analyse.py --dir mappe_med_alle_csv/ --out resultater/
# eller: python analyse.py --trials alle_forsok_*.csv --quest alle_sporreskjema_*.csv --out resultater/
```
- Gir `sammendrag_bred_JASP.csv` (én rad per deltaker), `sammendrag_lang.csv`, `hovedforsok_JASP.csv` (forsøksnivå) og `resultater.txt`.
- Eksportert fra eksperimentatorsiden fra flere telefoner? Legg alle filene i én mappe. Duplikater fjernes automatisk.

### JASP steg for steg
Menynavnene under er fra nyere JASP-versjoner (0.18/0.19) og kan avvike litt i deres versjon.
1. Åpne `sammendrag_bred_JASP.csv`: hovedmenyen (☰) → Open → Computer → Browse. Sjekk at tallkolonnene er «Scale» og at `order` og `preference` er «Nominal».
2. **Deskriptiv statistikk:** Descriptives → velg `time_ms_slider`, `time_ms_tallfelt` osv. Under Plots kan dere slå på boksplott til figurene.
3. **Paret test (H1, H2, SEQ):** T-Tests → Classical → Paired Samples T-Test.
   - Legg `time_ms_slider` og `time_ms_tallfelt` som et par.
   - Under Tests krysser dere av både Student og Wilcoxon signed-rank.
   - Under Alt. Hypothesis velger dere ≠ (tosidig). H1 og H2 er låst som tosidige.
   - Under Additional Statistics: Descriptives og Effect size.
   - Under Assumption Checks: Normality (Shapiro-Wilk).
   - Gjenta for `error_rate_*`, `mean_abs_error_*` og `seq_*`.
4. **Rekkefølge:** ANOVA → Repeated Measures ANOVA.
   - Repeated measures factor «grensesnitt» med nivåene slider og tallfelt. Legg `time_ms_slider` og `time_ms_tallfelt` i cellene, og `order` under Between Subject Factors.
   - Se på interaksjonen grensesnitt × order.
5. **Preferanse:**
   - Frequencies → Binomial Test på `preference` (test value 0,5). Fjern «ingen preferanse» først, med et filter eller en egen kolonne.
   - Eventuelt Frequencies → Multinomial Test for alle 3 kategorier.
6. **Fitts (valgfritt):** åpne `hovedforsok_JASP.csv` (fra `analyse.py`) og filtrer til `condition = slider`. Regression → Linear Regression med `time_ms` som avhengig variabel og `log2_distance_plus1` som kovariat.
7. Tre betingelser (stepper på): ANOVA → Repeated Measures ANOVA med 3 nivåer.
   - Under Assumption Checks: Sphericity tests og korreksjon (Greenhouse-Geisser).
   - Post hoc tests med Holm.
   - Under Nonparametrics: Friedman. Den kan også brukes til den ikke-parametriske varianten.

## 9. Kjøre testen på mobil
- **Hvorfor hosting:** `index.html` er én frakoblet fil uten eksterne avhengigheter, men å åpne en lokal HTML-fil på telefon fungerer dårlig (Android blokkerer ofte `file://`, og iOS Filer kjører ikke siden skikkelig). Legg den derfor på en gratis statisk side:
  - **GitHub Pages (ferdig satt opp):** testen ligger på **https://nhathuy-nguyen-dev.github.io/mmi-prosjekt3/**. Den oppdateres automatisk 1–2 min etter hver push til `main`.
  - **Netlify Drop:**
    1. Gå til https://app.netlify.com/drop.
    2. Dra inn en mappe som inneholder `index.html` (kopi av `index.html`).
    3. Dere får en URL. Kan kreve en gratis konto, og uten konto kan siden bli slettet etter kort tid.
- Åpne URL-en i **samme nettleser** på testtelefonen hver gang, f.eks. Chrome eller Safari. **Ikke privat modus**, ellers forsvinner localStorage.
- Etter at siden er lastet kan telefonen settes i flymodus, siden testen ikke trenger nett.
- Lagring er per nettleser og URL. Bytter dere URL eller nettleser, ser dere ikke gamle økter, så eksporter etter hver deltaker.
- **Automatisk lagring:** når deltakeren trykker *Fullfør*, lastes `forsok_<ID>_<tid>.csv` og `sporreskjema_<ID>_<tid>.csv` ned automatisk. Økta lagres også i nettleseren underveis. Siden har ingen server, så filene havner på telefonen. Send dem til dere selv etter hver økt.
- **Last ned** lagrer CSV i Nedlastinger (Android) eller Filer (iOS). Send filene til deg selv. **Kopier** er reserveløsning: lim inn i et notat eller en e-post til dere selv.
- Konfig (øverst i fila, under `CONFIG`):
  - `DEVICE: 'mobil'` (standard) eller `'laptop'`
  - `N_MAIN: 20`
  - `ENABLE_STEPPER: false`
  - `SLIDER_START: 0`
  - Endre **før** første pilot, og aldri underveis.
- **Pilot:** kjør 1–2 personer (gjerne dere selv, data kastes), så sjekk CSV og kjør `analyse.py`. Slett pilotdata på eksperimentatorsiden etter eksport.

## 10. Valgfri tredje betingelse: stepper (−10/−1/+1/+10)
- Slås på med `ENABLE_STEPPER: true`. Ingenting annet må endres.
- Fordel: mer originalt, og en mellomting mellom «diskret» og «kontinuerlig».
- Ulemper:
  - +50 % økttid (ca. 15–20 min)
  - 6 rekkefølger for full motbalansering, slik at n bør være et multiplum av 6 (12 eller 18)
  - tester blir RM-ANOVA/Friedman med post hoc, altså mer å forklare innenfor 2000 ord
- Anbefaling med under en uke: **hold dere til 2 betingelser**.

## 11. Tidsplan (7 dager)
- **Dag 1 (ons 18.11):** les planen, hypotesene er låst (tosidige H1 og H2). Bestem grep, startverdi og antall forsøk. Send kort plan til foreleser for veiledning, og spør om Sikt.
- **Dag 2 (tor 19.11):**
  - publiser på GitHub Pages
  - pilot med 1–2 personer, sjekk CSV og `analyse.py`
  - fiks eventuelle problemer, og frys konfigurasjonen
  - rekrutter deltakere og book tider
- **Dag 3–4 (fre 20.11–lør 21.11):** gjennomfør 14–16 økter på samme telefon. Eksporter etter hver økt og ta backup hver kveld.
- **Dag 5 (søn 22.11):** kjør `analyse.py` og JASP, lag figurer (boksplott for tid, feilrate og SEQ) og tabeller. Diskuter funn sammen i gruppa.
- **Dag 6–7 (man 23.11–tir 24.11):** **hver skriver sin egen rapport** med egne ord.
  - Krav: 1000–2000 ord, studentnumre for begge og antall ord på første side, nummererte figurer med figurtekst, APA med DOI, ingen forside eller innholdsfortegnelse, én kolonne, maks 10 sider, innebygde stiler (lys/mørk modus).
  - Lagre som PDF via «Lagre som», ikke via utskrift.
  - Felles materiale (testapp, spørreskjema, figurer) merkes som gruppearbeid.

## 12. Liknende studier (DOI sjekket mot api.crossref.org 18.11.2026)
- Couper, M. P., Tourangeau, R., Conrad, F. G., & Singer, E. (2006). Evaluating the effectiveness of visual analog scales: A web experiment. *Social Science Computer Review, 24*(2), 227–245. https://doi.org/10.1177/0894439305281503
  - Relevans: eksperiment med slider (VAS) mot andre svarformater på web. Slider gav mer frafall og lengre svartid.
- Funke, F., Reips, U.-D., & Thomas, R. K. (2011). Sliders for the smart: Type of rating scale on the Web interacts with educational level. *Social Science Computer Review, 29*(2), 221–231. https://doi.org/10.1177/0894439310376896
  - Relevans: slider gav flere problemer og lengre tid enn radioknapper, særlig for noen brukergrupper.
- Matejka, J., Glueck, M., Grossman, T., & Fitzmaurice, G. (2016). The effect of visual appearance on the performance of continuous sliders and visual analogue scales. I *Proceedings of the 2016 CHI Conference on Human Factors in Computing Systems* (s. 5421–5432). ACM. https://doi.org/10.1145/2858036.2858063
  - Relevans: HCI-studie av nøyaktighet og skjevhet ved slider-input, og hvordan utforming påvirker presisjonen.
- Fitts, P. M. (1954). The information capacity of the human motor system in controlling the amplitude of movement. *Journal of Experimental Psychology, 47*(6), 381–391. https://doi.org/10.1037/h0055392
  - Relevans: originalkilden til Fitts' lov (avstand og målbredde gir bevegelsestid).
- MacKenzie, I. S. (1992). Fitts' law as a research and design tool in human-computer interaction. *Human–Computer Interaction, 7*(1), 91–139. https://doi.org/10.1207/s15327051hci0701_3
  - Relevans: Shannon-formuleringen log2(D/W+1) og bruk av Fitts i HCI.
- Ekstra ved behov:
  - Parhi, P., Karlson, A. K., & Bederson, B. B. (2006). Target size study for one-handed thumb use on small touchscreen devices. I *Proceedings of the 8th Conference on Human-Computer Interaction with Mobile Devices and Services* (s. 203–210). ACM. https://doi.org/10.1145/1152215.1152260. Relevans: tommelstyring og målstørrelse på mobil.
  - Sauro, J., & Dumas, J. S. (2009). Comparison of three one-question, post-task usability questionnaires. I *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems* (s. 1599–1608). ACM. https://doi.org/10.1145/1518701.1518946. Relevans: kilde for SEQ-spørsmålet.
- Les i det minste sammendraget av hver kilde selv før dere siterer. Beskrivelsene over er korte stikkord.
- Lærebok (statistikk, kap. 15, ingen DOI): Sandnes, F. E. (2026). *Universell utforming og UX: Design av interaktive brukergrensesnitt for alle* (4. utg.). Universitetsforlaget. Sjekk sidetall i kap. 15 selv.
