#!/usr/bin/env python3
"""Figures 3-5 of the article (execution time; NASA-TLX and SEQ; work split and voice rejections).

Usage:  python figures.py --data-dir <folder with the participant-level tables> --out <folder>
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, FuncFormatter, NullFormatter

import argparse, os
ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); ap.add_argument('--out', required=True)
args = ap.parse_args(); os.makedirs(args.out, exist_ok=True)
OUT = args.out.rstrip('/') + '/'
T1, T2, T3 = [pd.read_csv(os.path.join(args.data_dir, f)) for f in ['rounds.csv', 'participant_condition.csv', 'questionnaire.csv']]
CONDS = ['C00', 'C10', 'C11']
LAB = {'C00': 'Manual\n(C00)', 'C10': 'Robot\n(C10)', 'C11': 'Robot + voice\n(C11)'}
COL = {'C00': '#2a78d6', 'C10': '#eb6834', 'C11': '#1baf7a'}
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.edgecolor': INK2, 'axes.labelcolor': INK,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'savefig.dpi': 300})
rng = np.random.default_rng(7)

def paired(ax, X, conds, ylabel, log=False, ylim=None, jit=0.07, lines=True):
    xs = np.arange(len(conds))
    J = rng.uniform(-jit, jit, size=(len(X), len(conds)))
    if lines:
        for k, (_, row) in enumerate(X.iterrows()):
            ax.plot(xs + J[k], row[conds].values, color='#b9b8b2', lw=0.5, alpha=0.6, zorder=1)
    for i, c in enumerate(conds):
        v = X[c].values
        ax.scatter(i + J[:, i], v, s=9, color=COL[c], edgecolor='white', linewidth=0.4, zorder=3)
        ax.boxplot(v, positions=[i], widths=0.42, showfliers=False, patch_artist=True, zorder=2,
                   medianprops=dict(color=INK, lw=1.4), boxprops=dict(facecolor='none', edgecolor=INK2, lw=0.8),
                   whiskerprops=dict(color=INK2, lw=0.8), capprops=dict(color=INK2, lw=0.8))
    ax.set_xticks(xs); ax.set_xticklabels([LAB[c] for c in conds])
    ax.set_ylabel(ylabel)
    if log:
        ax.set_yscale('log')
        ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator([20, 50, 100, 200, 500]))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f'{int(v)}'))
        ax.yaxis.set_minor_formatter(NullFormatter())
    if ylim: ax.set_ylim(*ylim)
    ax.yaxis.grid(True, color=GRID, lw=0.5); ax.set_axisbelow(True)
    ax.set_xlim(-0.5, len(conds) - 0.5)

def wide(df, var, conds=CONDS):
    return df.pivot(index='participant_id', columns='condition', values=var)[conds].dropna()

# Figure 3: execution time
X = wide(T2, 'trial_duration_s')
fig, ax = plt.subplots(figsize=(4.2, 3.0))
paired(ax, X, CONDS, 'Execution time per round, s (log scale)', log=True, ylim=(18, 500))
ax.set_title(f'N = {len(X)}; grey lines join each participant across conditions', fontsize=7.5, color=INK2, loc='left')
fig.tight_layout(); fig.savefig(OUT + 'fig3_time.pdf'); fig.savefig(OUT + 'fig3_time.png'); plt.close(fig)

# Figure 4: NASA-TLX and SEQ
T3 = T3.copy(); dims = ['tlx_mental', 'tlx_physical', 'tlx_temporal', 'tlx_performance', 'tlx_effort', 'tlx_frustration']
T3['TLX'] = T3[dims].sum(axis=1, min_count=6) / 6
fig, axs = plt.subplots(1, 2, figsize=(6.0, 2.9))
Xt = wide(T3, 'TLX'); paired(axs[0], Xt, CONDS, 'Raw NASA-TLX (0–100)', ylim=(-3, 103))
axs[0].set_title(f'(a) Perceived workload, N = {len(Xt)}', fontsize=8, loc='left', color=INK)
Xs = wide(T3, 'SEQ'); paired(axs[1], Xs, CONDS, 'SEQ (1 = very difficult, 7 = very easy)', ylim=(0.6, 7.4), jit=0.2, lines=False)
axs[1].set_yticks(range(1, 8))
axs[1].set_title(f'(b) Perceived ease, N = {len(Xs)}', fontsize=8, loc='left', color=INK)
fig.tight_layout(); fig.savefig(OUT + 'fig4_questionnaires.pdf'); fig.savefig(OUT + 'fig4_questionnaires.png'); plt.close(fig)

# Figure 5: work split and voice rejections
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.9), gridspec_kw=dict(width_ratios=[1, 1.6]))
Xr = wide(T2, 'robot_route_share', ['C10', 'C11']) * 100
paired(axs[0], Xr, ['C10', 'C11'], 'Boxes deposited by the robot, %', ylim=(-4, 104), jit=0.09)
axs[0].set_title(f'(a) Work split, N = {len(Xr)}', fontsize=8, loc='left', color=INK)
c11 = T1[T1.condition == 'C11']
groups = [('Speech not recognized', ['normalization_not_executable_Unrecognized']),
          ('Pick-only request (unsupported)', ['unsupported_operational_intent_Pick']),
          ('No valid deposit slot', ['no_valid_deposit_slot']),
          ('Nothing to resume', ['no_stopped_task_to_resume']),
          ('Ambiguous utterance', ['normalization_not_executable_Ambiguous']),
          ('Other reasons (7 types)', None)]
tot = {c.replace('voice_reason__', ''): c11[c].sum() for c in c11.columns if c.startswith('voice_reason__')}
used = set(); vals = []
for name, keys in groups:
    if keys: v = sum(tot[k] for k in keys); used |= set(keys)
    else: v = sum(val for k, val in tot.items() if k not in used)
    vals.append((name, v))
total_rej = sum(v for _, v in vals); total_in = c11.voice_inputs.sum()
names = [n for n, _ in vals][::-1]; v = [x for _, x in vals][::-1]
axs[1].barh(names, v, color=COL['C11'], height=0.62)
for i, x in enumerate(v):
    axs[1].text(x + 3, i, f'{int(x)} ({x / total_rej * 100:.0f}%)', va='center', fontsize=7, color=INK)
axs[1].set_xlim(0, max(v) * 1.32); axs[1].set_xlabel('Rejected voice inputs')
axs[1].xaxis.grid(True, color=GRID, lw=0.5); axs[1].set_axisbelow(True)
axs[1].spines['left'].set_visible(False); axs[1].tick_params(axis='y', length=0)
axs[1].set_title(f'(b) Voice rejections: {int(total_rej)} of {int(total_in)} inputs', fontsize=8, loc='left', color=INK)
fig.tight_layout(); fig.savefig(OUT + 'fig5_mechanism.pdf'); fig.savefig(OUT + 'fig5_mechanism.png'); plt.close(fig)
print('figures written:', len(X), len(Xt), len(Xs), len(Xr), int(total_rej), int(total_in))
