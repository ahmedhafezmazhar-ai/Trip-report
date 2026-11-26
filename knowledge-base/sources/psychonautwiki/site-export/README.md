# Source: PsychonautWiki full-site export (SQLite)

| Field | Value |
|---|---|
| Site | PsychonautWiki (psychonautwiki.org) |
| What | `psychonautwiki_db.zip` uploaded by Hany, containing `psychonautwiki.db` (SQLite, 21 MB, file dated 2026-11-25) |
| Imported | 2026-11-25 |
| Page edit dates | 2014-02-23 to 2026-11-24 |
| License | CC BY-SA 4.0 (credit PsychonautWiki; share derivatives alike) |
| Fidelity | Nothing summarized or dropped. Every row of all three database tables is in the JSON. Checked: 3,338/3,338 articles identical field by field, 4,691 category links, 26,380 substance box values. The original zip is kept in `raw/`. |

## What the database contained

- **articles** (3,338 rows): page id, title, URL, last-edited time, full wikitext, plain text, and which substance box template the page uses. 1,882 of them are redirects (alternate names), leaving 1,456 real pages.
- **article_categories** (4,691 rows, 335 distinct categories).
- **substance_params** (26,380 rows): the substance infobox data for 391 templates. Names, chemical and psychoactive class, and for each route of administration: bioavailability, dosage tiers (threshold, light, common, strong, heavy, sometimes microdose) and timeline (total duration, onset, come-up, peak, offset, after-effects). Each value is stored raw (wiki markup) and clean.

## Files

| Path | What it holds |
|---|---|
| `articles.jsonl` | **Master copy**: one JSON record per line for all 3,338 rows, including redirects |
| `by-type/<type>/<Title>.json` | The 1,456 real pages, one JSON file each, sorted into the folders below |
| `substances.json` | Quick table of all 339 substances: names, aliases, classes, and only the routes of administration that are switched on, with dosage and duration |
| `substance-boxes.json` | All 391 infobox templates with every parameter (raw and clean), the structured version, and which articles use each one |
| `index.json` | Every page: id, title, type, categories, URL, last edited, file path, aliases, summary page |
| `redirects.json` | 1,882 alternate names mapped to the article they point to (e.g. street names and misspellings) |
| `categories.json` | Each of the 335 categories with the titles in it |
| `raw/psychonautwiki_db.zip` | The original upload, untouched |

| Folder | Pages | Contents |
|---|---|---|
| `by-type/substance/` | 339 | Substance articles (339; 328 with a dosage/duration box) |
| `by-type/substance-summary/` | 361 | Short /Summary subpages for substances (mostly links to further reading) |
| `by-type/effect/` | 250 | Subjective effect articles (visual, cognitive, physical, etc.) |
| `by-type/responsible-use/` | 51 | Harm reduction, tripsitting, psychological first aid, antidotes, bad trips, serotonin syndrome |
| `by-type/substance-class/` | 41 | Chemical and psychoactive class pages (e.g. Tryptamines, Psychedelics) |
| `by-type/preparation/` | 40 | Extraction, cultivation, recipes, synthesis |
| `by-type/plants-and-fungi/` | 70 | Plants, mushrooms, genera and families |
| `by-type/pharmacology-and-science/` | 38 | Neurotransmitters, hormones, pharmacology concepts |
| `by-type/psychonautics/` | 23 | Psychonautics, lucid dreaming, transpersonal topics |
| `by-type/lists-and-indexes/` | 35 | Lists, galleries, index pages |
| `by-type/experience-reports-index/` | 9 | Indexes of trip reports by class |
| `by-type/site-meta/` | 9 | Wiki housekeeping pages (Main Page, Donate, Copyrights, disclaimers) |
| `by-type/other/` | 190 | Everything else (stubs, people, books, misc. topics) |

The folder sorting is my own grouping, based on each page's wiki categories and title. The original categories are kept on every record.

## Record shape (every JSON record)

```json
{
  "id": "psychonautwiki:<pageid>",
  "type": "substance | effect | responsible-use | ...",
  "title": "LSD",
  "source": {"site": "PsychonautWiki", "url": "...", "pageid": 0, "last_edited": "...", "dataset": "...", "license": "CC BY-SA 4.0", "imported": "2026-11-25"},
  "categories": ["Psychedelic", "Lysergamide", "..."],
  "substance_box_template": "SubstanceBox/LSD",
  "substance_box": {"names": {}, "classes": {}, "routes_of_administration": {"sublingual": {"enabled": true, "threshold": "15 µg", "common": "75 - 150 µg", "duration": "8 - 12 hours", "...": "..."}}, "semantic_properties": {"Sublingual min common dose": ["75"]}},
  "substance_box_params": {"<param>": {"raw": "...", "clean": "..."}},
  "redirect_to": "only on redirects",
  "summary_of": "only on /Summary pages",
  "plain_text": "...",
  "wikitext": "..."
}
```

`semantic_properties` pulls out the machine-readable numbers the wiki embeds in its markup (like `Sublingual min common dose = 75`), which suits building the app.

## Data caveats found during import

- **11 substances point to an infobox that is not in the export**, so they have no dosage data here: Tetrahydrocannabinol, Δ-8-, Δ-10- and Δ-11-Tetrahydrocannabinol, Tetrahydrocannabutol, Tetrahydrocannabihexol, Zopiclone, 2-Fluorodeschloroketamine, 5-Hydroxytryptophan, Cocoa, AET. They are flagged with `substance_box_missing_from_export` in `substances.json`.
- Routes a substance doesn't use still carry template placeholders like `x - x mg`. They are marked `"enabled": false`, and `substances.json` leaves them out.
- A few "clean" values are mangled by the exporter (e.g. `displayClasses` is `}`). The raw value is always kept next to it.
- 4 articles have no text at all (Beta-Endorphin, DMXE structure.svg, DSBT, Psychedelic neuroaesthetics), and 358 have wikitext but no plain text (mostly /Summary stubs and template pages).
- One page, "Visual effects - Psychedelics/en", is vandalism (abusive song lyrics), not content. It is kept as-is in `other/` for completeness and should be excluded from the app.
- 22 substance pages have no infobox at all (plants, combinations and similar).
