# LWG: from laws and whitepapers to GrassApps (prototype)

Goal: given the governing document of an organization, produce a GrassApp that follows it, with a record that shows what became of every provision.

Four modules, each filling its own columns of the record (one row for each provision):

| Module | File | Job | Basis |
|---|---|---|---|
| Read | `lwg/read.py` | split the document into provisions; attach the kind of each | Ostrom's seven types of rules, plus none / outside / judgment |
| Map | `lwg/map_.py`, `lwg/rules.py` | the bylaws: roles, and for each act who decides and by which decision rule; meeting provisions become app procedures | the organisations paper's bylaws; six-part decision rule |
| Review | `lwg/review.py` | open choices become questions; a person answers | — |
| Build | `lwg/build.py` | write the contract (clauses and schemas) and run the cascade's check | the generator of the organisations paper (`vendor/go_tools`, a copy, called as a library); `cascade.sh` |

Run: `python3 run.py examples/amutot --check` (the check needs Dart and takes about a minute).

What is done by a language model and what by code: the kind of each provision (`kinds.json`) and the bylaws with their questions (`map.json`) are written by a language model in session and saved as files; the code checks them, assembles the record, writes the contract and runs the check.

Not built yet: windows (periods), weight by shares, decisions of two bodies, abstention, and every provision the record marks "not built".

`vendor/` is a copy of `docs/tools` and the paper of the organisations project, taken 2026-11-11.

`vendor/` is not in the repository: it holds a copy of the generator and the paper of the organisations project, which are not public yet. To run Build, put the organisations project's `docs/tools/*.py` in `vendor/go_tools/` and its main `.tex` at `vendor/go_paper.tex`.
