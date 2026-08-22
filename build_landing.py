"""Render README.md into the landing page of the built site.

    python build_landing.py [site_dir]

Run this *after* `jupyter lite build`. It converts README.md to HTML and writes
it over the site's index.html, so visiting the root shows the README instead of
JupyterLite's file browser.

JupyterLite's own root page is kept at /tree.html. Nothing else is touched —
the notebooks still live at /lab/index.html?path=...

IMPORTANT — why the config script gets copied across
----------------------------------------------------
JupyterLite fetches the *root* index.html at runtime and reads its
`<script id="jupyter-config-data">` element to find the site config
(see getPageConfig in config-utils.js). If that element is missing, every
notebook page dies with:

    TypeError: Cannot read properties of null (reading 'textContent')

...and renders a blank white page. So the landing page must carry that element
through verbatim, even though it looks like dead markup. Do not remove it.
"""

import os
import re
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
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' rx='4' fill='%23e8823a'/%3E%3Crect x='3' y='6' width='9' height='3' fill='%23989aa0'/%3E%3C/svg%3E">
<!-- Required by JupyterLite: notebook pages fetch this file and read the
     element below to find the site config. Removing it makes every notebook
     render a blank page. -->
{config_script}
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
  /* the 1.4rem below a heading is deliberate: it leaves a gap a Smiski
     can peek up into without ever covering a word */
  h1, h2, h3 {{ line-height: 1.2; letter-spacing: -0.02em; margin: 2rem 0 1.4rem; }}
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
  a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}
  #pochita {{
    display: block;
    margin: 0 auto 1.75rem;
    image-rendering: pixelated;
  }}

  /* Smiskis hide behind a line of text and climb out of it now and then. */
  .peek-host {{ position: relative; height: 0; }}
  .smiski {{
    position: absolute;
    bottom: 0;
    image-rendering: pixelated;
    pointer-events: none;
    transform: translateY(100%);
    transition: transform 640ms cubic-bezier(.2, .85, .3, 1);
  }}
</style>
</head>
<body>
<main>
<canvas id="pochita" width="204" height="144" role="img"
        aria-label="Pixel art of Pochita, the chainsaw dog, bobbing gently"></canvas>
{body}
</main>
<script>
// ---------------------------------------------------------------- Pochita ---
// Drawn pixel by pixel. No image files, no requests.
(function () {{
  var PAL = {{
    'o': '#3e261a', 'O': '#e8823a', 'L': '#f7ac6a', 'D': '#c6622a',
    'K': '#282226', 'G': '#989aa0', 'W': '#f0f2f6', 'E': '#161212', 'N': '#fafafc'
  }};
  var A = [
    '..................................', '..................................', '..................................',
    '....................oooo..........', '..o................oKKKKo.ooooooo.', '.ooooo............oKKKKKKooKKKKKo.',
    '.ooGoooo.........oKKK..KKKooooooo.', 'ooGGGGGoooo.....oKK......KKooo....', 'ooGWWGGGGoooooooooooo....KKooo....',
    '.ooGGWWWGGGoooOOOOOOOooo.KKooo....', '..ooGGGGWWGoooLLLLOOOOOOooKooo....', '...ooGGGGGGoooLLLLLLOOOOOOoooo....',
    '...oooooooooooLLLLLLLLOOOOOooo....', '...oOLLLLoooLLLLLLLLLLOOOOOOoo....', '..oOOOOLooNooLLLLLLLOOOOOOOOOo....',
    '..oOOOOOoNENoLLLLLOOOOOOOOOOOo....', '...oOOOOooNooOOOOOOOOOOOOOOOo.....', '...ooOOOOoooDDDDDDDDDDOOOOOoo.....',
    '....ooODDDDDDDDDDDDDDDDDDDoo......', '......oDDDDDDDDDDDDDDDDDDD........', '......oDooooDoDDDDDoDooooDo.......',
    '......oDo..oDoooooooDo..oDo.......', '......ooo..ooo.....ooo..ooo.......', '..................................'
  ];
  var B = [
    '..................................', '..................................', '..................................',
    '..................................', '....................oooo..........', '..o................oKKKKo.ooooooo.',
    '.ooooo............oKKKKKKooKKKKKo.', '.ooGoooo.........oKKK..KKKooooooo.', 'ooGGGGGoooo.....oKK......KKooo....',
    'ooGWWGGGGoooooooooooo....KKooo....', '.ooGGWWWGGGoooOOOOOOOooo.KKooo....', '..ooGGGGWWGoooLLLLOOOOOOooKooo....',
    '...ooGGGGGGoooLLLLLLOOOOOOoooo....', '...oooooooooooLLLLLLLLOOOOOooo....', '...oOLLLLLLLLLLLLLLLLLOOOOOOoo....',
    '..oOOOOLLLLLLLLLLLLLOOOOOOOOOo....', '..oOOOOOooooLLLLLLOOOOOOOOOOOo....', '...oOOOOOOOOOOOOOOOOOOOOOOOOo.....',
    '...ooOOOOOODDDDDDDDDDDOOOOOoo.....', '....ooODDDDDDDDDDDDDDDDDDDoo......', '......oDDDDDDDDDDDDDDDDDDD........',
    '......oDooooDoDDDDDoDooooDo.......', '......oDo..oDoooooooDo..oDo.......', '......ooo..ooo.....ooo..ooo.......'
  ];

  var canvas = document.getElementById('pochita');
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext('2d');
  var SCALE = 6;

  function draw(rows) {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (var y = 0; y < rows.length; y++) {{
      for (var x = 0; x < rows[y].length; x++) {{
        var c = PAL[rows[y][x]];
        if (c) {{ ctx.fillStyle = c; ctx.fillRect(x * SCALE, y * SCALE, SCALE, SCALE); }}
      }}
    }}
  }}

  draw(A);

  // Some people get motion sick, and some just don't want it. Respect that.
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  if (still && still.matches) return;

  // Mostly sitting there, with the occasional bob and blink.
  var timeline = [[A, 1400], [B, 180], [A, 900], [B, 180], [A, 2200], [B, 160]];
  var i = 0;
  (function step() {{
    var f = timeline[i % timeline.length];
    draw(f[0]);
    i++;
    setTimeout(step, f[1]);
  }})();
}})();

// ---------------------------------------------------------------- Smiskis ---
// They hide behind a paragraph and peek out of it every so often.
//
// The trick: each Smiski lives in a zero-height div inserted just BEFORE a
// paragraph, and that paragraph is given the card's own background colour.
// Because the paragraph comes later in the DOM it paints on top, so nudging
// the Smiski down by its own height tucks it completely out of sight.
(function () {{
  var SPAL = {{ 'o': '#4a6a4a', 'L': '#a8d8a0', 'H': '#c6e8bc', 'K': '#2a3a2a' }};
  var POSES = [
    ['....oooooo....', '..ooHHHHHHoo..', '.oHHHHHHHHHHo.', '.oLLKKLLKKLLo.', '.oLLKKLLKKLLo.', '.oLLLLLLLLLLo.', '.oLLLLLLLLLLo.', '.oLLLLLLLLLLo.', '.ooLLLLLLLLoo.', 'ooLLLLLLLLLLoo', 'oLLLLLLLLLLLLo', 'oLLLLLLLLLLLLo'],
    ['....oooooo....', '..ooHHHHHHoo..', '.oHHHHHHHHHHo.', '.oLLLKKLLKKLo.', '.oLLLKKLLKKLo.', '.oLLLLLLLLLLo.', '.oLLLLLLLLLLo.', '.oLLLLLLLLLLo.', '.ooLLLLLLLLoo.', 'ooLLLLLLLLLLoo', 'oLLLLLLLLLLLLo', 'oLLLLLLLLLLLLo'],
    ['....oooooo....', '..ooHHHHHHoo..', '.oHHHHHHHHHHo.', '.oKKLLKKLLLLo.', '.oKKLLKKLLLLo.', '.oLLLLLLLLLLo.', '.oLLLLLLLLLLo.', '.oLLLLLLLLLLo.', '.ooLLLLLLLLoo.', 'ooLLLLLLLLLLoo', 'oLLLLLLLLLLLLo', 'oLLLLLLLLLLLLo']
  ];
  var SW = 14, SH = 12, SS = 4;

  var main = document.querySelector('main');
  if (!main) return;
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  if (still && still.matches) return;

  function paint(canvas, rows) {{
    var g = canvas.getContext('2d');
    g.clearRect(0, 0, canvas.width, canvas.height);
    for (var y = 0; y < rows.length; y++) {{
      for (var x = 0; x < rows[y].length; x++) {{
        var c = SPAL[rows[y][x]];
        if (c) {{ g.fillStyle = c; g.fillRect(x * SS, y * SS, SS, SS); }}
      }}
    }}
  }}

  // Anchor only to paragraphs, and only where there is blank space above to
  // rise into — so a Smiski can never cover a word or a link.
  var cands = [].slice.call(main.querySelectorAll('p')).filter(function (el) {{
    return el.offsetHeight >= SH * SS + 4;
  }});

  var slots = [];
  for (var k = 0; k < cands.length && slots.length < 3; k++) {{
    var el = cands[k];
    var prev = el.previousElementSibling;
    if (!prev) continue;

    // vertical blank space between the block above and this paragraph
    var gap = el.offsetTop - (prev.offsetTop + prev.offsetHeight);
    var show = Math.min(gap - 3, SH * SS - 8);       // how much head to reveal
    if (show < 10) continue;                          // not enough room, skip

    el.style.position = 'relative';
    el.style.background = 'var(--card)';

    var host = document.createElement('div');
    host.className = 'peek-host';
    var c = document.createElement('canvas');
    c.className = 'smiski';
    c.width = SW * SS;
    c.height = SH * SS;
    c.setAttribute('aria-hidden', 'true');
    c.style.left = (10 + slots.length * 30) + '%';
    c.dataset.rise = 'translateY(' + (SH * SS - show) + 'px)';
    paint(c, POSES[0]);
    host.appendChild(c);
    el.parentNode.insertBefore(host, el);
    slots.push(c);
  }}
  if (!slots.length) return;

  function peek() {{
    var hidden = slots.filter(function (c) {{ return c.style.transform.indexOf('100%') !== -1
                                                     || !c.style.transform; }});
    if (hidden.length) {{
      var c = hidden[Math.floor(Math.random() * hidden.length)];
      paint(c, POSES[Math.floor(Math.random() * POSES.length)]);
      c.style.transform = c.dataset.rise;
      setTimeout(function () {{ c.style.transform = 'translateY(100%)'; }},
                 2400 + Math.random() * 1400);
    }}
    setTimeout(peek, 3800 + Math.random() * 4500);
  }}
  setTimeout(peek, 1600);
}})();
</script>
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

    # Lift JupyterLite's config element out of its own root page before we
    # replace it. Without this every notebook renders blank — see the note
    # at the top of this file.
    source = kept if os.path.exists(kept) else index
    original = open(source, encoding="utf-8").read()
    match = re.search(
        r'<script id="jupyter-config-data".*?</script>', original, re.S)
    if not match:
        raise SystemExit(
            "\nCouldn't find <script id=\"jupyter-config-data\"> in %s.\n"
            "Without it the notebooks would render blank pages, so refusing\n"
            "to write a landing page.\n" % source)
    config_script = match.group(0)

    if os.path.exists(index) and not os.path.exists(kept):
        os.rename(index, kept)          # keep JupyterLite's own root page

    with open(index, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(title=TITLE, body=body,
                                config_script=config_script))

    print("landing page written to %s" % index)
    print("JupyterLite's original root kept at %s" % kept)
    print("carried over: %s" % config_script.split(">")[0][:70] + ">")


if __name__ == "__main__":
    main()
