import re, sys, json, urllib.parse
dl, out = sys.argv[1], sys.argv[2]
B="https://psychonautwiki.org/wiki/"
nb=open(f"{dl}/navbox.wikitext").read()
def link(m):
    tgt, _, lab = m.group(1).partition("|")
    lab = lab or tgt
    return f"[{lab}]({B}{urllib.parse.quote(tgt.strip().replace(' ','_'), safe='#()_-,.:')})"
groups = re.findall(r"\| group(\d+) = (.*?)\n\|  list\1 = (.*?)\n", nb)
man=json.load(open(f"{out}/manifest.json")); S=man["source"]
hdr=lambda title,cat,tags: (f"---\ntitle: \"{title}\"\nsource: \"PsychonautWiki: Template:Responsible use2 (navigation box shown at the bottom of the article)\"\nsource_url: https://psychonautwiki.org/wiki/Template:Responsible_use2\nfetched: {S['fetched']}\nlicense: \"{S['license']}\"\ncategory: {cat}\ntags: [{', '.join(tags)}]\nfidelity: verbatim (every link in the box, in order)\n---\n\n")
o=hdr("Responsible drug use index (related pages)","related-pages",["navigation","related-pages","to-fetch"])
o+="# Responsible drug use index (navigation box)\n\nThis box appears at the bottom of the article and links every related harm reduction page on PsychonautWiki. It is a ready-made list of candidate pages to extract next.\n\n"
for n,g,l in groups:
    g=re.sub(r"\[\[(.*?)\]\]",link,g).replace("'''","")
    o+=f"## {re.sub(r'\[(.*?)\]\(.*?\)',r'\1',g)}\n\n"
    l2=re.sub(r"\s*\}\}\s*$","",l); items=[];d=0;cur=""
    for ch_i,ch in enumerate(l2):
        d+= (ch=="(")-(ch==")")
        if d==0 and l2[ch_i:ch_i+3]==" • ": items.append(cur); cur=""; continue
        if d==0 and l2[ch_i-2:ch_i+1]==" • " : continue
        cur+=ch
    items.append(cur); items=[x.strip(" •") for x in items]
    for it in items:
        it=re.sub(r"\[\[(.*?)\]\]",link,it).replace("''","*")
        o+=f"- {it}\n"
    o+="\n"
open(f"{out}/related-pages.md","w").write(o)
man["files"].append(dict(path="related-pages.md",title="Responsible drug use index (related pages)",category="related-pages",tags=["navigation","related-pages","to-fetch"]))
# media
p=json.load(open(f"{dl}/parse.json"))["parse"]
icons={"Balance-scale.svg":"Dosage","Medkit.svg":"Recovery position","Eyedropper.svg":"Reagent testing kits","Ambulance.svg":"Dangerous combinations","Eye.svg":"Effects","Line-chart.svg":"Addiction","Home.svg":"Setting","User.svg":"Set (State of mind)","Child.svg":"Bodily state","Users.svg":"Trip sitters","Anchor.svg":"Anchors","Thumbs-down.svg":"Aborting trips","Warning.svg":"Responsible drug use index box"}
caps={}
full=open(f"{out}/full-page.md").read()
for m in re.finditer(r"\*\*Image:\*\* \[(.*?)\]\((.*?)\).*?\n\*Caption:\* (.*)",full):
    caps[m.group(1)]=(m.group(2),m.group(3))
m=hdr("Media (images) on the page","media",["images","media"]).replace("Template:Responsible use2 (navigation box shown at the bottom of the article)",S['title']).replace("https://psychonautwiki.org/wiki/Template:Responsible_use2",S['canonical_url']).replace("every link in the box, in order","every image on the page; captions verbatim")
m+="# Media on the page\n\n## Content images (with captions)\n\n| File | Caption (verbatim) |\n|---|---|\n"
for k,(u,c) in caps.items(): m+=f"| [{k}]({u}) | {c.replace('|','\\|').replace('](#ref-','](references.md#ref-')} |\n"
m+="\n## Decorative section icons\n\n| Icon file | Used beside |\n|---|---|\n"
for k,v in icons.items(): m+=f"| [{k}]({B}File:{k}) | {v} |\n"
open(f"{out}/media.md","w").write(m)
man["files"].append(dict(path="media.md",title="Media (images) on the page",category="media",tags=["images","media"]))
json.dump(man,open(f"{out}/manifest.json","w"),indent=2)
print(len(caps), [i for i in p["images"] if i not in icons and i.replace("%27","'") not in caps and i not in caps])
