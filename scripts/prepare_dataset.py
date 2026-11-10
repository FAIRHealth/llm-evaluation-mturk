#!/usr/bin/env python3
"""Normalize question headers and prepare a local, pseudonymized release candidate.

Uses the Python standard library. Does not upload, filter, or regrade annotations.
"""

import csv
import hashlib
import json
import math
import shutil
import uuid
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_NAME = "results_llama_mcq_attention_baseline_REVISED.csv"
CANONICAL_NAME = "results_llama_mcq_attention_baseline.csv"
CONDITIONS = {
    "pls": "human",
    "baseline": "baseline",
    "informativeness": "informativeness",
    "simplification": "simplification",
    "coherence": "coherence",
    "faithfulness": "faithfulness",
    "all": "all",
}
RATINGS = ["simplicity", "coherent", "informative", "background", "factual"]
SCORES = ["VAR_QUESTION1", "VAR_QUESTION2", "VAR_QUESTION3", "ATTENTION_QUESTION"]
RAW_FIELDS = ["index", "WorkerId", *SCORES, "familiarity", *RATINGS,
              "recall", "wmd_recall", "work_time_seconds"]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        if not fields or len(fields) != len(set(fields)):
            raise ValueError(f"Missing or duplicate headers: {path.name}")
        rows = list(reader)
        if any(None in row or None in row.values() for row in rows):
            raise ValueError(f"Malformed row: {path.name}")
        return fields, rows


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)
                    + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Non-finite numeric value")
    return result


def prepare():
    private = ROOT / ".private"
    backup = private / ORIGINAL_NAME
    original = ROOT / ORIGINAL_NAME
    source = backup if backup.exists() else original
    if not source.exists():
        raise FileNotFoundError(
            f"Supply {ORIGINAL_NAME} at the project root or in .private/. "
            "The canonical file alone lacks the original question provenance."
        )
    fields, source_items = read_csv(source)
    canonical_fields = [f for f in fields if not f.endswith("_REVISED")]
    canonical_items = []
    answer_positions_updated = 0
    for source_row in source_items:
        row = {field: source_row.get(field + "_REVISED", source_row[field])
               for field in canonical_fields}
        for n in (1, 2, 3):
            prefix = f"VAR_QUESTION{n}"
            options = [row[f"{prefix}-Opt{i}"] for i in (1, 2, 3, 4)]
            answer = row[f"{prefix}-Answer"]
            if options.count(answer) != 1:
                raise ValueError(f"Ambiguous answer for item {row['index']}, {prefix}")
            answer_num = str(options.index(answer) + 1)
            answer_positions_updated += answer_num != row[f"{prefix}-AnswerNum"]
            row[f"{prefix}-AnswerNum"] = answer_num
        canonical_items.append(row)
    item_ids = {row["index"] for row in canonical_items}
    if len(item_ids) != len(canonical_items):
        raise ValueError("Item index is not unique")

    raw_files = []
    for stem, condition in CONDITIONS.items():
        path = ROOT / "result_with_workerID" / f"{stem}_result_output.csv"
        raw_fields, rows = read_csv(path)
        if set(raw_fields) != set(RAW_FIELDS):
            raise ValueError(f"Unexpected schema: {path.name}")
        if any(row["index"] not in item_ids for row in rows):
            raise ValueError(f"Unmatched item index: {path.name}")
        raw_files.append((path, condition, rows))

    private.mkdir(exist_ok=True, mode=0o700)
    mapping_path = private / "participant_ids.json"
    mapping = json.loads(mapping_path.read_text()) if mapping_path.exists() else {}
    for _, _, rows in raw_files:
        for row in rows:
            if not row["WorkerId"].strip():
                raise ValueError("Empty worker ID")
            mapping.setdefault(row["WorkerId"], "p_" + uuid.uuid4().hex)
    if len(set(mapping.values())) != len(mapping):
        raise ValueError("Participant pseudonym collision")

    annotations = []
    per_condition = {}
    for path, condition, rows in raw_files:
        multiplicity = Counter(row["index"] for row in rows)
        seen = Counter()
        for row_num, row in enumerate(rows, 1):
            signature = tuple(row[field] for field in RAW_FIELDS)
            out = {"annotation_id": f"{condition}_{row_num:04d}",
                   "index": int(row["index"]), "condition": condition,
                   "participant_id": mapping[row["WorkerId"]],
                   "question_version": "not_recorded"}
            for field in SCORES + RATINGS:
                value = number(row[field])
                if not value.is_integer():
                    raise ValueError(f"Non-integer score in {field}")
                out[field] = int(value)
            if any(out[f] not in (0, 1) for f in SCORES):
                raise ValueError("Unexpected correctness code")
            if any(not 0 <= out[f] <= 5 for f in RATINGS):
                raise ValueError("Unexpected rating code")
            out["familiarity"] = row["familiarity"].strip() or None
            if out["familiarity"] not in (None, "never", "somewhat", "expert"):
                raise ValueError("Unexpected familiarity category")
            for field in ("recall", "wmd_recall", "work_time_seconds"):
                out[field] = number(row[field])
            out["mcq_accuracy"] = sum(out[f] for f in SCORES[:3]) / 3
            out["has_zero_rating"] = any(out[field] == 0 for field in RATINGS)
            out["is_duplicate_row"] = seen[signature] > 0
            seen[signature] += 1
            annotations.append(out)
        per_condition[condition] = {
            "rows": len(rows),
            "participants": len({row['WorkerId'] for row in rows}),
            "items": len(multiplicity),
            "annotations_per_item_distribution": dict(Counter(multiplicity.values())),
            "exact_duplicate_extra_rows": sum(v - 1 for v in seen.values()),
            "wmd_recall_distinct_values": len({row['wmd_recall'] for row in rows}),
        }

    # Keep all selected item fields except internal revision notes.
    items = [{key: int(value) if key == "index" or key.endswith("-AnswerNum") else value
              for key, value in row.items() if not key.endswith("_REVISION_NOTES")}
             for row in canonical_items]
    original_item_columns = list(items[0])
    data = ROOT / "huggingface" / "data"
    data.mkdir(parents=True, exist_ok=True)
    sources_path = data / "sources.jsonl"
    if not sources_path.exists():
        raise FileNotFoundError("Build the reviewed source audit before preparing public data")
    sources = [json.loads(line) for line in sources_path.read_text().splitlines()]
    source_lookup = {row['index']: row for row in sources}
    if len(source_lookup) != len(items) or set(source_lookup) != {row['index'] for row in items}:
        raise ValueError("Source audit does not cover the item collection exactly")
    for item in items:
        source_record = source_lookup[item['index']]
        for field, hash_field in [('abs_text', 'abs_sha256'), ('pls_text', 'pls_sha256')]:
            if hashlib.sha256(item[field].encode()).hexdigest() != source_record[hash_field]:
                raise ValueError("Item changed after source audit")
            if source_record['source_text_status'] == 'metadata_only':
                item[field] = None
        for field in ['title', 'doi', 'cells_id', 'source_license', 'source_license_url', 'source_text_status']:
            item[field] = source_record[field]
    payloads = {
        "items.jsonl": "".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n"
                               for row in items),
        "annotations.jsonl": "".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n"
                                     for row in annotations),
    }
    for name, payload in payloads.items():
        if any(worker_id in payload for worker_id in mapping):
            raise ValueError(f"Source worker ID found in {name}")

    # Preserve the exact input bytes before replacing the working CSV.
    if not backup.exists():
        shutil.copy2(source, backup)
    write_json(mapping_path, mapping)
    mapping_path.chmod(0o600)
    canonical_path = ROOT / CANONICAL_NAME
    with canonical_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=canonical_fields)
        writer.writeheader()
        writer.writerows(canonical_items)
    if original.exists():
        if digest(original) != digest(backup):
            raise ValueError("Root source differs from backup; preserved both for review")
        original.unlink()
    for name, payload in payloads.items():
        (data / name).write_text(payload, encoding="utf-8")
    manifest = {
        "status": "public release prepared with article-specific source-text policy",
        "dataset_id": "Guo-medicalAI/llm-evaluation-mturk",
        "question_policy": "canonical item fields use revised values; score question version not recorded",
        "items": len(items), "annotations": len(annotations),
        "original_item_columns": original_item_columns,
        "source_text_counts": dict(Counter(row['source_text_status'] for row in sources)),
        "source_license_counts": dict(Counter(row['source_license'] for row in sources)),
        "source_audit_sha256": digest(sources_path),
        "participants": len({row['participant_id'] for row in annotations}),
        "missing_familiarity_rows": sum(row['familiarity'] is None for row in annotations),
        "rows_with_zero_rating": sum(row['has_zero_rating'] for row in annotations),
        "zero_rating_counts": {f: sum(row[f] == 0 for row in annotations) for f in RATINGS},
        "failed_attention_rows": sum(row['ATTENTION_QUESTION'] == 0 for row in annotations),
        "exact_duplicate_extra_rows": sum(row['is_duplicate_row'] for row in annotations),
        "answer_positions_updated": answer_positions_updated,
        "conditions": per_condition,
        "sources": [{"path": str(path.relative_to(ROOT)), "sha256": digest(path)}
                    for path in [backup] + [entry[0] for entry in raw_files]],
        "outputs": {name: {"sha256": digest(data / name)} for name in [*payloads, 'sources.jsonl']},
        "excluded": ["source WorkerId", "participant mapping", "revision notes",
                     "superseded question and option values", "source text without verified redistribution permission"],
    }
    write_json(data / "manifest.json", manifest)
    print(json.dumps({key: manifest[key] for key in (
        "status", "items", "annotations", "participants", "answer_positions_updated",
        "missing_familiarity_rows", "rows_with_zero_rating", "exact_duplicate_extra_rows"
    )}, indent=2))


if __name__ == "__main__":
    prepare()
