# GAS, the GLP app store

A site that shows the grassroots contracts of this repository, how the cascade turns each into code, and a live app for each compiled contract: four persons, Alice, Bob, Carol and Dave, each running the contract's canonical platform as an agent of madGLP, in an isolate of its own, the persons' messages carried between the isolates as madGLP's. The owner is GAS; the paper responsible is GAS (https://github.com/nimrodtalmon/grassroots-contracts/blob/main/paper/main.pdf).

## Build and run

From this directory, with Python 3 and Dart:

    python3 -I tools/build.py      # the worlds and the site, from cascade/ and programs/
    dart pub get
    PORT=8080 dart run bin/server.dart

Then open http://localhost:8080/. A contract's world starts on its first visit, which takes about half a minute; at most `MAX_WORLDS` (default 3) run at once, and a world unused for an hour is dropped.

## What is where

- `tools/build.py` reads every contract with a recorded platform, `cascade/<NAME>/platform.vglp`, and writes:
  - `programs/vglp/cva/gas_worlds/live_<name>/`, its live harness (`tools/gen_harness.py`), in the scope of the canonical platforms as vGLP's plays are: `live_person/3`, one person alone, and `live_ui/3`, the four in one heap;
  - `build/www/specs/<name>.json`, the menu the app page draws, read off the platform (`tools/menu_spec.py`);
  - `build/www/stack/<NAME>/`, the cascade's layers, and `build/www/data.js`, every contract's text, owner, the contracts it extends, its schemas and verdict.
  
  Both directories are generated and gitignored, and the script rebuilds them whole. A contract recorded by `cascade.sh` appears on its next run.
- `bin/server.dart` serves `build/www` and the API the app page calls, `/api/<name>/{state,act,day,reset}`. The server is every person: it keeps what each person's dispatcher draws and injects the person's acts. Each person of a world is an agent of madGLP in its own Dart isolate, running `live_person/3` of the harness with its own heap and key pair; a message the person's platform sends goes out by `send_to_net`, a cold call to the person it names, and the server carries it to that person's isolate, as the simulation's network carries messages between agents. A world is ready when every event sent to its persons, and every message they sent, has been taken. With `GAS_WORLDS=heap` a world is instead the four persons in one heap (`live_ui/3`), their networks joined in GLP.
- `web/` holds the pages: `index.html` (the contracts, their text and the cascade's layers), `app.html` (the live app of one contract, `app.html?c=<name>`), `how.html` (an explainer for general readers), and `about.json` (the site's one line, icon and family for each contract).

## Environment

`PORT` (default 8080), `MAX_WORLDS` (default 3), `GAS_WORLDS` (`mad`, the default, or `heap`), and, to run from elsewhere, `GLP_ROOT` (the repository), `WORLDS_DIR` and `WEB_DIR`.
