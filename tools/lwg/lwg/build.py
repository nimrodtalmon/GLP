"""Build: write the grassroots contract (clauses and schemas) from the bylaws, and put it to the cascade's check."""
import os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vendor', 'go_tools'))
import sas_coop, sas_prag
from sas_lib import glp_file, check_names, check_dups
from . import rules

GO_PAPER = os.path.join(os.path.dirname(__file__), '..', 'vendor', 'go_paper.tex')
TABS = ["Organisations: the organisations Alice participates in, and her roles in each.", "Coins: the coins Alice holds.", "Bonds: the bonds Alice holds."]

def schemas(m):
    name = m['name']
    c = sas_coop.gcoop(bylaws='bylaws_' + name.lower())          # the cooperative of the organisations paper, with our bylaws' name
    c = [x for x in c if x.name not in ('first_officer', 'named_propose', 'named_vote')]   # as the generator does for an instance
    bylaws = {act: m['rules'][r] for act, r in m['acts'].items()}
    c = rules.officers(c, bylaws)
    check_names(c); assert not check_dups(c)
    return c

def clauses(m):
    n, noun, roles = m['name'], m['noun'], m['roles']
    special = [(a, r) for a, r in m['acts'].items() if a != '*']
    main = rules.english(m['rules'][m['acts']['*']], roles)
    lines = ['%s: %s' % (n, m['title']),
             '%s instantiates %s and restricts it.' % (n, m['base']),
             'An %s is a cooperative with two roles, %s, held by every participant, and %s; ' % (noun, roles['1'], roles['2'])
             + '; '.join('the %ss decide the admission of a member when %s' % (roles[str(m['rules'][r]['body'])], rules.english(m['rules'][r], roles)) for a, r in special if a == 'coop_join')
             + '; the %ss decide every other act of the %s when %s.' % (roles['1'], noun, main),
             'Alice and Bob are persons, Orga an %s.' % noun,
             '1. ■ Founding.  Alice may found Orga and become its first %s.' % roles['1'],
             '2. ■ Admission.  Bob becomes a %s of Orga by an act of Bob and the %ss.' % (roles['1'], roles['2']),
             '3. ■ Voting against.  A %s or a %s may vote against a proposed act of Orga, once, in place of voting for it.' % (roles['1'], roles['2'])]
    return lines

def write(m, glp_root):
    name = m['name']
    out = os.path.join(glp_root, 'programs', 'lwg'); os.makedirs(out, exist_ok=True)
    c = schemas(m)
    header = ['%s.glp --- %s, the speech-act schemas, written by tools/lwg from the bylaws drawn from: %s.' % (name, name, m['source']),
              'Instantiates GCoop (programs/go) and restricts it; the schemas of GCoop are produced by the generator of the organisations paper, called as a library, and the decision rules by tools/lwg/lwg/rules.py.',
              '%d schemas.' % len(c), 'Environment predicates: today.', 'Instantiates the parameter bylaws_p by the utterance bylaws_%s.' % name.lower()]
    open(os.path.join(out, name + '.glp'), 'w', encoding='utf8').write(glp_file(name, header, c, ['today']))
    acts, _ = sas_prag.lines(c, GO_PAPER)
    txt = ['%% %s --- written by tools/lwg; a trial contract, not registered.' % name, '% Owner: LWG (not yet ruled).',
           '% Extends: GCoop, instantiating its bylaws and restricting it.', '%% Schemas: %s.glp beside this file.' % name] + clauses(m) + ['Pragmas', 'Look: 🏛️, governance'] + TABS + acts
    open(os.path.join(out, name + '.txt'), 'w', encoding='utf8').write('\n'.join(txt) + '\n')
    return len(c)

def check(m, glp_root):
    """Run the cascade's check; return (verdict line, later lines)."""
    env = dict(os.environ)
    p = subprocess.run(['bash', 'cascade.sh', m['name'].lower(), '--check'], cwd=glp_root, capture_output=True, text=True, env=env)
    lines = [l for l in (p.stdout + p.stderr).split('\n') if l.strip()]
    verdict = next((l for l in lines if 'verdict' in l), 'no verdict')
    return verdict, lines
