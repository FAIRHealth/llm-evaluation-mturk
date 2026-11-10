# Human evaluation of LLM-generated plain language summaries

Dataset and reconstruction code for **Are LLM-generated plain language summaries truly understandable? A large-scale crowdsourced evaluation** by Yue Guo, Jae Ho Sohn, Gondy Leroy, and Trevor Cohen.

[Published paper](https://www.sciencedirect.com/science/article/pii/S1532046426000626) · [DOI](https://doi.org/10.1016/j.jbi.2026.105038) · [GitHub repository](https://github.com/FAIRHealth/llm-evaluation-mturk) · [Dataset card](huggingface/README.md) · [Data dictionary](huggingface/DATA_DICTIONARY.md)

Published in *Journal of Biomedical Informatics*, **179**, article 105038 (July 2026), [DOI: 10.1016/j.jbi.2026.105038](https://doi.org/10.1016/j.jbi.2026.105038).

This project supports research on how subjective quality ratings relate to reader comprehension of biomedical plain language summaries (PLSs). It pairs scientific abstracts and summary variants with human evaluation scores.

## Dataset availability

The dataset is public at [Guo-medicalAI/llm-evaluation-mturk](https://huggingface.co/datasets/Guo-medicalAI/llm-evaluation-mturk), with article-specific source-text licensing and a complete reconstruction script. See the [source audit](huggingface/SOURCE_AUDIT.md).

Hugging Face hosts the data. This GitHub repository provides documentation, source-license information, and the reconstruction script.

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

- `reconstructed/items_complete.csv`: 50 items with 37 columns.
- `reconstructed/items_complete.jsonl`: complete items plus DOI and license metadata.
- `reconstructed/evaluations_complete.csv`: all 1,750 evaluations joined to their texts and article identifiers.
- `reconstructed/reconstruction_report.json`: completeness and exact-match checks.

Reconstruction recovers all 50 items and preserves all 1,750 evaluations and participant groupings. Source text is checked against its recorded hashes. Source rights still apply to reconstructed local files. [Direct DOI retrieval, offline options, and limitations](huggingface/RECONSTRUCTION.md).

## Documentation

- [Data dictionary](huggingface/DATA_DICTIONARY.md): fields, score definitions, and condition mapping.
- [Reconstruction guide](huggingface/RECONSTRUCTION.md): commands, retrieval options, and output formats.
- [Dataset quality](huggingface/QUALITY.md): data limitations and analysis considerations.
- [Source licenses](huggingface/SOURCE_LICENSES.csv): article-level attribution and reuse terms.

## License and citation

Original contributions are offered under CC BY 4.0 to the extent contributors hold applicable rights. Retained article text uses its component-specific source terms; three pairs retain CC BY-NC-ND restrictions. Reconstruction code is MIT-licensed. See the [license](huggingface/LICENSE.md) and [per-paper audit](huggingface/SOURCE_LICENSES.csv).

Please cite the associated paper using [CITATION.bib](CITATION.bib).
