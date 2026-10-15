#!/usr/bin/env python3
"""Descriptive statistics of the Multimodal AI-VR study.

Produces the aggregated tables published in results/ (sample, participants, descriptive statistics by
condition, voice-channel questionnaire items, final preference, robot operation, voice rejections).
Inferential tests are in analysis.py.

Input: the participant-level tables (not shared; see docs/data_access.md) rounds.csv, participant_condition.csv, questionnaire.csv, participants.csv
Usage:  python descriptives.py --data-dir <folder> --out <folder>
"""
import argparse, os
import numpy as np, pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

ap = argparse.ArgumentParser()
ap.add_argument('--data-dir', required=True)
ap.add_argument('--out', required=True)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
rd = lambda f: pd.read_csv(os.path.join(args.data_dir, f))
R, PC, Q, P = rd('rounds.csv'), rd('participant_condition.csv'), rd('questionnaire.csv'), rd('participants.csv')
CONDS = ['C00', 'C10', 'C11']
TLX = ['tlx_mental', 'tlx_physical', 'tlx_temporal', 'tlx_performance', 'tlx_effort', 'tlx_frustration']
Q['Raw_TLX_0_100'] = Q[TLX].sum(axis=1, min_count=6) / 6

def save(df, name):
    df.to_csv(os.path.join(args.out, name), index=False, float_format='%.6g'); print('wrote', name, df.shape)

def wide(df, var, conds=CONDS):
    return df.pivot(index='participant_id', columns='condition', values=var)[conds].dropna()

def summary(x):
    x = pd.Series(x, dtype=float).dropna()
    return dict(n=len(x), mean=x.mean(), sd=x.std(ddof=1), median=x.median(), q1=x.quantile(.25), q3=x.quantile(.75),
                min=x.min(), max=x.max())

# ------------------------------------------------------------------ 1. sample
rows = [dict(item='participants included', value=P.participant_id.nunique()),
        dict(item='valid rounds', value=len(R))]
rows += [dict(item=f'valid rounds {c}', value=int((R.condition == c).sum())) for c in CONDS]
rows += [dict(item='rounds with five boxes deposited', value=int((R.deposited_boxes == 5).sum()))]
rows += [dict(item='questionnaire submissions', value=int(P.questionnaire_submitted.sum()))]
rows += [dict(item='participants with two valid rounds in every condition (time)', value=len(wide(PC, 'trial_duration_s')))]
rows += [dict(item='participants with two valid rounds in C10 and C11', value=len(wide(PC, 'robot_route_share', ['C10', 'C11'])))]
rows += [dict(item=f'participants with condition order {o}', value=int(n)) for o, n in P.condition_order.value_counts().sort_index().items()]
for c in CONDS:
    rows.append(dict(item=f'participants with two valid rounds in {c}', value=int(PC[(PC.condition == c) & PC.trial_duration_s.notna()].shape[0])))
save(pd.DataFrame(rows), 'sample.csv')

# ------------------------------------------------------------------ 2. participants (questionnaire respondents)
S = P[P.questionnaire_submitted].copy(); n = len(S)
# answer codes as defined in docs/questionnaire_xlsform.xlsx (sheet 'choices')
GENDER = {1: 'Woman', 2: 'Man', 3: 'Non-binary or other gender identity', 99: 'Prefer not to answer'}
EDU = {1: 'Primary education or less', 2: 'Compulsory secondary education or equivalent', 3: 'Upper secondary education (Bachillerato)',
       4: 'Intermediate vocational training', 5: 'Higher vocational training', 6: "Bachelor's degree or equivalent",
       7: "Master's degree, postgraduate or equivalent", 8: 'Doctorate', 97: 'Other level', 99: 'Prefer not to answer'}
AREA = {1: 'Computing, telecommunications, architecture or engineering', 2: 'Natural sciences, mathematics or health sciences',
        3: 'Social sciences, law, economics, education or humanities', 4: 'Arts, design or communication',
        5: 'Industry, technical trades, construction, transport or logistics', 6: 'Administration, commerce, hospitality or other services',
        7: 'Not currently studying or working in a defined area', 97: 'Other area', 99: 'Prefer not to answer'}
rows = []
a = summary(S.age); rows.append(dict(variable='age', category='', n=a['n'], percent=np.nan, mean=a['mean'], sd=a['sd'], median=a['median'],
                                     q1=a['q1'], q3=a['q3'], min=a['min'], max=a['max']))
for var, lab in [('gender_code', GENDER), ('education_code', EDU), ('area_code', AREA)]:
    vc = S[var].value_counts()
    for code, cnt in sorted(vc.items()):
        rows.append(dict(variable=var.replace('_code', ''), category=lab.get(int(code), f'code {int(code)}'), n=int(cnt), percent=100 * cnt / n))
for var in ['vr_sessions_12m', 'robot_interactions_12m', 'voice_assistant_days_30d']:
    a = summary(S[var]); z = int((S[var] == 0).sum())
    rows.append(dict(variable=var, category='summary', n=a['n'], percent=np.nan, mean=a['mean'], sd=a['sd'], median=a['median'],
                     q1=a['q1'], q3=a['q3'], min=a['min'], max=a['max']))
    rows.append(dict(variable=var, category='zero', n=z, percent=100 * z / a['n']))
save(pd.DataFrame(rows), 'participants_summary.csv')

# ------------------------------------------------------------------ 3. descriptive statistics by condition
spec = [  # variable, table, conditions required for the analysis sample, label
    ('trial_duration_s', PC, CONDS, 'Execution time per round (s)'),
    ('error_count', PC, CONDS, 'Recorded failure events per round'),
    ('error_count_without_no_slot_incidents', PC, CONDS, 'Recorded failure events per round, without no-slot voice rejections'),
    ('Raw_TLX_0_100', Q, CONDS, 'Raw NASA-TLX (0-100)')] + \
    [(d, Q, CONDS, f'NASA-TLX {d[4:]} (0-100)') for d in TLX] + [
    ('SEQ', Q, CONDS, 'Single Ease Question (1-7)'),
    ('robot_route_share', PC, ['C10', 'C11'], 'Share of boxes deposited by the robot'),
    ('robot_sequence_failure_active', PC, ['C10', 'C11'], 'Robot sequence failures per round'),
    ('target_selection_rejected_grasp_state', PC, ['C10', 'C11'], 'Grasp-state rejections per round'),
    ('safety_episodes', PC, ['C10', 'C11'], 'Safety-stop episodes per round'),
    ('safety_duration_unity_s', PC, ['C10', 'C11'], 'Safety-stop duration per round (s)'),
    ('voice_rate_aggregated', PC, ['C11'], 'Voice rejection rate (rejections / processed inputs)'),
    ('voice_comprehension', Q, ['C11'], 'Voice: comprehension of available commands (0-10)'),
    ('voice_correspondence', Q, ['C11'], 'Voice: command-response correspondence (0-10)'),
    ('voice_control', Q, ['C11'], 'Voice: perceived ability to intervene (0-10)')]
rows = []
for var, df, req, lab in spec:
    X = wide(df, var, req)
    for c in req:
        rows.append(dict(variable=var, label=lab, condition=c, sample='complete in ' + '+'.join(req), **summary(X[c])))
save(pd.DataFrame(rows), 'descriptives_by_condition.csv')

# ------------------------------------------------------------------ 4. final preference
pref = S.preference_code.dropna().astype(int)
PREF = {1: 'Manual, without the robot', 2: 'Autonomous robot without voice commands', 3: 'Autonomous robot with voice commands', 4: 'No clear preference'}
rows = []
for k in [1, 2, 3, 4]:
    x = int((pref == k).sum()); lo, hi = proportion_confint(x, len(pref), method='wilson')
    rows.append(dict(preference=PREF[k], n=x, percent=100 * x / len(pref), wilson_ci95_low=100 * lo, wilson_ci95_high=100 * hi))
obs = [int((pref == k).sum()) for k in [1, 2, 3]]
chi = stats.chisquare(obs)
rows.append(dict(preference=f'chi-square against a uniform split of the three options: chi2(2) = {chi.statistic:.4f}, p = {chi.pvalue:.4f}', n=len(pref)))
save(pd.DataFrame(rows), 'preference.csv')

# ------------------------------------------------------------------ 5. robot operation and voice rejections (all valid rounds)
rows = []
for c in ['C10', 'C11']:
    r = R[R.condition == c]
    rows += [dict(condition=c, measure='valid rounds', value=len(r)),
             dict(condition=c, measure='boxes deposited by the robot', value=r.robot_route_boxes.sum()),
             dict(condition=c, measure='boxes deposited', value=r.total_boxes.sum()),
             dict(condition=c, measure='robot sequence failures', value=r.robot_sequence_failure_active.sum()),
             dict(condition=c, measure='grasp-state rejections', value=r.target_selection_rejected_grasp_state.sum()),
             dict(condition=c, measure='grasp-state rejections, box held by the robot', value=r.target_selection_robot_held.sum()),
             dict(condition=c, measure='grasp-state rejections, holder undetermined', value=r.target_selection_actor_undetermined.sum()),
             dict(condition=c, measure='safety-stop episodes', value=r.safety_episodes.sum()),
             dict(condition=c, measure='rounds with a safety stop', value=int((r.safety_episodes > 0).sum()))]
for c in CONDS:
    r = R[R.condition == c]
    rows += [dict(condition=c, measure='recorded failure events', value=r.error_count.sum()),
             dict(condition=c, measure='rounds with a headset recovery failure', value=int((r.ui_recovery_failed > 0).sum()))]
r = R[R.condition == 'C11']
rows += [dict(condition='C11', measure='no-slot increments of the failure-event counter', value=r.no_slot_error_increments_removed.sum())]
save(pd.DataFrame(rows), 'robot_operation_totals.csv')

reasons = {c.replace('voice_reason__', ''): r[c].sum() for c in r.columns if c.startswith('voice_reason__')}
tot_rej = r.voice_rejections.sum(); tot_in = r.voice_inputs.sum()
rows = [dict(reason=k, rejections=v, percent_of_rejections=100 * v / tot_rej) for k, v in sorted(reasons.items(), key=lambda kv: -kv[1])]
per_participant = r.groupby('participant_id').voice_inputs.sum()
rows += [dict(reason='TOTAL rejections', rejections=tot_rej, percent_of_rejections=100.0),
         dict(reason='TOTAL processed voice inputs', rejections=tot_in, percent_of_rejections=np.nan),
         dict(reason='voice-condition rounds without processed input', rejections=int((r.voice_inputs == 0).sum()), percent_of_rejections=np.nan),
         dict(reason='participants without processed input in their valid voice rounds', rejections=int(P.participant_id.nunique() - (per_participant > 0).sum()), percent_of_rejections=np.nan)]
save(pd.DataFrame(rows), 'voice_rejections.csv')
