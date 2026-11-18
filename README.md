# MMI prosjekt 3: slider vs tallfelt (mobil)

**Testen:** https://nhathuy-nguyen-dev.github.io/mmi-prosjekt3/
(Eksperimentatorside med eksport av alle økter: legg til `#eksperimentator` på slutten.)

## Låste hypoteser (tosidige, α = .05)

- **H1:** Det er forskjell i tid mellom slider og tallfelt.
- **H2:** Det er forskjell i feilrate mellom slider og tallfelt.

Alt annet (absolutt avvik, SEQ, Likert, preferanse, Fitts) er utforskende. Se `eksperimentplan.md`, punkt 2.

## Hvordan data lagres

Siden er statisk og har ingen server. Hver økt lagres derfor på to steder:

1. **Automatisk CSV-nedlasting** når deltakeren trykker *Fullfør*:
   `forsok_P01_<tid>.csv` og `sporreskjema_P01_<tid>.csv`
2. **I nettleseren** (localStorage) underveis. Alt kan eksporteres samlet fra `#eksperimentator`.

Legg alle CSV-filene i én mappe (f.eks. `data/`) og kjør:

```bash
pip install pandas numpy scipy statsmodels
python analyse.py --dir data/ --out resultater/
```

## Filer

| Fil | Hva |
|---|---|
| `index.html` | Testappen (alt i én fil). Innstillinger i `CONFIG` øverst. |
| `analyse.py` | Statistikk og JASP-klare CSV-er |
| `eksperimentplan.md` | Hele planen: design, prosedyre, etikk, analyse |
| `eksempeldata_FIKTIV/` | Simulerte data kun for å teste `analyse.py`. Skal **ikke** brukes i rapporten. |
