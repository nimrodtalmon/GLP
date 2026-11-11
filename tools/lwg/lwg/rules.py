"""Decision rules: the six parts, their English, and their rendering as a constraint of a speech-act schema.

A rule is a dict:
  body       role number whose holders vote
  weight     'one'                      (one vote each; 'shares' is not built yet)
  base       'all' | 'cast'             (all the votes of the body | the votes cast for or against)
  threshold  [p, q, strict]             (votes for must exceed p/q of the base if strict, else reach it)
             or ['count', k]            (k holders must vote for)
  quorum     None | [a, b]              (at least a/b of the body must vote for or against)
  window     None                       (days; not built yet)
The four rules of the grassroots organisations paper are special cases and are passed through to its generator unchanged.
"""
import copy, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vendor', 'go_tools'))
from sas_lib import A, N, Q, AND, num, card      # the generator of the organisations paper, used as a library
import sas_off

FRACTION = {(1, 2): 'half', (2, 3): 'two thirds', (3, 4): 'three quarters', (1, 4): 'a quarter', (1, 3): 'a third', (1, 10): 'a tenth'}

def validate(r):
    assert isinstance(r['body'], int)
    assert r.get('weight', 'one') == 'one', 'weight by shares is not built yet'
    assert r['base'] in ('all', 'cast')
    t = r['threshold']
    assert (t[0] == 'count' and t[1] >= 1) or (0 < t[0] <= t[1] and isinstance(t[2], bool))
    assert r.get('quorum') is None or 0 < r['quorum'][0] <= r['quorum'][1]
    assert r.get('window') is None, 'windows are not built yet'
    return r

def english(r, roles):
    who = roles[str(r['body'])] + 's'
    t = r['threshold']
    if t[0] == 'count': s = '%d of the %s vote for' % (t[1], who)
    else:
        frac = FRACTION.get((t[0], t[1]), '%d/%d' % (t[0], t[1]))
        of = 'the votes cast' if r['base'] == 'cast' else 'the %s' % who
        s = '%s %s of %s are for' % ('more than' if t[2] else 'at least', frac, of)
    if r.get('quorum'):
        a, b = r['quorum']
        s += ', and at least %s of the %s voted' % (FRACTION.get((a, b), '%d/%d' % (a, b)), who)
    return s

def as_policy(r):
    """A rule that the organisations paper already has, in its generator's terms; else None."""
    t = r['threshold']
    if r['base'] == 'all' and not r.get('quorum') and t[0] != 'count':
        if (t[0], t[1], t[2]) == (1, 2, True): return ('majority', r['body'])
        if (t[0], t[1], t[2]) == (1, 1, False): return ('all', r['body'])
    if t[0] == 'count' and t[1] == 1: return ('one', r['body'])
    return None

def _apply(x, org, r, extra):
    """Rewrite the act x of the organisation org so that an officer takes it once the rule r holds over the votes."""
    p = as_policy(r)
    if p: return sas_off.officer(x, org, p, extra)
    tg = sas_off.OFF[org][2]
    vi, vn, xp, ni, v3 = 'vi' + tg, 'vn' + tg, 'xp' + tg, 'ni' + tg, 'v3' + tg
    role = num(str(r['body']))
    sas_off.officer(x, org, ('majority', r['body']), extra)          # the generator's plumbing: proposal, motion, votes for, count of the body
    old = "gt(mul(num(2), num(%s)), num(%s))" % (vi, vn)
    assert old in x.cons, x.name
    nays = "eq(num(%s), %s)" % (ni, card([v3], A('nay', Q(org), v3, xp, role)))
    cast = "plus(num(%s), num(%s))" % (vi, ni)
    t = r['threshold']
    if t[0] == 'count': th = "ge(num(%s), num(%d))" % (vi, t[1])
    else:
        base = cast if r['base'] == 'cast' else "num(%s)" % vn
        th = "%s(mul(num(%d), num(%s)), mul(num(%d), %s))" % ('gt' if t[2] else 'ge', t[1], vi, t[0], base)
    parts = [th, nays]
    if r.get('quorum'):
        a, b = r['quorum']
        parts.append("ge(mul(num(%d), %s), mul(num(%d), num(%s)))" % (b, cast, a, vn))
    x.cons = x.cons.replace(old, AND(*parts))
    x.vars.append(ni); x.names.append(v3)
    x.head.append(N(A('nay', Q(org), '_', xp, '_')))                 # the votes against a decided motion are cleared with the votes for
    x.note += '  Decided by: %s.' % english(r, {str(r['body']): 'holder of role %d' % r['body']})

def vote_against(schemas):
    """GO's vote, cast against: the same act, recording nay where vote records a vote for."""
    v = copy.deepcopy([x for x in schemas if x.name == 'vote'][0])
    v.name = 'vote_against'
    v.head = [h.replace('atom(vote, ', 'atom(nay, ') for h in v.head]
    v.note = 'A member of the body votes against the proposed act x, once for each role, in place of voting for it.'
    return v

def officers(schemas, bylaws, other=('all', None)):
    """As the generator's officers(), with a decision rule (a dict) allowed wherever it has a policy."""
    extra, used_new = [], False
    for x in schemas:
        if not hasattr(x, 'guards'): continue
        for org in [g for g in x.guards if g in sas_off.OFF and N(A('identity', Q(g))) not in x.body]:
            pol = bylaws.get(x.name, bylaws['*'])
            if x.name == 'retire' or org != 'Orga': pol = other
            if isinstance(pol, dict):
                used_new = used_new or as_policy(pol) is None
                _apply(x, org, validate(pol), extra)
            else:
                sas_off.officer(x, org, pol, extra)
                x.note += '  Taken for %s by its officers (%s).' % (org, ' '.join(str(q) for q in pol))
    out = schemas + extra
    if used_new: out.append(vote_against(schemas))
    return out
