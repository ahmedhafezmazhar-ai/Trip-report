import sqlite3, json, re, os, sys, collections
db, out = sys.argv[1], sys.argv[2]
c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
IMPORTED = "2026-11-25"
SRC = {"site": "PsychonautWiki", "dataset": "psychonautwiki_db.zip (psychonautwiki.db, SQLite export provided by Hany, file dated 2026-11-25)",
       "license": "CC BY-SA 4.0", "imported": IMPORTED}
cats = collections.defaultdict(list)
for pid, cat in c.execute("select pageid, category from article_categories"): cats[pid].append(cat)
params = collections.defaultdict(list)
for t, p, r, cl in c.execute("select template_title, param, value_raw, value_clean from substance_params"): params[t].append((p, r, cl))

def slug(s): return re.sub(r"[^A-Za-z0-9._()+,-]+", "_", s).strip("_")[:150] or "untitled"
SEM = re.compile(r"\[\[([^:\]|]+?)::([^\]|]*)(?:\|[^\]]*)?\]\]")
ROA_FIELDS = ["Caption","Collapsed","Bioavailability","Microdose","Threshold","Light","Common","Strong","Heavy","Duration","Total","Onset","Comeup","Peak","Offset","Aftereffects","After Effects","Afterglow","TimelineFile","TimelineWidth"]
def structure(plist):
    d = {p: {"raw": r, "clean": cl} for p, r, cl in plist}
    sem = {}
    for p, r, cl in plist:
        for k, v in SEM.findall(r or ""): sem.setdefault(k.strip(), []).append(v.strip())
    roas = {}
    for p in d:
        m = re.match(r"^([A-Za-z]+)ROA$", p)
        if m and m.group(1) != "Module":
            name = m.group(1)
            roa = {"enabled": (d[p]["clean"] or "").strip().lower() == "true"}
            for f in ROA_FIELDS:
                k = f"{name}ROA_{f}"
                if k in d: roa[f.lower().replace(" ", "_")] = d[k]["clean"]
            roas[name.lower()] = roa
    g = lambda k: d.get(k, {}).get("clean")
    return {"names": {"common": g("NameCommon"), "substitutive": g("NameSubstitution"), "systematic": g("NameSystematic")},
            "classes": {"psychoactive": g("EffectClass"), "chemical": g("ChemicalClass")},
            "routes_of_administration": roas, "semantic_properties": sem}, d

def classify(title, wt, cl, box):
    w = (wt or "").lstrip()
    if w[:9].upper() == "#REDIRECT": return "redirect"
    if title.endswith("/Summary"): return "substance-summary"
    s = set(x[9:] for x in cl)
    if title in ("Main Page","General disclaimer","Copyrights") or title.startswith(("Broken/","Donate")): return "site-meta"
    if box or s & {"Psychoactive substance","Substance"}: return "substance"
    if s & {"Effect","Effect group"} or re.match(r".*effects - ", title): return "effect"
    if s & {"Responsible drug use","Harm reduction","Harm Reduction","Safety"}: return "responsible-use"
    if s & {"Chemical class","Psychoactive class"}: return "substance-class"
    if s & {"Preparation","Extraction","Cultivation","Chemical synthesis","Ayahuasca recipes","Cannabis recipes","Amanita recipes","Mushroom cultivation","General extraction"} or title.startswith("Preparation/"): return "preparation"
    if title.startswith("Experience index") or "Experience" in s: return "experience-reports-index"
    if re.search(r"(?i)tripsitting|psychological first aid|antidotes|^bad trip$|serotonin syndrome|psychosis|^aborting trips$|integration techniques|reality tests|^Tripsitting/", title): return "responsible-use"
    if s & {"Plant","DMT-containing plants","Psilocybin containing mushroom","Deliriant plant","Botany","Mycology","Mushroom"} or any(x.endswith(("(family)","(genus)")) for x in s): return "plants-and-fungi"
    if s & {"Pharmacology","Neurotransmitter","Hormone","Neuroscience","Chemistry"}: return "pharmacology-and-science"
    if s & {"Psychonautics","Oneironautics","Transpersonal","Philosophy","Spirituality"}: return "psychonautics"
    if s & {"Substance-related lists","Product-related lists"} or title.startswith(("List/","Substances/","Effects/","Summary index","Psychoactive substance index")): return "lists-and-indexes"
    return "other"

os.makedirs(out, exist_ok=True)
rows = c.execute("select pageid,title,url,last_edited,wikitext,plain_text,substancebox_template from articles order by pageid").fetchall()
index, redirects, used_tpl, seen = [], {}, set(), set()
jl = open(f"{out}/articles.jsonl", "w")
counts = collections.Counter()
for pid, title, url, le, wt, pt, box in rows:
    typ = classify(title, wt, cats[pid], box); counts[typ] += 1
    rec = {"id": f"psychonautwiki:{pid}", "type": typ, "title": title,
           "source": dict(SRC, url=url, pageid=pid, last_edited=le),
           "categories": [x[9:] if x.startswith("Category:") else x for x in cats[pid]]}
    if typ == "redirect":
        m = re.match(r"\s*#REDIRECT\s*:?\s*\[\[([^\]|]+)", wt or "", re.I)
        rec["redirect_to"] = m.group(1).strip() if m else None
        redirects[title] = rec["redirect_to"]
    if box:
        tkey = "Template:" + box
        rec["substance_box_template"] = box
        if tkey in params:
            used_tpl.add(tkey)
            st, d = structure(params[tkey]); rec["substance_box"] = st; rec["substance_box_params"] = d
        else: rec["substance_box"] = None
    if title.endswith("/Summary"): rec["summary_of"] = title[:-8]
    rec["plain_text"] = pt; rec["wikitext"] = wt
    jl.write(json.dumps(rec, ensure_ascii=False) + "\n")
    path = None
    if typ != "redirect":
        path = f"by-type/{typ}/{slug(title)}.json"
        if path.lower() in seen: path = f"by-type/{typ}/{slug(title)}__{pid}.json"
        seen.add(path.lower())
        os.makedirs(os.path.dirname(f"{out}/{path}"), exist_ok=True)
        json.dump(rec, open(f"{out}/{path}", "w"), ensure_ascii=False, indent=1)
    index.append({"id": rec["id"], "pageid": pid, "title": title, "type": typ, "last_edited": le, "url": url,
                  "categories": rec["categories"], "file": path, "redirect_to": rec.get("redirect_to")})
jl.close()
# summaries + aliases attached to substances index
by_title = {i["title"]: i for i in index}
for i in index:
    if i["type"] == "substance-summary" and i["title"][:-8] in by_title: by_title[i["title"][:-8]]["summary_page"] = i["file"]
for a, t in redirects.items():
    if t and t in by_title: by_title[t].setdefault("aliases", []).append(a)
json.dump(index, open(f"{out}/index.json", "w"), ensure_ascii=False, indent=1)
json.dump(redirects, open(f"{out}/redirects.json", "w"), ensure_ascii=False, indent=1)
cmap = collections.defaultdict(list)
for i in index:
    for cc in i["categories"]: cmap[cc].append(i["title"])
json.dump(dict(sorted(cmap.items())), open(f"{out}/categories.json", "w"), ensure_ascii=False, indent=1)
boxes = {}
for t, pl in params.items():
    st, d = structure(pl)
    boxes[t] = {"used_by_articles": [r[1] for r in rows if r[6] and "Template:"+r[6] == t], "structured": st, "params": d,
                "source": dict(SRC, url="https://psychonautwiki.org/wiki/" + t.replace(" ", "_"))}
json.dump(boxes, open(f"{out}/substance-boxes.json", "w"), ensure_ascii=False, indent=1)
print(counts, len(redirects), len(boxes), len(used_tpl), sum(1 for r in rows if r[6] and "Template:"+r[6] not in params))
