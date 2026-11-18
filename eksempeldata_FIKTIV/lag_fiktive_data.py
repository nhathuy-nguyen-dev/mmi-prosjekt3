#!/usr/bin/env python3
"""FIKTIVE DATA – kun for å teste analyse.py. Skal ALDRI brukes som resultater i rapporten.
Simulerer 16 deltakere i samme CSV-format som test.html. --stepper gir tre betingelser."""
import csv, random, math, sys
STEPPER = '--stepper' in sys.argv
POOL = [3, 8, 14, 17, 22, 27, 33, 38, 41, 46, 53, 58, 62, 67, 73, 79, 84, 88, 92, 97]
rnd = random.Random(42)
conds = ['slider', 'tallfelt'] + (['stepper'] if STEPPER else [])
orders = ({'O1':['slider','tallfelt','stepper'],'O2':['slider','stepper','tallfelt'],'O3':['tallfelt','slider','stepper'],
           'O4':['tallfelt','stepper','slider'],'O5':['stepper','slider','tallfelt'],'O6':['stepper','tallfelt','slider']}
          if STEPPER else {'A':['slider','tallfelt'],'B':['tallfelt','slider']})
okeys = list(orders)
TC = ['participant_id','order','device','condition','condition_pos','trial_no','practice','target','start_value','distance','n_digits',
      'response','correct','abs_error','time_ms','first_interaction_ms','n_interactions','n_value_changes','n_backspaces','n_empty_submits',
      'slider_track_px','screen_w','screen_h','dpr','session_id','timestamp']
trials, quests = [], []
suffix = '_3betingelser' if STEPPER else ''
for i in range(1, 17):
    pid = f'P{i:02d}'; order = okeys[(i-1) % len(okeys)]; sid = f'{pid}_FIKTIV'
    speed = rnd.gauss(1.0, 0.15)
    q = {'participant_id': pid, 'order': order, 'device': 'mobil'}
    for pos, c in enumerate(orders[order], 1):
        targets = [12, 64, 89] + rnd.sample(POOL, 20)
        for k, t in enumerate(targets):
            prac = 1 if k < 3 else 0
            learn = 0.95 if pos > 1 else 1.0
            start = 0 if c != 'tallfelt' else ''
            if c == 'slider':
                tm = (900 + 380 * math.log2(t + 1)) * speed * learn + rnd.gauss(0, 300)
                err = rnd.choices([0, 1, 2, 3], [0.72, 0.18, 0.07, 0.03])[0]
            elif c == 'tallfelt':
                tm = (1500 + 280 * len(str(t))) * speed * learn + rnd.gauss(0, 280)
                err = 1 if rnd.random() < 0.03 else 0
            else:
                tm = (1300 + 260 * (t // 10 + t % 10)) * speed * learn + rnd.gauss(0, 300)
                err = 1 if rnd.random() < 0.04 else 0
            resp = max(0, min(100, t + err * rnd.choice([-1, 1])))
            trials.append(dict(participant_id=pid, order=order, device='mobil', condition=c, condition_pos=pos,
                trial_no=(k+1 if prac else k-2), practice=prac, target=t, start_value=start,
                distance=(abs(t-0) if c != 'tallfelt' else ''), n_digits=len(str(t)), response=resp,
                correct=int(resp == t), abs_error=abs(resp-t), time_ms=max(350, round(tm)),
                first_interaction_ms=round(rnd.uniform(350, 700)), n_interactions=rnd.randint(1, 4),
                n_value_changes=rnd.randint(1, 30), n_backspaces=(rnd.choice([0,0,0,1]) if c == 'tallfelt' else ''),
                n_empty_submits=0, slider_track_px=(354 if c == 'slider' else ''), screen_w=390, screen_h=844, dpr=3,
                session_id=sid, timestamp='FIKTIV'))
        base = {'slider': 5, 'tallfelt': 6, 'stepper': 4}[c]
        for item in ['seq', 'presisjon', 'behagelig']:
            q[f'{item}_{c}'] = max(1, min(7, base + rnd.choice([-1, 0, 0, 1])))
    q.update(preference=rnd.choices(conds + ['ingen preferanse'], [4, 9] + ([2] if STEPPER else []) + [2])[0],
             comment='FIKTIV', age_range=rnd.choice(['20-24', '25-29']), gender=rnd.choice(['kvinne', 'mann', 'vil ikke oppgi']),
             hand=rnd.choice(['hoyre'] * 7 + ['venstre']), completed=1, screen_w=390, screen_h=844, dpr=3,
             user_agent='FIKTIV', session_id=sid, timestamp='FIKTIV')
    quests.append(q)
with open(f'FIKTIV_forsok{suffix}.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, TC); w.writeheader(); w.writerows(trials)
qc = ['participant_id','order','device'] + [f'{it}_{c}' for c in conds for it in ['seq','presisjon','behagelig']] + \
     ['preference','comment','age_range','gender','hand','completed','screen_w','screen_h','dpr','user_agent','session_id','timestamp']
with open(f'FIKTIV_sporreskjema{suffix}.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, qc); w.writeheader(); w.writerows(quests)
print('Skrev FIKTIVE data', suffix)
