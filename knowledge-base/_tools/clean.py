import re, sys
BASE = "https://psychonautwiki.org"
src = open(sys.argv[1]).read()
lines = src.split("\n")
ICONS = {"Balance-scale.svg","Medkit.svg","Eyedropper.svg","Ambulance.svg","Eye.svg","Line-chart.svg","Home.svg","User.svg","Child.svg","Users.svg","Anchor.svg","Thumbs-down.svg","Warning.svg"}
out = []
i = 0
# pass 1: de-layout lists
while i < len(lines):
    l = lines[i]
    if l.startswith("- - "):
        out.append("- " + l[4:]); i += 1; continue
    if l.startswith("- ") and not l.startswith("- ["+"1") :
        body = l[2:]
        nxt = next((x for x in lines[i+1:] if x.strip()), "")
        layout = (body.startswith(("|", "[![", "####", "*[Main")) or len(body) > 150 or nxt.startswith("- - ") or (nxt.startswith("  ") and not nxt.startswith("  -")) or nxt.startswith("  - "))
        if layout and not body.startswith("[") or body.startswith("[!["):
            out.append(body); i += 1
            while i < len(lines) and (lines[i].startswith("  ") or lines[i] == ""):
                if lines[i].startswith("- "): break
                out.append(lines[i][2:] if lines[i].startswith("  ") else lines[i]); i += 1
            continue
    out.append(l); i += 1
t = "\n".join(out)
# main-article table boxes -> blockquote
t = re.sub(r"^\|[ \t]+\|[ \t]*\n\|-+\|[ \t]*\n\| (\*\[Main article:.*?\)\*) +\|[ \t]*$", r"> \1", t, flags=re.M)
t = re.sub(r"^\|\s+\|\s*$\n", "", t, flags=re.M)
t = re.sub(r"^(\*\[Main article:.*\)\*)$", r"> \1", t, flags=re.M)
# edit links
t = re.sub(r"\\\[\[edit\]\(.*?\) \\\| \[edit source\]\(.*?\)\\\]", "", t)
# enlarge links
t = re.sub(r"^\[\]\(/wiki/File:.*?\"Enlarge\"\)\s*$\n?", "", t, flags=re.M)
# decorative icons
t = re.sub(r"^!\[([^\]]+)\]\(https://psychonautwiki.org/w/thumb.php\?f=[^)]*\)\s*$\n?", lambda m: "" if m.group(1) in ICONS else m.group(0), t, flags=re.M)
# images -> labelled
def img(m):
    thumb, f = m.group(1), m.group(2)
    return f"**Image:** [{f.replace('%27',chr(39))}]({BASE}/wiki/File:{f}) ([thumbnail]({thumb}))"
t = re.sub(r"\[!\[\]\((.*?)\)\]\(/wiki/File:(.*?)\)", img, t)
# relative links -> absolute, drop titles
t = re.sub(r"\]\((/(?:wiki|w)/[^ )]*)(?: \"[^\"]*\")?\)", lambda m: f"]({BASE}{m.group(1)})", t)
t = re.sub(r"\]\((#cite_[^)]*)\)", r"](\1)", t)
# whitespace-only lines and collapse blank runs
t = re.sub(r"^[ \t]+$", "", t, flags=re.M)
t = re.sub(r"\n{3,}", "\n\n", t)
# heading trailing spaces
t = re.sub(r"^(#+ .*?)[ \t]+$", r"\1", t, flags=re.M)
open(sys.argv[2], "w").write(t.strip()+"\n")
