# Questionnaire

The questionnaire was administered once, in Spanish, on KoboToolbox, immediately after the three tests. The form definition (XLSForm) is in [`questionnaire_xlsform.xlsx`](questionnaire_xlsform.xlsx); this page reproduces its text in the order of the form, including the hints shown under each question (the scale anchors among them), with English translations for reference. Participants read the Spanish text. Field names are those of the exported data (see [data_dictionary.md](data_dictionary.md)).

Order of the form: introduction, consent confirmation, questionnaire code, demographic and prior-experience items, one block per test in the order in which the participant had experienced the tests, final preference and optional comment. The condition codes C00, C10 and C11 were never shown to participants.

The six-character questionnaire code displayed by the application linked each submission to the session logs without personal data. Its first character encodes the condition order, the next four are random and the last is a check character; the alphabet excludes 0, 1, I, L and O. The form validated the check character and derived from the code the order in which the test blocks were presented.

## 1. Introduction

> Has completado las tres pruebas del estudio. Este cuestionario recoge tu valoración de cada una y algunos datos generales. Tus respuestas se asociarán a la sesión mediante el código mostrado por la aplicación. No introduzcas tu nombre ni otros datos identificativos. Responde con calma y pensando en la prueba concreta que se indique en cada bloque.

*You have completed the three tests of the study. This questionnaire collects your assessment of each one and some general information. Your answers will be linked to the session through the code shown by the application. Do not enter your name or any other identifying information. Take your time and think about the specific test indicated in each block.*

## 2. Consent confirmation and code

| Field | Spanish (original) | English | Response |
|---|---|---|---|
| `A1_consent_confirm` | Confirmo que, antes de comenzar la sesión, recibí la información del estudio, pude plantear las preguntas que consideré necesarias, presté voluntariamente mi consentimiento para participar y mantengo mi autorización para utilizar los datos obtenidos conforme a dicha información. | I confirm that, before the session started, I received the study information, was able to ask any questions I considered necessary, voluntarily gave my consent to take part, and maintain my authorization to use the data obtained in accordance with that information. | Sí, lo confirmo (yes) / No, no lo confirmo (no) |
| `A2_questionnaire_code` | Introduce el código de cuestionario de seis caracteres que aparece en la aplicación. | Enter the six-character questionnaire code shown in the application. | Text; accepted only if the check character is valid. Hint: *Ejemplo de formato: C7K3M4* (format example: C7K3M4) |

If the participant did not confirm, the form showed: *No continúes con el cuestionario. Avisa al investigador para que gestione tus datos conforme al procedimiento de retirada del estudio* (Do not continue with the questionnaire. Tell the researcher, who will handle your data according to the withdrawal procedure of the study), and the rest of the form was not shown. The confirmation does not replace the written informed consent, which was signed on paper before the session.

## 3. General information and prior experience (*Datos generales y experiencia previa*)

| Field | Spanish (original) | English | Response (code) |
|---|---|---|---|
| `D1_age` | ¿Qué edad tienes, en años cumplidos? | How old are you, in completed years? | Integer 18-99; optional. Hint: *Puedes dejar esta pregunta en blanco si prefieres no responder* (you may leave this question blank if you prefer not to answer) |
| `D2_gender` | ¿Con cuál de las siguientes opciones de género te identificas? | Which of the following gender options do you identify with? | Woman (1); Man (2); Non-binary or other gender identity (3); Prefer not to answer (99) |
| `D3_education` | ¿Cuál es el nivel más alto de estudios que has completado? | What is the highest level of education you have completed? | Primary education or less (1); Compulsory secondary education or equivalent (2); Upper secondary education, *Bachillerato* (3); Intermediate vocational training (4); Higher vocational training (5); Bachelor's degree or equivalent (6); Master's degree, postgraduate or equivalent (7); Doctorate (8); Other level (97); Prefer not to answer (99) |
| `D4_area` | ¿Qué área describe mejor tu formación principal o tu actividad profesional actual? Si estudias y trabajas en áreas diferentes, elige la que consideres más relacionada con tu actividad principal. | Which area best describes your main field of study or your current professional activity? If you study and work in different areas, choose the one most related to your main activity. | Computing, telecommunications, architecture or engineering (1); Natural sciences, mathematics or health sciences (2); Social sciences, law, economics, education or humanities (3); Arts, design or communication (4); Industry, technical trades, construction, transport or logistics (5); Administration, commerce, hospitality or other services (6); Not currently studying or working in a defined area (7); Other area (97); Prefer not to answer (99) |
| `D5_vr_sessions_12m` | Aproximadamente, ¿en cuántas sesiones has utilizado un visor de realidad virtual inmersiva durante los últimos 12 meses? Escribe 0 si no lo has utilizado. | Approximately, in how many sessions have you used an immersive virtual reality headset in the last 12 months? Enter 0 if you have not used one. | Integer 0-365 |
| `D6_robot_interactions_12m` | Aproximadamente, ¿en cuántas ocasiones has interactuado directamente con un robot autónomo, físico o virtual, durante los últimos 12 meses? Escribe 0 si no has tenido ninguna interacción. | Approximately, on how many occasions have you interacted directly with an autonomous robot, physical or virtual, in the last 12 months? Enter 0 if you have had no interaction. | Integer 0-999. Hint: *No incluyas vídeos o demostraciones en los que no interactuaste directamente* (do not include videos or demonstrations in which you did not interact directly) |
| `D7_voice_days_30d` | Durante los últimos 30 días, ¿en cuántos días has utilizado un asistente de voz o has dado órdenes de voz a algún dispositivo? Escribe 0 si no lo has utilizado. | In the last 30 days, on how many days have you used a voice assistant or given voice commands to a device? Enter 0 if you have not used one. | Integer 0-30 |

## 4. Assessment of the tests (*Valoración de las pruebas*)

Introduction to the three blocks:

> A continuación valorarás las tres pruebas en el mismo orden en que las realizaste. Lee con atención la descripción de cada prueba y responde pensando únicamente en ella.

*Next you will assess the three tests in the same order in which you did them. Read the description of each test carefully and answer thinking only about that test.*

Each block was headed *Prueba N de 3* (Test N of 3) and opened with:

> Las siguientes preguntas se refieren únicamente a [description]. Trata de recordar esa prueba concreta y no valores el experimento completo.

*The following questions refer only to [description]. Try to remember that specific test and do not assess the whole experiment.*

| Condition | Description shown (Spanish) | English |
|---|---|---|
| C00 | la prueba en la que realizaste manualmente el traslado de cajas, sin intervención del robot | the test in which you moved the boxes by hand, without the robot |
| C10 | la prueba en la que el robot realizaba su tarea de forma autónoma y no podías darle órdenes de voz | the test in which the robot did its task autonomously and you could not give it voice commands |
| C11 | la prueba en la que el robot realizaba su tarea de forma autónoma y podías darle órdenes de voz | the test in which the robot did its task autonomously and you could give it voice commands |

Instruction before the NASA-TLX items:

> En las seis escalas siguientes, 0 representa el extremo izquierdo y 100 el extremo derecho, con valores disponibles de 5 en 5. Presta especial atención a «Rendimiento»: 0 significa «Perfecto» y 100 significa «Fracaso».

*In the following six scales, 0 is the left end and 100 the right end, with values available in steps of 5. Pay special attention to "Performance": 0 means "Perfect" and 100 means "Failure".*

| Field | Spanish (original) | English | Scale |
|---|---|---|---|
| `tlx_mental` | Pensando únicamente en esa prueba, ¿cuánta actividad mental y perceptiva necesitaste, por ejemplo para pensar, decidir, recordar, buscar o supervisar lo que ocurría? | Thinking only about that test, how much mental and perceptual activity did you need, for example to think, decide, remember, search or monitor what was happening? | Range 0-100, step 5; hint: 0 = *Muy baja* (very low), 100 = *Muy alta* (very high) |
| `tlx_physical` | Pensando únicamente en esa prueba, ¿cuánta actividad física necesitaste, por ejemplo para desplazarte, alcanzar, agarrar, transportar o colocar cajas? | Thinking only about that test, how much physical activity did you need, for example to move around, reach, grab, carry or place boxes? | Range 0-100, step 5; hint: 0 = *Muy baja* (very low), 100 = *Muy alta* (very high) |
| `tlx_temporal` | Pensando únicamente en esa prueba, ¿cuánta presión de tiempo sentiste debido al ritmo al que se desarrollaba la tarea? | Thinking only about that test, how much time pressure did you feel because of the pace of the task? | Range 0-100, step 5; hint: 0 = *Muy baja* (very low), 100 = *Muy alta* (very high) |
| `tlx_performance` | Pensando únicamente en esa prueba, ¿cómo valorarías tu propio rendimiento al alcanzar los objetivos de la tarea? | Thinking only about that test, how would you rate your own performance in achieving the goals of the task? | Range 0-100, step 5; hint: 0 = *Perfecto* (perfect), 100 = *Fracaso* (failure) |
| `tlx_effort` | Pensando únicamente en esa prueba, ¿cuánto esfuerzo mental y físico tuviste que realizar para alcanzar tu nivel de rendimiento? | Thinking only about that test, how much mental and physical effort did you have to make to achieve your level of performance? | Range 0-100, step 5; hint: 0 = *Muy bajo* (very low), 100 = *Muy alto* (very high) |
| `tlx_frustration` | Pensando únicamente en esa prueba, ¿hasta qué punto te sentiste inseguro/a, desanimado/a, irritado/a, estresado/a o molesto/a? | Thinking only about that test, how insecure, discouraged, irritated, stressed or annoyed did you feel? | Range 0-100, step 5; hint: 0 = *Nada* (not at all), 100 = *Muchísimo* (very much) |
| `seq` | En conjunto, ¿qué tan fácil o difícil te resultó completar esa prueba? | Overall, how easy or difficult was it to complete that test? | Range 1-7, step 1; hint: 1 = *Muy difícil* (very difficult), 4 = *Ni difícil ni fácil* (neither difficult nor easy), 7 = *Muy fácil* (very easy) |

Scoring: Raw NASA-TLX is the unweighted mean of the six dimensions, with performance not reversed. For SEQ, higher values mean greater ease.

In the block of the voice condition only, three further items followed, introduced by *Interacción vocal. Las siguientes preguntas se refieren únicamente a la prueba en la que podías dar órdenes de voz al robot* (Voice interaction. The following questions refer only to the test in which you could give voice commands to the robot). They are analysed separately and are not a validated scale.

| Field | Spanish (original) | English | Scale |
|---|---|---|---|
| `voice_comprehension` | Durante la prueba en la que podías dar órdenes de voz, ¿hasta qué punto comprendiste qué órdenes podías utilizar y en qué situaciones? | During the test in which you could give voice commands, to what extent did you understand which commands you could use and in which situations? | Range 0-10, step 1; hint: 0 = *No lo comprendí en absoluto* (I did not understand at all), 10 = *Lo comprendí completamente* (I understood completely) |
| `voice_correspondence` | Cuando intentaste dar una orden de voz, ¿hasta qué punto la respuesta posterior del robot coincidió con lo que pretendías solicitar? | When you tried to give a voice command, to what extent did the robot's subsequent response match what you intended to request? | Single choice: 0 (*No coincidió en absoluto*, it did not match at all) to 10 (*Coincidió completamente*, it matched completely); or *No intenté dar ninguna orden de voz* (I did not try to give any voice command, code 98, treated as not applicable) |
| `voice_control` | Durante la prueba en la que podías dar órdenes de voz, ¿hasta qué punto sentiste que podías intervenir en la actuación del robot cuando lo necesitabas? | During the test in which you could give voice commands, to what extent did you feel you could intervene in the robot's actions when you needed to? | Range 0-10, step 1; hint: 0 = *No podía intervenir en absoluto* (I could not intervene at all), 10 = *Podía intervenir completamente* (I could fully intervene) |

## 5. Final assessment (*Valoración final*)

| Field | Spanish (original) | English | Response (code) |
|---|---|---|---|
| `PF1_preference` | Pensando en toda la experiencia, ¿con cuál de las siguientes formas de realizar la tarea te quedarías? | Thinking about the whole experience, which of the following ways of doing the task would you choose? | Doing the task manually, without the robot (1); Doing the task with the autonomous robot, without voice commands (2); Doing the task with the autonomous robot and the possibility of giving it voice commands (3); I have no clear preference (4) |
| `CF1_comment` | Añade, si lo deseas, cualquier comentario que consideres relevante sobre la experiencia, incluidas dificultades o aspectos positivos. | If you wish, add any comment you consider relevant about the experience, including difficulties or positive aspects. | Free text, optional, up to 1,000 characters (hint: *Máximo recomendado: 1.000 caracteres*, recommended maximum 1,000 characters); summarized in the article as themes with participant counts ([`results/comment_themes.csv`](../results/comment_themes.csv)); the comments themselves are not shared |

The form closed with: *Gracias. Revisa tus respuestas y pulsa Enviar para finalizar* (Thank you. Review your answers and press Submit to finish).
