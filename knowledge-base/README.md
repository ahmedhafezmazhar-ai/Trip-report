# Mazhar App knowledge base

Raw material collected from websites, kept word for word and organized so it can later be turned into an app.

## How it is organized

```
knowledge-base/
├── README.md        ← this file: conventions + list of every source
├── TOPICS.md        ← cross-source index: each topic → every file (from any source) that covers it
├── taxonomy.json    ← families → branches → pages tree over everything (built by _tools/taxonomy.py)
├── visual/          ← animated map of taxonomy.json (also published as an artifact)
└── sources/
    └── <site>/                 one folder per website
        └── <page-slug>/        one folder per page or article
            ├── README.md       source card (URLs, revision, fetch date, license) + file list
            ├── manifest.json   same, machine-readable (files, categories, tags)
            ├── 00-overview.md
            ├── <section>/NN-<topic>.md   one file per topic, in page order
            ├── references.md, media.md, related-pages.md
            ├── full-page.md    the whole page in one file
            └── raw/            untouched originals (HTML, wikitext)
```

## Conventions for every source

- Text is kept verbatim. No summarizing. Any structural change (links made absolute, icons dropped) is stated in the file's `fidelity` field.
- Every Markdown file opens with front matter: `source_url` (with section anchor), `fetched` date, `revision_id` or last-edited date when the site gives one, `license`, `category`, `tags`.
- Untouched originals go in `raw/` so anything can be re-processed later.
- After adding a source: add a row below, and add its files under the matching topics in `TOPICS.md` (create a new topic heading if none fits).

## Sources

| # | Site | Page | Fetched | Folder |
|---|---|---|---|---|
| 1 | PsychonautWiki | Responsible drug use (requested as "Harm reduction practices") | 2026-11-25 | [sources/psychonautwiki/responsible-drug-use/](sources/psychonautwiki/responsible-drug-use/README.md) |
| 2 | PsychonautWiki | Full-site export, 3,338 pages as JSON (Hany's psychonautwiki_db.zip) | 2026-11-25 | [sources/psychonautwiki/site-export/](sources/psychonautwiki/site-export/README.md) |

## Families (taxonomy.json)

Ten families: Shulgin books (TiHKAL, Shulgin Index; split into also-on-PsychonautWiki and book-only), Substances (by psychoactive class, then chemical class), Subjective effects (by sense, then type), Harm reduction & safety, Substance classes, Plants & fungi, Preparation, Pharmacology & science, Psychonautics, Reference & other. Every page sits in exactly one branch and links to its source file and original URL. Animated map: https://claude.ai/artifact/SPgL6s1bXEUb3antygXsoo
| 3 | Book | TiHKAL: La continuación (Spanish ed.), 55 tryptamine entries + full text. Copyrighted | 2026-11-25 | [sources/books/tihkal-es/](sources/books/tihkal-es/README.md) |
| 4 | Book | The Shulgin Index Vol. 1, 126 phenethylamine entries + full text (OCR). Copyrighted | 2026-11-25 | [sources/books/shulgin-index-vol1/](sources/books/shulgin-index-vol1/README.md) |

Rights: PsychonautWiki is CC BY-SA 4.0. The two books are copyrighted; every book record has a `rights` field. Wiki substances that a book also covers carry a `books` list in taxonomy.json.
