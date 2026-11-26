import re, os, sys, json, shutil
dl, out = sys.argv[1], sys.argv[2]
t = open(f"{dl}/clean.md").read()
# --- extra fixes ---
t = t.replace("### Aborting trips\n\n- [Hallucinogens]", "### Aborting trips\n\n[Hallucinogens]")
t = re.sub(r"(### Aborting trips\n\n.*?)(?=\n## )", lambda m: re.sub(r"^  ", "", m.group(1), flags=re.M), t, flags=re.S)
t = re.sub(r"(\[TripSit\.me\]\([^)]*\))\n\n\.\n", r"\1.\n", t)
t = re.sub(r"^(\*\*Image:\*\* .*\))\n(?!\n)", r"\1  \n*Caption:* ", t, flags=re.M)
t = t.replace("**[Responsible drug use index](https://psychonautwiki.org/wiki/Responsible_use)**", "").rstrip()+"\n"
# references: anchors, drop backlinks
def refline(m):
    n, rest = m.group(1), m.group(2)
    rest = re.sub(r"^\[↑\]\(#cite_ref-[^)]*\)\s*", "", rest)
    rest = re.sub(r"^↑\s*(\^\(\[[\d.]+\]\(#cite_ref-[^)]*\)\)\s*)+", "", rest)
    return f'{n}. <a id="ref-{n}"></a>{rest.rstrip()}'
t = re.sub(r"^(\d+)\.\s+(.*)$", refline, t, flags=re.M)
full = t
def cites(text, rel):
    def rep(m):
        nums = re.findall(r"\\\[(\d+)\\\]", m.group(0))
        return "<sup>" + "".join(f"[[{n}]]({rel}#ref-{n})" for n in nums) + "</sup>"
    return re.sub(r"\^\((?:\[\\\[\d+\\\]\]\(#cite_note-[^)]*\))+\)", rep, text)

SRC = {
 "title": "Responsible drug use",
 "site": "PsychonautWiki",
 "requested_url": "https://psychonautwiki.org/wiki/Harm_reduction_practices",
 "canonical_url": "https://psychonautwiki.org/wiki/Responsible_drug_use",
 "note": "The requested URL redirects to the canonical article.",
 "revision_id": 168206,
 "last_edited": "2025-07-13 18:14 UTC (by David Hedlund)",
 "fetched": "2026-11-25",
 "license": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
}
def header(title, category, tags, anchor=None):
    url = SRC["canonical_url"] + (f"#{anchor}" if anchor else "")
    return (f"---\ntitle: \"{title}\"\nsource: \"{SRC['site']}: {SRC['title']}\"\nsource_url: {url}\n"
            f"requested_url: {SRC['requested_url']}\nrevision_id: {SRC['revision_id']}\nlast_edited: \"{SRC['last_edited']}\"\n"
            f"fetched: {SRC['fetched']}\nlicense: \"{SRC['license']}\"\ncategory: {category}\ntags: [{', '.join(tags)}]\n"
            f"fidelity: verbatim (article text unchanged; wiki links made absolute, section icons and edit links removed)\n---\n\n")

def section(start, end_pat):
    i = t.index(start)
    m = re.compile(end_pat, re.M).search(t, i + len(start))
    return t[i: m.start() if m else len(t)].strip()+"\n"

files = []
def write(rel, title, category, tags, body, anchor=None):
    depth = rel.count("/")
    body = cites(body, "../"*depth + "references.md")
    p = f"{out}/{rel}"; os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(header(title, category, tags, anchor) + body)
    files.append((rel, title, category, tags))

overview = t[: t.index("## Contents")].strip()
t = re.sub(r"^(> \*\[Main article:.*)\n(?!\n)", r"\1\n\n", t, flags=re.M)
write("00-overview.md", "Overview: what responsible drug use is + general harm reduction advice", "overview",
      ["harm-reduction","philosophy","general-advice"], "# Responsible drug use (overview)\n\n" + overview + "\n")

G = [("Dosage","dosage",["dosage","choosing-dose","allergy-testing","eyeballing","milligram-scales","volumetric-dosing"],"Dosage"),
     ("Routes of administration","routes-of-administration",["routes-of-administration","oral","sublingual","inhalation","injection","insufflation","nbome"],"Routes_of_administration"),
     ("Recovery position","recovery-position",["first-aid","recovery-position","overdose","respiratory-depression","vomiting"],"Recovery_position"),
     ("Reagent testing kits","reagent-testing-kits",["drug-checking","reagent-testing","adulteration","nbome","lsd"],"Reagent_testing_kits"),
     ("Dangerous combinations","dangerous-combinations",["interactions","combinations","depressants","prescription-medication"],"Dangerous_combinations"),
     ("Effects","effects-research",["effects","research","duration","trip-reports"],"Effects"),
     ("Addiction","addiction",["addiction","stimulants","opioids","depressants","hallucinogens"],"Addiction")]
for n,(name,slug,tags,anchor) in enumerate(G,1):
    head = re.search(r"^### (\[)?" + re.escape(name), t, re.M).group(0)
    body = section(head, r"^(### |## )")
    write(f"general/{n:02d}-{slug}.md", name, "general-harm-reduction", tags, "# General › " + body.lstrip("# "), anchor)

hi = section("## Hallucinogens", r"^### ")
write("hallucinogens/00-intro.md", "Hallucinogens: scope of this section", "hallucinogens", ["hallucinogens","psychedelics","dissociatives","deliriants"], "# Hallucinogens\n" + hi[len("## Hallucinogens"):])
H = [("Setting","setting",["set-and-setting","environment","preparation"],"Setting"),
     ("Set (State of mind)","set-state-of-mind",["set-and-setting","mindset","mental-health","letting-go"],"Set_.28State_of_mind.29"),
     ("Bodily state","bodily-state",["physical-state","body-load","preparation"],"Bodily_state"),
     ("Trip sitters","trip-sitters",["trip-sitter","safety","supervision"],"Trip_sitters"),
     ("Anchors","anchors",["anchors","grounding","ego-death","bad-trip"],"Anchors"),
     ("Aborting trips","aborting-trips",["aborting-trips","benzodiazepines","antipsychotics","bad-trip","panic"],"Aborting_trips")]
for n,(name,slug,tags,anchor) in enumerate(H,1):
    head = re.search(r"^### (\[)?" + re.escape(name), t, re.M).group(0)
    body = section(head, r"^(### |## )")
    write(f"hallucinogens/{n:02d}-{slug}.md", name, "hallucinogens", tags, "# Hallucinogens › " + body.lstrip("# "), anchor)

refs = "# See also, external links and references\n\n" + section("## See also", r"^## External links") + "\n" + section("## External links", r"^## References") + "\n" + section("## References", r"^\Z")
write("references.md", "See also, external links and references", "references", ["references","citations","external-links"], refs, "References")
write("full-page.md", "Full page (single file, complete)", "full-page", ["complete"], "# Responsible drug use\n\n" + cites(full, "references.md").replace("](#ref-", "](references.md#ref-").replace("references.md#ref-","#ref-"))
json.dump({"source": SRC, "files": [dict(path=f, title=ti, category=c, tags=tg) for f,ti,c,tg in files]}, open(f"{out}/manifest.json","w"), indent=2)
print("\n".join(f[0] for f in files))
