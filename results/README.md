# Results

Aggregated results produced by the scripts in [`analysis/`](../analysis). Variable names follow [`docs/data_dictionary.md`](../docs/data_dictionary.md).

| File | Content |
|---|---|
| `results.json` | All inferential results (confirmatory, exploratory, sensitivity); structure described in [`analysis/README.md`](../analysis/README.md) |
| `run_log.txt` | Human-readable log of the same run |
| `run_meta.json` | Library versions, random seed, number of bootstrap resamples and SHA-256 of the input tables |
| `sample.csv` | Sessions, valid rounds, condition orders and analysis sample sizes |
| `participants_summary.csv` | Age, gender, education, field and prior experience of the 57 questionnaire respondents. The prior-experience counts were free integers with an upper limit (365 VR sessions, 999 robot interactions, 30 days of voice-assistant use), and a few large answers inflate their means; the median, quartiles and number of zeros describe them better |
| `descriptives_by_condition.csv` | n, mean, SD, median, quartiles, minimum and maximum by condition, for the analysis sample of each variable |
| `preference.csv` | Final preference with 95% Wilson intervals and the chi-square test against a uniform split |
| `robot_operation_totals.csv` | Totals over all valid rounds: boxes delivered by the robot, robot sequence failures, grasp-state rejections, safety stops, failure events, headset recovery failures |
| `voice_rejections.csv` | Rejected voice inputs by reason, processed inputs, rounds and participants without processed input |
| `comment_themes.csv` | Themes of the optional free-text comments, with their definitions and the number of participants who mentioned each (coded inductively by the first author; a comment can contain several themes) |
| `power_analysis.csv` | A priori power analysis and power of the equivalence test |
| `figures/` | Figures 3-5 of the article (PDF and PNG) |
