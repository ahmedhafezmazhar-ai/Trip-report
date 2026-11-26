import json, collections, glob, os
os.chdir("/mnt/project-files/knowledge-base/sources/books")
out, rows = [], {}
for folder, label in [("tihkal-es", "TiHKAL (Spanish ed.)"), ("shulgin-index-vol1", "Shulgin Index Vol. 1")]:
    R = [json.loads(l) for l in open(f"{folder}/compounds.jsonl")]; rows[folder] = R
    for r in R:
        c = r.get("comparison_with_psychonautwiki")
        if c:
            out.append({"book": label, "book_id": r["id"], "book_name": r.get("name") or r.get("code"), "psychonautwiki": r["psychonautwiki_match"]["title"],
                        "psychonautwiki_url": r["psychonautwiki_match"]["url"], "status": c["status"], "flags": c.get("flags", []), "note": c.get("note"),
                        "book_says": c.get("book") or {}, "psychonautwiki_oral": c.get("pw_oral")})
json.dump(out, open("comparison-with-psychonautwiki.json", "w"), ensure_ascii=False, indent=1)
T, I = rows["tihkal-es"], rows["shulgin-index-vol1"]
st = lambda R: dict(collections.Counter((r.get("comparison_with_psychonautwiki") or {}).get("status") for r in R if r.get("comparison_with_psychonautwiki")))
diff = [o for o in out if o["status"] == "differs"]
tm = [r for r in T if r["psychonautwiki_match"]]; im = [r for r in I if r["psychonautwiki_match"]]
def bs(d): b = d["book_says"]; return (b.get("dose") or b.get("statement") or "") + ((" / " + b["duration"]) if b.get("duration") else "")
md = f"""# Books

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

- TiHKAL: {len(tm)} of 55 entries match a PsychonautWiki page (by code name, English name, or the book's own synonym index).
- Shulgin Index: {len(im)} of 126 entries match.
- The rest are compounds PsychonautWiki doesn't cover, mostly obscure research compounds.

Comparison results: TiHKAL {st(T)}; Shulgin Index {st(I)}.

"Consistent" means the book's dose range overlaps PsychonautWiki's common oral dose and the durations overlap. Only the first dose figure in a book statement is parsed, so the verbatim statement is always kept next to it.

Clear differences:
""" + "\n".join(f"- **{d['book_name']}** ({d['book']}): book says `{bs(d)}`; PsychonautWiki oral common dose {d['psychonautwiki_oral']['common']}, duration {d['psychonautwiki_oral']['duration']}. {'; '.join(d['flags'])}." for d in diff) + "\n"
open("README.md", "w").write(md)
def tbl(R, namek):
    return "\n".join(f"| {r['entry_number']} | {r.get(namek)} | {r['psychonautwiki_match']['title'] if r['psychonautwiki_match'] else ''} | `{r['_f']}` |" for r in R)
for folder, R, namek in [("tihkal-es", T, "name"), ("shulgin-index-vol1", I, "code")]:
    files = {json.load(open(f))["id"]: os.path.relpath(f, folder) for f in glob.glob(f"{folder}/compounds/*.json")}
    for r in R: r["_f"] = files[r["id"]]
    if folder == "tihkal-es":
        head = """# TiHKAL: La continuación (Spanish edition)

| Field | Value |
|---|---|
| Work | TIHKAL: The Continuation, Alexander and Ann Shulgin, 1997 |
| This file | Spanish translation by Proyecto Shulgin en Español (2015), revision 1.0 dated 09/11/2021 |
| Uploaded | Tihkal.txt by Hany, imported 2026-11-25 |
| Rights | Copyrighted. Not CC BY-SA. Check rights before reproducing text in the app. |

## What's inside

- `sections/00-front-matter.md`: description, prologues and forewords, translator's notes, Shulgin biography.
- `sections/libro-1/`: Book I, "La historia continúa": the Shulgins' narrative in 25 chapters, one file each.
- `sections/libro-2/00-indice-abreviado.md` and `compounds/`: Book II, "La química continúa": 55 tryptamine entries.
- `sections/apendices/`: A drug law, B glossary, C acknowledgments, D cactus alkaloids, E carbolines, F histamines, G known tryptamines (CAS citations), H full chemical index of Book II.
- `sections/zz-*`: sponsor pages and the translator's and editor's footnotes.

## Compound record fields

`name`, `entry_number`, `header_names_raw` (every name in the entry title), `aliases_from_book_index` (from Appendix H), `dosage_raw` and `dosage_parsed` (in mg), `route`, `duration_raw` and `duration_parsed` (in hours), `qualitative_comments` (each dose-tagged trip report as its own item, 252 in total), `synthesis_raw`, `extensions_and_commentary_raw`, `full_entry_text`, `citation` (entry number, plus line range and page breaks in the file), `psychonautwiki_match`, `comparison_with_psychonautwiki`, `source`.

All text is in Spanish, as in the file. Fields ending in `_raw` are verbatim.

| # | Name | PsychonautWiki page | File |
|---|---|---|---|
"""
    else:
        head = """# The Shulgin Index, Volume One

| Field | Value |
|---|---|
| Work | The Shulgin Index Vol. 1: Psychedelic Phenethylamines and Related Compounds. Alexander T. Shulgin, Tania Manning, Paul F. Daley. Transform Press, 2011. ISBN 978-0-9630096-3-0 |
| Uploaded | Shulgin-Index-Vol1.txt by Hany, imported 2026-11-25 |
| Rights | Copyright © 2011 Transform Press, all rights reserved. Not CC BY-SA. Check rights before reproducing text in the app. |
| Text quality | OCR scan. Expect split digits ("1 991"), Greek letters read as Latin ("a" for alpha, "f3" for beta), and chemical structure drawings turned into stray characters. Parsed numbers fix split digits; raw text is left exactly as uploaded. |

## What's inside

- `sections/`: front matter (introduction, how to use the book, nomenclature), Tables (pp. 317-362), CAS Registry Numbers Index (363), Appendix A on IUPAC naming (423), Appendix B state-law URLs (429), Appendix C mass spectra (434), Bibliography (521), Alphabetical Index (665).
- `compounds/`: the 126 main entries (pp. 1-316). Each entry also contains its homologue and analogue tables, so hundreds of related compounds are covered inside their parent entries.

## Compound record fields

`code`, `entry_number`, `names` (IUPAC and common names under the title), `cas_numbers_ocr`, `sections_raw` (Registry Numbers, Synthesis and Chemistry, Positional Isomers, Homologues and Analogues, Biochemistry, Pharmacology, Legal Status, all verbatim), `human_activity_statements` (every sentence in Pharmacology about human doses), `main_human_statement` with `human_activity_dosage_parsed` and `human_activity_duration_parsed`, `all_human_statements_in_entry_including_analogue_tables`, `legal_status_raw`, `full_entry_text`, `citation` (entry number, printed page range, file lines), `psychonautwiki_match`, `comparison_with_psychonautwiki`, `source`.

OCR damaged the code names of entries #66 and #67 ("F", "PEA"). Both are flagged `code_ocr_damaged` and are not matched by code. 73 of the 126 entries give a human dose.

| # | Code | PsychonautWiki page | File |
|---|---|---|---|
"""
    open(f"{folder}/README.md", "w").write(head + tbl(R, namek) + "\n")
print(len(out), len(diff), st(T), st(I))
