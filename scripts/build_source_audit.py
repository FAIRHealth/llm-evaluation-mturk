#!/usr/bin/env python3
"""Freeze the reviewed 50-paper audit from locally cached primary-source records.

The private audit cache contains the pinned CELLS archive and per-paper Europe
PMC/Crossref records. This script exports metadata and decisions, never article
abstracts, summaries, or participant identifiers.
"""
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / '.private/source_audit'
REVISION = 'a54b1ae8c2a7c2d7d14365df2b84584348e9e6ba'
ARCHIVE_URL = f'https://raw.githubusercontent.com/LinguisticAnomalies/pls_retrieval/{REVISION}/data/CELLS_metadata.zip'
LICENSES = {
    'cc by': ('cc-by-4.0', 'https://creativecommons.org/licenses/by/4.0/'),
    'cc by-nc-nd': ('cc-by-nc-nd-4.0', 'https://creativecommons.org/licenses/by-nc-nd/4.0/'),
    'cc0': ('cc0-1.0', 'https://creativecommons.org/publicdomain/zero/1.0/'),
}


def build():
    matches = json.loads((AUDIT / 'matches.json').read_text())
    canonical = {int(r['index']): r for r in csv.DictReader(
        (ROOT / 'results_llama_mcq_attention_baseline.csv').open(encoding='utf-8'))}
    archive_sha = hashlib.sha256((AUDIT / 'CELLS_metadata.zip').read_bytes()).hexdigest()
    sources = []
    for match in matches:
        evidence = json.loads((AUDIT / f"result_{match['index']}.json").read_text())
        article = evidence['europepmc']
        crossref = evidence.get('crossref', {})
        doi = article['doi'].lower()
        assert crossref.get('DOI', doi).lower() == doi
        label = article.get('license', '')
        license_id, license_url = LICENSES.get(label, ('not-established', ''))
        keep = label in LICENSES
        if not keep:
            reason = 'No article-specific permission for redistribution established; public reading access is insufficient.'
        elif license_id == 'cc-by-nc-nd-4.0':
            reason = 'Retained verbatim under original CC BY-NC-ND 4.0 terms: noncommercial redistribution only; no adapted source text.'
        elif license_id == 'cc0-1.0':
            reason = 'Primary source records identify a public-domain dedication.'
        else:
            reason = 'Primary source records identify CC BY 4.0; retain attribution and license link.'
        permissions = ''
        copyright_notice = ''
        xml_file = AUDIT / (article['pmcid'] + '.xml')
        if xml_file.exists():
            node = ET.parse(xml_file).getroot().find('./front/article-meta/permissions')
            if node is not None:
                permissions = ET.tostring(node, encoding='unicode')
                copyright_notice = ' '.join(''.join(e.itertext()) for e in node.findall('copyright-statement')).strip()
        record = {
            'index': match['index'],
            'cells_id': f"CELLS@{REVISION}:{match['cells_metadata_file']}:{match['cells_row_1based']}",
            'title': match['title'], 'doi': doi,
            'authors': article.get('authorString', ''),
            'journal': article.get('journalInfo', {}).get('journal', {}).get('title', match['journal']),
            'year': article.get('pubYear', ''),
            'article_url': 'https://doi.org/' + doi,
            'pmid': article.get('id', ''), 'pmcid': article['pmcid'],
            'source_license': license_id, 'source_license_url': license_url,
            'copyright_notice': copyright_notice,
            'source_text_status': 'included' if keep else 'metadata_only',
            'decision_reason': reason,
            'evidence_url': evidence['europepmc_query_url'],
            'crossref_url': evidence.get('crossref_url', ''),
            'crossref_license_urls': [x['URL'] for x in crossref.get('license', [])],
            'xml_evidence_url': f"https://www.ebi.ac.uk/europepmc/webservices/rest/{article['pmcid']}/fullTextXML" if xml_file.exists() else '',
            'xml_evidence_sha256': hashlib.sha256(xml_file.read_bytes()).hexdigest() if xml_file.exists() else '',
            'permissions_sha256': hashlib.sha256(permissions.encode()).hexdigest() if permissions else '',
            'checked_date': '2026-11-09',
            'cells_repository': 'https://github.com/LinguisticAnomalies/pls_retrieval',
            'cells_revision': REVISION, 'cells_archive_url': ARCHIVE_URL,
            'cells_archive_sha256': archive_sha,
            'cells_metadata_file': match['cells_metadata_file'],
            'cells_row_1based': match['cells_row_1based'],
            'abs_sha256': match['abs_sha256'], 'pls_sha256': match['pls_sha256'],
        }
        for field in ('abs_text', 'pls_text'):
            assert hashlib.sha256(canonical[match['index']][field].encode()).hexdigest() == record[
                'abs_sha256' if field == 'abs_text' else 'pls_sha256']
        sources.append(record)
    assert len(sources) == 50 and len({r['index'] for r in sources}) == 50
    data = ROOT / 'huggingface/data'
    (data / 'sources.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in sources))
    columns = ['index', 'doi', 'title', 'authors', 'journal', 'year', 'cells_id',
               'source_license', 'source_license_url', 'copyright_notice', 'source_text_status', 'decision_reason',
               'evidence_url', 'crossref_url', 'xml_evidence_url', 'checked_date']
    with (ROOT / 'huggingface/SOURCE_LICENSES.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(sources)
    print(dict(Counter(r['source_text_status'] for r in sources)))
    print(dict(Counter(r['source_license'] for r in sources)))


if __name__ == '__main__':
    build()
