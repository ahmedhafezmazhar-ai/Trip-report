# Extraction scripts (PsychonautWiki / MediaWiki pages)

Used for source #1. Pipeline:
1. Download: `index.php?title=<Page>&action=raw` (wikitext) and `api.php?action=parse&page=<Page>&prop=text|sections|revid|images|externallinks|links&format=json&formatversion=2` (rendered HTML), plus `api.php?action=query&prop=revisions|info` for revision/date.
2. `pandoc -f html -t gfm-raw_html --wrap=none page.html -o page.md`
3. `python3 clean.py page.md clean.md` (absolute links, drop edit links/icons, unwrap layout lists)
4. `python3 split.py <dl_dir> <out_dir>` (section files with front matter; section list and tags are hard-coded per page, edit before reuse)
5. `python3 extras.py <dl_dir> <out_dir>` (related-pages.md from the navbox, media.md)
6. Completeness check: every word of the rendered HTML must appear in the split files.
