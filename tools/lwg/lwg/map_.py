"""Map: take the bylaws an LLM drew from the rules (map.json), check them, and write them into the record."""
import json
from . import rules
BASES = {'GCoop': 'gcoop', 'GDAO': 'gdao'}
STATUS = ['built', 'absorbed', 'not built', 'open', 'no clause']
ACTS = {'*': 'every other act', 'coop_join': 'admit a member', 'dao_join': 'admit a member', 'expel': 'expel a member', 'appoint': 'appoint to a role',
        'dismiss': 'dismiss from a role', 'coop_board': 'elect a member to the board', 'amend': 'amend the bylaws'}
KIND = {'GCoop': 'a cooperative', 'GDAO': 'a DAO'}

def compose(m):
    """The contract's wording, where the bylaws do not carry their own: a definition drawn from the table of acts, the names, and the clauses."""
    if 'definition' in m: return m
    body = lambda r: m['roles'][str(r['policy'][1] if 'policy' in r else r['body'])] + 's'
    parts = ['the %s decide %s when {%s}' % (body(m['rules'][r]), 'every other act of the organization' if a == '*' else 'to ' + ACTS[a], r) for a, r in sorted(m['acts'].items(), key=lambda x: x[0] == '*')]
    m['definition'] = 'Orga is %s; ' % KIND[m['base']] + '; '.join(parts) + '.'
    m['names'] = 'Alice and Bob are persons, Orga %s.' % KIND[m['base']]
    m['clauses'] = ['○ ' + u for u in m.get('undertakings', [])]
    if any('policy' not in r and rules.as_policy(r) is None for r in m['rules'].values()):
        m['clauses'].append('■ Voting against.  A holder of a role may vote against a proposed act of Orga, once, in place of voting for it.')
    m.setdefault('act_names', {a: ACTS[a] for a in m['acts'] if a != '*'})
    return m

def run(rows, map_path):
    m = map_path if isinstance(map_path, dict) else json.load(open(map_path, encoding='utf8'))
    assert m['base'] in BASES, 'only the cooperative and the DAO are wired so far'
    for r in m['rules'].values():
        if 'policy' not in r: rules.validate(r)
    for act, name in m['acts'].items(): assert name in m['rules'] and act in ACTS, (act, name)
    assert '*' in m['acts'], 'no rule for every other act'
    compose(m)
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
