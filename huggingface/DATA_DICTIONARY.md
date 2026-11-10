# Data dictionary

## Item configuration

`items.jsonl` has one record per scientific abstract. `index` is unique in this configuration and is the foreign key used by annotations. Its original CELLS split or identifier namespace has not been independently verified.

| Field | Type | Meaning |
| --- | --- | --- |
| `index` | integer | Source item identifier preserved from the CSV |
| `abs_text` | string or null | Scientific abstract; null when redistribution permission was not established |
| `pls_text` | string or null | Human-authored PLS; null when redistribution permission was not established |
| `baseline` | string | Criteria-agnostic LLM summary |
| `Informativeness` | string | Summary for the informativeness condition |
| `Simplification` | string | Summary for the simplification condition |
| `Coherence` | string | Summary for the coherence condition |
| `Faithfulness` | string | Summary for the faithfulness condition |
| `Informativeness_Simplification_Coherence_Faithfulness` | string | Summary for all criteria combined |
| `VAR_QUESTION{n}` | string | Canonical comprehension question, for n = 1, 2, 3 |
| `VAR_QUESTION{n}-Opt{k}` | string | Option text, for k = 1, 2, 3, 4 |
| `VAR_QUESTION{n}-Answer` | string | Correct answer text in the canonical question file |
| `VAR_QUESTION{n}-AnswerNum` | integer | 1-based correct option position, derived from canonical answer text |
| `ATTENTION_QUESTION` | string | Attention-check question |
| `ATTENTION_QUESTION-Opt{k}` | string | Attention-check option text, for k = 1, 2, 3, 4 |
| `ATTENTION_QUESTION-Answer` | string | Correct attention-check answer text |
| `ATTENTION_QUESTION-AnswerNum` | integer | Source 1-based correct attention-check option position |

In the normalized working CSV, fields ending in `_REVISION_NOTES` remain for local provenance. These are excluded from the public candidate. There are no `_REVISED` columns in either canonical output.

The public item export adds `title`, `doi`, `cells_id`, `source_license`, `source_license_url`, and `source_text_status`. The latter is `included` for 29 pairs and `metadata_only` for 21 pairs. The original 37 public item columns are recorded in `manifest.json` and are restored by `reconstruct.py`.

## Source configuration

`sources.jsonl` has one record per item and joins on `index`. It contains the title, DOI, author attribution, journal, year, article URL, PMID/PMCID, source license and URL, copyright notice when available, inclusion decision and reason, audit date, primary evidence URLs, and evidence hashes.

`cells_id` is a composite pinned locator `CELLS@COMMIT:CSV_MEMBER:DATA_ROW`, not an asserted original numeric CELLS ID. `cells_metadata_file` and `cells_row_1based` identify the original archive member and data row, numbered from 1 excluding the header. `cells_revision`, `cells_archive_url`, and `cells_archive_sha256` identify the exact archive. `abs_sha256` and `pls_sha256` are hashes of the evaluated UTF-8 strings, including their original whitespace.

`source_license` is `cc-by-4.0`, `cc0-1.0`, `cc-by-nc-nd-4.0`, or `not-established`. The last value means redistribution permission was not established, not that every use is necessarily prohibited. Included source material retains its component-specific terms. [Full audit](SOURCE_AUDIT.md).

## Annotation configuration

`annotations.jsonl` contains one row per exported evaluation, including duplicated evaluations. `annotation_id` uniquely identifies an exported row. Multiple rows can have the same participant, item, and condition.

| Field | Type | Meaning and observed coding |
| --- | --- | --- |
| `annotation_id` | string | Condition plus original 1-based CSV row number; stable while source order is unchanged |
| `index` | integer | Item identifier; joins to `items.index` |
| `condition` | string | Summary condition, mapped below |
| `participant_id` | string | Random dataset-specific ID replacing `WorkerId`; mapping remains local |
| `question_version` | string | `not_recorded`; administered question version cannot be established from the result exports |
| `VAR_QUESTION1` | integer | Exported binary correctness score for comprehension question 1 |
| `VAR_QUESTION2` | integer | Exported binary correctness score for comprehension question 2 |
| `VAR_QUESTION3` | integer | Exported binary correctness score for comprehension question 3 |
| `ATTENTION_QUESTION` | integer | Exported binary correctness score for the attention check |
| `familiarity` | string or null | `never`, `somewhat`, `expert`, or null for a blank source value |
| `simplicity` | integer | Ease-of-understanding rating |
| `coherent` | integer | Organization/coherence rating |
| `informative` | integer | Coverage/informativeness rating |
| `background` | integer | Rating of necessary background information |
| `factual` | integer | Factual alignment/faithfulness rating |
| `recall` | float | Numeric recall score supplied by the source export, observed in [0, 1]; exact scoring implementation is unavailable |
| `wmd_recall` | float | Additional numeric recall-related score; name suggests a distance-based method, but algorithm, direction, and normalization are unverified |
| `work_time_seconds` | float | Exported task completion time in seconds; exact timing boundaries are not available |
| `mcq_accuracy` | float | `(VAR_QUESTION1 + VAR_QUESTION2 + VAR_QUESTION3) / 3` |
| `has_zero_rating` | boolean | True if any of the five ratings is zero |
| `is_duplicate_row` | boolean | True for subsequent exact copies of a complete source row within a condition; the first copy is False |

For the four binary scores, the provisional interpretation is 1 = correct and 0 = incorrect, consistent with their names, values, and the study procedure. Verify against the original export/scoring code before publication. They are not selected answer numbers. No answer-number column is present in the annotation files.

The intended rating scale is 1-5, with higher ratings indicating greater perceived quality. Zero occurs in the exports and its meaning is undocumented. It is preserved as an out-of-scale code, not recoded to a valid rating or silently interpreted as missing.

## Condition mapping

| Annotation condition | Original result file | Item summary field |
| --- | --- | --- |
| `human` | `pls_result_output.csv` | `pls_text` |
| `baseline` | `baseline_result_output.csv` | `baseline` |
| `informativeness` | `informativeness_result_output.csv` | `Informativeness` |
| `simplification` | `simplification_result_output.csv` | `Simplification` |
| `coherence` | `coherence_result_output.csv` | `Coherence` |
| `faithfulness` | `faithfulness_result_output.csv` | `Faithfulness` |
| `all` | `all_result_output.csv` | `Informativeness_Simplification_Coherence_Faithfulness` |

The mapping follows matching source filenames and item-column names, interpreted in the context of the paper's seven conditions. The original experiment configuration and exact model/prompt logs were not supplied, so author confirmation remains necessary.

## Manifest

`data/manifest.json` records input hashes, generated data hashes, row counts, participant counts, duplicate counts, missing familiarity, zero ratings, per-condition annotation multiplicity, and answer-position updates. It does not include the worker-ID mapping. It is provenance metadata, not a third dataset configuration.
