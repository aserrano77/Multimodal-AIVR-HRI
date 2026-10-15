#!/usr/bin/env python3
"""Statistical analysis of the Multimodal AI-VR study (C00 manual, C10 autonomous robot, C11 robot + voice).

Reproduces the inferential results reported in the article: confirmatory tests (H1-H3, RQ1),
exploratory measures and sensitivity analyses. Writes results.json, run_log.txt and run_meta.json.

Input: the participant-level tables, which are not shared (see docs/data_access.md):
  rounds.csv, participant_condition.csv, questionnaire.csv

Decision rules:
  * participant x condition value = mean of exactly two valid rounds (else missing); listwise per variable
  * omnibus test: repeated-measures ANOVA if Shapiro-Wilk on the additive-model residuals and Mauchly's test
    both give p >= .05, otherwise Friedman
  * pairwise contrasts C10-C00, C11-C10, C11-C00 only if the omnibus p < .05, Holm correction within variable
  * Wilcoxon signed-rank, two-sided, zero_method='wilcox', average ties, no continuity correction, method='auto'
  * Raw NASA-TLX analysed as the sum of the six integer items (exact ties); reported on the 0-100 scale (sum / 6)
  * H3: two one-sided tests on the C11-C10 NASA-TLX difference with equivalence bounds dz = +-0.5
  * effect sizes with 95% percentile bootstrap intervals (B = 10000, fixed seed)

Usage:
  python analysis.py --data-dir <folder with the three CSV files> --out <output folder>
"""
import argparse, json, hashlib, os, sys, warnings
import numpy as np, pandas as pd
from scipy import stats

warnings.filterwarnings('ignore')
ap = argparse.ArgumentParser()
ap.add_argument('--data-dir', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--B', type=int, default=10000)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
RNG = np.random.default_rng(20261010)
CONDS = ['C00', 'C10', 'C11']
PAIRS = [('C10', 'C00'), ('C11', 'C10'), ('C11', 'C00')]
ALPHA = .05

INPUTS = ['rounds.csv', 'participant_condition.csv', 'questionnaire.csv']
T1, T2, T3 = [pd.read_csv(os.path.join(args.data_dir, f)) for f in INPUTS]
T3 = T3.copy()
T3['TLX_sum'] = T3[['tlx_mental', 'tlx_physical', 'tlx_temporal', 'tlx_performance', 'tlx_effort', 'tlx_frustration']].sum(axis=1, min_count=6)
# participant whose session ran in a different application mode (sensitivity analysis S1)
DIFF_MODE = sorted(T2.loc[T2.sens_different_app_mode.astype(str).str.lower().isin(['true', '1']), 'participant_id'].unique())

OUT = {}   # everything that is written to results.json
LOG = []
def log(*a):
    s = ' '.join(str(x) for x in a); print(s); LOG.append(s)

# ---------------------------------------------------------------- helpers
def wide(df, var, req=CONDS, drop_codes=()):
    p = df.pivot(index='participant_id', columns='condition', values=var)
    p = p.reindex(columns=CONDS)
    p = p.drop(index=[c for c in drop_codes if c in p.index])
    return p[req].dropna()

def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * ps[i]); adj[i] = min(1, run)
    return adj

def mauchly(v):
    n, k = v.shape; p = k - 1
    C = np.zeros((p, k))
    for i in range(p):
        C[i, :i + 1] = 1; C[i, i + 1] = -(i + 1); C[i] /= np.linalg.norm(C[i])
    S = np.cov(v @ C.T, rowvar=False, ddof=1).reshape(p, p)
    W = np.linalg.det(S) / ((np.trace(S) / p) ** p)
    f = (2 * p * p + p + 2) / (6 * p * (n - 1))
    chi = -(n - 1) * (1 - f) * np.log(W); df = p * (p + 1) / 2 - 1
    return float(W), float(stats.chi2.sf(chi, df)), df

def gg_epsilon(v):
    k = v.shape[1]; S = np.cov(v, rowvar=False, ddof=1)
    Sc = S - S.mean(0, keepdims=True) - S.mean(1, keepdims=True)[:, :] + S.mean()
    return float(np.trace(Sc) ** 2 / ((k - 1) * np.sum(Sc ** 2)))

def anova_rm(v):
    n, k = v.shape; gm = v.mean()
    ss_c = n * ((v.mean(0) - gm) ** 2).sum(); ss_s = k * ((v.mean(1) - gm) ** 2).sum()
    ss_e = ((v - gm) ** 2).sum() - ss_c - ss_s
    d1, d2 = k - 1, (k - 1) * (n - 1)
    F = (ss_c / d1) / (ss_e / d2); p = stats.f.sf(F, d1, d2)
    eps = gg_epsilon(v); pgg = stats.f.sf(F, d1 * eps, d2 * eps)
    return dict(F=float(F), df1=d1, df2=d2, p=float(p), eta2p=float(ss_c / (ss_c + ss_e)), gg_eps=eps, p_gg=float(pgg))

def friedman(v):
    n, k = v.shape
    fr = stats.friedmanchisquare(*[v[:, j] for j in range(k)])
    return dict(chi2=float(fr.statistic), df=k - 1, p=float(fr.pvalue), W=float(fr.statistic / (n * (k - 1))))

def rank_biserial(d):
    nz = d[d != 0]
    if len(nz) == 0: return 0.0
    r = stats.rankdata(np.abs(nz)); wp = r[nz > 0].sum(); wm = r[nz < 0].sum()
    return float((wp - wm) / (wp + wm))

def dz(d):
    sd = d.std(ddof=1)
    return float(d.mean() / sd) if sd > 0 else np.nan

def boot(fn, data, B=None):
    B = B or args.B; n = len(data); vals = []
    for _ in range(B):
        idx = RNG.integers(0, n, n)
        try: vals.append(fn(data[idx]))
        except Exception: pass
    vals = np.array(vals, float); vals = vals[np.isfinite(vals)]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]

def wilcoxon_paired(d):
    w = stats.wilcoxon(d, zero_method='wilcox', method='auto', correction=False, alternative='two-sided')
    return float(w.statistic), float(w.pvalue)

def desc(x):
    x = np.asarray(x, float)
    return dict(n=int(len(x)), mean=float(x.mean()), sd=float(x.std(ddof=1)) if len(x) > 1 else np.nan,
                median=float(np.median(x)), q1=float(np.percentile(x, 25)), q3=float(np.percentile(x, 75)),
                min=float(x.min()), max=float(x.max()))

def analyse(X, name, force=None, quiet=False):
    """X: DataFrame participants x 3 conditions. Returns dict with both families; `primary` per rule."""
    v = X[CONDS].values.astype(float); n = len(v)
    resid = (v - v.mean(1, keepdims=True) - v.mean(0, keepdims=True) + v.mean()).ravel()
    sw = stats.shapiro(resid); W, pm, dfm = mauchly(v)
    rule_anova = (sw.pvalue >= ALPHA) and (pm >= ALPHA)
    # alternative assumption check (robustness): Shapiro-Wilk on the 3 paired differences, GG if sphericity fails
    sw_d = [float(stats.shapiro(v[:, a] - v[:, b]).pvalue) for a, b in [(1, 0), (2, 1), (2, 0)]]
    alt_anova = all(p >= ALPHA for p in sw_d)
    out = dict(var=name, n=n, shapiro_resid_W=float(sw.statistic), shapiro_resid_p=float(sw.pvalue),
               mauchly_W=W, mauchly_p=pm, shapiro_diffs_p=sw_d,
               rule_choice='ANOVA_RM' if rule_anova else 'Friedman',
               alt_rule_choice=('ANOVA_RM_GG' if alt_anova else 'Friedman'),
               desc={c: desc(X[c]) for c in CONDS})
    an = anova_rm(v); fr = friedman(v)
    an['eta2p_ci'] = boot(lambda s: anova_rm(s)['eta2p'], v)
    fr['W_ci'] = boot(lambda s: friedman(s)['W'], v)
    out['anova'] = an; out['friedman'] = fr
    primary = force or out['rule_choice']
    out['primary'] = primary
    for fam in ['ANOVA_RM', 'Friedman']:
        pom = an['p'] if fam == 'ANOVA_RM' else fr['p']
        rows = []
        if pom < ALPHA:
            for a, b in PAIRS:
                d = (X[a] - X[b]).values
                if fam == 'ANOVA_RM':
                    t = stats.ttest_rel(X[a], X[b]); sd = d.std(ddof=1)
                    ci = stats.t.interval(.95, n - 1, loc=d.mean(), scale=sd / np.sqrt(n))
                    rows.append(dict(contrast=f'{a}-{b}', test='paired_t', stat=float(t.statistic), df=n - 1, p=float(t.pvalue),
                                     effect_name='dz', effect=dz(d), effect_ci=boot(dz, d), mean_diff=float(d.mean()),
                                     mean_diff_ci=[float(ci[0]), float(ci[1])]))
                else:
                    wst, wp = wilcoxon_paired(d)
                    rows.append(dict(contrast=f'{a}-{b}', test='Wilcoxon', stat=wst, p=wp, effect_name='rank_biserial',
                                     effect=rank_biserial(d), effect_ci=boot(rank_biserial, d),
                                     mean_diff=float(d.mean()), median_diff=float(np.median(d)), n_nonzero=int((d != 0).sum())))
            adj = holm([r['p'] for r in rows])
            for r, a in zip(rows, adj): r['p_holm'] = float(a)
        out['contrasts_' + fam] = rows
        out['omnibus_sig_' + fam] = bool(pom < ALPHA)
    if not quiet:
        log(f"\n== {name}  N={n}  rule->{out['rule_choice']} (SW resid p={sw.pvalue:.3g}, Mauchly p={pm:.3g}); alternative rule->{out['alt_rule_choice']}")
        log('   ', {c: (round(out['desc'][c]['mean'], 3), round(out['desc'][c]['sd'], 3), round(out['desc'][c]['median'], 3)) for c in CONDS})
        log('    ANOVA F(%d,%d)=%.3f p=%.4g (GG eps=%.3f p_gg=%.4g) eta2p=%.3f %s' % (an['df1'], an['df2'], an['F'], an['p'], an['gg_eps'], an['p_gg'], an['eta2p'], np.round(an['eta2p_ci'], 3)))
        log('    Friedman chi2(2)=%.3f p=%.4g W=%.3f %s' % (fr['chi2'], fr['p'], fr['W'], np.round(fr['W_ci'], 3)))
        for fam in ['ANOVA_RM', 'Friedman']:
            for r in out['contrasts_' + fam]:
                log('    [%s] %s %s stat=%.3f p=%.4g p_holm=%.4g %s=%.3f %s' % (fam, r['contrast'], r['test'], r['stat'], r['p'], r['p_holm'], r['effect_name'], r['effect'], np.round(r['effect_ci'], 3)))
    return out

def paired_two(X, a, b, label, test='Wilcoxon'):
    """Exploratory paired comparison a-b (no omnibus), Wilcoxon two-sided."""
    d = (X[a] - X[b]).values; n = len(d)
    wst, wp = wilcoxon_paired(d) if np.any(d != 0) else (np.nan, np.nan)
    r = dict(label=label, n=n, a=a, b=b, mean_a=float(X[a].mean()), mean_b=float(X[b].mean()),
             median_a=float(X[a].median()), median_b=float(X[b].median()), W=wst, p=wp,
             rank_biserial=rank_biserial(d), rb_ci=boot(rank_biserial, d), mean_diff=float(d.mean()), median_diff=float(np.median(d)),
             n_nonzero=int((d != 0).sum()))
    log('  %-48s n=%d  %s: med %.3f  %s: med %.3f  W=%s p=%s rb=%.3f %s' % (label, n, a, r['median_a'], b, r['median_b'], r['W'], None if np.isnan(wp) else round(wp, 4), r['rank_biserial'], np.round(r['rb_ci'], 3)))
    return r

def tost_dz(d, bound=0.5):
    """TOST on the paired difference, equivalence bounds dz=+-bound (noncentral t)."""
    n = len(d); df = n - 1; m = d.mean(); sd = d.std(ddof=1); se = sd / np.sqrt(n); t = m / se
    p_lo = float(1 - stats.nct.cdf(t, df, -bound * np.sqrt(n)))   # H0: dz <= -bound
    p_hi = float(stats.nct.cdf(t, df, bound * np.sqrt(n)))        # H0: dz >= +bound
    # raw-units version with bounds = +-bound*sd
    L, U = -bound * sd, bound * sd
    t_lo = (m - L) / se; t_hi = (m - U) / se
    p_lo_raw = float(1 - stats.t.cdf(t_lo, df)); p_hi_raw = float(stats.t.cdf(t_hi, df))
    ci90 = stats.t.interval(.90, df, loc=m, scale=se)
    # nonparametric robustness: Wilcoxon on shifted differences
    shift = bound * sd
    try:
        p_np_lo = float(stats.wilcoxon(d + shift, zero_method='wilcox', method='auto', correction=False, alternative='greater').pvalue)
        p_np_hi = float(stats.wilcoxon(d - shift, zero_method='wilcox', method='auto', correction=False, alternative='less').pvalue)
    except Exception:
        p_np_lo = p_np_hi = np.nan
    return dict(n=n, bound_dz=bound, mean_diff=float(m), sd_diff=float(sd), dz=float(m / sd), dz_ci_boot=boot(dz, d),
                p_lower=p_lo, p_upper=p_hi, p_tost=max(p_lo, p_hi), equivalent=bool(max(p_lo, p_hi) < ALPHA),
                p_tost_rawunits=max(p_lo_raw, p_hi_raw), ci90_mean_diff=[float(ci90[0]), float(ci90[1])],
                bounds_raw=[float(L), float(U)], p_tost_wilcoxon=max(p_np_lo, p_np_hi), equivalent_wilcoxon=bool(max(p_np_lo, p_np_hi) < ALPHA))

# ---------------------------------------------------------------- 0. sample description
sess = T2.drop_duplicates('participant_id')
OUT['sample'] = dict(sessions=int(sess.participant_id.nunique()), trials_valid=int(len(T1)),
                     trials_by_condition=T1.groupby('condition').size().to_dict(),
                     perms=sess.condition_order.value_counts().sort_index().to_dict(),
                     questionnaire_sessions=int(T3[T3.Raw_TLX.notna()].participant_id.nunique()))
log(OUT['sample'])
for var in ['trial_duration_s', 'error_count']:
    Xc = wide(T2, var); OUT['sample'][f'N_complete_{var}'] = int(len(Xc))
OUT['sample']['N_B'] = {v: {c: int(T2[(T2.condition == c) & T2[v].notna()].shape[0]) for c in CONDS} for v in ['trial_duration_s', 'error_count']}
log('complete time/error N:', OUT['sample']['N_complete_trial_duration_s'], OUT['sample']['N_B'])

# ---------------------------------------------------------------- 1. CONFIRMATORY
log('\n#################  CONFIRMATORY  #################')
R = {}
X_time = wide(T2, 'trial_duration_s'); R['time'] = analyse(X_time, 'time (s) H1')
X_tlx = wide(T3, 'TLX_sum'); R['tlx'] = analyse(X_tlx, 'Raw NASA-TLX (sum of six items) RQ1, H3')
X_seq = wide(T3, 'SEQ'); R['seq'] = analyse(X_seq, 'SEQ H2')
# H1 verdict: C10-C00 on time
# H3: TOST on TLX C11-C10 (dz scale-free; composite = sum/6)
d_tlx = (X_tlx['C11'] - X_tlx['C10']).values
R['H3_tost'] = tost_dz(d_tlx / 6.0)  # composite scale; dz identical
R['H3_tost']['sum_scale_mean_diff'] = float(d_tlx.mean())
log('\n== H3 TOST (TLX C11-C10, bounds dz=+-0.5): n=%d mean diff(composite)=%.3f dz=%.3f p_TOST=%.4g equivalent=%s | raw-units p=%.4g | 90%%CI=%s | Wilcoxon-TOST p=%.4g' % (
    R['H3_tost']['n'], R['H3_tost']['mean_diff'], R['H3_tost']['dz'], R['H3_tost']['p_tost'], R['H3_tost']['equivalent'], R['H3_tost']['p_tost_rawunits'], np.round(R['H3_tost']['ci90_mean_diff'], 3), R['H3_tost']['p_tost_wilcoxon']))
OUT['confirmatory'] = R

# ---------------------------------------------------------------- 2. EXPLORATORY
log('\n#################  EXPLORATORY  #################')
E = {}
# 2.1 recorded failure events
X_err = wide(T2, 'error_count'); E['error_count'] = analyse(X_err, 'error_count (recorded failure events)')
ev_cols = [c for c in T2.columns if c.startswith('error_event__')]
brk = {}
for c in CONDS:
    sub = T2[(T2.condition == c) & T2.error_count.notna()]
    brk[c] = {e.replace('error_event__', ''): float(sub[e].sum() * 2) for e in ev_cols}   # per-participant means x2 trials = event totals
E['error_breakdown_event_totals_B'] = brk
tot = T1.groupby('condition').error_count.sum().to_dict(); E['error_total_events_all_valid_trials'] = {k: float(v) for k, v in tot.items()}
log('error events (all valid trials, A):', tot)
X_err2 = wide(T2, 'error_count_without_no_slot_incidents'); E['error_count_without_no_slot'] = analyse(X_err2, 'error_count without no-slot increments (SENS)')
# 2.2 robot sequence failure: McNemar C11 vs C10 on flag_any
fl = T2.pivot(index='participant_id', columns='condition', values='robot_sequence_failure__flag_any')[['C10', 'C11']].dropna()
b = int(((fl.C10 == 1) & (fl.C11 == 0)).sum()); c = int(((fl.C10 == 0) & (fl.C11 == 1)).sum())
mc = stats.binomtest(b, b + c, .5).pvalue if (b + c) > 0 else np.nan
E['robot_sequence_failure'] = dict(n=int(len(fl)), prop_C10=float(fl.C10.mean()), prop_C11=float(fl.C11.mean()), C10_only=b, C11_only=c,
                                   both=int(((fl.C10 == 1) & (fl.C11 == 1)).sum()), neither=int(((fl.C10 == 0) & (fl.C11 == 0)).sum()), mcnemar_exact_p=float(mc))
log('\nrobot sequence failure (any, active): n=%d  C10=%.3f C11=%.3f  discordant C10only=%d C11only=%d  McNemar exact p=%.4g' % (len(fl), fl.C10.mean(), fl.C11.mean(), b, c, mc))
# 2.3 two-condition exploratory (C11 vs C10)
def w2(var, label, df=T2):
    X = df.pivot(index='participant_id', columns='condition', values=var)[['C10', 'C11']].dropna()
    return paired_two(X, 'C11', 'C10', label)
E['target_selection_rejected'] = w2('target_selection_rejected_grasp_state', 'target selection rejected (grasp state)')
E['target_selection_robot_held'] = w2('target_selection_robot_held', 'target selection rejected, robot-held (is_held)')
E['robot_route_share'] = w2('robot_route_share', 'robot-route share of boxes')
E['safety_episodes'] = w2('safety_episodes', 'safety-stop episodes')
E['safety_duration_unity_s'] = w2('safety_duration_unity_s', 'safety-stop duration, Unity clock (s)')
# Spearman route share vs time
sp = {}
for c in ['C10', 'C11']:
    d = T2[T2.condition == c].set_index('participant_id')[['robot_route_share', 'trial_duration_s']].dropna()
    r = stats.spearmanr(d.robot_route_share, d.trial_duration_s); sp[c] = dict(n=int(len(d)), rho=float(r.statistic), p=float(r.pvalue))
E['spearman_route_share_time'] = sp; log('Spearman route share~time:', sp)
# 2.4 voice friction (C11)
vf = T2[T2.condition == 'C11'].set_index('participant_id')
va = vf.voice_rate_aggregated.dropna()
E['voice_friction'] = dict(n_rate_aggregated=int(len(va)), rate_aggregated_desc=desc(va), n_rate_mean=int(vf.voice_rate_mean.notna().sum()),
                           rate_mean_desc=desc(vf.voice_rate_mean.dropna()))
T1c = T1[T1.condition == 'C11']
E['voice_friction']['total_inputs'] = float(T1c.voice_inputs.sum()) if 'voice_inputs' in T1c else None
E['voice_friction']['total_rejections'] = float(T1c.voice_rejections.sum()) if 'voice_rejections' in T1c else None
if E['voice_friction']['total_inputs']:
    E['voice_friction']['pooled_rate'] = E['voice_friction']['total_rejections'] / E['voice_friction']['total_inputs']
reasons = [c for c in T1c.columns if c.startswith('voice_reason__')]
E['voice_friction']['reasons_total'] = {c.replace('voice_reason__', ''): float(T1c[c].sum()) for c in reasons if T1c[c].sum() > 0}
log('\nvoice friction C11:', json.dumps(E['voice_friction'], default=float)[:900])
q11 = T3[T3.condition == 'C11'].set_index('participant_id')
tdiff = (T2[T2.condition == 'C11'].set_index('participant_id').trial_duration_s - T2[T2.condition == 'C10'].set_index('participant_id').trial_duration_s)
spv = {}
for lab, s in [('SEQ_C11', q11.SEQ), ('voice_comprehension', q11.voice_comprehension), ('voice_correspondence', q11.voice_correspondence),
               ('voice_control', q11.voice_control), ('time_C11_minus_C10', tdiff)]:
    d = pd.concat([va.rename('rate'), s.rename('y')], axis=1).dropna()
    if len(d) > 3:
        r = stats.spearmanr(d.rate, d.y); spv[lab] = dict(n=int(len(d)), rho=float(r.statistic), p=float(r.pvalue))
E['voice_spearman'] = spv; log('voice rate Spearman:', spv)
# 2.5 headset failures
uit = T1.groupby('condition').apply(lambda g: dict(trials=int(len(g)), trials_with_ui_recovery_failed=int((g.ui_recovery_failed > 0).sum()),
                                                  sessions=int(g.loc[g.ui_recovery_failed > 0, 'participant_id'].nunique())))
E['ui_recovery_failed_trials'] = uit.to_dict(); log('\nui_recovery_failed trials:', E['ui_recovery_failed_trials'])
OUT['exploratory'] = E

# ---------------------------------------------------------------- 3. SENSITIVITY
log('\n#################  SENSITIVITY  #################')
S = {}
log('\n-- S1 without the session that ran in a different application mode')
dropc = DIFF_MODE
S['diffmode_excluded_time'] = analyse(wide(T2, 'trial_duration_s', drop_codes=dropc), 'time without different-mode session')
S['diffmode_excluded_error'] = analyse(wide(T2, 'error_count', drop_codes=dropc), 'error_count without different-mode session')
S['diffmode_excluded_tlx'] = analyse(wide(T3, 'TLX_sum', drop_codes=dropc), 'TLX without different-mode session')
S['diffmode_excluded_seq'] = analyse(wide(T3, 'SEQ', drop_codes=dropc), 'SEQ without different-mode session')
Xn = wide(T3, 'TLX_sum', drop_codes=dropc)
S['diffmode_excluded_H3'] = tost_dz(((Xn['C11'] - Xn['C10']) / 6.).values)
log('H3 without different-mode session: n=%d dz=%.3f p_TOST=%.4g equivalent=%s' % (S['diffmode_excluded_H3']['n'], S['diffmode_excluded_H3']['dz'], S['diffmode_excluded_H3']['p_tost'], S['diffmode_excluded_H3']['equivalent']))
log('\n-- S2 time without trials with ui_recovery_failed (mean of remaining valid trials, >=1)')
S['time_no_ui'] = analyse(wide(T2, 'trial_duration_s__no_ui'), 'time without ui_recovery_failed trials')
S['error_no_ui'] = analyse(wide(T2, 'error_count__no_ui'), 'error_count without ui_recovery_failed trials')
log('\n-- S3 participants with at least one valid round per condition (any1)')
S['time_any1'] = analyse(wide(T2, 'trial_duration_s__any1'), 'time, >=1 valid trial per condition')
S['error_any1'] = analyse(wide(T2, 'error_count__any1'), 'error_count, >=1 valid trial per condition')

# round-level mixed models
import statsmodels.formula.api as smf
import statsmodels.api as sm
tr = T1.copy()
tr['log_time'] = np.log(tr.trial_duration_s)
tr['cond'] = pd.Categorical(tr.condition, categories=CONDS)
tr['pos'] = tr.position_of_condition_in_order.astype(int).astype(str)
tr['rnd'] = tr.round_index.astype(int).astype(str)
tr['pid'] = tr.participant_id
M = {}
try:
    m = smf.mixedlm('log_time ~ C(cond, Treatment("C00")) + C(pos) + C(rnd)', tr, groups=tr['pid']).fit(reml=True)
    M['logtime_lmm'] = {k: dict(coef=float(m.params[k]), se=float(m.bse[k]), p=float(m.pvalues[k]), ci=[float(m.conf_int().loc[k, 0]), float(m.conf_int().loc[k, 1])]) for k in m.params.index if k != 'Group Var'}
    M['logtime_lmm']['n_trials'] = int(len(tr)); M['logtime_lmm']['n_participants'] = int(tr.pid.nunique())
    # C11 vs C10
    tr['cond2'] = pd.Categorical(tr.condition, categories=['C10', 'C00', 'C11'])
    m2 = smf.mixedlm('log_time ~ C(cond2) + C(pos) + C(rnd)', tr, groups=tr['pid']).fit(reml=True)
    k = 'C(cond2)[T.C11]'; M['logtime_lmm_C11_vs_C10'] = dict(coef=float(m2.params[k]), se=float(m2.bse[k]), p=float(m2.pvalues[k]))
    log('\nLMM log-time (round level, %d trials, %d participants):' % (len(tr), tr.pid.nunique()))
    for k, v in M['logtime_lmm'].items():
        if isinstance(v, dict): log('   %-40s coef=%.4f se=%.4f p=%.4g' % (k, v['coef'], v['se'], v['p']))
    log('   C11 vs C10: coef=%.4f p=%.4g' % (M['logtime_lmm_C11_vs_C10']['coef'], M['logtime_lmm_C11_vs_C10']['p']))
except Exception as e:
    M['logtime_lmm'] = {'error': str(e)}; log('LMM error', e)
# counts: Poisson GEE (exchangeable) and NB GLM with cluster-robust SE
try:
    for outc in ['error_count', 'error_count_without_no_slot_incidents']:
        g = sm.GEE.from_formula(f'{outc} ~ C(cond, Treatment("C00")) + C(pos) + C(rnd)', 'pid', tr, family=sm.families.Poisson(), cov_struct=sm.cov_struct.Exchangeable()).fit()
        M['gee_poisson_' + outc] = {k: dict(coef=float(g.params[k]), irr=float(np.exp(g.params[k])), p=float(g.pvalues[k]), ci_irr=[float(np.exp(g.conf_int().loc[k, 0])), float(np.exp(g.conf_int().loc[k, 1]))]) for k in g.params.index}
        log(f'\nGEE Poisson {outc}:', {k: (round(v['irr'], 3), round(v['p'], 4)) for k, v in M['gee_poisson_' + outc].items() if 'cond' in k})
        tr['cond2'] = pd.Categorical(tr.condition, categories=['C10', 'C00', 'C11'])
        g2 = sm.GEE.from_formula(f'{outc} ~ C(cond2) + C(pos) + C(rnd)', 'pid', tr, family=sm.families.Poisson(), cov_struct=sm.cov_struct.Exchangeable()).fit()
        k = 'C(cond2)[T.C11]'; M['gee_poisson_' + outc + '_C11_vs_C10'] = dict(irr=float(np.exp(g2.params[k])), p=float(g2.pvalues[k]))
        log('   C11 vs C10 IRR=%.3f p=%.4g' % (np.exp(g2.params[k]), g2.pvalues[k]))
except Exception as e:
    M['gee_error'] = str(e); log('GEE error', e)
# questionnaires, participant-condition level LMM (all participants with any questionnaire data)
q = T3.copy(); q['pos'] = q.position_of_condition_in_order.astype(int).astype(str)
for var, lab in [('TLX_sum', 'tlx'), ('SEQ', 'seq')]:
    d = q[q[var].notna()]
    try:
        m = smf.mixedlm(f'{var} ~ C(condition, Treatment("C00")) + C(pos)', d, groups=d['participant_id']).fit(reml=True)
        M['lmm_' + lab] = {k: dict(coef=float(m.params[k]), se=float(m.bse[k]), p=float(m.pvalues[k])) for k in m.params.index if k != 'Group Var'}
        d2 = d.copy(); d2['c2'] = pd.Categorical(d2.condition, categories=['C10', 'C00', 'C11'])
        m2 = smf.mixedlm(f'{var} ~ C(c2) + C(pos)', d2, groups=d2['participant_id']).fit(reml=True)
        M['lmm_' + lab + '_C11_vs_C10'] = dict(coef=float(m2.params['C(c2)[T.C11]']), p=float(m2.pvalues['C(c2)[T.C11]']))
        log(f'\nLMM {lab} (n obs={len(d)}):', {k: (round(v['coef'], 3), round(v['p'], 4)) for k, v in M['lmm_' + lab].items() if 'condition' in k}, 'C11-C10:', M['lmm_' + lab + '_C11_vs_C10'])
    except Exception as e:
        M['lmm_' + lab] = {'error': str(e)}; log('LMM q error', e)
S['mixed_models'] = M

# order / learning effect (descriptive check of position)
ordr = tr.groupby(['pos']).trial_duration_s.agg(['mean', 'median', 'size']).round(2).to_dict('index'); S['time_by_position_of_condition'] = ordr; log('\ntime by position of condition in order:', ordr)
ordr2 = tr.groupby(['rnd']).trial_duration_s.agg(['mean', 'median', 'size']).round(2).to_dict('index'); S['time_by_round'] = ordr2; log('time by round:', ordr2)
OUT['sensitivity'] = S

# ---------------------------------------------------------------- write
def default(o):
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, np.ndarray): return o.tolist()
    if isinstance(o, (np.bool_,)): return bool(o)
    return str(o)
json.dump(OUT, open(os.path.join(args.out, 'results.json'), 'w'), indent=1, default=default)
open(os.path.join(args.out, 'run_log.txt'), 'w').write('\n'.join(LOG))
inp = {f: hashlib.sha256(open(os.path.join(args.data_dir, f), 'rb').read()).hexdigest() for f in INPUTS}
json.dump(dict(inputs=inp, script_sha256=hashlib.sha256(open(__file__, 'rb').read()).hexdigest(), python=sys.version, numpy=np.__version__,
               pandas=pd.__version__, scipy=__import__('scipy').__version__, statsmodels=__import__('statsmodels').__version__, B=args.B, seed=20261010),
          open(os.path.join(args.out, 'run_meta.json'), 'w'), indent=1)
log('\nDONE')
