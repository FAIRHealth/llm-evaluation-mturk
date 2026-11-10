import copy
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reconstruct', ROOT / 'huggingface/reconstruct.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        if not all((ROOT / 'huggingface/data' / name).exists() for name in ['items.jsonl', 'sources.jsonl']):
            self.skipTest('Release integration checks require the public dataset files in huggingface/data/')
        self.items = module.load_jsonl(ROOT / 'huggingface/data/items.jsonl')
        self.sources = module.load_jsonl(ROOT / 'huggingface/data/sources.jsonl')
        self.archive = ROOT / '.private/source_audit/CELLS_metadata.zip'

    def test_public_policy_and_attribution(self):
        audit = {row['index']: row for row in self.sources}
        self.assertEqual(50, len(audit))
        self.assertEqual(29, sum(row['source_text_status'] == 'included' for row in self.items))
        for row in self.items:
            source = audit[row['index']]
            self.assertTrue(source['doi'] and source['title'] and source['cells_id'])
            if source['source_text_status'] == 'metadata_only':
                self.assertIsNone(row['abs_text'])
                self.assertIsNone(row['pls_text'])
            else:
                self.assertEqual(source['abs_sha256'], module.sha256(row['abs_text']))
                self.assertEqual(source['pls_sha256'], module.sha256(row['pls_text']))
                self.assertTrue(source['source_license_url'])

    def test_unavailable_text_stays_unresolved(self):
        rows, report = module.reconstruct(self.items, self.sources, 'none', Path('/unused'))
        self.assertEqual(21, sum(not row['complete'] for row in report))
        self.assertEqual(21, sum(row['abs_text'] is None for row in rows))

    def test_released_text_tampering_is_rejected(self):
        items = copy.deepcopy(self.items)
        next(row for row in items if row['abs_text'] is not None)['abs_text'] += ' changed'
        with self.assertRaisesRegex(ValueError, 'Released source text changed'):
            module.reconstruct(items, self.sources, 'none', Path('/unused'))

    def test_publisher_version_drift_is_not_silently_accepted(self):
        missing = next(row for row in self.items if row['abs_text'] is None)
        source = next(row for row in self.sources if row['index'] == missing['index'])
        with patch.object(module, 'from_doi', return_value={'abs_text': 'updated abstract', 'pls_text': 'updated summary'}):
            rows, report = module.reconstruct([missing], [source], 'doi', Path('/unused'))
        self.assertIsNone(rows[0]['abs_text'])
        self.assertFalse(report[0]['complete'])
        self.assertFalse(report[0]['exact_match'])

    def test_corrupted_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / 'incorrect.zip'
            archive.write_bytes(b'not the reviewed archive')
            with self.assertRaisesRegex(ValueError, 'checksum'):
                module.from_cells(archive, self.sources)

    def test_pinned_snapshot_reconstructs_original_values(self):
        original_path = ROOT / 'results_llama_mcq_attention_baseline.csv'
        if not self.archive.exists() or not original_path.exists():
            self.skipTest('Exact maintainer comparison requires the local upstream archive and original CSV')
        rows, report = module.reconstruct(self.items, self.sources, 'cells', Path('/unused'), self.archive)
        self.assertEqual(50, sum(row['complete'] and row['exact_match'] for row in report))
        with original_path.open(newline='', encoding='utf-8') as stream:
            original = {int(row['index']): row for row in csv.DictReader(stream)}
        for row in rows:
            for field in ['abs_text', 'pls_text']:
                self.assertEqual(original[row['index']][field], row[field])

    def test_supplied_authorized_texts_need_no_network(self):
        if not self.archive.exists():
            self.skipTest('Optional upstream archive is not cached locally')
        exact = module.from_cells(self.archive, self.sources)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'authorized.csv'
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.DictWriter(stream, fieldnames=['index', 'abs_text', 'pls_text'])
                writer.writeheader()
                writer.writerows(dict(index=index, **row) for index, row in exact.items())
            with patch.object(module, 'request', side_effect=AssertionError('Network must not be used')):
                _, report = module.reconstruct(self.items, self.sources, 'cells', Path(folder), authorized_texts=path)
        self.assertEqual(50, sum(row['complete'] for row in report))
        self.assertEqual(21, sum(row['method'] == 'authorized_csv' for row in report))


if __name__ == '__main__':
    unittest.main()
