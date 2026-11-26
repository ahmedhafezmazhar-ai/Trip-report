import json, re, collections, sys, os, glob
booklinks = {}
kb = sys.argv[1]  # knowledge-base root (local copy layout)
SE = "sources/psychonautwiki/site-export"
ix = json.load(open(f"{kb}/{SE}/index.json"))
subs = {s["title"]: s for s in json.load(open(f"{kb}/{SE}/substances.json"))}
def item(i): return {"name": i["title"], "id": i["id"], "file": f"{SE}/{i['file']}" if i.get("file") else None, "url": i["url"]}
def tree(): return collections.defaultdict(lambda: collections.defaultdict(list))
PSY = ["Psychedelic","Dissociative","Deliriant","Entactogen","Stimulant","Depressant","Opioid","Cannabinoid","Nootropic","Hallucinogen","Antipsychotic","Oneirogen","Antidepressant","Anxiolytic","Eugeroic"]
def first(v): return re.split(r"\s*/\s*|,\s*|\s+and\s+", v.strip())[0] if v and v.strip() else None
def norm(v): return re.sub(r"\s*\(.*?\)", "", v).strip() if v else v
T = {}
# 1 substances
t = tree()
for i in ix:
    if i["type"] != "substance": continue
    s = subs[i["title"]]; cl = s["classes"] or {}
    fam = norm(first(cl.get("psychoactive")))
    if not fam: fam = next((p for p in PSY if p in i["categories"]), "Unclassified")
    br = norm(first(cl.get("chemical"))) or "Chemical class not given"
    it = item(i); it["psychoactive_class"] = cl.get("psychoactive"); it["chemical_class"] = cl.get("chemical")
    t[fam + "s" if not fam.endswith("s") and fam != "Unclassified" else fam][br].append(it)
T["Substances"] = t
# 2 effects
SENSE = [("Visual","Visual effects"),("Auditory","Auditory effects"),("Tactile","Tactile effects"),("Gustatory","Gustatory effects"),("Olfactory","Olfactory effects"),("Multisensory","Multisensory effects"),("Cognitive","Cognitive effects"),("Physical","Physical effects"),("Bodily","Physical effects"),("Cardiovascular","Physical effects"),("Transpersonal","Transpersonal effects"),("Effect group","Effect groups")]
MODE = ["Enhancement","Suppression","Intensification","Depression","Distortion","Alterations","Hallucinatory","Geometric","Novel","Disconnective","Amplification","Cardiovascular","Cerebrovascular","Uncomfortable","Bodily"]
t = tree()
for i in ix:
    if i["type"] != "effect": continue
    c = i["categories"]
    fam = next((f for k, f in SENSE if k in c), None)
    if not fam:
        m = re.match(r"(\w+) effects - ", i["title"]); fam = f"{m.group(1)} effects" if m else "Other effects"
    br = next((m for m in MODE if m in c), "General")
    t[fam][br].append(item(i))
T["Subjective effects"] = t
# 3 harm reduction
HR = [("Tripsitting & first aid", r"tripsitting|first aid|Reality tests|Integration|Bad trip|Aborting|Set and setting|Stimfapping"),
      ("Antidotes", r"antidotes"), ("Dosage & measurement", r"Dosage|Volumetric|overdose"),
      ("Drug checking", r"Reagent|Checking Day|Research chemicals"),
      ("Health risks & emergencies", r"Serotonin|psychosis|Recovery position|Dangerous combinations|Cotton fever"),
      ("Injection safety", r"injection|Needle"), ("Addiction & withdrawal", r"Tapering|withdrawal|Cold turkey|Addiction")]
t = tree()
for i in ix:
    if i["type"] != "responsible-use": continue
    fam = next((f for f, rx in HR if re.search(rx, i["title"], re.I)), "General harm reduction")
    sub = "Psychological first aid" if "first aid" in i["title"] else ("By substance class" if re.search(r"\w+ (tripsitting|antidotes)$", i["title"]) else "Guides")
    t[fam][sub].append(item(i))
cur = json.load(open(f"{kb}/sources/psychonautwiki/responsible-drug-use/manifest.json"))
for f in cur["files"]:
    if f["category"] in ("overview","general-harm-reduction","hallucinogens"):
        t["Curated article: Responsible drug use"]["Hallucinogens" if f["category"]=="hallucinogens" else "General"].append(
            {"name": f["title"], "id": "pw-rdu:" + f["path"], "file": "sources/psychonautwiki/responsible-drug-use/" + f["path"], "url": cur["source"]["canonical_url"]})
T["Harm reduction & safety"] = t
# 4 classes
t = tree()
for i in ix:
    if i["type"] == "substance-class":
        fam = "Psychoactive classes" if "Psychoactive class" in i["categories"] or i["title"].rstrip("s") in PSY else "Chemical classes"
        t[fam]["All"].append(item(i))
T["Substance classes"] = t
# 5 plants
t = tree()
for i in ix:
    if i["type"] != "plants-and-fungi": continue
    c = i["categories"]
    fam = next((x for x in c if x.endswith("(family)")), None) or ("Fungi" if any(k in c for k in ("Mycology","Mushroom","Psilocybin containing mushroom")) or any("Psilocybe" in x or "Amanita" in x or "Panaeolus" in x for x in c) else "Other plants")
    br = next((x for x in c if x.endswith("(genus)")), "General")
    t[fam][br].append(item(i))
T["Plants & fungi"] = t
# 6 preparation
PR = [("Extraction", r"extract|tek|wash|salting|Changa|brewing|solution"), ("Cultivation", r"cultivat|growing|Spore"), ("Recipes", r"brownies|chocolate|Recipes"), ("Synthesis & conversion", r"Synthesis|Conversion|conversion|synthesis"), ("Administration & handling", r"spray|Vaporizing|Drying|LSD stable")]
t = tree()
for i in ix:
    if i["type"] != "preparation": continue
    fam = next((f for f, rx in PR if re.search(rx, i["title"])), "Other preparation")
    t[fam]["All"].append(item(i))
T["Preparation"] = t
# 7,8 science / psychonautics
for typ, name, keys in [("pharmacology-and-science","Pharmacology & science",["Neurotransmitter","Hormone","Pharmacology","Neuroscience","Chemistry"]),("psychonautics","Psychonautics",["Oneironautics","Psychonautics","Transpersonal","Philosophy","Spirituality"])]:
    t = tree()
    for i in ix:
        if i["type"] == typ: t[next((k for k in keys if k in i["categories"]), "General")]["All"].append(item(i))
    T[name] = t
# 9 reference
t = tree()
for typ, fam in [("lists-and-indexes","Lists & indexes"),("experience-reports-index","Trip report indexes"),("substance-summary","Substance summary pages"),("site-meta","Wiki housekeeping"),("other","Other articles")]:
    for i in ix:
        if i["type"] == typ:
            br = "All"
            if typ == "other": br = "Stubs" if "Stub" in i["categories"] else ("Uncategorized" if not i["categories"] else "Categorized")
            t[fam][br].append(item(i))
T["Reference & other"] = t

# 10 books
bk = {}
for folder, label in [("tihkal-es", "TiHKAL (Spanish ed.)"), ("shulgin-index-vol1", "Shulgin Index Vol. 1")]:
    fp = f"{kb}/sources/books/{folder}/compounds.jsonl"
    if not os.path.exists(fp): continue
    t = tree()
    for l in open(fp):
        r = json.loads(l); m = r["psychonautwiki_match"]
        nm = r.get("name") or r.get("code")
        files = {json.load(open(f))["id"]: f for f in glob.glob(f"{kb}/sources/books/{folder}/compounds/*.json")} if not bk.get(folder) else bk[folder]
        bk[folder] = files
        it = {"name": f"#{r['entry_number']} {nm}", "id": r["id"], "file": os.path.relpath(files[r["id"]], kb), "url": m["url"] if m else None, "psychonautwiki": m["title"] if m else None}
        t["Also on PsychonautWiki" if m else "Only in this book"]["All"].append(it)
        if m:
            booklinks.setdefault(m["title"], []).append({"book": label, "entry": r["entry_number"], "id": r["id"]})
    T.setdefault("Shulgin books", {})[label] = t

def build(name, node, depth):
    if isinstance(node, list):
        return {"name": name, "count": len(node), "items": sorted(node, key=lambda x: x["name"].lower())}
    kids = [build(k, v, depth+1) for k, v in node.items()]
    # collapse single "All" level
    kids = [ {"name": k["name"], "count": k["count"], "items": k["children"][0]["items"]} if k.get("children") and len(k["children"]) == 1 and k["children"][0]["name"] in ("All",) else k for k in kids]
    kids.sort(key=lambda k: -k["count"])
    return {"name": name, "count": sum(k["count"] for k in kids), "children": kids}
for fam in T.values():
    pass
def attach(n):
    for it in n.get("items", []):
        if it["name"] in booklinks and it.get("id", "").startswith("psychonautwiki:"): it["books"] = booklinks[it["name"]]
    for k in n.get("children", []): attach(k)
root = build("Mazhar knowledge base", T, 0)
attach(root)
root["aliases"] = sum(1 for i in ix if i["type"] == "redirect")
root["generated"] = "2026-11-25"
root["note"] = "Families and branches are an organizing layer over the sources; each item links to its source file and original URL."
json.dump(root, open(f"{kb}/taxonomy.json", "w"), ensure_ascii=False, indent=1)
def pr(n, d=0):
    if d < 3: print("  "*d + f"{n['name']} ({n['count']})")
    for k in n.get("children", []): pr(k, d+1)
pr(root)
