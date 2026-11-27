#!/usr/bin/env python3
"""Build the data files the v2 site reads (docs/v2/data/).

Reads the PsychonautWiki site export (CC BY-SA 4.0) from the project knowledge
base and the approved substance map data, and writes small JSON files:

  substances.json   per substance: names, classes, dose + timeline per route,
                    dangerous / unsafe / uncertain interactions, Shulgin refs
  effects.json      effect index with a one-paragraph plain description
  reagents.json     reagent colour chart (from "Reagent testing kits")

Usage: python3 tools/build_v2_data.py [path-to-site-export]
"""
import json, re, sys, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORT = Path(sys.argv[1] if len(sys.argv) > 1 else
              "/mnt/project-files/knowledge-base/sources/psychonautwiki/site-export")
OUT = ROOT / "docs/v2/data"
OUT.mkdir(parents=True, exist_ok=True)
MAP = json.load(open(ROOT / "docs/design/substance-map/substance-map-data.json"))

index = json.load(open(EXPORT / "index.json"))
by_title = {r["title"]: r for r in index if not r.get("redirect_to")}
subs = {s["title"]: s for s in json.load(open(EXPORT / "substances.json"))}

def article(title):
    r = by_title.get(title)
    if not r or not r.get("file"):
        return None
    p = EXPORT / r["file"]
    return json.load(open(p)) if p.exists() else None

def strip_wiki(t):
    t = re.sub(r"<ref[^>]*/>", "", t)
    t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    t = re.sub(r"\{\{citation needed[^}]*\}\}", "", t, flags=re.I)
    for _ in range(3):
        t = re.sub(r"\{\{[^{}]*\}\}", "", t)
    t = re.sub(r"\[\[(?:[A-Za-z]+::)?([^\]|]+)\|([^\]]+)\]\]", r"\2", t)
    t = re.sub(r"\[\[(?:[A-Za-z]+::)?([^\]]+)\]\]", r"\1", t)
    t = re.sub(r"\[https?://\S+ ([^\]]+)\]", r"\1", t)
    t = re.sub(r"'''?", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    return html.unescape(re.sub(r"\s+", " ", t)).strip()

ROUTE_KEYS = ["bioavailability", "microdose", "threshold", "light", "common", "strong", "heavy",
              "onset", "comeup", "peak", "offset", "aftereffects", "duration"]
def clean_val(v):
    v = (v or "").strip()
    if not v or re.search(r"\bx\b", v) or v in (">  mg", "<  mg"):
        return ""
    return v

SEV = {"DangerousInteraction": "dangerous", "UnsafeInteraction": "unsafe", "UncertainInteraction": "uncertain"}
TEMPLATES = {"Depressants": [("Depressants", "dangerous", "Depressant effects multiply rather than add up. Together they can stop breathing, cause unexpected unconsciousness and choking on vomit.")],
             "Stimulants": [("Stimulants", "unsafe", "Stimulants together strain the heart and raise body temperature, blood pressure and anxiety.")],
             "Serotonergic": [("MAOIs", "dangerous", "Risk of serotonin syndrome."), ("SSRIs", "unsafe", "Risk of serotonin syndrome.")]}
def interactions(w):
    out = []
    m = re.search(r"==+\s*Dangerous interactions\s*==+", w) or re.search(r"\{\{DangerousInteractions/Intro\}\}", w)
    if not m:
        return out
    seg = w[m.end():]
    m2 = re.search(r"\n==[^=]|\n===[^=]", seg)
    if m2:
        seg = seg[:m2.start()]
    for tname, items in TEMPLATES.items():
        if "{{DangerousInteractions/" + tname in seg:
            for t, sev, why in items:
                out.append({"with": t, "sev": sev, "why": why})
    for line in seg.split("\n"):
        if not line.startswith("*"):
            continue
        tags = re.findall(r"\[\[(DangerousInteraction|UnsafeInteraction|UncertainInteraction)::([^\]|]+)(?:\|[^\]]*)?\]\]", line)
        if not tags:
            lead = re.match(r"\*\s*'''(.*?)'''", line)
            if not lead:
                continue
            names = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", lead.group(1)) or [strip_wiki(lead.group(1))]
            tags = [("Caution", n) for n in names]
        txt = strip_wiki(line.lstrip("*"))
        parts = re.split(r"\s*:\s+|\s+[-–—]+\s+", txt, maxsplit=1)
        desc = parts[1] if len(parts) > 1 else ""
        if len(desc) > 600:
            desc = desc[:600].rsplit(". ", 1)[0] + "."
        for kind, target in tags:
            out.append({"with": target.strip().replace("_", " "), "sev": SEV.get(kind, "caution"), "why": desc})
    return out

substances = []
for s in MAP["s"]:
    if "preparations" in (s.get("iss") or []):
        continue
    name = s["n"]
    rec = subs.get(name, {})
    a = article(name)
    w = a.get("wikitext", "") if a else ""
    routes = {}
    for rname, r in (rec.get("routes_of_administration") or {}).items():
        vals = {k: clean_val(r.get(k)) for k in ROUTE_KEYS}
        vals = {k: v for k, v in vals.items() if v}
        if vals:
            routes[rname] = vals
    # intro: first paragraph of plain text, short
    intro = ""
    if a and a.get("plain_text"):
        for para in a["plain_text"].split("\n"):
            para = para.strip()
            if len(para) > 80 and not para.startswith(("{", "|", "!", "[")):
                intro = re.sub(r"\[\d+\]", "", para)[:700]
                break
    # addiction / toxicity snippet
    tox = ""
    m = re.search(r"===\s*Dependence and abuse potential\s*===(.*?)(\n==)", w, flags=re.S)
    if m:
        tox = strip_wiki(m.group(1))[:500]
    substances.append({
        "n": name,
        "aka": [x for x in (rec.get("aliases") or [])][:12],
        "common": (rec.get("names") or {}).get("common", ""),
        "pc": (rec.get("classes") or {}).get("psychoactive", ""),
        "cc": (rec.get("classes") or {}).get("chemical", ""),
        "u": s["u"],
        "sh": s.get("sh") or [],
        "routes": routes,
        "ix": interactions(w),
        "intro": intro,
        "dep": tox,
    })

# effects
effects = []
for e in MAP["e"]:
    a = article(e["n"])
    desc = ""
    if a and a.get("plain_text"):
        for para in a["plain_text"].split("\n"):
            para = para.strip()
            if len(para) > 60 and not para.startswith(("{", "|", "!")):
                desc = re.sub(r"\[\d+\]", "", para)
                break
    if len(desc) > 420:
        cut = desc[:420].rsplit(". ", 1)[0]
        desc = cut + "." if len(cut) > 120 else desc[:420] + "…"
    url = by_title.get(e["n"], {}).get("url") or "https://psychonautwiki.org/wiki/" + e["n"].replace(" ", "_")
    effects.append({"n": e["n"], "s": e["s"], "t": e.get("t", ""), "d": desc, "u": url})

# reagent colour chart
reagents = {"columns": [], "rows": []}
a = article("Reagent testing kits")
if a:
    w = a["wikitext"]
    i = w.find("Color chart==")
    tbl = w[i:w.find("|}", i)]
    rows = re.split(r"\n\|-", tbl)
    head = rows[0] if "!Substance" in rows[0] else rows[1]
    hl = head[head.find("!Substance"):]
    cols = [c.strip() for c in re.split(r"!!|\n!", hl.lstrip("!")) if c.strip()]
    reagents["columns"] = cols[1:]
    for r in rows:
        r = r.strip()
        if not r.startswith("!") or r.startswith("!Substance"):
            continue
        lines = r.split("\n")
        subst = strip_wiki(lines[0].lstrip("!"))
        cells = []
        for ln in lines[1:]:
            ln = ln.strip()
            if not ln.startswith("|"):
                continue
            ln = ln.lstrip("|")
            colour = None
            m = re.match(r'\s*style="([^"]*)"\s*\|(.*)', ln)
            if m:
                bg = re.search(r"background:\s*(#[0-9A-Fa-f]{3,6})", m.group(1))
                grad = re.findall(r"#[0-9A-Fa-f]{6}", m.group(1))
                colour = bg.group(1) if bg else (grad or [None])[0]
                ln = m.group(2)
            cells.append({"t": strip_wiki(ln), "c": colour})
        while len(cells) < len(reagents["columns"]):
            cells.append({"t": "", "c": None})
        reagents["rows"].append({"s": subst, "r": cells[:len(reagents["columns"])]})

meta = {"source": "PsychonautWiki (psychonautwiki.org) site export, CC BY-SA 4.0",
        "license": "CC BY-SA 4.0", "built_from": "Mazhar knowledge base"}
for fn, data in [("substances.json", substances), ("effects.json", effects), ("reagents.json", reagents)]:
    json.dump({"meta": meta, "data": data}, open(OUT / fn, "w"), ensure_ascii=False, separators=(",", ":"))
    print(fn, len(data) if isinstance(data, list) else len(data["rows"]), (OUT / fn).stat().st_size // 1024, "KB")

# learning paths (D31d): curated reading lists over PsychonautWiki pages
PATHS = [
    ("basics", "Harm reduction basics", "Start here. What every person who uses or might use a substance should know.",
     ["Responsible drug use", "Set and setting", "Dosage", "Dosage classification", "Volumetric liquid dosing",
      "Dangerous combinations", "Reagent testing kits", "Substance overdose", "Recovery position"]),
    ("pharm", "How drugs work: pharmacology basics", "The science behind effects, doses and interactions.",
     ["Psychoactive substance index", "Routes of administration", "Neurotransmitter", "Receptor", "Agonist",
      "Serotonin", "Dopamine", "Noradrenaline", "GABA", "Glutamate", "MAOI"]),
    ("classes", "Drug classes", "The main families on the map and what sets them apart.",
     ["Psychedelic", "Dissociatives", "Stimulants", "Depressant", "Entactogen", "Opioids", "Cannabinoid", "Deliriant",
      "Substituted phenethylamines", "Substituted tryptamines", "Lysergamides"]),
    ("effects", "Understanding effects", "The vocabulary used in trip reports, from PsychonautWiki's Subjective Effect Index.",
     ["Subjective effect index", "Visual effects", "Cognitive effects", "Physical effects", "Geometry", "Hallucinatory states",
      "Increased introspection"]),
    ("care", "Looking after people", "Tripsitting, bad trips, and what to do afterwards.",
     ["Tripsitting index", "Psychedelic tripsitting", "Bad trip", "Psychedelic psychological first aid", "Serotonin syndrome",
      "Stimulant psychosis", "Hallucinogen persisting perception disorder", "Integration techniques"]),
    ("long", "Long-term use and getting help", "Tolerance, dependence, stopping safely, and support.",
     ["Substance withdrawal", "Tapering", "Addiction treatment resources", "Research chemicals"]),
]
learn = []
for pid, title, blurb, pages in PATHS:
    items = []
    for t in pages:
        a = article(t)
        if not a:
            print("learning path: missing", t)
            continue
        snip = ""
        for para in (a.get("plain_text") or "").split("\n"):
            para = para.strip()
            if len(para) > 80 and not para.startswith(("{", "|", "!", "[")):
                snip = re.sub(r"\[\d+\]", "", para)
                break
        if len(snip) > 300:
            snip = snip[:300].rsplit(" ", 1)[0] + "…"
        items.append({"t": t, "u": by_title[t]["url"], "d": snip})
    learn.append({"id": pid, "t": title, "d": blurb, "items": items})
json.dump({"meta": meta, "data": learn}, open(OUT / "learn.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("learn.json", sum(len(p["items"]) for p in learn), "pages")
