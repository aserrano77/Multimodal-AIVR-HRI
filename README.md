# Multimodal AI-VR: an autonomous robot co-worker with voice supervision in virtual reality

This repository contains the experimental platform, analysis code, aggregated results and study materials of the article:

> Serrano, A., & Banegas-Luna, A. J. *Does voice supervision add value to an autonomous robot co-worker? A within-subjects virtual reality study of package sorting.* Manuscript under review.

In the study, 58 participants sorted packages in a virtual warehouse (Meta Quest 3) under three conditions, in counterbalanced order:

| Code | Condition |
|---|---|
| C00 | Manual work, without robot or voice |
| C10 | Work alongside an autonomous TIAGo++ robot, voice disabled |
| C11 | Work alongside the same robot, with Spanish voice commands enabled |

The first digit of the code indicates whether the robot is active and the second whether voice is enabled.

## Contents

| Folder | Content |
|---|---|
| [`platform/`](platform) | Unity 6 project of the experimental application: scripts, scenes, prefabs, materials, project settings and package manifest. Third-party assets are not included (see below). |
| [`analysis/`](analysis) | Scripts that reproduce every statistic, table and figure of the article from the participant-level tables, plus the code that derives round-level metrics from the session logs. |
| [`results/`](results) | Aggregated results: descriptive statistics by condition, inferential results, sample description, power analysis and figures. |
| [`docs/`](docs) | Data dictionary, questionnaire (KoboToolbox form, Spanish original and English translation), voice command vocabulary, data access and platform notes. |

## Experimental platform

- Unity 6000.0.68f1 (revision e1e9baaf294b), Universal Render Pipeline, OpenXR and XR Interaction Toolkit 3.0, built for Meta Quest 3 (Android).
- Main scenes: `Assets/Scenes/experiment_start_scene.unity` (session creation and condition order) and `Assets/Scenes/final_scene.unity` (warehouse and task).
- Robot: TIAGo++ (PAL Robotics) imported from its URDF description with the Unity Robotics URDF Importer; behaviour tree and state machine in `Assets/Scripts/Autonomy`.
- Speech recognition on the headset with sherpa-onnx and the Parakeet TDT 0.6B v3 model (INT8); vocabulary and grammar in [`docs/voice_command_vocabulary.md`](docs/voice_command_vocabulary.md).
- The participant-facing interface, the voice vocabulary and the robot's spoken feedback are in Spanish, as in the study.

The scripts in `platform/Assets/Scripts` are those of the application build used in the study. The SHA-256 of that build is recorded in [`docs/study_build.csv`](docs/study_build.csv); the binary itself is not distributed.

**Not included**, because their licences do not allow redistribution or because they are restored by the Unity Package Manager: the Factory Interior and Factory Props Vol. 1 environment assets (Unity Asset Store), the TIAGo++ meshes and URDF description (PAL Robotics), the sherpa-onnx native libraries and the speech recognition model, the prerecorded audio clips, and the packages listed in `platform/Packages/manifest.json`. The project needs these dependencies to compile and run; without the environment assets and the robot model, the scenes show missing references. See [`docs/platform_notes.md`](docs/platform_notes.md).

## Analysis

The scripts in [`analysis/`](analysis) reproduce the results reported in the article: [`analysis.py`](analysis/analysis.py) (confirmatory, exploratory and sensitivity analyses), [`descriptives.py`](analysis/descriptives.py), [`power_analysis.py`](analysis/power_analysis.py) and [`figures.py`](analysis/figures.py). Their outputs are in [`results/`](results). Instructions are in [`analysis/README.md`](analysis/README.md).

## Data availability

- **Open, in this repository:** aggregated results, data dictionary, questionnaire, voice command vocabulary and analysis code.
- **Not shared:** the participant-level tables that the analysis scripts read (rounds, participant x condition values, questionnaire responses and participant characteristics), voice recordings, transcripts and free-text comments. To minimize the risk of re-identification in a small sample, participants were informed that their data would be accessible only to the research team and kept for a limited period.

## Licence

The code and documentation in this repository are released under the MIT licence (see [`LICENSE`](LICENSE)). Third-party components keep their own licences.

## Citation

Until the article is published, please cite this repository and the manuscript as given above.
