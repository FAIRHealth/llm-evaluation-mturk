# Reconstructing the complete evaluated dataset

## Automatic reconstruction

```bash
curl -L --fail -o reconstruct.py https://huggingface.co/datasets/Guo-medicalAI/llm-evaluation-mturk/resolve/main/reconstruct.py
python3 reconstruct.py
```

Python 3.9+ is sufficient. No extra packages, API keys, model calls, or manual article downloads are needed for the default path. It downloads release files and the approximately 60.6 MB pinned CELLS metadata archive, then caches them. Retrieval depends on upstream availability and remains subject to source terms.

The script joins released records to the DOI-resolved source manifest, selects each exact CELLS revision/member/row, checks archive and text SHA-256 values, and fills missing `abs_text` and `pls_text`. Generated variants, questions, keys, and historical scores stay unchanged. It retrieves existing text rather than generating replacements.

DOIs identify papers but do not guarantee access, a PLS, or historical wording. The pinned CELLS archive is the exact-reproduction path.

## Outputs

| File in `reconstructed/` | Contents |
| --- | --- |
| `items_complete.csv` | 50 rows in the original 37 public item columns |
| `items_complete.jsonl` | Complete items plus DOI and source/license metadata |
| `evaluations_complete.csv` | 1,750 evaluations plus abstract, human PLS, evaluated summary, and article identifiers |
| `reconstruction_report.json` | Per-item completeness, retrieval method, and exact-hash checks |

All values in all 37 item columns were checked against the original canonical CSV: 50/50 rows match exactly. Three internal revision-note columns and original worker IDs are intentionally excluded. Scores are never regraded.

## Offline or authorized inputs

If release files and the audited archive are already on disk:

```bash
python3 reconstruct.py --data-dir data --cells-archive /path/to/CELLS_metadata.zip
```

A different archive revision is rejected by checksum. For text obtained through another authorized route, provide a UTF-8 CSV with `index,abs_text,pls_text`:

```bash
python3 reconstruct.py --data-dir data --source none --authorized-texts /path/to/authorized_texts.csv
```

Original hashes are checked before accepting supplied text. Missing fields remain unresolved and are reported rather than invented.

## Optional direct DOI retrieval

```bash
python3 reconstruct.py --source doi --output-dir reconstructed-from-doi
```

This resolves missing items' DOIs through Europe PMC, retrieves available full-text XML, and extracts an abstract plus author summary, synopsis, or significance section. It is best effort: readable papers may lack downloadable XML, a PLS, or the historical wording. By default, different text is reported and left unresolved. `--allow-text-drift` explicitly accepts current text with nonmatching hashes; the report still marks it as inexact. That output is not an exact reproduction.

The script does not bypass paywalls, authentication, CAPTCHAs, or publisher access controls. The default pinned-corpus mode is the tested path to the complete historical file.

## Reproducibility and rights

Use `--revision HUB_COMMIT_SHA` to pin the release and `--cache-dir PATH` to reuse downloads. `--source none` exports the released view without retrieving omitted text. Exit code 0 means complete reconstruction, 2 means unresolved fields, and 1 means an execution or integrity error.

`cells_id` is the composite locator `CELLS@COMMIT:CSV_MEMBER:DATA_ROW`, not an asserted original numeric CELLS ID. The original study `index` remains separate. Data rows start at 1, excluding the header.

Downloading the publicly accessible upstream archive does not make every article MIT-licensed or authorize redistribution of complete reconstructed files. Use retrieved text only as permitted by its source terms, and keep the [component licenses](LICENSE.md) with local output.
