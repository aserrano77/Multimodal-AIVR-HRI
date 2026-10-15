# Analysis

| Script | Reproduces | Output in `results/` |
|---|---|---|
| [`analysis.py`](analysis.py) | Confirmatory tests (H1-H3, RQ1), exploratory comparisons and sensitivity analyses: assumption checks, Friedman / repeated-measures ANOVA, Wilcoxon contrasts with Holm correction, rank-biserial correlations and Kendall's W with bootstrap intervals, TOST, McNemar, Spearman correlations, mixed models and GEE | `results.json`, `run_log.txt`, `run_meta.json` |
| [`descriptives.py`](descriptives.py) | Sample, participant characteristics, descriptive statistics by condition (Tables 2 and 3), voice items, final preference with Wilson intervals, robot operation and voice rejection totals | `sample.csv`, `participants_summary.csv`, `descriptives_by_condition.csv`, `preference.csv`, `robot_operation_totals.csv`, `voice_rejections.csv` |
| [`power_analysis.py`](power_analysis.py) | A priori power analysis and power of the equivalence test | `power_analysis.csv` |
| [`figures.py`](figures.py) | Figures 3, 4 and 5 | `figures/` |
| [`log_processing/`](log_processing) | Derivation of round-level metrics from the raw session logs (not shared) | — |

The decision rules are documented at the top of `analysis.py` and in the Method section of the article. The bootstrap uses a fixed seed and 10,000 resamples, so the results are reproducible exactly; `analysis.py` takes about three minutes.

## Running

The scripts read the participant-level tables, which are not shared to protect participants from re-identification ([`docs/data_access.md`](../docs/data_access.md)). The outputs they produced are in [`results/`](../results). With those tables in `../data`:

```bash
pip install -r requirements.txt
python analysis.py      --data-dir ../data --out ../results
python descriptives.py  --data-dir ../data --out ../results
python power_analysis.py                   --out ../results
python figures.py       --data-dir ../data --out ../results/figures
```

`requirements.txt` pins the library versions used to produce the published results (Python 3.13).

## Reading `results.json`

- `sample`: sessions, valid rounds per condition, condition orders, analysis sample sizes.
- `confirmatory`: `time` (H1), `tlx` (RQ1, H3) and `seq` (H2). For each variable: descriptive statistics by condition, assumption checks (`shapiro_resid_p`, `mauchly_p`), the test chosen by the rule (`rule_choice`), both omnibus families (`anova`, `friedman`) and the pairwise contrasts of each family. The family reported in the article is the one in `primary`. `H3_tost` holds the equivalence test. The NASA-TLX is analysed as the sum of the six items; divide differences by 6 for the 0-100 scale.
- `exploratory`: recorded failure events, robot sequence failures (McNemar), grasp-state rejections, work split, safety stops, voice friction and the associated Spearman correlations, headset recovery failures.
- `sensitivity`: S1 without the session that ran in a different application mode (`diffmode_excluded_*`), S2 without rounds with a headset recovery failure (`*_no_ui`), S3 with at least one valid round per condition (`*_any1`), and the round-level mixed models and GEE (`mixed_models`).
