# Reconstruction verification

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

## Public view versus local reconstruction

The public `items` configuration intentionally has null source-text fields for 21 items whose redistribution permission was not established. The tested reconstruction restores those fields from the pinned CELLS archive and verifies the original text hashes. Source licensing continues to apply to complete local files.

For dataset quality and study limitations, see [QUALITY.md](QUALITY.md).
