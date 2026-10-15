# Data dictionary

Variables of the participant-level tables read by the analysis scripts. These tables are not shared (see [data_access.md](data_access.md)); the dictionary documents what each variable means and how it was computed. The same definitions apply to the aggregated tables in [`results/`](../results). A machine-readable version is in [`data_dictionary.csv`](data_dictionary.csv).

Only valid rounds are included: rounds invalidated by technical incidents during the sessions are not part of the tables. Event-log measures are counts of logged events, not counts of independent incidents, because retries and cascades are not deduplicated. Robot and voice measures are structurally zero or empty in the conditions where the robot or the voice channel was disabled.

## `rounds.csv`

One row per valid round (338 rows).

| Column | Unit | Definition |
|---|---|---|
| `participant_id` |  | Pseudonymous participant code (P01-P58). One session per participant. |
| `condition` |  | C00 = manual work, without robot or voice; C10 = autonomous robot, voice disabled; C11 = autonomous robot with voice commands. |
| `condition_order` |  | Order of the three conditions in the session (e.g. C10>C00>C11), assigned by the application with randomized complete blocks of the six possible orders. |
| `position_of_condition_in_order` | 1-3 | Position of the condition in the session order. |
| `round_index` | 1-2 | Round number within the condition. |
| `round_position_in_session` | 1-6 | Position of the round in the session. |
| `deposited_boxes` | boxes | Boxes deposited in their correct zone during the round. Only completed (valid) rounds are included, so the value is always 5. |
| `trial_duration_s` | s | Execution time: duration of the round, from its start until the fifth correct deposit. |
| `error_count` | events | Recorded failure events: count of logged events whose name ends in "_failed", plus "multimodal_intent_rejected" and "task_failed" (subsystem faults, retries, rejected intents, robot sequence failures). Not deduplicated, so it is not a count of independent incidents. Three post-deposit egress warnings are excluded; "voice_command_rejected" does not increment it. |
| `error_count_without_no_slot_incidents` | events | error_count minus the increments caused by voice commands rejected because no valid deposit slot was available (each such rejection adds two events). |
| `no_slot_error_increments_removed` | events | Number of increments removed to obtain error_count_without_no_slot_incidents. |
| `error_event__assisted_pick_failed` | events | Recorded failure events of type "assisted_pick_failed" (assisted pick failed). Component of error_count. |
| `error_event__assisted_place_selection_failed` | events | Recorded failure events of type "assisted_place_selection_failed" (assisted place selection failed). Component of error_count. |
| `error_event__manipulation_pick_failed` | events | Recorded failure events of type "manipulation_pick_failed" (manipulation pick failed). Component of error_count. |
| `error_event__multimodal_intent_rejected` | events | Recorded failure events of type "multimodal_intent_rejected" (multimodal (voice) intent rejected). Component of error_count. |
| `error_event__navigation_to_pick_failed` | events | Recorded failure events of type "navigation_to_pick_failed" (navigation to the pick point failed). Component of error_count. |
| `error_event__navigation_to_place_failed` | events | Recorded failure events of type "navigation_to_place_failed" (navigation to the deposit zone failed). Component of error_count. |
| `error_event__perception_target_selection_failed` | events | Recorded failure events of type "perception_target_selection_failed" (perception target selection failed). Component of error_count. |
| `error_event__task_failed` | events | Recorded failure events of type "task_failed" (robot task failed). Component of error_count. |
| `error_event__tts_speak_failed` | events | Recorded failure events of type "tts_speak_failed" (speech feedback playback failed). Component of error_count. |
| `error_event__ui_recovery_failed` | events | Recorded failure events of type "ui_recovery_failed" (headset or controller recovery failed). Component of error_count. |
| `error_event__voice_immediate_slot_planning_failed` | events | Recorded failure events of type "voice_immediate_slot_planning_failed" (deposit-slot planning for a voice command failed). Component of error_count. |
| `robot_sequence_failure_raw` | events | Failures of the robot task sequence (task_failed with reason bt_sequence_failure) attributed to the round, including events up to 2 s outside the active round window. |
| `robot_sequence_failure_active` | events | Failures of the robot task sequence inside the active round window. This is an internal robot failure, not a failed round. Structural zero in C00. |
| `target_selection_rejected_grasp_state` | events | Robot target selections rejected because the selected box was already being held. |
| `target_selection_robot_held` | events | Grasp-state rejections in which the box was held by the robot itself (is_held = true). |
| `target_selection_actor_undetermined` | events | Grasp-state rejections that could not be attributed to either agent. Never attributed to the participant. |
| `robot_route_boxes` | boxes | Boxes deposited through the robot delivery route (robot-registered deposits). |
| `zone_route_boxes` | boxes | Boxes registered through the zone route. The zone route does not identify the participant as the agent. |
| `total_boxes` | boxes | Boxes counted for the work-split measure. |
| `robot_route_share` | fraction 0-1 | Work split: robot_route_boxes / total_boxes. |
| `robot_sequence_failure_flag` | 0/1 | 1 if robot_sequence_failure_active > 0 in the round. |
| `safety_episodes` | episodes | Safety-pause episodes (the robot paused because the participant entered the zone around it), from entry until exit or explicit reset. |
| `safety_timeouts` | events | Safety-pause timeout events (a timeout does not close an episode). |
| `safety_exited_events` | events | Safety-pause exit events. |
| `safety_resets_all` | events | All safety resets in the round. |
| `safety_closed_by_exit` | episodes | Safety episodes closed by an exit event. |
| `safety_closed_by_reset` | episodes | Safety episodes closed by an explicit reset. |
| `safety_unclosed` | episodes | Safety episodes without a closing event (their duration is missing). |
| `safety_duration_unity_s` | s | Total duration of the safety episodes, simulation (Unity) clock. Primary duration measure. |
| `safety_duration_wall_s` | s | Total duration of the safety episodes, wall clock. Secondary check. |
| `safety_resets_other` | events | Safety resets that did not close an episode. |
| `voice_inputs` | inputs | Voice inputs processed by the command router (voice_command_received_diagnostic). Not every utterance spoken. C11 only; empty in C00 and C10. |
| `voice_rejections` | inputs | Processed voice inputs that were rejected (voice_command_rejected). |
| `voice_rejection_rate` | fraction 0-1 | voice_rejections / voice_inputs in the round; missing if voice_inputs = 0. |
| `voice_reason__mapped_intent_without_executable_bridge_task_NearestAmbiguity` | inputs | Rejected voice inputs with reason "mapped_intent_without_executable_bridge_task_NearestAmbiguity" ("nearest box" reference without an executable task). |
| `voice_reason__mapping_not_executable_Ambiguous` | inputs | Rejected voice inputs with reason "mapping_not_executable_Ambiguous" (ambiguous command (mapper)). |
| `voice_reason__mapping_not_executable_Incomplete` | inputs | Rejected voice inputs with reason "mapping_not_executable_Incomplete" (incomplete command (mapper)). |
| `voice_reason__mapping_not_executable_NotMapped` | inputs | Rejected voice inputs with reason "mapping_not_executable_NotMapped" (command not mapped to an intent). |
| `voice_reason__no_stopped_task_to_resume` | inputs | Rejected voice inputs with reason "no_stopped_task_to_resume" (resume requested but there was no stopped task). |
| `voice_reason__no_valid_deposit_slot` | inputs | Rejected voice inputs with reason "no_valid_deposit_slot" (no valid deposit slot available for the requested box). |
| `voice_reason__normalization_not_executable_Ambiguous` | inputs | Rejected voice inputs with reason "normalization_not_executable_Ambiguous" (ambiguous utterance (normalizer)). |
| `voice_reason__normalization_not_executable_Unrecognized` | inputs | Rejected voice inputs with reason "normalization_not_executable_Unrecognized" (utterance not recognized by the normalizer). |
| `voice_reason__unsupported_operational_intent_Pick` | inputs | Rejected voice inputs with reason "unsupported_operational_intent_Pick" (recognized as a pick-only request, an intent not supported operationally). |
| `voice_reason__voice_stop_latched_pick_and_place_rejected` | inputs | Rejected voice inputs with reason "voice_stop_latched_pick_and_place_rejected" (delivery request rejected while a stop was active). |
| `voice_reason__voice_target_not_selectable_Excluded` | inputs | Rejected voice inputs with reason "voice_target_not_selectable_Excluded" (requested box not selectable (excluded)). |
| `voice_reason__requested_object_not_available` | inputs | Rejected voice inputs with reason "requested_object_not_available" (requested box not available). |
| `ui_recovery_failed` | events | Failed recoveries of the headset or controllers (ui_recovery_failed events). |
| `ui_recovery_failed_flag` | 0/1 | 1 if ui_recovery_failed > 0 in the round. |
| `asr_backend_recorded` |  | Speech recognizer recorded in the session manifest (SherpaOnnx); empty when the manifest does not record it. |
| `sens_different_app_mode` | true/false | True for the one session that ran in a different application mode (excluded in sensitivity analysis S1). |

## `participant_condition.csv`

One row per participant x condition (174 rows). Participant x condition value: mean of the two valid rounds of the condition (missing if the condition has fewer than two valid rounds).

| Column | Unit | Definition |
|---|---|---|
| `participant_id` |  | Pseudonymous participant code (P01-P58). One session per participant. |
| `condition` |  | C00 = manual work, without robot or voice; C10 = autonomous robot, voice disabled; C11 = autonomous robot with voice commands. |
| `condition_order` |  | Order of the three conditions in the session (e.g. C10>C00>C11), assigned by the application with randomized complete blocks of the six possible orders. |
| `position_of_condition_in_order` | 1-3 | Position of the condition in the session order. |
| `n_valid_rounds` | rounds | Valid rounds of the participant in the condition (0-2). |
| `trial_duration_s` | s | Execution time: duration of the round, from its start until the fifth correct deposit. Mean of the two valid rounds. |
| `error_count` | events | Recorded failure events: count of logged events whose name ends in "_failed", plus "multimodal_intent_rejected" and "task_failed" (subsystem faults, retries, rejected intents, robot sequence failures). Not deduplicated, so it is not a count of independent incidents. Three post-deposit egress warnings are excluded; "voice_command_rejected" does not increment it. Mean of the two valid rounds. |
| `error_count_without_no_slot_incidents` | events | error_count minus the increments caused by voice commands rejected because no valid deposit slot was available (each such rejection adds two events). Mean of the two valid rounds. |
| `error_event__assisted_pick_failed` | events | Recorded failure events of type "assisted_pick_failed" (assisted pick failed). Component of error_count. Mean of the two valid rounds. |
| `error_event__assisted_place_selection_failed` | events | Recorded failure events of type "assisted_place_selection_failed" (assisted place selection failed). Component of error_count. Mean of the two valid rounds. |
| `error_event__manipulation_pick_failed` | events | Recorded failure events of type "manipulation_pick_failed" (manipulation pick failed). Component of error_count. Mean of the two valid rounds. |
| `error_event__multimodal_intent_rejected` | events | Recorded failure events of type "multimodal_intent_rejected" (multimodal (voice) intent rejected). Component of error_count. Mean of the two valid rounds. |
| `error_event__navigation_to_pick_failed` | events | Recorded failure events of type "navigation_to_pick_failed" (navigation to the pick point failed). Component of error_count. Mean of the two valid rounds. |
| `error_event__navigation_to_place_failed` | events | Recorded failure events of type "navigation_to_place_failed" (navigation to the deposit zone failed). Component of error_count. Mean of the two valid rounds. |
| `error_event__perception_target_selection_failed` | events | Recorded failure events of type "perception_target_selection_failed" (perception target selection failed). Component of error_count. Mean of the two valid rounds. |
| `error_event__task_failed` | events | Recorded failure events of type "task_failed" (robot task failed). Component of error_count. Mean of the two valid rounds. |
| `error_event__tts_speak_failed` | events | Recorded failure events of type "tts_speak_failed" (speech feedback playback failed). Component of error_count. Mean of the two valid rounds. |
| `error_event__ui_recovery_failed` | events | Recorded failure events of type "ui_recovery_failed" (headset or controller recovery failed). Component of error_count. Mean of the two valid rounds. |
| `error_event__voice_immediate_slot_planning_failed` | events | Recorded failure events of type "voice_immediate_slot_planning_failed" (deposit-slot planning for a voice command failed). Component of error_count. Mean of the two valid rounds. |
| `robot_sequence_failure_raw` | events | Failures of the robot task sequence (task_failed with reason bt_sequence_failure) attributed to the round, including events up to 2 s outside the active round window. Mean of the two valid rounds. |
| `robot_sequence_failure_active` | events | Failures of the robot task sequence inside the active round window. This is an internal robot failure, not a failed round. Structural zero in C00. Mean of the two valid rounds. |
| `target_selection_rejected_grasp_state` | events | Robot target selections rejected because the selected box was already being held. Mean of the two valid rounds. |
| `target_selection_robot_held` | events | Grasp-state rejections in which the box was held by the robot itself (is_held = true). Mean of the two valid rounds. |
| `target_selection_actor_undetermined` | events | Grasp-state rejections that could not be attributed to either agent. Never attributed to the participant. Mean of the two valid rounds. |
| `robot_route_boxes` | boxes | Boxes deposited through the robot delivery route (robot-registered deposits). Mean of the two valid rounds. |
| `zone_route_boxes` | boxes | Boxes registered through the zone route. The zone route does not identify the participant as the agent. |
| `total_boxes` | boxes | Boxes counted for the work-split measure. Mean of the two valid rounds. |
| `robot_route_share` | fraction 0-1 | Work split: robot_route_boxes / total_boxes. Mean of the two valid rounds. |
| `safety_episodes` | episodes | Safety-pause episodes (the robot paused because the participant entered the zone around it), from entry until exit or explicit reset. Mean of the two valid rounds. |
| `safety_timeouts` | events | Safety-pause timeout events (a timeout does not close an episode). Mean of the two valid rounds. |
| `safety_exited_events` | events | Safety-pause exit events. Mean of the two valid rounds. |
| `safety_resets_all` | events | All safety resets in the round. Mean of the two valid rounds. |
| `safety_closed_by_exit` | episodes | Safety episodes closed by an exit event. Mean of the two valid rounds. |
| `safety_closed_by_reset` | episodes | Safety episodes closed by an explicit reset. Mean of the two valid rounds. |
| `safety_unclosed` | episodes | Safety episodes without a closing event (their duration is missing). Mean of the two valid rounds. |
| `safety_duration_unity_s` | s | Total duration of the safety episodes, simulation (Unity) clock. Primary duration measure. Mean of the two valid rounds. |
| `safety_duration_wall_s` | s | Total duration of the safety episodes, wall clock. Secondary check. Mean of the two valid rounds. |
| `safety_resets_other` | events | Safety resets that did not close an episode. Mean of the two valid rounds. |
| `robot_sequence_failure__n_rounds_with_event` | rounds | Number of the two valid rounds with at least one active robot sequence failure. |
| `robot_sequence_failure__proportion` | fraction 0-1 | robot_sequence_failure__n_rounds_with_event / 2. |
| `robot_sequence_failure__flag_any` | 0/1 | 1 if at least one of the two valid rounds had an active robot sequence failure (used in the McNemar test). |
| `voice_inputs` | inputs | Voice inputs processed by the command router (voice_command_received_diagnostic). Not every utterance spoken. C11 only; empty in C00 and C10. Mean of the two valid rounds. |
| `voice_rejections` | inputs | Processed voice inputs that were rejected (voice_command_rejected). Mean of the two valid rounds. |
| `voice_rate_mean` | fraction 0-1 | Mean of the two per-round rejection rates; missing unless both rates exist. |
| `voice_rate_aggregated` | fraction 0-1 | Voice friction: sum of rejections / sum of processed inputs over the two rounds; missing if there were no inputs. Used in the article. |
| `voice_reason__mapped_intent_without_executable_bridge_task_NearestAmbiguity` | inputs | Rejected voice inputs with reason "mapped_intent_without_executable_bridge_task_NearestAmbiguity" ("nearest box" reference without an executable task). Mean of the two valid rounds. |
| `voice_reason__mapping_not_executable_Ambiguous` | inputs | Rejected voice inputs with reason "mapping_not_executable_Ambiguous" (ambiguous command (mapper)). Mean of the two valid rounds. |
| `voice_reason__mapping_not_executable_Incomplete` | inputs | Rejected voice inputs with reason "mapping_not_executable_Incomplete" (incomplete command (mapper)). Mean of the two valid rounds. |
| `voice_reason__mapping_not_executable_NotMapped` | inputs | Rejected voice inputs with reason "mapping_not_executable_NotMapped" (command not mapped to an intent). Mean of the two valid rounds. |
| `voice_reason__no_stopped_task_to_resume` | inputs | Rejected voice inputs with reason "no_stopped_task_to_resume" (resume requested but there was no stopped task). Mean of the two valid rounds. |
| `voice_reason__no_valid_deposit_slot` | inputs | Rejected voice inputs with reason "no_valid_deposit_slot" (no valid deposit slot available for the requested box). Mean of the two valid rounds. |
| `voice_reason__normalization_not_executable_Ambiguous` | inputs | Rejected voice inputs with reason "normalization_not_executable_Ambiguous" (ambiguous utterance (normalizer)). Mean of the two valid rounds. |
| `voice_reason__normalization_not_executable_Unrecognized` | inputs | Rejected voice inputs with reason "normalization_not_executable_Unrecognized" (utterance not recognized by the normalizer). Mean of the two valid rounds. |
| `voice_reason__unsupported_operational_intent_Pick` | inputs | Rejected voice inputs with reason "unsupported_operational_intent_Pick" (recognized as a pick-only request, an intent not supported operationally). Mean of the two valid rounds. |
| `voice_reason__voice_stop_latched_pick_and_place_rejected` | inputs | Rejected voice inputs with reason "voice_stop_latched_pick_and_place_rejected" (delivery request rejected while a stop was active). Mean of the two valid rounds. |
| `voice_reason__voice_target_not_selectable_Excluded` | inputs | Rejected voice inputs with reason "voice_target_not_selectable_Excluded" (requested box not selectable (excluded)). Mean of the two valid rounds. |
| `voice_reason__requested_object_not_available` | inputs | Rejected voice inputs with reason "requested_object_not_available" (requested box not available). Mean of the two valid rounds. |
| `ui_recovery_failed` | events | Failed recoveries of the headset or controllers (ui_recovery_failed events). Mean of the two valid rounds. |
| `ui_recovery_failed__n_rounds_with_event` | rounds | Number of the two valid rounds with a headset recovery failure. |
| `ui_recovery_failed__proportion` | fraction 0-1 | ui_recovery_failed__n_rounds_with_event / 2. |
| `ui_recovery_failed__flag_any` | 0/1 | 1 if at least one of the two valid rounds had a headset recovery failure. |
| `trial_duration_s__any1` | s | Same as trial_duration_s, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `error_count__any1` | events | Same as error_count, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `robot_sequence_failure_raw__any1` | events | Same as robot_sequence_failure_raw, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `robot_sequence_failure_active__any1` | events | Same as robot_sequence_failure_active, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `target_selection_rejected_grasp_state__any1` | events | Same as target_selection_rejected_grasp_state, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `target_selection_robot_held__any1` | events | Same as target_selection_robot_held, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `target_selection_actor_undetermined__any1` | events | Same as target_selection_actor_undetermined, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `robot_route_boxes__any1` | boxes | Same as robot_route_boxes, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `zone_route_boxes__any1` | boxes | Same as zone_route_boxes, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `total_boxes__any1` | boxes | Same as total_boxes, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `robot_route_share__any1` | fraction 0-1 | Same as robot_route_share, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `safety_episodes__any1` | episodes | Same as safety_episodes, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `safety_timeouts__any1` | events | Same as safety_timeouts, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `safety_exited_events__any1` | events | Same as safety_exited_events, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `safety_resets_all__any1` | events | Same as safety_resets_all, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `safety_closed_by_exit__any1` | episodes | Same as safety_closed_by_exit, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `safety_closed_by_reset__any1` | episodes | Same as safety_closed_by_reset, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `safety_unclosed__any1` | episodes | Same as safety_unclosed, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `safety_duration_unity_s__any1` | s | Same as safety_duration_unity_s, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `safety_duration_wall_s__any1` | s | Same as safety_duration_wall_s, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `safety_resets_other__any1` | events | Same as safety_resets_other, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `voice_inputs__any1` | inputs | Same as voice_inputs, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `voice_rejections__any1` | inputs | Same as voice_rejections, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `ui_recovery_failed__any1` | events | Same as ui_recovery_failed, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `error_count_without_no_slot_incidents__any1` | events | Same as error_count_without_no_slot_incidents, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `voice_rate_mean__any1` | fraction 0-1 | Same as voice_rate_mean, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `voice_rate_aggregated__any1` | fraction 0-1 | Same as voice_rate_aggregated, but computed from the valid rounds available when at least one is valid (sensitivity analysis S3). |
| `n_rounds_used__no_ui` | rounds | Valid rounds left after removing rounds with a headset recovery failure (sensitivity analysis S2). |
| `trial_duration_s__no_ui` | s | Mean execution time of the valid rounds without a headset recovery failure; requires at least one such round (S2). |
| `error_count__no_ui` | events | Mean recorded failure events of the valid rounds without a headset recovery failure (S2). |
| `sens_different_app_mode` | true/false | True for the one session that ran in a different application mode (excluded in sensitivity analysis S1). |

## `questionnaire.csv`

One row per participant x condition (174 rows): questionnaire items about each condition.

| Column | Unit | Definition |
|---|---|---|
| `participant_id` |  | Pseudonymous participant code (P01-P58). One session per participant. |
| `condition` |  | C00 = manual work, without robot or voice; C10 = autonomous robot, voice disabled; C11 = autonomous robot with voice commands. |
| `condition_order` |  | Order of the three conditions in the session (e.g. C10>C00>C11), assigned by the application with randomized complete blocks of the six possible orders. |
| `position_of_condition_in_order` | 1-3 | Position of the condition in the session order. |
| `questionnaire_submitted` | true/false | Whether the participant submitted the questionnaire. |
| `tlx_mental` | 0-100 | NASA-TLX mental demand (slider 0-100 in steps of 5). |
| `tlx_physical` | 0-100 | NASA-TLX physical demand. |
| `tlx_temporal` | 0-100 | NASA-TLX temporal demand. |
| `tlx_performance` | 0-100 | NASA-TLX performance (0 = perfect, 100 = failure, as stated in the form; not reversed). |
| `tlx_effort` | 0-100 | NASA-TLX effort. |
| `tlx_frustration` | 0-100 | NASA-TLX frustration. |
| `Raw_TLX` | 0-100 | Raw NASA-TLX: unweighted mean of the six dimensions, performance not reversed. |
| `Raw_TLX_sum_integer` | 0-600 | Sum of the six integer NASA-TLX items (used for rank tests; equivalent to Raw_TLX x 6). |
| `SEQ` | 1-7 | Single Ease Question (slider 1-7; higher = easier). |
| `voice_comprehension` | 0-10 | C11 only. Comprehension of which commands could be used and when. |
| `voice_correspondence` | 0-10 | C11 only. Correspondence between the command given and the robot's response (0 = it did not match at all, 10 = it matched completely); missing when the participant chose "I did not try to give any voice command". |
| `voice_correspondence_status` |  | observed; did_not_try (answered "I did not try to give any voice command"); not_shown (item not asked in C00/C10); no_submission. |
| `voice_control` | 0-10 | C11 only. Perceived ability to intervene in the robot's actions. |
| `preference_final` | 1-4 | Final preference (repeated on the three rows of the participant; count once): 1 = manual; 2 = robot without voice; 3 = robot with voice; 4 = no clear preference. |
| `sens_different_app_mode` | true/false | True for the one session that ran in a different application mode (excluded in sensitivity analysis S1). |

## `participants.csv`

One row per participant (58 rows): demographic and prior-experience items, final preference.

| Column | Unit | Definition |
|---|---|---|
| `participant_id` |  | Pseudonymous participant code (P01-P58). One session per participant. |
| `condition_order` |  | Order of the three conditions in the session (e.g. C10>C00>C11), assigned by the application with randomized complete blocks of the six possible orders. |
| `questionnaire_submitted` | true/false | Whether the participant submitted the questionnaire. |
| `age` | years | Age in completed years (optional item). |
| `gender_code` | code | 1 = woman; 2 = man; 3 = non-binary or other gender identity; 99 = prefer not to answer. |
| `education_code` | code | Highest completed level: 1 = primary or less; 2 = compulsory secondary or equivalent; 3 = upper secondary (Bachillerato); 4 = intermediate vocational training; 5 = higher vocational training; 6 = bachelor's degree or equivalent; 7 = master's, postgraduate or equivalent; 8 = doctorate; 97 = other level; 99 = prefer not to answer. |
| `area_code` | code | Main field of study or work: 1 = computing, telecommunications, architecture or engineering; 2 = natural sciences, mathematics or health; 3 = social sciences, law, economics, education or humanities; 4 = arts, design or communication; 5 = industry, technical trades, construction, transport or logistics; 6 = administration, commerce, hospitality or other services; 7 = not currently studying or working in a defined area; 97 = other area; 99 = prefer not to answer. |
| `vr_sessions_12m` | sessions | Approximate number of sessions with an immersive VR headset in the previous 12 months. |
| `robot_interactions_12m` | occasions | Approximate number of direct interactions with an autonomous robot, physical or virtual, in the previous 12 months. |
| `voice_assistant_days_30d` | days | Days in the previous 30 days on which the participant used a voice assistant or gave voice commands to a device. |
| `preference_code` | 1-4 | Final preference (see preference_final). |
| `sens_different_app_mode` | true/false | True for the one session that ran in a different application mode (excluded in sensitivity analysis S1). |
