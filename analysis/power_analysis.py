#!/usr/bin/env python3
"""Power analysis reported in the article (no data needed).

1. Repeated-measures omnibus test across three conditions (alpha = .05, power = .90, correlation .5 between
   repeated measures, nonsphericity correction 1): minimum N for f = 0.25, and smallest f detectable with N = 50.
   Noncentrality lambda = f^2 * N * m / (1 - rho), as in G*Power ("ANOVA: repeated measures, within factors").
2. Equivalence test of H3 (two one-sided tests, bounds dz = +-b) with N = 57 and no true difference.

Usage:  python power_analysis.py --out <folder>
"""
import argparse, os
import numpy as np, pandas as pd
from scipy import stats, optimize

ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)

def power_rm(f, n, m=3, rho=.5, alpha=.05):
    lam = f ** 2 * n * m / (1 - rho); d1 = m - 1; d2 = (n - 1) * (m - 1)
    return float(stats.ncf.sf(stats.f.ppf(1 - alpha, d1, d2), d1, d2, lam))

def power_tost(n, bound, alpha=.05):
    """Power of the dz-scale TOST used in analysis.py (noncentral t), true dz = 0."""
    df = n - 1; nc = bound * np.sqrt(n)
    lo = stats.nct.ppf(1 - alpha, df, -nc); hi = stats.nct.ppf(alpha, df, nc)
    return float(max(0.0, stats.t.cdf(hi, df) - stats.t.cdf(lo, df)))

rows = []
n_min = next(n for n in range(3, 500) if power_rm(.25, n) >= .90)
rows.append(dict(analysis='RM omnibus, f = 0.25, power .90', quantity='minimum N', value=n_min, power=power_rm(.25, n_min)))
f50 = optimize.brentq(lambda f: power_rm(f, 50) - .90, .01, 1)
rows.append(dict(analysis='RM omnibus, N = 50, power .90', quantity='smallest detectable f', value=f50, power=.90))
for b in [.5, .4, .3]:
    rows.append(dict(analysis=f'H3 TOST, N = 57, bounds dz = +-{b}', quantity='power', value=power_tost(57, b), power=np.nan))
df = pd.DataFrame(rows); print(df.to_string(index=False))
df.to_csv(os.path.join(args.out, 'power_analysis.csv'), index=False, float_format='%.4f')
