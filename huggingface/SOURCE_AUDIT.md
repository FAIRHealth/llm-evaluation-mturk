# Audit of the 50 source papers

Audit date: November 9, 2026. [Article-by-article decisions](SOURCE_LICENSES.csv). Machine-readable records are in `data/sources.jsonl`.

## Matching and bibliographic evidence

All 50 abstract/human-summary pairs were matched to the original [CELLS metadata archive](https://github.com/LinguisticAnomalies/pls_retrieval/blob/a54b1ae8c2a7c2d7d14365df2b84584348e9e6ba/data/CELLS_metadata.zip). The archive revision is pinned to `a54b1ae8c2a7c2d7d14365df2b84584348e9e6ba`; its checksum is recorded per source. Both source strings match the working study CSV byte-for-byte.

Every item has a metadata CSV member and 1-based data-row locator. Some article pairs also appear in another CELLS split; the frozen manifest records the selected exact location. Study `index` values are preserved but are not asserted to be universal CELLS identifiers.

Titles were resolved through the [Europe PMC API](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1073/pnas.1912409116&format=json&resultType=core), choosing the published MED record. HTML typography is ignored when comparing titles. DOI records were checked through [Crossref's publisher-deposited metadata API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/). Every manifest row includes its actual evidence URLs.

The Cochrane item had a blank title in CELLS. Its content was matched to the review and [official Cochrane evidence page](https://www.cochrane.org/evidence/CD008991_can-inserting-cervical-stitch-prevent-early-births-single-babies), resolving DOI `10.1002/14651858.CD008991.pub3`. Its source record is metadata-only in this release. The review was amended after the corpus snapshot, so present-day publisher text is not assumed to reproduce the evaluated strings.

## Licensing decisions

| Source group | Papers | Decision |
| --- | ---: | --- |
| PLOS, CC BY | 25 | Retain original strings and article attribution |
| PLOS, public-domain dedication | 1 | Retain; preserve the primary record's CC0/public-domain description |
| PNAS, explicit CC BY-NC-ND 4.0 | 3 | Retain verbatim with source-specific restrictions |
| PNAS, redistribution permission not established | 20 | Omit source strings; preserve DOI/title/CELLS locator |
| Cochrane, redistribution permission not established | 1 | Omit source strings; preserve DOI/title/CELLS locator |

Open article XML permissions were inspected where available, with XML and permission-section hashes recorded. Per-paper Europe PMC license fields and Crossref license deposits support the explicit license decisions. The three CC BY-NC-ND articles have DOI, attribution, original terms, and unchanged string hashes in the manifest. They are not relicensed as CC BY.

For the 21 metadata-only items, no article-specific redistribution permission was established. This is an omission decision under uncertainty, not a legal conclusion that every use is prohibited. A license URL for a publisher's general terms, free reading access, or the corpus code's MIT notice is not counted as a CC license for the article.

The [PLOS reuse policy](https://journals.plos.org/plosone/s/licenses-and-copyright) permits attributed reuse under its stated open licenses. [PNAS licensing guidance](https://www.pnas.org/author-center/publication-charges) distinguishes free access, Creative Commons options, and older standard-license terms. The per-paper records, rather than publisher name alone, determine inclusion.

## Reconstruction and release history

The tested reconstruction script retrieves the pinned public CELLS archive and verifies all 50 source pairs before merging with generated material and evaluations. Direct DOI retrieval is optional and cannot guarantee exact historical text. Retrieval does not expand redistribution rights.

The earlier private draft contained all source strings. It must remain private as an archive. The public release is created with a clean history at the original dataset name so previously omitted text is not exposed through an older commit.
