import json, re, os, shutil
os.chdir(os.path.expanduser('~/kb'))
A = {}
for l in open('articles.jsonl'):
    a = json.loads(l); A[a['id']] = a
IX = {i['id']: i for i in json.load(open('index.json'))}
SUB = {s['id']: s for s in json.load(open('substances.json'))}
T = json.load(open('taxonomy.json'))
SKIP = {'psychonautwiki:7344'}  # vandalism page flagged in the export README

def blocks_from_plain(a):
    heads = [(len(m.group(1)), re.sub(r"'{2,}|\[\[|\]\]", '', m.group(2)).strip())
             for m in re.finditer(r'^(={2,6})\s*(.*?)\s*=+\s*$', a.get('wikitext') or '', re.M)]
    out = []; hp = 0
    for para in re.split(r'\n\s*\n', a.get('plain_text') or ''):
        p = '\n'.join(x.strip() for x in para.strip().split('\n') if x.strip())
        if not p: continue
        hit = None
        if '\n' not in p and len(p) < 90:
            for j in range(hp, min(hp + 6, len(heads))):
                if heads[j][1] == p: hit = j; break
        if hit is not None:
            out.append('\x01%d%s' % (min(heads[hit][0], 4), p)); hp = hit + 1
        else: out.append(p)
    return out

def blocks_from_md(path):
    s = open(path).read()
    s = re.sub(r'^---\n.*?\n---\n', '', s, flags=re.S)
    s = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', s)
    s = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', s)
    s = re.sub(r'\[\^?\d+\]', '', s)
    s = re.sub(r'\*\*|__', '', s)
    s = re.sub(r'^>\s?', '', s, flags=re.M)
    s = re.sub(r'(?<!\w)\*([^*\n]+)\*', r'\1', s)
    out = []
    for para in re.split(r'\n\s*\n', s):
        p = para.strip()
        if not p or p.startswith('Image:'): continue
        m = re.match(r'^(#{1,6})\s+(.*)$', p)
        if m and '\n' not in p: out.append('\x01%d%s' % (min(len(m.group(1)) + 1, 4), m.group(2)))
        else: out.append(re.sub(r'^\s*[-*]\s+', '• ', p, flags=re.M))
    return out

DOSE = ['threshold', 'light', 'common', 'strong', 'heavy']
TIME = ['onset', 'comeup', 'peak', 'offset', 'duration', 'aftereffects']
def box(s):
    b = {}
    n = s.get('names') or {}; c = s.get('classes') or {}
    if n.get('common'): b['common'] = n['common']
    if n.get('substitutive'): b['subst'] = n['substitutive']
    if n.get('systematic'): b['syst'] = n['systematic']
    if c.get('psychoactive'): b['psy'] = c['psychoactive']
    if c.get('chemical'): b['chem'] = c['chemical']
    routes = []
    for rn, rv in (s.get('routes_of_administration') or {}).items():
        if not rv.get('enabled'): continue
        clean = lambda v: '' if not v or re.search(r'\bx\b', v) else v.strip()
        d = [clean(rv.get(k)) for k in DOSE]; t = [clean(rv.get(k)) for k in TIME]
        r = {'r': rn}
        if any(d): r['d'] = d
        if any(t): r['t'] = t
        if clean(rv.get('microdose')): r['m'] = clean(rv['microdose'])
        if clean(rv.get('bioavailability')): r['b'] = clean(rv['bioavailability'])
        if len(r) > 1: routes.append(r)
    if routes: b['routes'] = routes
    if s.get('substance_box_missing_from_export'): b['missing'] = 1
    return b

pages = []; content = []
title_to_idx = {}
def conv(n, fam=None):
    o = {'n': n['name']}
    if n.get('children'):
        o['k'] = [conv(k) for k in n['children']]
        o['k'] = [k for k in o['k'] if k['c']]
        o['c'] = sum(k['c'] for k in o['k'])
    else:
        idx = []
        for it in sorted(n.get('items') or [], key=lambda x: x['name'].lower()):
            if it['id'] in SKIP: continue
            p = {'t': it['name'], 'u': it['url']}
            c = {}
            if it['id'].startswith('pw-rdu:'):
                c['x'] = blocks_from_md('rdu/' + it['id'][7:]); p['y'] = 'curated'
            else:
                a = A[it['id']]; i = IX[it['id']]
                c['x'] = blocks_from_plain(a); p['y'] = a['type']
                if i.get('aliases'): p['a'] = i['aliases']
                if i.get('last_edited'): p['e'] = i['last_edited'][:10]
                if it['id'] in SUB:
                    b = box(SUB[it['id']])
                    if b: c['b'] = b
                    cm = (SUB[it['id']].get('names') or {}).get('common')
                    if cm: p['a'] = list(dict.fromkeys((p.get('a') or []) + [x.strip() for x in cm.split(',') if x.strip() and x.strip() != it['name']]))
            if not c['x']: p['z'] = 1  # no stored text
            title_to_idx.setdefault(it['name'], len(pages))
            idx.append(len(pages)); pages.append(p); content.append(c)
        o['i'] = idx; o['c'] = len(idx)
    return o
tree = conv(T)
tree['k'].sort(key=lambda k: (k['n'].startswith('Reference'), -k['c']))
# summary stubs point to their main page
for i, p in enumerate(pages):
    if p['t'].endswith('/Summary'):
        m = title_to_idx.get(p['t'][:-8])
        if m is not None: p['m'] = m
# shards
shutil.rmtree('out/text', ignore_errors=True); os.makedirs('out/text')
shard = {}; size = 0; sn = 0
def flush():
    global shard, size, sn
    if shard:
        json.dump(shard, open('out/text/%02d.json' % sn, 'w'), ensure_ascii=False, separators=(',', ':')); sn += 1
    shard = {}; size = 0
for i, c in enumerate(content):
    s = len(json.dumps(c, ensure_ascii=False))
    if size and size + s > 140000: flush()
    pages[i]['s'] = sn; shard[str(i)] = c; size += s
flush()
json.dump({'tree': tree, 'pages': pages, 'aliases': T['aliases'], 'generated': T['generated']},
          open('out/map.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(pages), 'pages', sn, 'shards', os.path.getsize('out/map.json'), sum(os.path.getsize('out/text/' + f) for f in os.listdir('out/text')))
print(sum(1 for p in pages if p.get('z')), 'no text;', sum(1 for c in content if c.get('b', {}).get('routes')), 'with routes')
h = sum(1 for c in content for x in c['x'] if x[0] == '\x01'); print('headings', h)
