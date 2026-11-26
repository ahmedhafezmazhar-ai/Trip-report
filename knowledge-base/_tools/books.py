import re, json, os, sys, unicodedata, collections
BK, KB = sys.argv[1], sys.argv[2]
OUT = f"{KB}/sources/books"
PW = f"{KB}/sources/psychonautwiki/site-export"
IMPORTED = "2026-11-25"

# ---------- PsychonautWiki lookup ----------
pw_index = json.load(open(f"{PW}/index.json"))
pw_subs = {s["title"]: s for s in json.load(open(f"{PW}/substances.json"))}
redir = json.load(open(f"{PW}/redirects.json"))
def key(s):
    s = unicodedata.normalize("NFKD", s).replace("α", "a").replace("β", "b")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())
title_of = {}
for i in pw_index:
    if i["type"] in ("substance", "plants-and-fungi", "other", "substance-class", "pharmacology-and-science"):
        title_of.setdefault(key(i["title"]), i["title"])
for a, t in redir.items():
    if t:
        t2 = redir.get(t, t)
        title_of.setdefault(key(a), t2.split("#")[0])
def pw_match(names):
    for n in names:
        k = key(n)
        if k and k in title_of:
            t = title_of[k]
            ent = next((i for i in pw_index if i["title"] == t), None)
            if ent and ent["type"] != "redirect":
                return {"title": t, "id": ent["id"], "url": ent["url"], "type": ent["type"], "matched_on": n}
    return None

# ---------- numeric helpers ----------
UNIT = {"µg": 0.001, "ug": 0.001, "microgramos": 0.001, "microgramo": 0.001, "mg": 1, "miligramos": 1, "g": 1000, "gramos": 1000}
def rng(s):
    s = s.replace(",", ".").replace("–", "-").replace("—", "-")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:(?:-|to)\s*(\d+(?:\.\d+)?))?\s*(µg|ug|microgramos?|mg|miligramos|gramos|g)\b(?!\s*/\s*kg)", s)
    if not m: return None
    a = float(m.group(1)); b = float(m.group(2)) if m.group(2) else a
    return {"min_mg": a * UNIT[m.group(3)], "max_mg": b * UNIT[m.group(3)], "unit_in_text": m.group(3)}
def hrs(s):
    s = s.replace(",", ".").replace("–", "-").replace("—", "-")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:(?:-|to)\s*(\d+(?:\.\d+)?))?\s*(horas?|hours?|hrs?|minutos|minutes|min)\b", s)
    if not m: return None
    f = 1/60 if m.group(3).startswith("min") else 1
    a = float(m.group(1)); b = float(m.group(2)) if m.group(2) else a
    return {"min_h": round(a*f, 3), "max_h": round(b*f, 3)}
def pw_oral(title):
    s = pw_subs.get(title)
    if not s or not s.get("routes_of_administration"): return None
    r = s["routes_of_administration"]
    return r.get("oral") or r.get("sublingual") or None

def compare(title, book_dose, book_dur, label):
    roa = pw_oral(title)
    if not roa: return {"status": "no PsychonautWiki oral data", "book": label}
    parts = [rng(roa.get(k) or "") for k in ("threshold","light","common","strong","heavy")]
    pts = [p for p in parts if p]
    out = {"pw_oral": {k: roa.get(k) for k in ("threshold","light","common","strong","heavy","duration")}, "book": label, "flags": []}
    if not book_dose and not book_dur:
        out["status"] = "book gives no comparable oral dose or duration"; return out
    if book_dose and pts:
        lo = min(p["min_mg"] for p in pts); hi = max(p["max_mg"] for p in pts)
        com = parts[2]
        if book_dose["max_mg"] < lo or book_dose["min_mg"] > hi:
            out["flags"].append("book dose range lies outside PsychonautWiki's whole oral range")
        elif com and (book_dose["max_mg"] < com["min_mg"] or book_dose["min_mg"] > com["max_mg"]):
            out["flags"].append("book dose range does not overlap PsychonautWiki's common oral dose")
    d = hrs(roa.get("duration") or "")
    if book_dur and d and (book_dur["max_h"] < d["min_h"] or book_dur["min_h"] > d["max_h"]):
        out["flags"].append("book duration does not overlap PsychonautWiki's oral duration")
    out["status"] = "differs" if out["flags"] else "consistent"
    return out

def unhyph(t): return re.sub(r"(\w)[-­]\s*\n\s*(\w)", r"\1\2", t)
def slug(s): return re.sub(r"[^A-Za-z0-9.,()+-]+", "_", unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode()).strip("_") or "x"

# =================== TiHKAL (Spanish) ===================
T = open(f"{BK}/tihkal.txt", encoding="utf-8").read().split("\n")
SRC_T = {"work": "TiHKAL: La continuación (Spanish translation of TIHKAL: The Continuation)", "authors": "Alexander Shulgin, Ann Shulgin",
         "original_year": 1997, "translation": "Proyecto Shulgin en Español, 2015 (Revisión 1.0, 09/11/2021)", "language": "es",
         "file": "Tihkal.txt (uploaded by Hany)", "imported": IMPORTED,
         "rights": "Copyrighted book (© Alexander and Ann Shulgin 1997; Spanish translation © its translators). Not CC BY-SA. Stored for private research; check rights before reproducing text in the app."}
ABBR = ["AL-LAD","DBT","DET","DIPT","α,O-DMS","DMT","2,α-DMT","α,N-DMT","DPT","EIPT","α-ET","ETH-LAD","Harmalina","Harmina","4-OH-DBT","4-OH-DET","4-OH-DIPT","4-OH-DMT","5-OH-DMT","4-OH-DPT","4-OH-MET","4-OH-MIPT","4-OH-MPT","4-OH-pir-T","Ibogaína","LSD","MBT","4,5-MDO-DIPT","5,6-MDO-DIPT","4,5-MDO-DMT","5,6-MDO-DMT","5,6-MDO-MIPT","2-Me-DET","2-Me-DMT","Melatonina","5-MeO-DET","5-MeO-DIPT","5-MeO-DMT","4-MeO-MIPT","5-MeO-MIPT","5,6-MeO-MIPT","5-MeO-NMT","5-MeO-pir-T","6-MeO-THH","5-MeO-TMT","5-MeS-DMT","MIPT","α-MT","NET","NMT","PRO-LAD","pir-T","T","Tetrahidroharmina","α,N,O-TMS"]
EN = {"Harmalina":["Harmaline"],"Harmina":["Harmine"],"Ibogaína":["Ibogaine"],"Melatonina":["Melatonin"],"T":["Tryptamine"],"Tetrahidroharmina":["Tetrahydroharmine"],
      "4-OH-DMT":["Psilocin"],"5-OH-DMT":["Bufotenin"],"α-ET":["AET","alpha-ET"],"α-MT":["AMT","alpha-MT"],"4-OH-pir-T":["4-HO-pyr-T"],"5-MeO-pir-T":["5-MeO-pyr-T"],"pir-T":["pyr-T"],
      "4-OH-MET":["4-HO-MET"],"4-OH-DET":["4-HO-DET"],"4-OH-DIPT":["4-HO-DiPT"],"4-OH-MIPT":["4-HO-MiPT"],"4-OH-DPT":["4-HO-DPT"],"4-OH-MPT":["4-HO-MPT"],"4-OH-DBT":["4-HO-DBT"],"α,O-DMS":["5-MeO-AMT"],"α,N-DMT":["alpha,N-DMT"]}
heads = {}
for i, l in enumerate(T):
    m = re.match(r"^\f?N\.º\s*(\d+)\s*[\.\s—–-]", l)
    if m and 18400 < i < 28722 and int(m.group(1)) not in heads: heads[int(m.group(1))] = i
heads[4] = 19117
assert sorted(heads) == list(range(1, 56)), sorted(set(range(1,56)) - set(heads))
APP_A = next(i for i, l in enumerate(T) if "APÉNDICE A:" in l)
tpage = []; c = 1
for l in T:
    c += l.count("\f"); tpage.append(c)
# aliases from Appendix H index
alias = collections.defaultdict(set)
idx_start = next(i for i, l in enumerate(T) if "APÉNDICE H" in l)
idx_end = next(i for i, l in enumerate(T) if i > idx_start and "ENTIDADES COLABORADORAS" in l)
idx_text = re.sub(r"\n(?=\d+\s*$)", " ", "\n".join(T[idx_start:idx_end]))
for m in re.finditer(r"^\s*(.+?):?\s+ver\s+(.+?),\s*n\.º\s*(\d+)", idx_text, re.M):
    alias[int(m.group(3))].add(m.group(1).strip().rstrip(":"))
LBL = ["SÍNTESIS", "DOSIS", "DURACIÓN", "COMENTARIOS CUALITATIVOS", "ANEXOS Y COMENTARIOS", "ANEXOS Y COMENTARIO"]
tk = []
order = sorted(heads)
for n in order:
    a = heads[n]; b = heads[n+1] if n < 55 else APP_A
    text = "\n".join(T[a:b]).rstrip()
    m = re.search(r"^\s*SÍNTESIS:", text, re.M)
    header = text[:m.start()] if m else text.split("\n\n")[0]
    sec = {}
    pos = [(mm.start(1), mm.group(1)) for mm in re.finditer(r"(?:^|\s)(SÍNTESIS|DOSIS|DURACIÓN|COMENTARIOS\s+CUALITATIVOS|ANEXOS\s+Y\s+COMENTARIOS?)\s*:", text, re.M)]
    for j, (p, lab) in enumerate(pos):
        q = pos[j+1][0] if j+1 < len(pos) else len(text)
        body = text[p:q].split(":", 1)[1].strip()
        lab = "ANEXOS Y COMENTARIOS" if lab.startswith("ANEXOS") else ("COMENTARIOS CUALITATIVOS" if lab.startswith("COMENTARIOS") else lab)
        sec[lab] = (sec.get(lab, "") + "\n\n" + body).strip()
    reports = []
    qc = sec.get("COMENTARIOS CUALITATIVOS", "")
    for mm in re.finditer(r"\(\s*[Cc]on\s+([^)]*?)\)\s*:?\s*(«.*?»)", qc, re.S):
        reports.append({"dose_and_route": " ".join(mm.group(1).split()), "report": " ".join(mm.group(2).split())})
    dose_raw = " ".join(sec.get("DOSIS", "").split()) or None
    dur_raw = " ".join(sec.get("DURACIÓN", "").split()) or None
    names = [ABBR[n-1]] + EN.get(ABBR[n-1], []) + sorted(alias[n])
    match = pw_match([ABBR[n-1]] + EN.get(ABBR[n-1], []) + sorted(alias[n]))
    d, du = (rng(dose_raw) if dose_raw else None), (hrs(dur_raw) if dur_raw else None)
    rec = {"id": f"tihkal-es:{n}", "source_type": "book", "book": "TiHKAL (Spanish edition)", "entry_number": n, "name": ABBR[n-1],
           "header_names_raw": " ".join(header.split()), "aliases_from_book_index": sorted(alias[n]),
           "dosage_raw": dose_raw, "dosage_parsed": d, "route": ("oral" if dose_raw and "oral" in dose_raw else None),
           "duration_raw": dur_raw, "duration_parsed": du,
           "qualitative_comments": reports, "qualitative_comments_raw": qc or None,
           "synthesis_raw": sec.get("SÍNTESIS"), "extensions_and_commentary_raw": sec.get("ANEXOS Y COMENTARIOS"),
           "full_entry_text": text,
           "citation": {"book": "TiHKAL, Libro II (La química continúa)", "entry": f"n.º {n}", "file_lines": [a+1, b], "file_pages": [tpage[a], tpage[b-1]]},
           "psychonautwiki_match": match, "source": SRC_T}
    if match and match["type"] == "substance":
        rec["comparison_with_psychonautwiki"] = compare(match["title"], d, du, {"dose": dose_raw, "duration": dur_raw})
    tk.append(rec)

# TiHKAL sections
sections_t = [("00-front-matter", "Portada, proemios y prólogos", 0, 2795)]
caps = [(i, l.strip()) for i, l in enumerate(T) if re.match(r"^\s*CAPÍTULO \d+ /", l)]
book1_end = next(i for i, l in enumerate(T) if l.strip() == "LIBRO II")
for j, (i, t) in enumerate(caps):
    end = caps[j+1][0] if j+1 < len(caps) else book1_end
    start = 2795 if j == 0 else i
    num = int(re.search(r"\d+", t).group())
    sections_t.append((f"libro-1/capitulo-{num:02d}", t.title(), start, end))
sections_t.append(("libro-2/00-indice-abreviado", "Libro II: índice abreviado de las triptaminas", book1_end, heads[1]))
apps = [(i, l.strip()) for i, l in enumerate(T) if re.match(r"^\s*APÉNDICE [A-H]", l)]
for j, (i, t) in enumerate(apps):
    end = apps[j+1][0] if j+1 < len(apps) else idx_end
    sections_t.append((f"apendices/{slug(t.split(':')[0].split('/')[0]).lower()}", t, i, end))
notes = next(i for i, l in enumerate(T) if l.lstrip("\f").startswith("[1] "))
sections_t.append(("zz-entidades-colaboradoras", "Entidades colaboradoras", idx_end, notes))
sections_t.append(("zz-notas", "Notas del traductor y del editor", notes, len(T)))

# =================== Shulgin Index Vol 1 ===================
I = open(f"{BK}/index1.txt", encoding="utf-8").read().split("\n")
SRC_I = {"work": "The Shulgin Index, Volume One: Psychedelic Phenethylamines and Related Compounds", "authors": "Alexander T. Shulgin, Tania Manning, Paul F. Daley",
         "publisher": "Transform Press, Berkeley CA", "year": 2011, "isbn": "978-0-9630096-3-0", "language": "en",
         "file": "Shulgin-Index-Vol1.txt (uploaded by Hany; OCR text, contains scanning errors)", "imported": IMPORTED,
         "rights": "Copyright © 2011 Transform Press, all rights reserved. Not CC BY-SA. Stored for private research; check rights before reproducing text in the app."}
page = [None]*len(I); cur = None
for i, l in enumerate(I):
    m1 = re.match(r"^\s*(\d[\d ]{0,4})\s{3,}The Shulgin Index", l)
    m2 = re.match(r"^\s{5,}(Main En ?try Compounds|Tables|CAS Registry Numbers Index|Appendix\s+[ABC]|Bibliography|Alphabetical Index|Introduction)\s{2,}(\d[\d ]{0,4})\s*$", l)
    m3 = re.match(r"^\s{5,}(Main En ?try Compounds|Tables|CAS Registry Numbers Index|Appendix\s+[ABC]|Bibliography|Alphabetical Index)\s*$", l)
    num = None
    if m1: num = int(m1.group(1).replace(" ", ""))
    elif m2: num = int(m2.group(2).replace(" ", ""))
    elif m3 and cur: num = cur + 1
    if num is not None and (cur is None or 0 < num - cur <= 3): cur = num
    elif num is not None and cur is not None and num - cur > 3 and (m3 or m1 or m2): cur = cur + 1
    page[i] = cur
first_p = next(i for i, x in enumerate(page) if x)
for i in range(first_p): page[i] = None
MAINP = next(i for i, l in enumerate(I) if l.strip() == "MAIN ENTRY COMPOUNDS")
for i in range(MAINP, first_p): page[i] = 1
MAIN0 = next(i for i, l in enumerate(I) if l.strip() == "MAIN ENTRY COMPOUNDS")
FM_END = MAIN0
TAB0 = next(i for i, l in enumerate(I) if re.match(r"^\s+Tables\s+317\s*$", l))
heads_i = [(i, int(m.group(1)), m.group(2).strip()) for i, l in enumerate(I) if (m := re.match(r"^#\s*(\d+)\s*\.\s+(\S.*)$", l)) and MAIN0 <= i < TAB0]
assert len(heads_i) == 126, len(heads_i)
SUBS = ["Registry Numbers", "Synthesis and Chemistry", "Positional Isomers", "Homologues and Analogues", "Homologues", "Analogues", "Biochemistry", "Pharmacology", "Legal Status"]
HUM = re.compile(r"((?:Orally active|Active|Threshold(?: oral)? activity|Threshold effects|Inactive|Not active|Effective|Intravenously active|Active orally|Psychedelic activity|Human activity|Human dose|Doses? of)[^.]*?(?:\d|human|inactive)[^.]*?(?:\([^)]*\))?\s*\.)", re.S)
def ocrnum(s):
    s = re.sub(r"(?<=\d) (?=\d)", "", s); s = re.sub(r"(?<=\d) \.(?=\d)", ".", s); s = re.sub(r"(?<=\d)\. (?=\d)", ".", s)
    return re.sub(r"(?<=\d) (?=\d)", "", s)
ix = []
for j, (a, n, code) in enumerate(heads_i):
    b = heads_i[j+1][0] if j+1 < len(heads_i) else TAB0
    lines = I[a:b]
    text = "\n".join(lines).rstrip()
    names = []
    for l in lines[1:]:
        s = l.strip()
        if not s: 
            if names: break
            continue
        if s.startswith("Registry Numbers"): break
        ind = len(l) - len(l.lstrip())
        if ind <= 12 and "�" not in s and len(s) < 90: names.append(s)
    # split subsections
    pos = [(k, l.strip()) for k, l in enumerate(lines) if l.strip() in SUBS]
    sec = {}
    for q, (k, lab) in enumerate(pos):
        e = pos[q+1][0] if q+1 < len(pos) else len(lines)
        sec[lab] = (sec.get(lab, "") + "\n" + "\n".join(lines[k+1:e])).strip("\n")
    def hsent(t):
        flat = re.sub(r"\s+([.,;])", r"\1", " ".join(unhyph(t).split()))
        sents = re.split(r"(?<=[.])\s+(?=[A-Z0-9(])|(?:(?<=\d{4}\))|(?<=\d{4}[a-z]\)))\s+(?=[A-Z0-9])", flat)
        return [x for x in sents if re.search(r"\bhumans?\b|\bman\b|volunteers|subjects", x, re.I) and re.search(r"\d\s*(?:-\s*\d[\d ]*)?\s*(?:mg|µg|ug|micrograms|milligrams)\b|duration", ocrnum(x))]
    HDR = re.compile(r"^\s*\f?\s*(\d[\d ]{0,4}\s{3,}The Shulgin Index.*|(Main En ?try Compounds)(\s{2,}\d[\d ]{0,4})?)\s*$")
    def dehead(t):
        out, skip = [], False
        for l in t.split("\n"):
            if HDR.match(l): skip = True; continue
            if skip and l.strip():
                skip = False
                if len(l.strip()) < 40 and re.fullmatch(r"[A-Za-z0-9,.\-* /|I]+", l.strip()) and len(l) - len(l.lstrip()) > 20: continue
            out.append(l)
        return "\n".join(out)
    human = hsent(dehead(sec.get("Pharmacology", "")))
    allhum = hsent(dehead(text))
    def score(h):
        hs = ocrnum(h); sc = 0
        if re.search(r"(active|activity)[^.;]{0,30} in humans", hs, re.I): sc += 4
        if re.search(r"orally|oral", hs, re.I): sc += 2
        if "duration" in hs: sc += 2
        if re.search(r"Shulgin and Shulgin|Shulgin, 19", hs): sc += 1
        if re.search(r"i\.m\.|i\.v\.|intraven|intramusc|/\s*kg", hs, re.I): sc -= 5
        if not rng(hs): sc -= 10
        if not re.search(r"(active|activity|effective|dose|threshold)[^.]{0,60}\bhumans?\b|\bhumans?\b[^.]{0,60}(active|activity|dose|threshold)", hs, re.I): sc -= 10
        return sc
    cands = sorted(human, key=score, reverse=True)
    main_stmt = cands[0] if cands and score(cands[0]) > 0 else None
    d = du = None
    if main_stmt:
        ms = ocrnum(main_stmt)
        d = rng(ms)
        mm = re.search(r"duration\s+(?:of\s+)?([^;(]*)", ms); du = hrs(mm.group(1)) if mm else None
    legal = " ".join(sec.get("Legal Status", "").split()) or None
    cas = re.findall(r"\[\s*([\d -]+-\d)\s*\]", sec.get("Registry Numbers", ""))
    damaged = n in (66, 67)
    cand = ([] if damaged else [code.rstrip("*")]) + names
    match = pw_match(cand)
    pages = sorted({p for p in page[a:b] if p})
    rec = {"id": f"shulgin-index-v1:{n}", "source_type": "book", "book": "The Shulgin Index, Vol. 1", "entry_number": n, "code": code,
           "code_ocr_damaged": damaged, "names": names, "cas_numbers_ocr": [c.replace(" ", "") for c in cas],
           "human_activity_statements": human, "main_human_statement": main_stmt, "human_activity_dosage_parsed": d, "human_activity_duration_parsed": du,
           "all_human_statements_in_entry_including_analogue_tables": allhum, "legal_status_raw": legal,
           "sections_raw": sec, "full_entry_text": text,
           "citation": {"book": "The Shulgin Index Vol. 1 (2011)", "entry": f"#{n}", "pages": [pages[0], pages[-1]] if pages else None, "file_lines": [a+1, b]},
           "ocr_note": "Text is OCR output: expect broken digits (e.g. '1 991'), Greek letters read as Latin ('a' for alpha, 'f3' for beta) and structure drawings rendered as stray characters.",
           "psychonautwiki_match": match, "source": SRC_I}
    if match and match["type"] == "substance":
        oral_ok = bool(main_stmt) and re.search(r"oral", main_stmt, re.I) and not re.search(r"without oral|not orally|inactive", main_stmt, re.I)
        rec["comparison_with_psychonautwiki"] = compare(match["title"], d if oral_ok else None, du if oral_ok else None, {"statement": main_stmt})
        if not oral_ok: rec["comparison_with_psychonautwiki"]["note"] = "Book statement is not an oral human dose, so doses were not compared."
    ix.append(rec)
bounds = [("00-front-matter", "Title, acknowledgments, contents, introduction, how to use, nomenclature", 0, MAIN0), ("02-tables", "Tables (pp. 317-362)", TAB0, None)]
def first_page_line(p): return next(i for i, x in enumerate(page) if x and x >= p)
secs_i = [("00-front-matter", "Title, acknowledgments, contents, introduction, nomenclature", 0, MAIN0), ("01-main-entries-title-page", "Main Entry Compounds (section title)", MAIN0, heads_i[0][0]),
          ("02-tables", "Tables", TAB0, first_page_line(363) - 3),
          ("03-cas-registry-numbers-index", "CAS Registry Numbers Index", first_page_line(363) - 3, first_page_line(423) - 3),
          ("04-appendix-a-iupac-nomenclature", "Appendix A - Additional Notes on IUPAC Nomenclature", first_page_line(423) - 3, first_page_line(429) - 3),
          ("05-appendix-b-state-law-on-the-web", "Appendix B - State Law on the Web", first_page_line(429) - 3, first_page_line(434) - 3),
          ("06-appendix-c-mass-spectra", "Appendix C - Mass Spectra", first_page_line(434) - 3, first_page_line(521) - 3),
          ("07-bibliography", "Bibliography", first_page_line(521) - 3, first_page_line(665) - 3),
          ("08-alphabetical-index", "Alphabetical Index", first_page_line(665) - 3, len(I))]

# =================== write ===================
def md_header(src, title, extra):
    return "---\n" + "\n".join([f'title: "{title}"', f'source: "{src["work"]}"', f'authors: "{src["authors"]}"', f'rights: "{src["rights"]}"', f"imported: {IMPORTED}"] + extra) + "\n---\n\n"
for folder, src, L, secs, recs, kind in [("tihkal-es", SRC_T, T, sections_t, tk, "t"), ("shulgin-index-vol1", SRC_I, I, secs_i, ix, "i")]:
    base = f"{OUT}/{folder}"; os.makedirs(f"{base}/raw", exist_ok=True)
    for path, title, a, b in secs:
        p = f"{base}/sections/{path}.md"; os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(md_header(src, title, [f"file_lines: [{a+1}, {b}]", "fidelity: verbatim text of these lines from the uploaded file"]) + "```text\n" + "\n".join(L[a:b]) + "\n```\n")
    os.makedirs(f"{base}/compounds", exist_ok=True)
    for r in recs:
        nm = r.get("name") or r.get("code")
        stem = f"{r['entry_number']:03d}-{slug(nm)}"
        json.dump(r, open(f"{base}/compounds/{stem}.json", "w"), ensure_ascii=False, indent=1)
        r["_file"] = f"compounds/{stem}.json"
    with open(f"{base}/compounds.jsonl", "w") as f:
        for r in recs: f.write(json.dumps({k: v for k, v in r.items() if k != "_file"}, ensure_ascii=False) + "\n")
# coverage check: every line of each file is inside exactly one saved section or compound entry
def cover(L, ranges): 
    c = [0]*len(L)
    for a, b in ranges:
        for k in range(a, b): c[k] += 1
    return sum(1 for x in c if x == 0), sum(1 for x in c if x > 1)
ct = cover(T, [(a, b) for _, _, a, b in sections_t] + [(r["citation"]["file_lines"][0]-1, r["citation"]["file_lines"][1]) for r in tk])
ci_ranges = [(a, b) for _, _, a, b in secs_i] + [(r["citation"]["file_lines"][0]-1, r["citation"]["file_lines"][1]) for r in ix]
cc = [0]*len(I)
for a, b in ci_ranges:
    for k in range(a, b): cc[k] += 1
print("uncovered index lines:", [(k+1, I[k][:60]) for k, x in enumerate(cc) if x == 0])
ci = cover(I, [(a, b) for _, _, a, b in secs_i] + [(r["citation"]["file_lines"][0]-1, r["citation"]["file_lines"][1]) for r in ix])
json.dump({"tihkal": [(r["entry_number"], r["name"], r["_file"]) for r in tk], "index": [(r["entry_number"], r["code"], r["_file"]) for r in ix]}, open(f"{OUT}/_files.json", "w"))
print("tihkal uncovered/overlap lines", ct, "index", ci)
print("tihkal matched", sum(1 for r in tk if r["psychonautwiki_match"]), "/55; with dose", sum(1 for r in tk if r["dosage_raw"]), "reports", sum(len(r["qualitative_comments"]) for r in tk))
print("index matched", sum(1 for r in ix if r["psychonautwiki_match"]), "/126; human stmt", sum(1 for r in ix if r["human_activity_statements"]))
for r in tk + ix:
    c = r.get("comparison_with_psychonautwiki")
    if c and c["status"] == "differs": print("DIFF", r["id"], r.get("name") or r.get("code"), r["psychonautwiki_match"]["title"], c["book"], c["pw_oral"]["common"], c["pw_oral"]["duration"], c["flags"])
