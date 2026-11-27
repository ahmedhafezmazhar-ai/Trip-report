# Mazhar App (Trip Report)

Mazhar is a harm reduction and research tool that tells people what a substance can do to them: effects, dose ranges, timelines, risks and interactions, in plain language and with sources on every answer. It is also meant for researchers and students.

This repository holds the design and the source material gathered so far. The app itself (Next.js, Supabase, Vercel) has not been built yet.

## What's here

| Folder | Contents |
|---|---|
| [docs/design/DESIGN-LOG.md](docs/design/DESIGN-LOG.md) | Every agreed design decision (D1 to D46), open questions and change history. The design is finished; the next step is the build. |
| [docs/design/substance-map/](docs/design/substance-map/) | The substance map page and its data. |
| [knowledge-base/](knowledge-base/README.md) | Source material, kept verbatim, with a cross-source topic index (`TOPICS.md`), a taxonomy (`taxonomy.json`), a visual map (`visual/`) and the scripts that built it (`_tools/`). |

## Published pages

- New site (v2), on GitHub Pages: https://ahmedhafezmazhar-ai.github.io/Trip-report/v2/ with substance pages (`substance.html`), the trip report writer (`report.html`) and tools (`tools.html`). Its data files in `docs/v2/data/` are built by `python3 tools/build_v2_data.py` from the PsychonautWiki export in the project knowledge base.

- Substance map: https://claude.ai/artifact/HR819smztZeLjFUAFS1L6R
- Featured FAQs: https://claude.ai/artifact/AsmpUPkQ9p4YUp8TmHt953

## Sources and licences

- **PsychonautWiki** (https://psychonautwiki.org): the full-site export and the Responsible drug use page are used under **CC BY-SA 4.0**. Credit: PsychonautWiki contributors. Material derived from it stays under CC BY-SA 4.0.
- **Shulgin books** (TiHKAL, Spanish edition; The Shulgin Index Vol. 1) are **copyrighted**. Because this repository is public, the full book text, the book sections and the per-compound book records are **not** included. Only the folder READMEs and the dose/duration comparison with PsychonautWiki are here.

## Disclaimer

This is harm reduction information, not medical advice. In an emergency, call your local emergency number.
