# Books

Two books uploaded by Hany on 2026-11-25. Both are **copyrighted** (not CC BY-SA like PsychonautWiki). Every record carries a `rights` note so the app design can decide what may be shown. They are stored here for private research.

| Folder | Book | Language | Compound entries |
|---|---|---|---|
| [tihkal-es/](tihkal-es/README.md) | TiHKAL: La continuación (Shulgin & Shulgin, 1997; Spanish translation by Proyecto Shulgin en Español, 2015) | Spanish | 55 tryptamines |
| [shulgin-index-vol1/](shulgin-index-vol1/README.md) | The Shulgin Index Vol. 1: Psychedelic Phenethylamines and Related Compounds (Shulgin, Manning, Daley; Transform Press 2011) | English (OCR scan) | 126 phenethylamines |

## Layout (same for both books)

- `raw/`: the uploaded text file, byte for byte.
- `sections/`: the whole book split into Markdown files by chapter or section, verbatim, each with its line range. The sections and compound entries together cover every line of the file exactly once (checked: no lines missing, none overlapping).
- `compounds/NNN-<name>.json`: one record per compound entry, and `compounds.jsonl` with all of them.
- `comparison-with-psychonautwiki.json` (in this folder): every matched compound, with the book's dose and duration next to PsychonautWiki's oral data.

## Matching to PsychonautWiki

- TiHKAL: 26 of 55 entries match a PsychonautWiki page (by code name, English name, or the book's own synonym index).
- Shulgin Index: 30 of 126 entries match.
- The rest are compounds PsychonautWiki doesn't cover, mostly obscure research compounds.

Comparison results: TiHKAL {'consistent': 16, 'no PsychonautWiki oral data': 5, 'book gives no comparable oral dose or duration': 3, 'differs': 1}; Shulgin Index {'consistent': 20, 'book gives no comparable oral dose or duration': 8, 'differs': 1, 'no PsychonautWiki oral data': 1}.

"Consistent" means the book's dose range overlaps PsychonautWiki's common oral dose and the durations overlap. Only the first dose figure in a book statement is parsed, so the verbatim statement is always kept next to it.

Clear differences:
- **5-MeO-MIPT** (TiHKAL (Spanish ed.)): book says `4 – 6 mg, vía oral. 12 – 20 mg, fumado / 4 – 6 horas`; PsychonautWiki oral common dose 7 - 15 mg, duration 5 - 8 hours. book dose range does not overlap PsychonautWiki's common oral dose.
- **2C-T-2** (Shulgin Index Vol. 1): book says `2C-T-2 is orally active in humans at 8-20 mg; duration 12-18 hours (Shulgin and Shulgin, 1 991).`; PsychonautWiki oral common dose 10 - 20 mg, duration 6 - 10 hours. book duration does not overlap PsychonautWiki's oral duration.
