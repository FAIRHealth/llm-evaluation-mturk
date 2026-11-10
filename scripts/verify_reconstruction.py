#!/usr/bin/env python3
"""Compare reconstructed data with all original local study CSVs.

Requires maintainer-only originals and the private participant mapping. The
saved report contains aggregate counts and hashes, never participant IDs or text.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = {
    'pls': ('human', 'pls_text'), 'baseline': ('baseline', 'baseline'),
    'informativeness': ('informativeness', 'Informativeness'),
    'simplification': ('simplification', 'Simplification'),
    'coherence': ('coherence', 'Coherence'), 'faithfulness': ('faithfulness', 'Faithfulness'),
    'all': ('all', 'Informativeness_Simplification_Coherence_Faithfulness'),
}


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        if len(fields) != len(set(fields)):
            raise ValueError('Duplicate CSV headers')
        return fields, list(reader)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reconstructed-dir', type=Path, default=ROOT / '.private/whole-dataset-check')
    parser.add_argument('--report', type=Path, default=ROOT / '.private/whole-dataset-check/comparison.json')
    args = parser.parse_args()
    raw_path = ROOT / '.private/results_llama_mcq_attention_baseline_REVISED.csv'
    original_fields, backup = read_csv(raw_path)
    canonical_fields, canonical = read_csv(ROOT / 'results_llama_mcq_attention_baseline.csv')
    reconstructed_fields, reconstructed = read_csv(args.reconstructed_dir / 'items_complete.csv')
    _, evaluations = read_csv(args.reconstructed_dir / 'evaluations_complete.csv')
    notes = [field for field in canonical_fields if field.endswith('_REVISION_NOTES')]
    public_fields = [field for field in canonical_fields if field not in notes]
    assert reconstructed_fields == public_fields
    assert len(backup) == len(canonical) == len(reconstructed) == 50
    canon_by_id = {row['index']: row for row in canonical}
    restored_by_id = {row['index']: row for row in reconstructed}
    assert len(canon_by_id) == len(restored_by_id) == 50
    cells_checked = revised_cells = 0
    for raw in backup:
        identifier = raw['index']
        assert identifier in restored_by_id
        for field in public_fields:
            expected = raw.get(field + '_REVISED', raw[field])
            assert canon_by_id[identifier][field] == expected, ('canonical', identifier, field)
            assert restored_by_id[identifier][field] == expected, ('reconstructed', identifier, field)
            cells_checked += 1
            revised_cells += field + '_REVISED' in raw and raw[field] != expected

    mapping = json.loads((ROOT / '.private/participant_ids.json').read_text())
    eval_by_id = {row['annotation_id']: row for row in evaluations}
    assert len(evaluations) == len(eval_by_id) == 1750
    all_worker_ids = set()
    numeric_comparisons = familiarity_comparisons = id_comparisons = joined_comparisons = 0
    zero_ratings = missing_familiarity = failed_attention = exact_duplicates = 0
    conditions = {}
    ratings = ['simplicity', 'coherent', 'informative', 'background', 'factual']
    for stem, (condition, summary_field) in CONDITIONS.items():
        path = ROOT / 'result_with_workerID' / (stem + '_result_output.csv')
        fields, rows = read_csv(path)
        seen = Counter()
        for position, raw in enumerate(rows, 1):
            identifier = f'{condition}_{position:04d}'
            restored = eval_by_id[identifier]
            assert restored['condition'] == condition
            all_worker_ids.add(raw['WorkerId'])
            assert restored['participant_id'] == mapping[raw['WorkerId']]
            id_comparisons += 1
            for field in fields:
                if field not in ['WorkerId', 'familiarity']:
                    assert Decimal(raw[field]) == Decimal(restored[field]), (identifier, field)
                    numeric_comparisons += 1
            assert restored['familiarity'] == raw['familiarity'].strip()
            familiarity_comparisons += 1
            item = canon_by_id[raw['index']]
            for field, expected in [('abs_text', item['abs_text']), ('pls_text', item['pls_text']),
                                    ('summary_text', item[summary_field])]:
                assert restored[field] == expected, (identifier, field)
                joined_comparisons += 1
            signature = tuple(raw[field] for field in fields)
            expected_duplicate = seen[signature] > 0
            assert restored['is_duplicate_row'].lower() == str(expected_duplicate).lower()
            exact_duplicates += expected_duplicate
            seen[signature] += 1
            expected_zero = any(Decimal(raw[field]) == 0 for field in ratings)
            assert restored['has_zero_rating'].lower() == str(expected_zero).lower()
            zero_ratings += expected_zero
            missing_familiarity += not raw['familiarity'].strip()
            failed_attention += Decimal(raw['ATTENTION_QUESTION']) == 0
        conditions[condition] = {'original_rows': len(rows), 'reconstructed_rows': sum(
            row['condition'] == condition for row in evaluations)}
        assert conditions[condition]['original_rows'] == conditions[condition]['reconstructed_rows']
    manifest = json.loads((ROOT / 'huggingface/data/manifest.json').read_text())
    for source in manifest['sources']:
        assert hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256']
    report = {
        'result': 'all comparisons passed',
        'items': len(reconstructed), 'item_columns': len(public_fields),
        'exact_item_cells': cells_checked,
        'evaluations': len(evaluations), 'exact_numeric_evaluation_cells': numeric_comparisons,
        'familiarity_values_preserved': familiarity_comparisons,
        'participant_mapping_checks': id_comparisons,
        'joined_source_and_summary_checks': joined_comparisons,
        'participants': len(all_worker_ids), 'source_files_hash_verified': len(manifest['sources']),
        'conditions': conditions,
        'preserved_quality_issues': {'extra_exact_duplicate_rows': exact_duplicates,
                                    'rows_with_zero_rating': zero_ratings,
                                    'blank_familiarity_rows': missing_familiarity,
                                    'failed_attention_rows': failed_attention},
        'intentional_differences': {
            'original_question_file_columns': len(original_fields),
            'canonical_working_columns': len(canonical_fields),
            'reconstructed_item_columns': len(public_fields),
            'superseded_duplicate_columns_removed': sum(field.endswith('_REVISED') for field in original_fields),
            'canonical_values_changed_by_selecting_revised_fields': revised_cells,
            'internal_revision_note_columns_excluded': notes,
            'source_worker_ids_replaced': True,
            'numeric_serialization_normalized': True,
            'derived_and_provenance_fields_added': True,
            'evaluation_rows_filtered': 0,
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
