#!/usr/bin/env python3
"""Reconstruct the original 50 item records and join the 1,750 evaluations.

Python 3.9+, standard library only. No model inference, scraping of paywalls,
cookies, or credentials is used. The default downloads the pinned public CELLS
metadata archive to recover exact evaluated strings, verified with SHA-256.
Retrieving source text does not grant rights to redistribute reconstructed files.

Code: MIT; see CODE_LICENSE.txt. Article text retains its original source terms.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

DEFAULT_REPO = 'Guo-medicalAI/llm-evaluation-mturk'
CONDITION_FIELDS = {
    'human': 'pls_text', 'baseline': 'baseline',
    'informativeness': 'Informativeness', 'simplification': 'Simplification',
    'coherence': 'Coherence', 'faithfulness': 'Faithfulness',
    'all': 'Informativeness_Simplification_Coherence_Faithfulness',
}
UA = 'GuoMedicalAI-PLS-reconstruction/1.0 (+https://huggingface.co/Guo-medicalAI)'


def sha256(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def request(url, timeout=30):
    headers = {'User-Agent': UA}
    # A token is optional for an authorized private copy; never sent upstream.
    if urllib.parse.urlparse(url).hostname == 'huggingface.co' and os.getenv('HF_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['HF_TOKEN']
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout)


def download(url, destination, expected_hash=None):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        if expected_hash is None or digest == expected_hash:
            return destination
        raise ValueError(f'Cached file checksum mismatch: {destination}. Remove it and retry.')
    temporary = destination.with_suffix(destination.suffix + '.part')
    for attempt in range(3):
        try:
            with request(url) as response, temporary.open('wb') as target:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    target.write(chunk)
            digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
            if expected_hash is not None and digest != expected_hash:
                raise ValueError(f'Download checksum mismatch for {url}')
            temporary.replace(destination)
            return destination
        except (urllib.error.URLError, TimeoutError, OSError):
            if temporary.exists():
                temporary.unlink()
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def load_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


def read_bundle(data_dir, repo_id, revision, cache):
    if data_dir is None:
        adjacent = Path(__file__).resolve().parent / 'data'
        if (adjacent / 'manifest.json').exists():
            data_dir = adjacent
        else:
            data_dir = cache / 'release' / sha256(repo_id + '@' + revision)[:16]
            base = f'https://huggingface.co/datasets/{repo_id}/resolve/{urllib.parse.quote(revision, safe="")}/data/'
            # Validate every file against a single release manifest.
            download(base + 'manifest.json', data_dir / 'manifest.json')
            manifest = json.loads((data_dir / 'manifest.json').read_text())
            for name in ['items.jsonl', 'sources.jsonl', 'annotations.jsonl']:
                download(base + name, data_dir / name, manifest['outputs'][name]['sha256'])
    data_dir = Path(data_dir)
    manifest = json.loads((data_dir / 'manifest.json').read_text())
    for name in ['items.jsonl', 'sources.jsonl', 'annotations.jsonl']:
        if hashlib.sha256((data_dir / name).read_bytes()).hexdigest() != manifest['outputs'][name]['sha256']:
            raise ValueError(f'Release file checksum mismatch: {name}')
    return (load_jsonl(data_dir / 'items.jsonl'), load_jsonl(data_dir / 'sources.jsonl'),
            load_jsonl(data_dir / 'annotations.jsonl'), manifest)


def from_cells(archive, sources):
    """Use pinned member/row plus exact hashes, not a guessed original index."""
    expected = {source['cells_archive_sha256'] for source in sources}
    if len(expected) != 1 or hashlib.sha256(Path(archive).read_bytes()).hexdigest() not in expected:
        raise ValueError('CELLS archive does not match the audited revision and checksum')
    result = {}
    with zipfile.ZipFile(archive) as zipped:
        members = {source['cells_metadata_file'] for source in sources}
        tables = {}
        for member in members:
            # Read only named CSV members; do not extract arbitrary archive paths.
            with zipped.open(member) as stream:
                tables[member] = list(csv.DictReader(io.TextIOWrapper(stream, encoding='utf-8-sig')))
        for source in sources:
            row = tables[source['cells_metadata_file']][source['cells_row_1based'] - 1]
            values = {field: row[field] for field in ('abs_text', 'pls_text')}
            for field, hash_field in [('abs_text', 'abs_sha256'), ('pls_text', 'pls_sha256')]:
                if sha256(values[field]) != source[hash_field]:
                    raise ValueError(f"CELLS row/hash mismatch for item {source['index']}, {field}")
            result[source['index']] = values
    return result


def xml_text(node):
    """Extract readable text, omitting the section heading only."""
    if node is None:
        return None
    pieces = []
    if node.text:
        pieces.append(node.text)
    for child in node:
        if child.tag.rsplit('}', 1)[-1] != 'title':
            pieces.extend(child.itertext())
        if child.tail:
            pieces.append(child.tail)
    return re.sub(r'\s+', ' ', ' '.join(pieces)).strip()


def from_doi(source, cache):
    """Try the official Europe PMC record resolved from the paper's DOI.

    No open XML or no summary -> explicit failure. A DOI alone cannot promise
    access, a lay summary, or the exact historical wording/formatting.
    """
    query = urllib.parse.urlencode({'query': 'DOI:' + source['doi'], 'format': 'json',
                                   'resultType': 'core', 'pageSize': 5})
    with request('https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + query) as response:
        records = json.load(response).get('resultList', {}).get('result', [])
    published = [row for row in records if row.get('source') == 'MED'
                 and row.get('doi', '').lower() == source['doi'].lower()]
    if len(published) != 1 or not published[0].get('pmcid'):
        raise ValueError('DOI did not resolve to one published full-text record')
    pmcid = published[0]['pmcid']
    xml_url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML'
    xml_path = download(xml_url, cache / 'publisher' / (pmcid + '.xml'))
    root = ET.parse(xml_path).getroot()
    meta = root.find('./front/article-meta')
    if meta is None:
        raise ValueError('Article metadata unavailable in XML')
    abstract = summary = None
    for element in meta.findall('abstract'):
        kind = element.get('abstract-type', '')
        if kind in ('summary', 'synopsis', 'executive-summary', 'plain-language-summary'):
            summary = xml_text(element)
        elif not kind:
            abstract = xml_text(element)
    if not abstract or not summary:
        raise ValueError('Publisher record lacks an abstract or lay summary')
    return {'abs_text': abstract, 'pls_text': summary}


def reconstruct(items, sources, source_mode, cache, cells_archive=None, allow_text_drift=False,
                authorized_texts=None):
    sources_by_id = {row['index']: row for row in sources}
    if len(sources_by_id) != len(sources) or set(sources_by_id) != {row['index'] for row in items}:
        raise ValueError('Item/source keys are not a unique complete match')
    required = [sources_by_id[row['index']] for row in items
                if any(row.get(field) is None for field in ('abs_text', 'pls_text'))]
    recovered, backend_error = {}, ''
    if authorized_texts:
        with Path(authorized_texts).open(encoding='utf-8-sig', newline='') as stream:
            for row in csv.DictReader(stream):
                index = int(row['index'])
                if index in recovered:
                    raise ValueError('Duplicate index in supplied text CSV')
                recovered[index] = {field: row[field] for field in ('abs_text', 'pls_text')}
    provided_ids = set(recovered)
    missing_sources = [row for row in required if row['index'] not in recovered]
    if source_mode == 'cells' and missing_sources:
        if cells_archive is None:
            source = required[0]
            cells_archive = download(source['cells_archive_url'], cache / 'CELLS_metadata.zip',
                                     source['cells_archive_sha256'])
        recovered.update(from_cells(cells_archive, missing_sources))
    completed, report = [], []
    for item in items:
        row = dict(item)
        source = sources_by_id[row['index']]
        entry = {'index': row['index'], 'doi': source['doi'], 'method': 'included_in_release',
                 'exact_match': True, 'error': ''}
        missing = [field for field in ('abs_text', 'pls_text') if row.get(field) is None]
        candidate = recovered.get(row['index'])
        if missing and candidate is not None:
            entry['method'] = 'authorized_csv' if row['index'] in provided_ids else 'pinned_cells'
        if missing and candidate is None and source_mode == 'doi':
            try:
                candidate = from_doi(source, cache)
                entry['method'] = 'doi_europepmc'
            except Exception as error:
                entry['error'] = str(error)
        if missing and candidate is None:
            entry['method'] = 'unresolved'
            entry['error'] = entry['error'] or backend_error or 'Source text was omitted and no retrieval source was selected'
        for field, hash_field in [('abs_text', 'abs_sha256'), ('pls_text', 'pls_sha256')]:
            value = row.get(field)
            if value is None and candidate is not None:
                value = candidate.get(field)
                if value is not None:
                    exact = sha256(value) == source[hash_field]
                    if exact or allow_text_drift:
                        row[field] = value
                    if not exact:
                        entry['exact_match'] = False
                        entry['error'] = 'Retrieved text differs from the evaluated text; use pinned CELLS for exact reproduction'
            elif value is not None and sha256(value) != source[hash_field]:
                raise ValueError(f"Released source text changed for item {row['index']}, {field}")
        entry['missing_fields'] = [field for field in ('abs_text', 'pls_text') if row.get(field) is None]
        entry['complete'] = not entry['missing_fields']
        completed.append(row)
        report.append(entry)
    return completed, report


def write_csv(path, rows, columns):
    with Path(path).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--data-dir', type=Path, help='Local release data folder; otherwise download from the Hub')
    parser.add_argument('--repo-id', default=DEFAULT_REPO)
    parser.add_argument('--revision', default='main', help='Pin a Hub commit for a reproducible release')
    parser.add_argument('--source', choices=['cells', 'doi', 'none'], default='cells')
    parser.add_argument('--cells-archive', type=Path, help='Existing audited CELLS_metadata.zip for offline use')
    parser.add_argument('--authorized-texts', type=Path, help='Optional local CSV with index,abs_text,pls_text')
    parser.add_argument('--allow-text-drift', action='store_true', help='Explicitly accept current text differing from historical hashes')
    parser.add_argument('--output-dir', type=Path, default=Path('reconstructed'))
    parser.add_argument('--cache-dir', type=Path, help='Defaults to output-dir/.cache')
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cache = args.cache_dir or args.output_dir / '.cache'
    try:
        items, sources, annotations, manifest = read_bundle(args.data_dir, args.repo_id, args.revision, cache)
        complete, details = reconstruct(items, sources, args.source, cache, args.cells_archive,
                                        args.allow_text_drift, args.authorized_texts)
        write_csv(args.output_dir / 'items_complete.csv', complete, manifest['original_item_columns'])
        (args.output_dir / 'items_complete.jsonl').write_text(
            ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in complete), encoding='utf-8')
        by_id = {row['index']: row for row in complete}
        joined = []
        for annotation in annotations:
            item = by_id[annotation['index']]
            joined.append(dict(annotation, abs_text=item['abs_text'], pls_text=item['pls_text'],
                               summary_text=item[CONDITION_FIELDS[annotation['condition']]],
                               title=item['title'], doi=item['doi'], cells_id=item['cells_id']))
        write_csv(args.output_dir / 'evaluations_complete.csv', joined, list(joined[0]))
        report = {'items': len(complete), 'evaluations': len(joined), 'source': args.source,
                  'complete_items': sum(row['complete'] for row in details),
                  'exact_items': sum(row['complete'] and row['exact_match'] for row in details),
                  'details': details,
                  'notice': 'Local reconstruction is not licensed as a whole under CC BY. Original source rights still apply.'}
        (args.output_dir / 'reconstruction_report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(f"Reconstructed {report['complete_items']}/{len(complete)} items; "
              f"{report['exact_items']} exact matches; joined {len(joined)} evaluations.")
        print(f'Files saved to {args.output_dir.resolve()}')
        return 0 if report['complete_items'] == len(complete) else 2
    except Exception as error:
        print(f'Reconstruction failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
