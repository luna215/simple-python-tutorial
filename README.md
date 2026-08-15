# Notebook trial

A standalone experiment — **not** wired into any of the session folders. Nothing
here is required to run the sessions.

The idea: host the *concept* half of a lesson as a notebook the student can run
in a browser with nothing installed, and keep the game itself in the `.py` files.

Two sample notebooks in `content/`:

| notebook | what it covers |
|---|---|
| `devil-hunter-training.ipynb` | **start here** — variables, f-strings, `if`/`elif`/`else`, functions, `return`, lists, `for`, `while`, `break`, `random`. Themed on *Chainsaw Man*, closing on *Look Back*. |
| `lists-and-loops.ipynb` | a shorter drill on lists, `for`, `range`, `append`, and the loop-variable trap |

`game.py` in this folder is the same game loop with pixels instead of text — 87
lines, a complete game. It can't run in a notebook (see "What doesn't work"), so
run it directly:

```
./venv/bin/python notebook-trial/game.py
```

---

## Try it locally

```
cd notebook-trial
./venv/bin/jupyter lite build --contents content --output-dir _site
./venv/bin/python -m http.server 8000 --directory _site
```

Then open either:

- <http://localhost:8000/lab/index.html?path=devil-hunter-training.ipynb>
- <http://localhost:8000/lab/index.html?path=lists-and-loops.ipynb>

Rebuild after every content change — `jupyter lite build` copies the notebooks
into `_site`, it doesn't read them live.

## The venv here is separate on purpose

The game's `venv/` at the repo root is Python 3.9.6. JupyterLite needs **3.10+**,
so this folder has its own venv built on Homebrew's 3.11:

```
/opt/homebrew/bin/python3.11 -m venv venv
./venv/bin/pip install jupyterlite-core jupyterlite-pyodide-kernel jupyter-server
```

`jupyter-server` is **not** optional despite not being a listed dependency — without
it the build fails at the last step with *"jupyter-server is not installed. You
cannot add custom content to jupyterlite."*

---

## Publishing to GitHub Pages

It's a plain static site, so this works. `dev-games` isn't a git repo yet, so:

```
cd /Users/paul/development/dev-games
git init && git add . && git commit -m "sessions + notebook trial"
gh repo create dev-games --private --source=. --push
```

Then add `.github/workflows/notebooks.yml`:

```yaml
name: notebooks
on:
  push:
    branches: [main]
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install jupyterlite-core jupyterlite-pyodide-kernel jupyter-server
      - run: jupyter lite build --contents notebook-trial/content --output-dir _site
      - uses: actions/upload-pages-artifact@v3
        with:
          path: _site
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
    steps:
      - uses: actions/deploy-pages@v4
```

Then in the repo: **Settings → Pages → Source → GitHub Actions**. Every push
rebuilds and republishes.

**Note:** a private repo needs GitHub Pro for Pages, or make the repo public.

### Don't commit the build

```
notebook-trial/venv/
notebook-trial/_site/
```

The Action rebuilds `_site` from source; committing it just adds 70 MB of churn.

---

## What doesn't work

**pygame in a notebook cell.** `pygame-ce` exists in Pyodide, but it does not run
inside a JupyterLite cell — see
[jupyterlite/pyodide-kernel#195](https://github.com/jupyterlite/pyodide-kernel/issues/195).
Even if it did, a notebook cell runs to completion and a game loop never
completes, so it's the wrong shape.

For the game in a browser, the tool is **pygbag** (compiles pygame-ce to
WebAssembly). That's a separate thing from notebooks.

Which is why `devil-hunter-training.ipynb` isn't about a game at all. A devil's
name is a noun and its power is a number — that's a variable and an `if`, and it
needs no window. Text is what a notebook is actually good at.

Two other kernel limits worth knowing: **`time.sleep()` does not work**, and
`input()` is unverified — neither notebook depends on either.

## Things to know before committing to this

- **First page load is slow.** The browser downloads the Pyodide runtime (tens of
  MB). Cached afterwards, but the first visit on school wifi is a wait.
- **Student edits don't come back to you.** Changes save to browser local storage,
  not to the repo. Fine for a scratchpad, no good for handing work in.
- **Two sets of material to maintain.** Change a concept and you edit the notebook
  *and* the session card.
