---
language:
  - en
pretty_name: Human Evaluation of LLM-generated Plain Language Summaries
license: other
license_name: component-specific-licenses
license_link: LICENSE.md
task_categories:
  - summarization
  - question-answering
tags:
  - biomedical
  - plain-language-summaries
  - human-evaluation
  - comprehension
size_categories:
  - 1K<n<10K
configs:
  - config_name: items
    data_files:
      - split: test
        path: data/items.jsonl
  - config_name: annotations
    default: true
    data_files:
      - split: test
        path: data/annotations.jsonl
  - config_name: sources
    data_files:
      - split: test
        path: data/sources.jsonl
---

# Human Evaluation of LLM-generated Plain Language Summaries

Biomedical scientific abstracts and plain language summaries (PLSs) paired with crowdsourced human evaluation scores.

- **Paper:** [Are LLM-generated plain language summaries truly understandable? A large-scale crowdsourced evaluation](https://www.sciencedirect.com/science/article/pii/S1532046426000626), *Journal of Biomedical Informatics*, 179, 105038 (2026). [DOI](https://doi.org/10.1016/j.jbi.2026.105038).
- **Authors:** Yue Guo, Jae Ho Sohn, Gondy Leroy, and Trevor Cohen.
- **Maintainer:** [Guo Medical AI](https://huggingface.co/Guo-medicalAI).
- **Related repository:** [FAIRHealth/llm-evaluation-mturk](https://github.com/FAIRHealth/llm-evaluation-mturk). The complete reconstruction script is included directly here.

## Contents

| Configuration | Rows | Unit |
| --- | ---: | --- |
| `items` | 50 | Scientific item, seven summary variants, and question sets |
| `annotations` | 1,750 | Exported participant evaluation under one summary condition |
| `sources` | 50 | Article DOI/title, exact CELLS locator, license evidence, and text hashes |

All configurations join on `index`. Only a `test` split is supplied. There are no established training or validation splits. [Field definitions and condition mapping](DATA_DICTIONARY.md).

The seven conditions are human-authored PLS, criteria-agnostic LLM baseline, informativeness, simplification, coherence, faithfulness, and all criteria combined. The study identifies GPT-4 as the summary generator and Llama-3-70B as the question generator. Exact model snapshots and full prompt logs are absent from the supplied exports.

## Source text and licenses

All 50 pairs match the CELLS metadata archive at commit `a54b1ae8c2a7c2d7d14365df2b84584348e9e6ba`. Every article has a resolved DOI and title. [Per-paper audit](SOURCE_LICENSES.csv) and [method](SOURCE_AUDIT.md).

| Source terms established by primary records | Items | Public text treatment |
| --- | ---: | --- |
| CC BY 4.0 | 25 | Original abstract and human PLS included with attribution |
| Public-domain dedication, recorded as CC0 | 1 | Original text included |
| CC BY-NC-ND 4.0 | 3 | Strings included verbatim under original noncommercial/no-derivatives terms |
| Redistribution permission not established | 21 | `abs_text` and `pls_text` are null; DOI, title, and CELLS locator provided |

The three CC BY-NC-ND items retain their original terms. They are **not CC BY material**. Users must respect restrictions on commercial use and sharing adapted source text. Free-to-read access or a corpus repository's MIT license is not treated as permission to relicense publisher text.

Original dataset contributions are offered under CC BY 4.0 to the extent contributors hold applicable rights. Source material retains its original terms. Code is MIT-licensed. See [LICENSE.md](LICENSE.md), [CODE_LICENSE.txt](CODE_LICENSE.txt), and [upstream notices](THIRD_PARTY_NOTICES.md). This is a collection with component-specific licenses, not one blanket license.

## Load the public release

Install the loading library with `python -m pip install datasets`. No login is required.

```python
from datasets import load_dataset

repo_id = "Guo-medicalAI/llm-evaluation-mturk"
items = load_dataset(repo_id, "items", split="test")
annotations = load_dataset(repo_id, "annotations", split="test")
sources = load_dataset(repo_id, "sources", split="test")
```

Use `revision=` to pin a Hub commit for reproducible analyses.

## Reconstruct the complete evaluated files

Python 3.9+ is sufficient; no packages or model calls are required:

```bash
curl -L --fail -o reconstruct.py https://huggingface.co/datasets/Guo-medicalAI/llm-evaluation-mturk/resolve/main/reconstruct.py
python3 reconstruct.py
```

The script combines the release with the exact source strings in the pinned, publicly accessible CELLS archive and writes:

- `reconstructed/items_complete.csv`: all 50 items with 37 columns.
- `reconstructed/items_complete.jsonl`: complete items plus source/licensing metadata.
- `reconstructed/evaluations_complete.csv`: all 1,750 evaluations joined to the abstract, human PLS, evaluated summary, and identifiers.
- `reconstructed/reconstruction_report.json`: completeness, retrieval method, and original text-hash verification for every item.

Reconstruction recovers all 50 items and preserves all 1,750 evaluations and participant groupings. Source text is retrieved from the archive and checked against its recorded hashes.

A DOI identifies an article but does not guarantee a PLS, access, or the evaluated wording. The pinned CELLS route is the exact-reproduction path. An optional direct-DOI mode reports unavailable or changed text explicitly. [Complete instructions](RECONSTRUCTION.md).

Retrieval does not expand source-text rights. Reconstructed complete files are for uses authorized by original source terms and must not be treated as wholly CC BY. The script does not bypass publisher access controls.

## Usage and limitations

Use `participant_id` to group repeated evaluations by the same participant. These IDs are dataset-specific pseudonyms. Missing topic familiarity is null; mean MCQ accuracy and flags for zero-valued ratings and duplicate rows are provided.

The dataset contains 151 participant pseudonyms, four extra exact duplicate rows, and 35 rows with zero-valued ratings. All evaluation rows are retained, so state any exclusions when reporting analyses. The simplification `wmd_recall` field is constant. Raw selected answers, free-text recall responses, demographics, score implementation details, paper-subset membership, and the full automated metric table are unavailable. [Quality notes](QUALITY.md).

Comprehension scores are supplied as recorded evaluations; raw answer selections are unavailable for independent rescoring.

This collection has only 50 source items and repeated participant measurements. Account for item and participant clustering, state exclusions, and group future data splits by source item. This English-language biomedical benchmark does not establish generalization to other populations or clinical use. Generated content can contain errors.

## Citation

Credit the dataset contributors and retain article attribution from `sources` when reusing source text. Please cite the study:

```bibtex
@article{guo2026plainlanguagesummaries,
  title = {Are {LLM}-generated plain language summaries truly understandable? A large-scale crowdsourced evaluation},
  author = {Guo, Yue and Sohn, Jae Ho and Leroy, Gondy and Cohen, Trevor},
  journal = {Journal of Biomedical Informatics},
  volume = {179},
  pages = {105038},
  year = {2026},
  month = jul,
  doi = {10.1016/j.jbi.2026.105038},
  url = {https://www.sciencedirect.com/science/article/pii/S1532046426000626}
}
```
