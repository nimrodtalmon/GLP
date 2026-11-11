"""Map: take the bylaws an LLM drew from the rules (map.json), check them, and write them into the record."""
import json
from . import rules
BASES = {'GCoop': 'gcoop', 'GDAO': 'gdao'}
STATUS = ['built', 'absorbed', 'not built', 'open', 'no clause']

def run(rows, map_path):
    m = json.load(open(map_path, encoding='utf8'))
    assert m['base'] in BASES, 'only the cooperative and the DAO are wired so far'
    for r in m['rules'].values():
        if 'policy' not in r: rules.validate(r)
    for act, name in m['acts'].items(): assert name in m['rules'], (act, name)
    ids = {r['id'] for r in rows}
    assert set(m['rows']) == ids, sorted(ids ^ set(m['rows']))
    for r in rows:
        x = m['rows'][r['id']]
        assert x['status'] in STATUS, x
        r['mapped_to'], r['status'], r['question'] = x['mapped_to'], x['status'], x.get('question', '')
    return m

def bylaws_table(m):
    out = ['| Act | Decided by | Rule |', '|---|---|---|']
    for act, name in m['acts'].items():
        r = m['rules'][name]
        who = m['roles'][str(r['policy'][1] if 'policy' in r else r['body'])] + 's'
        out.append('| %s | %s | %s |' % ('every other act' if act == '*' else m.get('act_names', {}).get(act, act), who, rules.describe(r, m['roles'])))
    return '\n'.join(out)
