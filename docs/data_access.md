# Data access

## What is open

Everything in this repository: aggregated results ([`results/`](../results)), the data dictionary, the questionnaire, the voice command vocabulary, the analysis code and the source code of the experimental platform.

## What is not shared, and why

To minimize the risk of re-identification in a small sample, participants were informed that their data would be accessible only to the research team and kept for a limited period. For that reason, the following are not shared:

- **Participant-level tables.** The analysis scripts read four tables, documented column by column in [data_dictionary.md](data_dictionary.md):

  | File | Rows | Content |
  |---|---|---|
  | `rounds.csv` | 338 | One row per valid round: execution time, event-log measures, voice inputs and rejections |
  | `participant_condition.csv` | 174 | One row per participant x condition: values used in the analyses |
  | `questionnaire.csv` | 174 | One row per participant x condition: NASA-TLX, SEQ, voice items, final preference |
  | `participants.csv` | 58 | One row per participant: condition order, demographic and prior-experience items |

- **Voice recordings and their transcripts**, because a voice can identify a speaker. They will be deleted at the end of their retention period.
- **Free-text comments** of the questionnaire. Participants were told that only aggregated results would be published, so the article reports them as themes with participant counts ([`results/comment_themes.csv`](../results/comment_themes.csv)).
- **Raw session logs** (event streams and session manifests). The code that derives the round-level metrics from them is in [`analysis/log_processing/`](../analysis/log_processing).

## What can be checked without the data

- The exact analysis code that produced every reported statistic and figure ([`analysis/`](../analysis)), with its decision rules.
- Its complete output ([`results/results.json`](../results/results.json) and [`results/run_log.txt`](../results/run_log.txt)), including assumption checks, both omnibus families, all contrasts and the sensitivity analyses.
- The SHA-256 of the input tables and the library versions used ([`results/run_meta.json`](../results/run_meta.json)).
- Descriptive statistics by condition and the sample description ([`results/`](../results)).
- The instruments: questionnaire form and text ([questionnaire.md](questionnaire.md)) and voice command vocabulary ([voice_command_vocabulary.md](voice_command_vocabulary.md)).

## Running the scripts

With the participant-level tables in a folder `data/`:

```bash
cd analysis
pip install -r requirements.txt
python analysis.py      --data-dir ../data --out ../results
python descriptives.py  --data-dir ../data --out ../results
python power_analysis.py                   --out ../results
python figures.py       --data-dir ../data --out ../results/figures
```

`power_analysis.py` needs no data.
