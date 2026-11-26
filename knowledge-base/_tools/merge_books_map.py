import json, sys, os
art, kb = sys.argv[1], sys.argv[2]
d = json.load(open(os.path.join(art, 'map.json')))
tax = json.load(open(os.path.join(kb, 'taxonomy.json')))
assert not any(f['n'] == 'Shulgin books' for f in d['tree']['k']), 'already merged'
recs = {}
for p in ['sources/books/tihkal-es/compounds.jsonl', 'sources/books/shulgin-index-vol1/compounds.jsonl']:
    for line in open(os.path.join(kb, p)):
        r = json.loads(line); recs[r['id']] = r
pages = d['pages']; shards = {}
H = lambda lv, t: '\x01' + str(lv) + t
def fmt_range(a, b, u):
    if a is None: return None
    return f"{a:g}{u}" if a == b else f"{a:g}–{b:g}{u}"
def blocks(r):
    x = []; c = r['citation']
    if r['id'].startswith('tihkal'):
        x.append(f"TiHKAL (Spanish edition), entry n.º {r['entry_number']}. {c.get('book','')}, pages {c['file_pages'][0]}–{c['file_pages'][1]} of the file.")
        x.append(H(2, 'Dosage and duration'))
        x.append(f"Dosage: {r.get('dosage_raw') or 'not given'}" + (f" (route: {r['route']})" if r.get('route') else ''))
        x.append(f"Duration: {r.get('duration_raw') or 'not given'}")
        qc = r.get('qualitative_comments') or []
        if qc:
            x.append(H(2, 'Qualitative comments (Spanish, quoted from the book)'))
            for q in qc: x.append(f"{q.get('dose_and_route','')}: {q.get('report','')}".strip(': '))
        al = [a for a in (r.get('aliases_from_book_index') or []) if a.strip(', ')]
    else:
        x.append(f"The Shulgin Index Vol. 1 (2011), entry #{r['entry_number']} ({r['code']}), page {c['pages'][0]}" + (f"–{c['pages'][1]}" if c['pages'][1] != c['pages'][0] else '') + ".")
        x.append(H(2, 'Human activity'))
        st = r.get('human_activity_statements') or []
        x.extend(st if st else ['The book gives no human dose for this compound.'])
        dp, tp = r.get('human_activity_dosage_parsed'), r.get('human_activity_duration_parsed')
        if dp or tp:
            x.append('Parsed: ' + '; '.join(filter(None, [dp and 'dose ' + fmt_range(dp['min_mg'], dp['max_mg'], ' mg'), tp and 'duration ' + fmt_range(tp['min_h'], tp['max_h'], ' h')])))
        if r.get('legal_status_raw'):
            x.append(H(2, 'Legal status (as printed, 2011)')); x.append(r['legal_status_raw'].replace('�', '').strip())
        x.append(r['ocr_note'])
        al = [a for a in (r.get('names') or []) if a.strip(', ')]
    if al:
        x.append(H(2, 'Names in the book')); x.append(', '.join(al))
    m = r.get('psychonautwiki_match'); cmp = r.get('comparison_with_psychonautwiki')
    x.append(H(2, 'Compared with PsychonautWiki'))
    if not m: x.append('No matching PsychonautWiki page.')
    else:
        x.append(f"Matches the PsychonautWiki page “{m['title']}”.")
        if cmp:
            if cmp.get('status'): x.append('Result: ' + cmp['status'] + '.')
            for f in cmp.get('flags') or []: x.append('Flag: ' + f + '.')
            pw = cmp.get('pw_oral')
            if pw: x.append('PsychonautWiki oral: ' + ', '.join(f"{k} {v}" for k, v in pw.items() if v))
    x.append(H(2, 'Rights'))
    x.append(r['source'].get('rights', 'Copyrighted book, not CC BY-SA.'))
    x.append(f"Full structured record in the knowledge base: {r['id']}.")
    return x
fam = {'n': 'Shulgin books', 'k': []}; total = 0
src = [f for f in tax['children'] if f['name'] == 'Shulgin books'][0]
order = sorted(src['children'], key=lambda b: 0 if b['name'].startswith('TiHKAL') else 1)
for si, br in enumerate(order):
    shard = 42 + si; shards[shard] = {}
    node = {'n': br['name'], 'k': [], 'c': 0}
    for sub in br['children']:
        leaf = {'n': sub['name'], 'i': [], 'c': 0}
        for it in sorted(sub['items'], key=lambda it: recs[it['id']]['entry_number']):
            r = recs[it['id']]
            name = r['name'] if 'name' in r else r['code']
            al = [a for a in (r.get('aliases_from_book_index') or r.get('names') or []) if a.strip(', ')][:6]
            m = r.get('psychonautwiki_match')
            if m and m['title'] not in al: al = [m['title']] + al
            pg = {'t': f"#{r['entry_number']} {name}", 'u': m['url'] if m else None, 'y': 'book-entry', 'a': al, 's': shard}
            idx = len(pages); pages.append(pg); leaf['i'].append(idx)
            shards[shard][str(idx)] = {'x': blocks(r)}
        leaf['c'] = len(leaf['i']); node['k'].append(leaf); node['c'] += leaf['c']
    fam['k'].append(node); total += node['c']
fam['c'] = total
d['tree']['k'].append(fam); d['tree']['c'] += total
d['aliases'] = d['aliases'] + sum(len(p['a']) for p in pages[-total:])
os.makedirs(os.path.join(art, 'text'), exist_ok=True)
json.dump(d, open(os.path.join(art, 'map.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
for s, v in shards.items():
    json.dump(v, open(os.path.join(art, 'text', f'{s:02d}.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('added', total, 'pages; root', d['tree']['c'], 'aliases', d['aliases'])
