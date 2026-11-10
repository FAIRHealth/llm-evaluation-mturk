# Data quality and provenance

These observations concern the eight local source CSVs inspected for this candidate. The preparation script regenerates the counts and hashes in `data/manifest.json`. No annotation rows are removed and no historical scores are recalculated.

## Coverage and integrity

| Check | Observed result | Implication |
| --- | --- | --- |
| Item keys | 50 unique `index` values | One-to-many join from items to annotations |
| Annotation coverage | 1,750 rows, 250 per condition | Exported population, before any release-specific filtering |
| Item joins | Every annotation index has an item | No unmatched keys in the supplied exports |
| Source worker IDs | 151 distinct IDs across all files | Differs from the paper's reported 150 participants; reason unknown |
| Exact duplicate rows | Four extra rows, all in simplification | Preserve and flag; determine intended deduplication before analysis |
| Annotation multiplicity | Five per item in six conditions; simplification has 42 items with five, four with four, and four with six | Simplification does not uniformly have five evaluations per item |
| Blank familiarity | Nine rows | Exported as null |
| Zero ratings | 35 rows contain at least one zero | Outside the intended 1-5 scale; missing-value semantics unknown |
| Incorrect attention checks | 508 rows with numeric code zero | Retained in this candidate; public analysis should state its quality filter |
| Simplification `wmd_recall` | One distinct value across all 250 rows, approximately 0.483615 | Suspected export or calculation issue; upstream code is needed to diagnose it |

Zero counts by field are 13 for simplicity, 12 for coherence, five for informativeness, three for background, and six for factual alignment. A row may have zeros in more than one field.

## Relationship to the paper

The associated publication is the [2026 Journal of Biomedical Informatics article](https://www.sciencedirect.com/science/article/pii/S1532046426000626), [DOI: 10.1016/j.jbi.2026.105038](https://doi.org/10.1016/j.jbi.2026.105038). The supplied exports contain 1,750 evaluations but do not identify the paper's analysis-subset membership or include the original analysis script. The available fields are insufficient to establish the exact complete-case and quality-control exclusions. This release does not manufacture those subsets or claim to reproduce the paper's final analysis population.

A full comparison with all eight original input files confirms that reconstruction preserves the selected public item fields and all evaluation values. The attention-check count above was corrected from an earlier documentation count that counted only the literal string `0`, missing values written as `0.0`. The actual numeric total is 508; no stored score was changed. [Verification details](VERIFICATION.md).

## Question provenance

The supplied item file contains original and revised question, option, and answer columns. Revised content differs in 15 of the first questions, six of the second questions, and six of the third questions. These are counts of changed question text, not necessarily distinct source items across all three question positions.

The canonical working CSV and item export select the revised values and remove the `_REVISED` suffix. The exact original file remains in a local, ignored `.private/` backup. Internal revision notes remain only in the working CSV and backup. Canonical comprehension answer numbers are derived by matching the selected answer text to exactly one selected option.

The result exports contain correctness scores but no raw selected answers, question text, administration timestamp, or question-version identifier. It is therefore unknown whether any recorded annotation was collected against the revised questions. Renaming columns does not resolve this provenance gap. Historical scores remain unchanged, and `question_version` is `not_recorded` for every annotation. Do not use the canonical question key to claim a regraded historical score.

To establish exact alignment, recover the task templates/question versions actually shown to participants and the raw selected answers. If unavailable, publish the revised question bank as an updated resource with this limitation stated beside the historical evaluation results.

## Missing provenance and materials

- Original model snapshots, generation dates, complete prompt logs, random seed, and experiment configuration are absent.
- Source article DOIs/titles, exact CELLS release/member/row locators, and license evidence were recovered in the 50-paper audit. Twenty-one source-text pairs are omitted from the public item view because redistribution permission was not established. See [SOURCE_AUDIT.md](SOURCE_AUDIT.md).
- Raw answer choices, free-text recall responses, and recall-scoring code are absent. `recall` is numeric despite the paper's discussion of a written recall task.
- Participant demographics and full automated metric outputs are absent.
- The meaning of zero ratings and the simplification `wmd_recall` flatline require upstream confirmation.

## Privacy and interpretation

The candidate replaces source MTurk IDs with random participant identifiers and keeps the mapping local. Records still contain participant grouping, task time, and familiarity. No assertion of full anonymization or consent for public release is made by the preparation script.

The source-text license audit does not resolve the worker-count discrepancy, missing analysis-subset membership, historical question-version gap, or score-provenance issues above. Reconstruction restores source strings exactly and leaves these original evaluation limitations unchanged.

No demographics or clinical records are present in these CSVs. The topic texts are biomedical literature. Statistical analyses should account for repeated item and participant measurements, document handling of the flagged rows, and avoid treating the release candidate as the paper's final analysis population.
