# Voice command vocabulary

In the voice condition (C11) participants could speak to the robot in Spanish. Speech was recognized on the headset (sherpa-onnx with the Parakeet TDT 0.6B v3 model, INT8), with continuous listening and voice activity detection. The transcript was normalized, mapped to an intent and checked against the condition, the robot's state and the boxes of the round before it could change the robot's plan. The grammar is restricted: it accepts the command families and word variants listed here, not unrestricted natural language.

The authoritative definitions are in the source code:

- [`VoiceCommandVocabulary.cs`](../platform/Assets/Scripts/Autonomy/Domain/VoiceCommandVocabulary.cs): action words, stop phrases, object and destination words, zone labels, filler words.
- [`VoiceCommandNormalizer.cs`](../platform/Assets/Scripts/Autonomy/Domain/VoiceCommandNormalizer.cs): cleaning, accepted variants, resume phrases, corrections of observed recognition errors.
- [`VoiceCommandIntentMapper.cs`](../platform/Assets/Scripts/Autonomy/Domain/VoiceCommandIntentMapper.cs): mapping to intents, cancellation of a pending order, "nearest box" references.
- [`ExperimentRuntimeProtocolUI.cs`](../platform/Assets/Scripts/ExperimentRuntimeProtocolUI.cs): instructions and example utterances shown to participants.
- [`RobotVoiceFeedbackTemplateBuilder.cs`](../platform/Assets/Scripts/Autonomy/Domain/RobotVoiceFeedbackTemplateBuilder.cs): the robot's spoken feedback.

## Command families

| Family | Effect | Accepted forms (Spanish) | English |
|---|---|---|---|
| Delivery request | The robot takes a given box to its zone or to a named zone. A command can replace the robot's current target only before the pick; after the pick it is deferred until the current delivery ends. | Action: *lleva*, *mueve*, *deposita*, *deja*; object: *caja*, *paquete*; box alias (A1, A2, B1, B2, C1...); destination: *a su zona*, *a la zona A/B/C* (*zona*, *depósito*) | take, move, deposit, leave; box, package; "to its zone", "to zone A/B/C" |
| Stop | Pauses the robot at a safe interruption point, without cancelling its task. Takes priority over autonomy. | *para*, *para robot*, *parar*, *parar robot*, *para la tarea*, *detente*, *espera*, *alto*, *alto robot*, *stop*, *stop robot*, *cancela la tarea*, *pausa seguridad* | stop, wait, halt |
| Resume | Resumes a stopped task. | *reanuda*, *reanuda la tarea (actual)*, *retoma*, *retoma la tarea (actual)*, *continúa*, *continúa la tarea*, *continúa con la tarea*, *sigue*, *sigue con la tarea* | resume, continue |
| Cancel | Removes a pending order that has not started yet. | *cancela la orden pendiente*, *cancelar la orden pendiente*, *cancela orden pendiente* | cancel the pending order |

Words such as *por favor*, *eh* and *ah* are ignored. Accents and capitalization are removed before matching.

A request to pick up a box without a destination (*coge*, *recoge*, *toma la caja...*, *coge la caja más cercana*) was recognized but was not an operational intent: the robot rejected it and said so. References to "the nearest box" (*la caja más cercana*) were recognized as ambiguous between "nearest to me" and "nearest to the robot".

## Box aliases

Each round contained five boxes with distinct visible aliases, formed by the category letter (A, B or C, which matches the zone) and a number within the category, for example A1, A2, B1, B2 and C1. The aliases available depended on the categories spawned in the round.

## Examples shown to participants

The instruction panel of the voice condition showed seven example utterances:

| Spanish | English |
|---|---|
| lleva la caja A1 a su zona de depósito | take box A1 to its deposit zone |
| lleva la caja B2 a su zona de depósito | take box B2 to its deposit zone |
| coge la caja más cercana | pick up the nearest box |
| para | stop |
| detente | stop (halt) |
| retoma la tarea | resume the task |
| continúa la tarea actual | continue the current task |

The third example, *coge la caja más cercana*, named no box and could not be executed. The robot answered it with a clarification request (*Necesito una aclaración: dime si te refieres a la caja más cercana a ti o al robot*, "I need a clarification: tell me whether you mean the box nearest to you or to the robot"); the possible answers (*más cercana a mí*, *más cercana al robot*) were recognized but did not start a task. A request to pick up a named box without a destination (*coge la caja A1*) was rejected as an unsupported intent (see above).

## Corrections of recognition errors

The normalizer maps some recognition errors observed during development to the intended words, only when the context makes the intended command clear. Examples: *caza*, *casa* → *caja*; *coce*, *cose* → *coge*; *debosita* → *deposita*; *bosito* → *depósito*; *de tente* → *detente*; *espeda* → *espera*. The full list is in `VoiceCommandNormalizer.cs`.

## Robot feedback

The robot answered every processed command with prerecorded Spanish audio indicating acceptance, rejection with a short reason, deferral, stopping or resumption (for example, *No hay ninguna tarea detenida que pueda reanudar*, "There is no stopped task that I can resume"). The complete list of the 54 feedback utterances, plus two diagnostic test phrases, is in [`robot_voice_phrases_es-ES.csv`](../platform/Tools/VoiceClips/RobotFeedback/robot_voice_phrases_es-ES.csv) (columns: clip identifier, category, text). The clips were generated offline from that list with Windows speech synthesis (voice Microsoft Helena) and played on the headset. The rejection reasons recorded in the logs are listed in [data_dictionary.md](data_dictionary.md) (`voice_reason__*`).
