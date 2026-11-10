# Dataset publication and maintenance

Dataset: [Guo-medicalAI/llm-evaluation-mturk](https://huggingface.co/datasets/Guo-medicalAI/llm-evaluation-mturk). Organization: [Guo Medical AI](https://huggingface.co/Guo-medicalAI), free tier. This GitHub repository hosts the public documentation and code; data remains on Hugging Face.

## Source review and release policy

All 50 source pairs were matched exactly to the pinned CELLS metadata archive and resolved to article DOIs and titles. The source audit retains 29 pairs with explicit source terms (25 CC BY, one public-domain dedication, three CC BY-NC-ND). The other 21 pairs have null abstract/human-summary fields and retain DOI/title/CELLS locators. Review [SOURCE_AUDIT.md](../huggingface/SOURCE_AUDIT.md), [SOURCE_LICENSES.csv](../huggingface/SOURCE_LICENSES.csv), and the [component license](../huggingface/LICENSE.md).

Original contributions use CC BY 4.0 only to the extent contributors hold relevant rights. Source-specific terms remain in force. Code uses MIT. Licensing is not evidence of participant consent; study owners remain responsible for their participant-data sharing permissions. The public files omit source MTurk identifiers and the private pseudonym mapping.

## Protect the earlier private history

The initial private draft contains source text now omitted from the public view, including in commit `8af4a24907cc95fbc765353cb72d7d73bbd0008a`. Replacing current files alone would leave that text in history.

That draft has been preserved privately at `llm-evaluation-mturk-private-archive`. The clean public repository uses the original `llm-evaluation-mturk` name and contains only its new initial commit and audited release. Keep the archive private. Future updates must continue to exclude omitted text from public history.

## Local preparation

The audit cache, upstream archive, and original source CSVs remain in ignored local folders. To rebuild a maintainer release:

```bash
python3 scripts/build_source_audit.py
python3 scripts/prepare_dataset.py
python3 -m unittest discover -s tests -v
python3 huggingface/reconstruct.py --data-dir huggingface/data --output-dir .private/whole-dataset-check
python3 scripts/verify_reconstruction.py
```

`build_source_audit.py` uses the reviewed per-paper primary metadata in `.private/source_audit/`. It exports metadata, not raw article text. Preparation fails if audit coverage, keys, or source hashes no longer match. It retains all 1,750 evaluation rows and documented quality flags. Changing source decisions requires reviewing their evidence and updating documentation and counts together.

Users need only `reconstruct.py` and the public release. They do not need private maintainer inputs. The script downloads the pinned public upstream archive, restores missing source strings with exact-hash checks, and writes the complete 50-item table plus all joined evaluations. [User instructions](../huggingface/RECONSTRUCTION.md).

## Upload allowlist

Upload the following from `huggingface/`, preserving `data/` paths:

```text
README.md
DATA_DICTIONARY.md
QUALITY.md
SOURCE_AUDIT.md
SOURCE_LICENSES.csv
LICENSE.md
CODE_LICENSE.txt
THIRD_PARTY_NOTICES.md
RECONSTRUCTION.md
VERIFICATION.md
reconstruct.py
data/items.jsonl
data/annotations.jsonl
data/sources.jsonl
data/manifest.json
```

Never upload the project root, raw worker exports, `.private/`, reconstructed complete files, `__pycache__/`, or the upstream CELLS archive. Future API uploads should use an explicit allowlist with these files. See the official [upload guide](https://huggingface.co/docs/huggingface_hub/guides/upload).

## Validation

Before publication, verify the file allowlist, exclusion of source worker IDs, all item/source/annotation joins, 29 retained and 21 omitted source pairs, unchanged included source hashes, and all source attribution fields. Seven meaningful tests cover missing text, version drift, archive corruption, released text tampering, exact reconstruction, and authorized local input without network calls.

The complete local reconstruction was compared against all values in all 37 original public item columns; every row matches. The original working CSV's three internal revision-note columns are excluded, as are source worker IDs. Historical scores are not regraded.

The release integration tests use the public package's `data/` files under `huggingface/data/`. Download the Hugging Face dataset repository there to run them from a fresh GitHub clone. Checks requiring the original private CSV or cached upstream archive skip when those maintainer-only inputs are absent.

After upload, verify the file tree, rendered card, license metadata, clean history, public visibility, and anonymous download access. Run the reconstruction script from the actual public release and pin the verified Hub commit when reporting results. Keep any evidence, snapshots, and fully reconstructed files local.

## Remaining scientific limitations

The public source audit does not resolve the worker-count discrepancy (151 source IDs versus 150 reported participants), four duplicate evaluations, 35 rows with zero ratings, constant simplification `wmd_recall`, historical question-version uncertainty, or missing paper-subset membership. These remain documented in [QUALITY.md](../huggingface/QUALITY.md).

## Verified public release

The clean dataset was made public on November 9, 2026 at [Guo-medicalAI/llm-evaluation-mturk](https://huggingface.co/datasets/Guo-medicalAI/llm-evaluation-mturk). Release commit: `5612aa22db13898a214c6b8ddd774c8fcfe6d905`. Its public history contains only the new initial commit and the reviewed release commit. The original draft was preserved at the private `llm-evaluation-mturk-private-archive` repository. Anonymous checks returned 404 for the old draft commit at the public repository and 401 for the private archive.

The published script was downloaded without credentials and run against the pinned public release. It reconstructed 50/50 exact item records and joined all 1,750 evaluations. Every value in the 37-column reconstructed item CSV matches the original canonical CSV. The server-side viewer initially reported `ResponseNotReady` while processing the newly public dataset; this is a service preparation state rather than a reported data-format error.

Anonymous Python `load_dataset` verification also passed for all three pinned public configurations: 50 items, 1,750 annotations, and 50 sources. The item view has exactly 21 null abstract/human-summary pairs, as intended.

The subsequent whole-input comparison verifies all 1,850 item values and 22,750 numeric evaluation values, all participant mappings, all 1,750 familiarity values, and all 5,250 joined text values. See [VERIFICATION.md](../huggingface/VERIFICATION.md). The journal references and verification report were published in a documentation-only Hub update, commit `fe7dec537f0056f9effb45f46d0cd02614fe1eb9`; the released data and reconstruction code are unchanged.
