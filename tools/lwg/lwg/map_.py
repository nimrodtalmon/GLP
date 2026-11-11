"""Map: take the bylaws an LLM drew from the rules (map.json), check them, and write them into the record."""
import json
from . import rules
BASES = {'GCoop': 'gcoop'}
STATUS = ['built', 'absorbed', 'not built', 'open', 'no clause']

def run(rows, map_path):
    m = json.load(open(map_path, encoding='utf8'))
    assert m['base'] in BASES, 'only the cooperative is wired so far'
    for r in m['rules'].values(): rules.validate(r)
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
        out.append('| %s | %ss | %s |' % ('every other act' if act == '*' else act, m['roles'][str(r['body'])], rules.english(r, m['roles'])))
    return '\n'.join(out)
