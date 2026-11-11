"""Build: write the grassroots contract (clauses and schemas) from the bylaws, and put it to the cascade's check."""
import copy, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vendor', 'go_tools'))
import sas_coop, sas_prag
from sas_lib import glp_file, check_names, check_dups
from . import rules

GO_PAPER = os.path.join(os.path.dirname(__file__), '..', 'vendor', 'go_paper.tex')
TABS = ["Organisations: the organisations Alice participates in, and her roles in each.", "Coins: the coins Alice holds.", "Bonds: the bonds Alice holds."]

def schemas(m):
    name = m['name']
    c = {'GCoop': sas_coop.gcoop, 'GDAO': sas_coop.gdao}[m['base']](bylaws='bylaws_' + name.lower())   # an organisation of the organisations paper, with our bylaws' name
    c = [x for x in c if x.name not in ('first_officer', 'named_propose', 'named_vote')]   # as the generator does for an instance
    for new, spec in m.get('also', {}).items():                   # a second way to take an act: the same act, decided by another body
        y = copy.deepcopy([x for x in c if x.name == spec['copy_of']][0]); y.name = new
        y.note = spec['clause']; c.append(y)
    pol = lambda r: tuple(r['policy']) if 'policy' in r else r
    bylaws = {act: pol(m['rules'][r]) for act, r in m['acts'].items()}
    bylaws.update({new: m['rules'][spec['rule']] for new, spec in m.get('also', {}).items()})
    c = rules.officers(c, bylaws)
    check_names(c); assert not check_dups(c)
    return c

def clauses(m):
    """The contract's box: title, relation, definition, names, clauses. The definition and the clauses are written with the bylaws (map.json); {rule} stands for the English of that rule."""
    words = {k: rules.describe(r, m['roles']) for k, r in m['rules'].items()}
    lines = ['%s: %s' % (m['name'], m['title']), '%s instantiates %s and restricts it.' % (m['name'], m['base']),
             m['definition'].format(**words), m['names']]
    lines += ['%d. %s' % (i, c.format(**words)) for i, c in enumerate(m['clauses'], 1)]
    return lines

def write(m, glp_root):
    name = m['name']
    out = os.path.join(glp_root, 'programs', 'lwg'); os.makedirs(out, exist_ok=True)
    c = schemas(m)
    header = ['%s.glp --- %s, the speech-act schemas, written by tools/lwg from the bylaws drawn from: %s.' % (name, name, m['source']),
              'Instantiates %s (programs/go) and restricts it;' % m['base'] + ' the schemas of GCoop are produced by the generator of the organisations paper, called as a library, and the decision rules by tools/lwg/lwg/rules.py.',
              '%d schemas.' % len(c), 'Environment predicates: today.', 'Instantiates the parameter bylaws_p by the utterance bylaws_%s.' % name.lower()]
    open(os.path.join(out, name + '.glp'), 'w', encoding='utf8').write(glp_file(name, header, c, ['today']))
    acts, _ = sas_prag.lines(c, GO_PAPER)
    txt = ['%% %s --- written by tools/lwg; a trial contract, not registered.' % name, '% Owner: LWG (not yet ruled).',
           '%% Extends: %s, instantiating its bylaws and restricting it.' % m['base'], '%% Schemas: %s.glp beside this file.' % name] + clauses(m) + ['Pragmas', 'Look: 🏛️, governance'] + TABS + acts
    open(os.path.join(out, name + '.txt'), 'w', encoding='utf8').write('\n'.join(txt) + '\n')
    return len(c)

def check(m, glp_root):
    """Run the cascade's check; return (verdict line, later lines)."""
    env = dict(os.environ)
    p = subprocess.run(['bash', 'cascade.sh', m['name'].lower(), '--check'], cwd=glp_root, capture_output=True, text=True, env=env)
    lines = [l for l in (p.stdout + p.stderr).split('\n') if l.strip()]
    verdict = next((l for l in lines if 'verdict' in l), 'no verdict')
    return verdict, lines
