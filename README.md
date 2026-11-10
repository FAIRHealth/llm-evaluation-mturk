# Human evaluation of LLM-generated plain language summaries

Data and release preparation for **Are LLM-generated plain language summaries truly understandable? A large-scale crowdsourced evaluation** by Yue Guo, Jae Ho Sohn, Gondy Leroy, and Trevor Cohen.

[Published paper](https://www.sciencedirect.com/science/article/pii/S1532046426000626) · [DOI](https://doi.org/10.1016/j.jbi.2026.105038) · [GitHub repository](https://github.com/FAIRHealth/llm-evaluation-mturk) · [Dataset card](huggingface/README.md) · [Data dictionary](huggingface/DATA_DICTIONARY.md)

Published in *Journal of Biomedical Informatics*, **179**, article 105038 (July 2026), [DOI: 10.1016/j.jbi.2026.105038](https://doi.org/10.1016/j.jbi.2026.105038).

This project supports research on how subjective quality ratings relate to reader comprehension of biomedical plain language summaries (PLSs). It pairs scientific abstracts and summary variants with human evaluation scores.

## Dataset availability

The dataset is public at [Guo-medicalAI/llm-evaluation-mturk](https://huggingface.co/datasets/Guo-medicalAI/llm-evaluation-mturk), with article-specific source-text licensing and a complete reconstruction script. See the [source audit](huggingface/SOURCE_AUDIT.md).

Hugging Face hosts the data; this GitHub repository contains documentation, the license audit, and preparation/reconstruction code. Dataset files are excluded from Git. The earlier draft is preserved as a private archive because its history contains source text omitted from the public release.

## What is included

The public release contains:

| Configuration | Rows | Unit |
| --- | ---: | --- |
| `items` | 50 | One abstract, seven summary variants, and question sets per item |
| `annotations` | 1,750 | One exported participant evaluation of an item under one condition |
| `sources` | 50 | Article DOI/title, exact CELLS locator, licensing evidence, and text hashes |

Twenty-nine source-text pairs are included under their original licenses: 25 CC BY, one public-domain dedication, and three CC BY-NC-ND. For 21 items, source text is replaced by null plus DOI/title/CELLS references. All generated summaries, questions, and evaluation records remain available. [Component licenses](huggingface/LICENSE.md).

The seven conditions are human-authored PLS, criteria-agnostic LLM baseline, informativeness, simplification, coherence, faithfulness, and all criteria combined. Each condition has 250 exported rows. The paper identifies GPT-4 as the summary generator and Llama-3-70B as the question generator. Exact model snapshots are not recorded in the supplied files.

Annotations contain three binary comprehension scores, one attention-check score, five quality ratings, topic familiarity, two numeric recall-related fields, and completion time. Raw answer selections, free-text recall responses, participant demographics, and the full set of automated metrics from the paper are **not present in these exports**.

The [quality notes](huggingface/QUALITY.md) describe duplicate rows, out-of-scale rating codes, uncertain recall-score provenance, and differences from the paper's analysis population. These files do not yet reproduce the paper's filtered analysis subsets.

## Load the dataset

Install the optional loading library:

```bash
python -m pip install datasets
```

No login is required for the public release:

```python
from datasets import load_dataset

repo_id = "Guo-medicalAI/llm-evaluation-mturk"
items = load_dataset(repo_id, "items", split="test")
annotations = load_dataset(repo_id, "annotations", split="test")
sources = load_dataset(repo_id, "sources", split="test")
```

Join on `index`, then choose the summary column corresponding to `condition` using the data dictionary. There are no established training or validation splits. For reproducible analyses, add `revision="5612aa22db13898a214c6b8ddd774c8fcfe6d905"` to pin the audited release.

## Reconstruct the complete files

From a clone of this GitHub repository:

```bash
python3 huggingface/reconstruct.py
```

Python 3.9+ is sufficient. The script automatically downloads the public dataset and pinned CELLS archive, checks exact text hashes, and writes:

- `reconstructed/items_complete.csv`: 50 items in the original 37 public columns.
- `reconstructed/items_complete.jsonl`: complete items plus DOI and license metadata.
- `reconstructed/evaluations_complete.csv`: all 1,750 evaluations joined to their texts and article identifiers.
- `reconstructed/reconstruction_report.json`: completeness and exact-match checks.

It was checked against all eight original input CSVs: every value in the 37 public item columns and every numeric evaluation value matches, all 1,750 evaluations are preserved, and participant grouping is intact. The files use the revised question values, omit superseded/internal columns, and replace worker IDs with pseudonyms. [Full comparison and intentional differences](huggingface/VERIFICATION.md). Source rights still apply to reconstructed local files. [Direct DOI retrieval, offline options, and limitations](huggingface/RECONSTRUCTION.md).

## Prepare the data locally

This maintainer workflow requires the original exports and private audit cache, which are not included in this GitHub repository. Dataset users should use the reconstruction command above.

```bash
python3 scripts/build_source_audit.py
python3 scripts/prepare_dataset.py
```

Preparation uses only the Python standard library. It:

1. Backs up the original question CSV to `.private/` without changing its bytes.
2. Selects revised question, option, and answer values as the canonical fields, removes `_REVISED` columns, and writes `results_llama_mcq_attention_baseline.csv`. Answer positions are derived from the selected options and answer text.
3. Replaces source `WorkerId` values with random participant IDs. The mapping stays in `.private/participant_ids.json` and is reused on subsequent runs.
4. Writes `huggingface/data/items.jsonl`, `annotations.jsonl`, and a manifest with counts and SHA-256 checksums. It flags duplicate rows and zero-valued ratings without filtering or changing those source values.
5. Requires the reviewed `sources.jsonl` audit and removes `abs_text`/`pls_text` from items without established redistribution permission. Missing audit coverage or changed source text causes an error.

**Question version matters:** the annotation exports contain correctness scores, not the selected answers or an administered-question version. Selecting revised question text does not regrade those historical scores. See [question provenance](huggingface/QUALITY.md#question-provenance).

## Repository layout

```text
README.md                       GitHub overview
CITATION.bib                    Paper citation
docs/PUBLISHING.md              Release and maintenance instructions
scripts/build_source_audit.py   Export the reviewed source audit
scripts/prepare_dataset.py      Local preparation and validation
huggingface/reconstruct.py      Complete public reconstruction script
huggingface/RECONSTRUCTION.md   User instructions and output formats
huggingface/LICENSE.md          Component-specific dataset terms
huggingface/CODE_LICENSE.txt    MIT license for code
huggingface/SOURCE_LICENSES.csv Article-level attribution and decisions
huggingface/README.md           Hugging Face dataset card
huggingface/DATA_DICTIONARY.md   Field definitions and condition mapping
huggingface/QUALITY.md           Observed limitations and provenance
huggingface/data/               Generated dataset files; ignored by GitHub Git
result_with_workerID/           Original exports; ignored by Git
.private/                      Original question backup and ID mapping; ignored by Git
```

The normalized working CSV is also ignored by Git. Upload only the intended Hugging Face package, following the publishing guide. Keep `.private/` and source worker IDs local.

## License and citation

Original contributions are offered under CC BY 4.0 to the extent contributors hold applicable rights. Retained article text uses its component-specific source terms; three pairs retain CC BY-NC-ND restrictions. Reconstruction code is MIT-licensed. See the [license](huggingface/LICENSE.md) and [per-paper audit](huggingface/SOURCE_LICENSES.csv).

Please cite the associated paper using [CITATION.bib](CITATION.bib).
