"""Run the four modules on an example: python3 run.py examples/amutot [--check]"""
import os, sys
from lwg import read, map_, review, build, record
ex = sys.argv[1]; glp_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
rows = read.run(os.path.join(ex, 'source.txt'), os.path.join(ex, 'kinds.json'))                # Read
m = map_.run(rows, os.path.join(ex, 'map.json'))                                               # Map
qs = review.run(rows, os.path.join(ex, 'answers.json'))                                        # Review
n = build.write(m, glp_root)                                                                   # Build
cl = build.clauses(m)
for r in rows: r['clause'] = {'built': m['name']}.get(r['status'], '')
print('%d provisions; %d questions; %d schemas written' % (len(rows), len(qs), n))
verdict = 'not checked'
if '--check' in sys.argv:
    verdict, lines = build.check(m, glp_root); print('\n'.join(lines[-6:]))
record.save(rows, os.path.join(ex, 'record.json'))
head = '\n'.join(['', '## Bylaws', '', map_.bylaws_table(m), '', '## Contract', ''] + ['    ' + l for l in cl] + ['', 'Check: `%s`' % verdict, ''])
open(os.path.join(ex, 'record.md'), 'w', encoding='utf8').write(record.markdown(rows, m['title']) + head)
open(os.path.join(ex, 'questions.md'), 'w', encoding='utf8').write(review.markdown(qs, m['title']))
