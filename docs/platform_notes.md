# Platform notes

## Opening the project

The Unity project is in [`platform/`](../platform) (`Assets`, `Packages`, `ProjectSettings`). Open it with Unity 6000.0.68f1. Before the scenes work, add the components that are not distributed here:

| Component | Source | Where it goes |
|---|---|---|
| Factory Interior and Factory Props Vol. 1 | Unity Asset Store (commercial licence) | `Assets/` (warehouse environment and props) |
| TIAGo++ URDF description and meshes | PAL Robotics | Imported with the Unity Robotics URDF Importer as `tiago_dual` |
| Unity Robotics URDF Importer | Unity Technologies (GitHub) | Local package `Packages/com.unity.robotics.urdf-importer` (referenced as `file:` in `manifest.json`) |
| sherpa-onnx runtime and the Parakeet TDT 0.6B v3 INT8 model | k2-fsa / NVIDIA | Native Android plugin and model files on the headset (see `Assets/Scripts/Autonomy/UnityIntegration/SherpaOnnxBackendOptions.cs`) |
| Prerecorded Spanish audio clips (robot feedback and instructions) | Generated offline with Windows speech synthesis | `Assets/Resources`; the generation scripts are in [`platform/Tools/VoiceClips`](../platform/Tools/VoiceClips) (the script for the robot feedback reads the phrase list [`robot_voice_phrases_es-ES.csv`](../platform/Tools/VoiceClips/RobotFeedback/robot_voice_phrases_es-ES.csv); the audio files themselves are not distributed) |
| Other packages | Unity Package Manager | Restored automatically from `Packages/manifest.json` |

## Identifiers in the code

Some class and file names keep internal development codes (for example `P43ATtsSceneIntegrationUtility`) or refer to the robot x voice factor structure from which the three conditions are derived (for example `Experiment2x2ConditionDefinition`, `ExperimentRunMode.Orchestrated2x2`). The study used three conditions: C00, C10 and C11. A voice channel without an active robot (C01) was not used, and the application blocks it.

The desktop helper that suggests where to copy the exported session data (`ExperimentDataPathResolver.cs`) contains the developer's local project path; adapt it if you use that helper.

## Running the tests

The project tests (`Assets/Tests` and `Assets/Scripts/Autonomy/BT/Tests`) run with the Unity Test Framework.

Before running `Unity.Robotics.UrdfImporter.Runtime.Tests` in PlayMode, back up `Assets/Tests` or check the version-control status immediately after the run. The third-party fixture `RuntimeUrdfTests` has a defect that can delete `Assets/Tests` if the folder already existed when the suite started: its `SetUp` creates `Tests 1` when `Tests` exists, but its `TearDown` deletes `Tests` anyway. The duplicated folder is not a valid replacement for the project tests.

## Study build

The application build used in all sessions is identified in [`study_build.csv`](study_build.csv) by its SHA-256. The binary is not distributed because it embeds third-party assets.
