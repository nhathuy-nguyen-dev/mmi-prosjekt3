#!/usr/bin/env python3
"""
analyse.py – analyse av data fra index.html (testappen) (slider vs tallfelt [+ stepper]).

Bruk:
    python analyse.py --trials forsok.csv [flere.csv ...] --quest sporreskjema.csv [...] --out resultater/
    python analyse.py --dir mappe_med_csv/ --out resultater/        (finner *forsok*.csv og *sporreskjema*.csv)

Krever: pandas, numpy, scipy (statsmodels valgfritt, brukes til RM-ANOVA ved 3 betingelser)
    pip install pandas numpy scipy statsmodels

Utdata i --out:
    sammendrag_lang.csv        én rad per deltaker x betingelse
    sammendrag_bred_JASP.csv   én rad per deltaker (åpnes direkte i JASP)
    hovedforsok_JASP.csv       alle hovedforsøk med kolonnen log2_distance_plus1 (Fitts-regresjon)
    resultater.txt             alle tester med tall
Kun hovedforsøk (practice=0) brukes. Øvingsforsøk forkastes.
"""
import argparse, glob, math, os, sys, warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
import numpy as np
import pandas as pd
from scipy import stats

ORDER_PREF = ['slider', 'tallfelt', 'stepper']
OUT_LINES = []

def say(s=''):
    print(s); OUT_LINES.append(s)

def fmt_p(p):
    return 'p < .001' if p < 0.001 else f'p = {p:.3f}'

def read_many(paths):
    frames = [pd.read_csv(p, dtype={'comment': str}) for p in paths]
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return df

def rank_biserial(diff):
    """Matched-pairs rank-biserial correlation (samme mål som JASP rapporterer for Wilcoxon)."""
    d = np.asarray(diff, float); d = d[d != 0]
    if len(d) == 0: return float('nan')
    r = stats.rankdata(np.abs(d))
    wpos, wneg = r[d > 0].sum(), r[d < 0].sum()
    return (wpos - wneg) / (wpos + wneg)

def paired_tests(wide, a, b, label, unit=''):
    x, y = wide[a], wide[b]
    m = x.notna() & y.notna(); x, y = x[m], y[m]
    d = x - y; n = len(d)
    say(f'\n--- {label}: {a} vs {b} (n = {n}) ---')
    say(f'  M({a}) = {x.mean():.2f}{unit} (SD {x.std(ddof=1):.2f}), Mdn = {x.median():.2f}')
    say(f'  M({b}) = {y.mean():.2f}{unit} (SD {y.std(ddof=1):.2f}), Mdn = {y.median():.2f}')
    say(f'  Differanse ({a} − {b}): M = {d.mean():.2f}, SD = {d.std(ddof=1):.2f}')
    if n < 3:
        say('  For få deltakere for tester.'); return
    if d.std(ddof=1) == 0:
        say('  Alle differanser er like (f.eks. 0) – ingen test meningsfull.'); return
    sw = stats.shapiro(d)
    normal = sw.pvalue >= 0.05
    say(f'  Shapiro-Wilk på differansene: W = {sw.statistic:.3f}, {fmt_p(sw.pvalue)} -> '
        + ('normalfordeling ikke forkastet (paret t-test OK)' if normal else 'avvik fra normalfordeling (bruk Wilcoxon)'))
    t = stats.ttest_rel(x, y)
    dz = d.mean() / d.std(ddof=1)
    say(f'  Paret t-test (tosidig): t({n-1}) = {t.statistic:.3f}, {fmt_p(t.pvalue)}, Cohens d (dz) = {dz:.3f}')
    try:
        w = stats.wilcoxon(x, y)
        nz = int((d != 0).sum())
        say(f'  Wilcoxon signed-rank (tosidig): W = {w.statistic:.1f}, {fmt_p(w.pvalue)}, '
            f'rank-biserial r = {rank_biserial(d):.3f} (n uten nulldifferanser = {nz})')
    except ValueError as e:
        say(f'  Wilcoxon ikke mulig: {e}')
    say(f'  Anbefalt rapportert test: {"paret t-test" if normal else "Wilcoxon signed-rank"}')

def rm_tests(long, dv, conds, label):
    sub = long[long.condition.isin(conds)][['participant_id', 'condition', dv]].dropna()
    wide = sub.pivot(index='participant_id', columns='condition', values=dv).dropna()
    conds = [c for c in conds if c in wide.columns]
    if len(conds) < 3:
        say(f'\n--- {label}: hoppet over (ikke alle deltakere har tre betingelser – blandet data?) ---'); return
    say(f'\n--- {label}: {", ".join(conds)} (n = {len(wide)}) ---')
    for c in conds:
        say(f'  {c}: M = {wide[c].mean():.2f} (SD {wide[c].std(ddof=1):.2f}), Mdn = {wide[c].median():.2f}')
    if len(wide) < 3: say('  For få deltakere.'); return
    fr = stats.friedmanchisquare(*[wide[c] for c in conds])
    k, n = len(conds), len(wide)
    kendall_w = fr.statistic / (n * (k - 1))
    say(f'  Friedman: chi2({k-1}) = {fr.statistic:.3f}, {fmt_p(fr.pvalue)}, Kendalls W = {kendall_w:.3f}')
    try:
        from statsmodels.stats.anova import AnovaRM
        res = AnovaRM(sub[sub.participant_id.isin(wide.index)], dv, 'participant_id', within=['condition']).fit()
        row = res.anova_table.iloc[0]
        say(f'  RM-ANOVA: F({row["Num DF"]:.0f}, {row["Den DF"]:.0f}) = {row["F Value"]:.3f}, {fmt_p(row["Pr > F"])} '
            '(ingen sfærisitetskorreksjon her – bruk JASP for Mauchly/Greenhouse-Geisser)')
    except Exception as e:
        say(f'  RM-ANOVA hoppet over ({e.__class__.__name__}: {e})')
    # Post hoc: parvise Wilcoxon med Holm-korreksjon
    pairs = [(a, b) for i, a in enumerate(conds) for b in conds[i+1:]]
    ps = []
    for a, b in pairs:
        try: ps.append(stats.wilcoxon(wide[a], wide[b]).pvalue)
        except ValueError: ps.append(float('nan'))
    order = np.argsort(ps); m = len(ps); adj = [None]*m; running = 0
    for rank, idx in enumerate(order):
        val = min(1.0, (m - rank) * ps[idx]); running = max(running, val); adj[idx] = running
    for (a, b), p, pa in zip(pairs, ps, adj):
        say(f'  Post hoc Wilcoxon {a} vs {b}: {fmt_p(p)} (Holm-justert {fmt_p(pa)})')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trials', nargs='*', default=[])
    ap.add_argument('--quest', nargs='*', default=[])
    ap.add_argument('--dir')
    ap.add_argument('--out', default='resultater')
    ap.add_argument('--time', choices=['median', 'mean'], default='median',
                    help='aggregering av tid per deltaker/betingelse (median er robust mot enkeltstående trege forsøk)')
    ap.add_argument('--exclude', nargs='*', default=[], help='deltaker-ID-er som skal utelates (f.eks. ufullstendige)')
    a = ap.parse_args()
    if a.dir:
        a.trials += sorted(glob.glob(os.path.join(a.dir, '*forsok*.csv')))
        a.quest += sorted(glob.glob(os.path.join(a.dir, '*sporreskjema*.csv')))
    if not a.trials: sys.exit('Fant ingen forsøksfiler. Bruk --trials eller --dir.')
    os.makedirs(a.out, exist_ok=True)

    tr = read_many(a.trials).drop_duplicates(subset=['session_id', 'condition', 'practice', 'trial_no'])
    q = read_many(a.quest).drop_duplicates(subset=['session_id']) if a.quest else pd.DataFrame()
    if a.exclude:
        tr = tr[~tr.participant_id.isin(a.exclude)]
        if len(q): q = q[~q.participant_id.isin(a.exclude)]
    # Hvis samme ID har flere økter: behold den siste fullførte økten
    last = tr.groupby('participant_id').session_id.agg(lambda s: sorted(s)[-1])
    if tr.groupby('participant_id').session_id.nunique().max() > 1:
        say('ADVARSEL: noen ID-er har flere økter – bruker siste økt per ID: ' + ', '.join(last.index))
    tr = tr[tr.session_id.isin(last.values)]
    if len(q): q = q[q.session_id.isin(last.values)]

    main_tr = tr[tr.practice == 0].copy()
    main_tr['log2_distance_plus1'] = np.log2(pd.to_numeric(main_tr.distance, errors='coerce') + 1)
    main_tr.to_csv(os.path.join(a.out, 'hovedforsok_JASP.csv'), index=False)  # forsøksnivå, til Fitts-regresjon i JASP
    conds = [c for c in ORDER_PREF if c in set(main_tr.condition)]
    say('Analyse av slider vs tallfelt' + (' vs stepper' if 'stepper' in conds else ''))
    say(f'Deltakere: {main_tr.participant_id.nunique()}  |  Betingelser: {", ".join(conds)}  |  '
        f'Hovedforsøk: {len(main_tr)}  |  Enhet(er): {", ".join(map(str, main_tr.device.unique()))}')
    if main_tr.device.nunique() > 1 or main_tr.screen_w.nunique() > 1:
        say('ADVARSEL: data fra ulike enheter/skjermbredder – mulig konfunderende variabel. '
            f'Skjermbredder: {sorted(int(x) for x in main_tr.screen_w.dropna().unique())}')
    cnt = main_tr.groupby(['participant_id', 'condition']).size().unstack()
    if cnt.isna().any().any() or cnt.nunique().max() > 1:
        say('ADVARSEL: ulikt antall forsøk per deltaker/betingelse:\n' + cnt.to_string())

    agg = main_tr.groupby(['participant_id', 'order', 'condition', 'condition_pos']).agg(
        time_mean_ms=('time_ms', 'mean'), time_median_ms=('time_ms', 'median'),
        error_rate=('correct', lambda s: 1 - s.mean()), mean_abs_error=('abs_error', 'mean'),
        first_interaction_median_ms=('first_interaction_ms', 'median'),
        interactions_mean=('n_interactions', 'mean'), n_trials=('time_ms', 'size')).reset_index()
    tcol = 'time_median_ms' if a.time == 'median' else 'time_mean_ms'
    agg['time_ms'] = agg[tcol]

    # Spørreskjema -> lang
    if len(q):
        for c in conds:
            for item in ['seq', 'presisjon', 'behagelig']:
                col = f'{item}_{c}'
                if col in q:
                    agg.loc[agg.condition == c, item] = agg.loc[agg.condition == c, 'participant_id'].map(q.set_index('participant_id')[col])
    agg.round(4).to_csv(os.path.join(a.out, 'sammendrag_lang.csv'), index=False)

    # Bred format for JASP
    dvs = ['time_ms', 'time_mean_ms', 'time_median_ms', 'error_rate', 'mean_abs_error'] + \
          [c for c in ['seq', 'presisjon', 'behagelig'] if c in agg]
    wide = agg.pivot(index='participant_id', columns='condition', values=dvs)
    wide.columns = [f'{dv}_{c}' for dv, c in wide.columns]
    wide = wide.join(agg.groupby('participant_id').order.first())
    if len(q):
        keep = [c for c in ['preference', 'age_range', 'gender', 'hand'] if c in q]
        wide = wide.join(q.set_index('participant_id')[keep])
    if len(conds) >= 2:
        wide['diff_time_slider_minus_tallfelt'] = wide['time_ms_slider'] - wide['time_ms_tallfelt']
    wide.reset_index().round(4).to_csv(os.path.join(a.out, 'sammendrag_bred_JASP.csv'), index=False)

    say(f'\nTid = {a.time} av hovedforsøk per deltaker og betingelse (ms). Feilrate = andel ikke-eksakte svar.')
    say('LÅSTE HYPOTESER (tosidige, alfa = .05):')
    say('  H1: Det er forskjell i tid mellom slider og tallfelt.        -> se «Tid» under')
    say('  H2: Det er forskjell i feilrate mellom slider og tallfelt.   -> se «Feilrate» under')
    say('Alle andre sammenlikninger er utforskende.')
    labels = [('time_ms', 'Tid', ' ms'), ('error_rate', 'Feilrate', ''), ('mean_abs_error', 'Gjennomsnittlig absolutt avvik', ''),
              ('seq', 'SEQ (1–7)', ''), ('presisjon', 'Opplevd presisjon (1–7)', ''), ('behagelig', 'Behagelig (1–7)', '')]
    say('\n================ PARVISE SAMMENLIKNINGER (slider vs tallfelt) ================')
    for dv, lab, unit in labels:
        if f'{dv}_slider' in wide and f'{dv}_tallfelt' in wide:
            paired_tests(wide, f'{dv}_slider', f'{dv}_tallfelt', lab, unit)
    if len(conds) >= 3:
        say('\n================ TRE BETINGELSER: RM-ANOVA / FRIEDMAN ================')
        for dv, lab, _ in labels:
            if dv in agg: rm_tests(agg, dv, conds, lab)

    # Rekkefølgeeffekt
    say('\n================ REKKEFØLGEEFFEKT ================')
    pos = agg.pivot(index='participant_id', columns='condition_pos', values='time_ms')
    if 1 in pos and 2 in pos:
        d = (pos[1] - pos[2]).dropna()
        t = stats.ttest_rel(pos[1], pos[2], nan_policy='omit')
        say(f'Tid i første vs andre betingelse (uansett grensesnitt): M diff = {d.mean():.1f} ms, '
            f't({len(d)-1}) = {t.statistic:.3f}, {fmt_p(t.pvalue)}  (positiv = raskere i andre del -> læring)')
    if 'diff_time_slider_minus_tallfelt' in wide and wide.order.nunique() == 2 and len(conds) == 2:
        g = [wide.loc[wide.order == o, 'diff_time_slider_minus_tallfelt'].dropna() for o in sorted(wide.order.unique())]
        say(f'Differansen slider − tallfelt per rekkefølge: A: M = {g[0].mean():.1f} (n={len(g[0])}), '
            f'B: M = {g[1].mean():.1f} (n={len(g[1])})')
        if min(len(g[0]), len(g[1])) >= 2:
            tw = stats.ttest_ind(g[0], g[1], equal_var=False); mw = stats.mannwhitneyu(g[0], g[1])
            say(f'  Welch t = {tw.statistic:.3f}, {fmt_p(tw.pvalue)}; Mann-Whitney U = {mw.statistic:.1f}, {fmt_p(mw.pvalue)}'
                '  (signifikant = rekkefølgen påvirker forskjellen; asymmetrisk overføring)')
        say('  I JASP: Repeated Measures ANOVA med betingelse som within-faktor og "order" som between-faktor; '
            'se på interaksjonen betingelse × order.')

    # Preferanse
    if len(q) and 'preference' in q:
        say('\n================ PREFERANSE ================')
        pc = q.preference.value_counts()
        say('Fordeling: ' + ', '.join(f'{k}: {v}' for k, v in pc.items()))
        if len(conds) == 2:
            ns, nt = int(pc.get('slider', 0)), int(pc.get('tallfelt', 0))
            if ns + nt > 0:
                bt = stats.binomtest(nt, ns + nt, 0.5)
                say(f'Binomialtest (tosidig, ingen preferanse utelatt): {nt} av {ns+nt} foretrakk tallfelt, '
                    f'andel = {nt/(ns+nt):.2f}, {fmt_p(bt.pvalue)}')
        cats = [c for c in conds] + ['ingen preferanse']
        obs = np.array([int(pc.get(c, 0)) for c in cats])
        if obs.sum() > 0:
            ch = stats.chisquare(obs)
            exp = obs.sum() / len(cats)
            say(f'Kji-kvadrat goodness-of-fit (alle {len(cats)} kategorier, lik forventning): chi2({len(cats)-1}) = '
                f'{ch.statistic:.3f}, {fmt_p(ch.pvalue)}' + ('  OBS: forventet frekvens < 5 – tolk med forsiktighet' if exp < 5 else ''))

    # Fitts-inspirert analyse
    say('\n================ FITTS-INSPIRERT ANALYSE (forsøksnivå) ================')
    sl = main_tr[(main_tr.condition == 'slider') & main_tr.distance.notna()].copy()
    if len(sl) > 5 and sl.distance.astype(float).nunique() > 2:
        sl['ID_bits'] = np.log2(sl.distance.astype(float) / 1.0 + 1)  # Shannon-form, W = 1 enhet (steg)
        lr = stats.linregress(sl.ID_bits, sl.time_ms)
        say(f'Slider: tid = {lr.intercept:.0f} + {lr.slope:.0f} × log2(D/W + 1) ms, r = {lr.rvalue:.3f}, R² = {lr.rvalue**2:.3f}, '
            f'{fmt_p(lr.pvalue)} (alle forsøk samlet, N = {len(sl)}; W = 1 verdisteg)')
        slopes = []
        for pid, g in sl.groupby('participant_id'):
            if g.ID_bits.nunique() > 2: slopes.append(stats.linregress(g.ID_bits, g.time_ms).slope)
        if len(slopes) >= 3:
            ts = stats.ttest_1samp(slopes, 0)
            say(f'  Stigning per deltaker: M = {np.mean(slopes):.0f} ms/bit, t({len(slopes)-1}) = {ts.statistic:.2f}, {fmt_p(ts.pvalue)} '
                '(tester om tiden øker med avstand; bedre enn samlet regresjon fordi forsøk ikke er uavhengige)')
        say('  NB: med konstant startverdi 0 er avstand = målverdi, så avstand og posisjon på skalaen er sammenblandet.')
    tf = main_tr[main_tr.condition == 'tallfelt']
    if len(tf):
        g = tf.groupby('n_digits').time_ms.median()
        say('Tallfelt: median tid per antall siffer: ' + ', '.join(f'{int(k)} siffer: {v:.0f} ms' for k, v in g.items())
            + ' (tallfelt forventes uavhengig av avstand)')
    say('\nMerk: Fitts\' lov gjelder pekebevegelser; for slider er dette en tilnærming (finjustering til eksakt verdi spiller også inn).')

    with open(os.path.join(a.out, 'resultater.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(OUT_LINES) + '\n')
    print(f'\nSkrev {a.out}/: sammendrag_lang.csv, sammendrag_bred_JASP.csv, hovedforsok_JASP.csv og resultater.txt')

if __name__ == '__main__':
    main()
