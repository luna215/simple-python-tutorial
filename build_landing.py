"""Render README.md into the landing page of the built site.

    python build_landing.py [site_dir]

Run this *after* `jupyter lite build`. It converts README.md to HTML and writes
it over the site's index.html, so visiting the root shows the README instead of
JupyterLite's file browser.

JupyterLite's own root page is kept at /tree.html. Nothing else is touched —
the notebooks still live at /lab/index.html?path=...
"""

import os
import sys

try:
    import markdown
except ImportError:
    raise SystemExit(
        "\nThis needs the 'markdown' package:\n"
        "    ./venv/bin/pip install markdown\n")

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "_site")

TITLE = "Python Tutorial"

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{
    --bg: #f4f5f9;
    --card: #ffffff;
    --ink: #1a1c25;
    --soft: #5a5f73;
    --rule: #e0e2ec;
    --accent: #b3313f;
    --accent-ink: #ffffff;
    --quote-bg: #f7f2f3;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #191b24;
      --card: #21242f;
      --ink: #e9ebf3;
      --soft: #a3a8bd;
      --rule: #333747;
      --accent: #ff6b78;
      --accent-ink: #1a0d10;
      --quote-bg: #2b1f24;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font: 17px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
    padding: 3rem 1.25rem 5rem;
  }}
  main {{
    max-width: 40rem;
    margin: 0 auto;
    background: var(--card);
    border: 1px solid var(--rule);
    border-radius: 10px;
    padding: 2.5rem 2.25rem 2.75rem;
  }}
  h1, h2, h3 {{ line-height: 1.2; letter-spacing: -0.02em; margin: 2rem 0 0.75rem; }}
  h1 {{ font-size: 1.9rem; margin-top: 0; }}
  h2 {{ font-size: 1.3rem; padding-top: 1.25rem; border-top: 1px solid var(--rule); }}
  main > :first-child {{ margin-top: 0; }}
  p, ul, ol {{ margin: 0 0 1rem; }}
  li {{ margin-bottom: 0.4rem; }}
  a {{ color: var(--accent); text-underline-offset: 2px; }}
  strong {{ font-weight: 650; }}
  code {{
    font: 0.88em ui-monospace, SFMono-Regular, Menlo, monospace;
    background: var(--bg); padding: 0.12em 0.38em; border-radius: 4px;
  }}
  blockquote {{
    margin: 1.25rem 0; padding: 0.9rem 1.15rem;
    background: var(--quote-bg); border-left: 3px solid var(--accent);
    border-radius: 0 6px 6px 0; font-size: 1.03rem;
  }}
  blockquote p {{ margin: 0; }}
  hr {{ border: 0; border-top: 1px solid var(--rule); margin: 2rem 0; }}
  /* a lone bold link on its own line becomes the call-to-action button */
  p > strong:only-child > a:only-child {{
    display: inline-block;
    background: var(--accent);
    color: var(--accent-ink);
    padding: 0.7rem 1.4rem;
    border-radius: 7px;
    text-decoration: none;
    font-weight: 650;
  }}
  p > strong:only-child > a:only-child:hover {{ filter: brightness(1.08); }}
  a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}
</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def main():
    readme = os.path.join(HERE, "README.md")
    if not os.path.exists(readme):
        raise SystemExit("No README.md next to this script.")
    if not os.path.isdir(SITE):
        raise SystemExit("No site at %s — run `jupyter lite build` first." % SITE)

    body = markdown.markdown(
        open(readme, encoding="utf-8").read(),
        extensions=["extra", "sane_lists"],
    )

    index = os.path.join(SITE, "index.html")
    kept = os.path.join(SITE, "tree.html")
    if os.path.exists(index) and not os.path.exists(kept):
        os.rename(index, kept)          # keep JupyterLite's own root page

    with open(index, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(title=TITLE, body=body))

    print("landing page written to %s" % index)
    print("JupyterLite's original root kept at %s" % kept)


if __name__ == "__main__":
    main()
