# Comparison with the complete original inputs

The reconstruction was rerun from the published script against audited Hugging Face data revision `5612aa22db13898a214c6b8ddd774c8fcfe6d905`. The comparison covered the original question/summary CSV, the normalized working CSV, and all seven original evaluation exports. Hashes for all eight original input files match the hashes recorded in the release manifest.

## Results

| Check | Result |
| --- | --- |
| Original study items recovered | 50 of 50 |
| Selected public item fields | 37 columns, all 1,850 values match exactly |
| Abstracts and human-written PLSs | All 50 pairs restored exactly, including whitespace |
| Generated summaries, current questions/options/keys, and item IDs | All preserved in the item-field comparison |
| Evaluation rows | All 1,750 preserved; none filtered |
| Evaluations per condition | 250 in each of seven conditions |
| Numeric evaluation fields, including item IDs | All 22,750 values match using exact decimal comparisons |
| Topic familiarity | All 1,750 values preserved; blank source values remain missing |
| Participant grouping | All 1,750 mapping checks pass, preserving 151 distinct participants |
| Joined abstract, human PLS, and evaluated summary | All 5,250 row-level text checks pass |
| Duplicate evaluations | All four extra exact duplicate rows preserved and flagged |
| Rows containing zero-valued ratings | All 35 preserved and flagged |

The comparison script is `scripts/verify_reconstruction.py` in the GitHub repository. It uses original local files and the private participant mapping. Its aggregate output contains no source worker IDs or article text.

## Why the files are not byte-for-byte copies of every original column

The original question/summary CSV has **58 columns**. Following the requested normalization, the working CSV has **40**, and the reconstructed public item table has **37**:

1. The 18 `_REVISED` columns replace their corresponding original columns under the canonical field names. Selecting those revised values changes 160 cells relative to the superseded original question/option/answer values. The reconstructed file matches the selected revised values, not both historical versions simultaneously.
2. Three internal `VAR_QUESTION{n}_REVISION_NOTES` columns remain in the private working CSV but are intentionally excluded from public reconstruction.
3. Original `WorkerId` strings are replaced by dataset-specific participant pseudonyms. Group membership is preserved, but the public release cannot recover the original identifiers.
4. Numeric serialization is normalized (for example, `1.0` can become `1`). Exact decimal comparisons confirm numeric values are unchanged. CSV serialization, file hashes, and formatting need not match the original files byte-for-byte.
5. Derived fields, quality flags, and article metadata are added. The joined evaluation file includes the relevant source and summary text alongside the original evaluation measures.

Therefore, the reconstructed files preserve the complete selected research data and all evaluation rows, subject to these documented transformations. They do not reproduce superseded columns, internal notes, source identities, or original file formatting.

## Public view versus local reconstruction

The public `items` configuration intentionally has null source-text fields for 21 items whose redistribution permission was not established. The tested reconstruction restores those fields from the pinned CELLS archive and verifies the original text hashes. Source licensing continues to apply to complete local files.

## Documentation correction

The original numeric attention-check scores contain **508 zeros**, including both `0` and `0.0` representations. An earlier documentation count of 374 missed the latter string representation. The release manifest and evaluation data already contain the correct numeric values; only the prose count required correction.

These checks establish data preservation. They do not resolve the original study's participant-count discrepancy, historical administered-question versions, unavailable analysis-subset membership, or recall-score implementation. See [QUALITY.md](QUALITY.md).
