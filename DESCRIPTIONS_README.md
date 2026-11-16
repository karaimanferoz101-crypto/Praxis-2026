# Candidate diagnosis descriptions

The retrieval models rank 388 candidate diagnoses by comparing a case against a short text description of each one. This folder holds those descriptions and the record of where every one came from.

## Files

| File | What it is |
|---|---|
| candidate_descriptions.json | 388 entries, {"diagnosis label": "description text"}. This is the file the notebooks load. |
| candidate_descriptions_provenance.json | 388 entries, one record per label: source dataset, version, licence, download URL, download date, matched term identifier, matched term name, match tier, source reference, whether the text was modified, whether it was truncated, and any other label sharing the same text. |
| AppendixA_descriptions.csv | The same information as one flat table, for reading. This is the full listing that Appendix A of the praxis points to. |

## Sources

All 388 descriptions are taken verbatim from five versioned public datasets. No description is generated, paraphrased or edited. All files were downloaded on 15 November 2026.

| Source | Labels | Version | Licence |
|---|---|---|---|
| Mondo Disease Ontology | 206 | releases/2026-11-03 | CC BY 4.0 |
| MedlinePlus Health Topic XML | 119 | file generated 13 November 2026 | Public domain, U.S. National Library of Medicine |
| NCI Thesaurus, OBO Edition | 35 | releases/2024-05-07, EVS 24.04e | CC BY 4.0 |
| Human Phenotype Ontology | 17 | hp/releases/2026-09-01 | HPO licence |
| Human Disease Ontology | 11 | doid/releases/2026-10-29 | CC0 1.0 |

Health information in this corpus is from MedlinePlus.gov.

## How a label was matched to a description

Each label was matched to a source record by exact name, then exact synonym, then a morphological variant, then an order-insensitive token set, giving 337 direct matches; the remaining 51 use the nearest broader term from the same dataset, recorded as `broader_term`, and approximate string matches were rejected after review because they produced medically invalid pairings. Two mechanical rules were applied uniformly: MedlinePlus summaries were truncated to their leading 150 words at the last complete sentence, affecting 98 descriptions, and 49 labels share a description with another label, which is safe because candidate text is built as the label followed by the description.

## Reproducing this

The five source files are downloadable at the URLs in the provenance records. Matching was performed once, on 15 November 2026, against the versions named above. Later releases of these datasets will not reproduce this file exactly.
