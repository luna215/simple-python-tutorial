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
  h1, h2, h3 {{ line-height: 1.2; letter-spacing: -0.02em; margin: 2rem 0 2rem; }}
  h1 {{ font-size: 1.9rem; margin-top: 0; }}
  h2 {{ font-size: 1.3rem; padding-top: 1.25rem; border-top: 1px solid var(--rule); }}
  main > :first-child {{ margin-top: 0; }}
  p, ul, ol {{ margin: 0 0 1.5rem; }}
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
  .poch-wrap {{
    position: relative;
    display: flex;
    justify-content: center;
    margin-bottom: 1.75rem;
  }}
  #pochita {{ display: block; image-rendering: pixelated; }}
  .poch-say {{
    position: absolute;
    left: 50%;
    margin-left: 145px;
    top: 30px;
    max-width: 9.5rem;
    font-size: 0.72rem;
    line-height: 1.35;
    font-weight: 650;
    color: var(--ink);
    background: var(--card);
    border: 2px solid #b8763c;
    border-radius: 6px;
    padding: 0.25rem 0.45rem;
    opacity: 0;
    transform: translateX(-6px);
    transition: opacity 300ms ease, transform 300ms ease;
    pointer-events: none;
  }}
  .poch-say::before,
  .poch-say::after {{ content: ''; position: absolute; top: 9px; border: 6px solid transparent; }}
  .poch-say::before {{ left: -12px; border-right-color: #b8763c; }}
  .poch-say::after  {{ left: -9px;  border-right-color: var(--card); }}
  .poch-say.show {{ opacity: 1; transform: none; }}

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

  /* The first Smiski says hello. Real text, not pixels — it has to be readable. */
  .smiski-say {{
    position: absolute;
    bottom: 4px;
    white-space: nowrap;
    font-size: 0.68rem;
    line-height: 1.25;
    font-weight: 650;
    color: var(--ink);
    background: var(--card);
    border: 2px solid #3d5c7d;
    border-radius: 5px;
    padding: 0.08rem 0.36rem;
    opacity: 0;
    transform: translate(-5px, 3px);
    transition: opacity 220ms ease, transform 220ms ease;
    pointer-events: none;
  }}
  .smiski-say::before,
  .smiski-say::after {{
    content: '';
    position: absolute;
    bottom: 3px;
    border: 5px solid transparent;
  }}
  .smiski-say::before {{ left: -10px; border-right-color: #3d5c7d; }}
  .smiski-say::after  {{ left: -7px;  border-right-color: var(--card); }}
  /* on the right-hand Smiskis the bubble sits to their left, so the tail flips */
  .smiski-say.flip::before {{ left: auto; right: -10px; border-right-color: transparent; border-left-color: #3d5c7d; }}
  .smiski-say.flip::after  {{ left: auto; right: -7px;  border-right-color: transparent; border-left-color: var(--card); }}
  .smiski-say.show {{ opacity: 1; transform: translate(0, 0); }}

  /* Hovering a lesson link starts the chainsaw. Whole pixels only, no blur. */
  @keyframes rev-shake {{
    0%   {{ transform: translate(0, 0); }}
    25%  {{ transform: translate(-1px, 1px); }}
    50%  {{ transform: translate(1px, -1px); }}
    75%  {{ transform: translate(1px, 1px); }}
    100% {{ transform: translate(0, 0); }}
  }}
  #pochita.revving {{ animation: rev-shake 100ms steps(1) infinite; }}
</style>
</head>
<body>
<main>
<div class="poch-wrap">
<canvas id="pochita" width="270" height="162" role="img"
        aria-label="Pixel art of Pochita, the chainsaw dog, walking"></canvas>
<span class="poch-say">Hi Evolett! Lesson 3 is up!</span>
</div>
{body}
</main>
<script>
// ---------------------------------------------------------------- Pochita ---
// Traced from Paul's reference art, then given a four-frame walk cycle.
// Drawn pixel by pixel — no image files, no requests.
(function () {{
  var PAL = {{
    'a': '#000000',
    'b': '#373737',
    'c': '#646464',
    'd': '#1e0000',
    'e': '#979797',
    'f': '#5b210b',
    'g': '#482917',
    'h': '#aa4e29',
    'i': '#ff7c14',
    'j': '#5d3221',
    'k': '#e07c40',
    'l': '#f07e28',
    'm': '#c24c1e',
    'n': '#d44a02',
    'o': '#d9dbda',
    'p': '#d54d19',
    'q': '#701f00',
    'r': '#fff9e9'
  }};
  var W1 = [
    '.......................aaaa..................', '....................aaabccca.................', '.................adabcccbcba.................',
    '................abcccbaabcba.................', '....bb..bb..bb..acbaaa.acba..................', '....beb.beb.bebfffffffgacba..................',
    '.gb.bbbbbbbbbbghiiiiiiiacbagff...............', '.bebcececececjkliiiiiiiacbaklmffj..jgfaa.....', '..bcebbbbbbbghiiiiiiiilaaaiiiiilnffhllbcaaa..',
    '.bbebooeeooojliiiiiiiiiiiiiiiiiiilmlpqaacccaa', 'bebcbooeeooghiiiiiorrliiiiiiiiiiiiiif..abaaca', 'bbbebeooeeofliiiioahrriiiiiiiiiiiiinq.abaabba',
    '..bccbeoeeofliiiiraaarliiiiiiiiiiiiqa.abbbaa.', '.bebecbbbbbfliiiiraahriiiiiiiiiiiiiqbaabaa...', '.bbbbcececefiiiiilrrrkiiiiiiiiiiiiiqbaaa.....',
    '....bbbbbbbfliiiiiiiiiiiiiiiiiiiiiiqaba......', '....beb.bebfliiniiiiiiiiiiiiiiiiiiiqaba......', '.....bb.fbbfmlnqiiniiiiniiiiiniiiiiqaba......',
    '........flmffqfkiinmiipniiiiqliiiiiqbba......', '.........qqmmliiiinmppnniiiiqliiiiiqaa.......', '..........apnnpppiimpmmnliilqpiiiina.........',
    '..........mpnmpnppnmpmpplppnqppppna..........', '..........mpnmpmpppppliilmppddpnnd...........', '..........mmnmpmpppppmlllmpdhaplma...........',
    '.........ajmaaaajmaaaaajmaaaajma.............', '.........ahpa..ahpa...ahpa..ahpa.............', '.........adaa..adaa...adaa..adaa.............'
  ];
  var W2 = [
    '.......................aaaa..................', '....................aaabccca.................', '.................adabcccbcba.................',
    '................abcccbaabcba.................', '....bb..bb..bb..acbaaa.acba..................', '....beb.beb.bebfffffffgacba..................',
    '.gb.bbbbbbbbbbghiiiiiiiacbagff...............', '.bebcececececjkliiiiiiiacbaklmffj..jgfaa.....', '..bcebbbbbbbghiiiiiiiilaaaiiiiilnffhllbcaaa..',
    '.bbebooeeooojliiiiiiiiiiiiiiiiiiilmlpqaacccaa', 'bebcbooeeooghiiiiiorrliiiiiiiiiiiiiif..abaaca', 'bbbebeooeeofliiiioahrriiiiiiiiiiiiinq.abaabba',
    '..bccbeoeeofliiiiraaarliiiiiiiiiiiiqa.abbbaa.', '.bebecbbbbbfliiiiraahriiiiiiiiiiiiiqbaabaa...', '.bbbbcececefiiiiilrrrkiiiiiiiiiiiiiqbaaa.....',
    '....bbbbbbbfliiiiiiiiiiiiiiiiiiiiiiqaba......', '....beb.bebfliiniiiiiiiiiiiiiiiiiiiqaba......', '.....bb.fbbfmlnqiiniiiiniiiiiniiiiiqaba......',
    '........flmffqfkiinmiipniiiiqliiiiiqbba......', '.........qqmmliiiinmppnniiiiqliiiiiqaa.......', '..........apnnpppiimpmmnliilqpiiiina.........',
    '..........mpnmpnppnmpmpplppnqppppna..........', '..........mpnmpmpppppliilmppddpnnd...........', '..........mmnmpmpppppmlllmpdhaplma...........',
    '.........ajmaaaajmaaaaajmaaaajma.............', '..........ahpa.ahpa....ahpa.ahpa.............', '..........adaa.adaa....adaa.adaa.............'
  ];
  var W3 = [
    '.......................aaaa..................', '....................aaabccca.................', '.................adabcccbcba.................',
    '................abcccbaabcba.................', '....bb..bb..bb..acbaaa.acba..................', '....beb.beb.bebfffffffgacba..................',
    '.gb.bbbbbbbbbbghiiiiiiiacbagff...............', '.bebcececececjkliiiiiiiacbaklmffj..jgfaa.....', '..bcebbbbbbbghiiiiiiiilaaaiiiiilnffhllbcaaa..',
    '.bbebooeeooojliiiiiiiiiiiiiiiiiiilmlpqaacccaa', 'bebcbooeeooghiiiiiorrliiiiiiiiiiiiiif..abaaca', 'bbbebeooeeofliiiioahrriiiiiiiiiiiiinq.abaabba',
    '..bccbeoeeofliiiiraaarliiiiiiiiiiiiqa.abbbaa.', '.bebecbbbbbfliiiiraahriiiiiiiiiiiiiqbaabaa...', '.bbbbcececefiiiiilrrrkiiiiiiiiiiiiiqbaaa.....',
    '....bbbbbbbfliiiiiiiiiiiiiiiiiiiiiiqaba......', '....beb.bebfliiniiiiiiiiiiiiiiiiiiiqaba......', '.....bb.fbbfmlnqiiniiiiniiiiiniiiiiqaba......',
    '........flmffqfkiinmiipniiiiqliiiiiqbba......', '.........qqmmliiiinmppnniiiiqliiiiiqaa.......', '..........apnnpppiimpmmnliilqpiiiina.........',
    '..........mpnmpnppnmpmpplppnqppppna..........', '..........mpnmpmpppppliilmppddpnnd...........', '..........mmnmpmpppppmlllmpdhaplma...........',
    '.........ajmaaaajmaaaaajmaaaajma.............', '.........ahpa..ahpa...ahpa..ahpa.............', '.........adaa..adaa...adaa..adaa.............'
  ];
  var W4 = [
    '.......................aaaa..................', '....................aaabccca.................', '.................adabcccbcba.................',
    '................abcccbaabcba.................', '....bb..bb..bb..acbaaa.acba..................', '....beb.beb.bebfffffffgacba..................',
    '.gb.bbbbbbbbbbghiiiiiiiacbagff...............', '.bebcececececjkliiiiiiiacbaklmffj..jgfaa.....', '..bcebbbbbbbghiiiiiiiilaaaiiiiilnffhllbcaaa..',
    '.bbebooeeooojliiiiiiiiiiiiiiiiiiilmlpqaacccaa', 'bebcbooeeooghiiiiiorrliiiiiiiiiiiiiif..abaaca', 'bbbebeooeeofliiiioahrriiiiiiiiiiiiinq.abaabba',
    '..bccbeoeeofliiiiraaarliiiiiiiiiiiiqa.abbbaa.', '.bebecbbbbbfliiiiraahriiiiiiiiiiiiiqbaabaa...', '.bbbbcececefiiiiilrrrkiiiiiiiiiiiiiqbaaa.....',
    '....bbbbbbbfliiiiiiiiiiiiiiiiiiiiiiqaba......', '....beb.bebfliiniiiiiiiiiiiiiiiiiiiqaba......', '.....bb.fbbfmlnqiiniiiiniiiiiniiiiiqaba......',
    '........flmffqfkiinmiipniiiiqliiiiiqbba......', '.........qqmmliiiinmppnniiiiqliiiiiqaa.......', '..........apnnpppiimpmmnliilqpiiiina.........',
    '..........mpnmpnppnmpmpplppnqppppna..........', '..........mpnmpmpppppliilmppddpnnd...........', '..........mmnmpmpppppmlllmpdhaplma...........',
    '.........ajmaaaajmaaaaajmaaaajma.............', '.........ahpa.ahpa....ahpa.ahpa..............', '.........adaa.adaa....adaa.adaa..............'
  ];
  var WALK = [W1, W2, W3, W4];

  // exhaust puffs above the blade, only while the chainsaw is revving
  var TICK_A = [[3,1],[4,1],[7,0],[8,0],[11,1],[12,1]];
  var TICK_B = [[4,2],[5,2],[8,1],[9,1],[12,2],[13,2]];

  var canvas = document.getElementById('pochita');
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext('2d');
  var S = 6;

  function draw(rows, ticks) {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (var y = 0; y < rows.length; y++) {{
      for (var x = 0; x < rows[y].length; x++) {{
        var c = PAL[rows[y][x]];
        if (c) {{ ctx.fillStyle = c; ctx.fillRect(x * S, y * S, S, S); }}
      }}
    }}
    if (ticks) {{
      ctx.fillStyle = '#3e261a';
      for (var i = 0; i < ticks.length; i++) ctx.fillRect(ticks[i][0]*S, ticks[i][1]*S, S, S);
    }}
  }}

  draw(WALK[0], null);

  var bubble = document.querySelector('.poch-say');
  if (bubble) setTimeout(function () {{ bubble.classList.add('show'); }}, 700);

  // Some people get motion sick, and some just don't want it. Respect that.
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  if (still && still.matches) return;

  var i = 0, revving = false, timer = null;
  function loop() {{
    var f = WALK[i % WALK.length];
    draw(f, revving ? (i % 2 ? TICK_B : TICK_A) : null);
    i++;
    timer = setTimeout(loop, revving ? 90 : 180);   // he picks up the pace when revving
  }}
  loop();

  // Hover a lesson link: chainsaw starts, he speeds up, the CSS class shakes him.
  function setRev(on) {{
    if (revving === on) return;
    revving = on;
    canvas.classList.toggle('revving', on);
    clearTimeout(timer);
    loop();
  }}
  [].slice.call(document.querySelectorAll('main a')).forEach(function (a) {{
    a.addEventListener('mouseenter', function () {{ setRev(true); }});
    a.addEventListener('mouseleave', function () {{ setRev(false); }});
    a.addEventListener('focus',      function () {{ setRev(true); }});
    a.addEventListener('blur',       function () {{ setRev(false); }});
  }});
}})();

// ---------------------------------------------------------------- Smiskis ---
// They hide behind a paragraph and peek out of it every so often.
//
// The trick: each Smiski lives in a zero-height div inserted just BEFORE a
// paragraph, and that paragraph is given the card's own background colour.
// Because the paragraph comes later in the DOM it paints on top, so nudging
// the Smiski down by its own height tucks it completely out of sight.
(function () {{
  var SPAL = {{ 'o': '#3d5c7d', 'L': '#9cc7e2', 'H': '#c6e3f4', 'K': '#22303e' }};
  var POSES = [
    ['...oooooo...', '..oHHHHHHo..', '.oHHHHHHHHo.', '.oHHHHHHHHo.', '.oLKKLLKKLo.', '.oLKKLLKKLo.', '.oLLLLLLLLo.', '.ooLLLLLLoo.', 'ooLLLLLLLLoo', 'oLoLLLLLLoLo', 'oLoLLLLLLoLo', 'oLoLLLLLLoLo', 'oooLLLLLLooo', '..oLLLLLLo..', '..oLLLLLLo..', '..oooooooo..'],
    ['...oooooo...', '..oHHHHHHo..', '.oHHHHHHHHo.', '.oHHHHHHHHo.', '.oLLKKLKKLo.', '.oLLKKLKKLo.', '.oLLLLLLLLo.', '.ooLLLLLLoo.', 'ooLLLLLLLLoo', 'oLoLLLLLLoLo', 'oLoLLLLLLoLo', 'oLoLLLLLLoLo', 'oooLLLLLLooo', '..oLLLLLLo..', '..oLLLLLLo..', '..oooooooo..'],
    ['...oooooo...', '..oHHHHHHo..', '.oHHHHHHHHo.', '.oHHHHHHHHo.', '.oKKLKKLLLo.', '.oKKLKKLLLo.', '.oLLLLLLLLo.', '.ooLLLLLLoo.', 'ooLLLLLLLLoo', 'oLoLLLLLLoLo', 'oLoLLLLLLoLo', 'oLoLLLLLLoLo', 'oooLLLLLLooo', '..oLLLLLLo..', '..oLLLLLLo..', '..oooooooo..']
  ];
  var SW = 12, SH = 16, SS = 3;

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

  // Anchor to blocks with blank space above them, and only rise as far as that
  // blank space allows — so a Smiski can never cover a word or a link.
  var blocks = [];
  [].slice.call(main.querySelectorAll('p, h3')).forEach(function (el) {{
    var prev = el.previousElementSibling;
    if (!prev || el.offsetHeight < SH * SS + 4) return;
    var gap = el.offsetTop - (prev.offsetTop + prev.offsetHeight);
    var show = Math.min(gap - 3, SH * SS - 6);
    if (show >= 12) blocks.push({{ el: el, show: show }});
  }});
  if (!blocks.length) return;

  function makeSlot(b, leftPct) {{
    b.el.style.position = 'relative';
    b.el.style.background = 'var(--card)';
    var host = document.createElement('div');
    host.className = 'peek-host';
    var c = document.createElement('canvas');
    c.className = 'smiski';
    c.width = SW * SS;
    c.height = SH * SS;
    c.setAttribute('aria-hidden', 'true');
    c.style.left = leftPct + '%';
    c.style.transform = 'translateY(100%)';
    c.dataset.rise = 'translateY(' + (SH * SS - b.show) + 'px)';
    paint(c, POSES[0]);
    host.appendChild(c);

    // Every slot carries a greeting; only the first one to actually appear
    // will ever show it. Right-hand slots put the bubble on their left so it
    // can't run off the edge of the card.
    var say = document.createElement('span');
    say.className = 'smiski-say';
    if (leftPct > 50) {{
      say.classList.add('flip');
      say.style.right = 'calc(' + (100 - leftPct) + '% + ' + (SW * SS + 12) + 'px)';
    }} else {{
      say.style.left = 'calc(' + leftPct + '% + ' + (SW * SS + 12) + 'px)';
    }}
    host.appendChild(say);
    c.bubble = say;

    b.el.parentNode.insertBefore(host, b.el);
    return c;
  }}

  // Several per block if need be, spread across the width, up to six.
  var LEFTS = [7, 38, 66, 22, 52, 80];
  var slots = [];
  var PHRASES = [
    'You found me.',
    'I was here the whole time.',
    "Don't mind me. Keep going.",
    'Oh \u2014 hello!',
    'Still here. Still hiding.',
    "Psst\u2026 you've got this.",
    'Welcome back, Evolett!',
    "How's it going, Evolett?",
    'Ready for lesson 3?'
  ];
  var lastPhrase = -1;
  for (var pass = 0; pass < 3 && slots.length < 6; pass++) {{
    for (var k = 0; k < blocks.length && slots.length < 6; k++) {{
      slots.push(makeSlot(blocks[k], LEFTS[slots.length % LEFTS.length]));
    }}
  }}

  function hiddenOnes() {{
    return slots.filter(function (c) {{ return c.style.transform.indexOf('100%') !== -1; }});
  }}

  function peek() {{
    var out = slots.length - hiddenOnes().length;
    if (out < 2) {{
      var hidden = hiddenOnes();
      if (hidden.length) {{
        var c = hidden[Math.floor(Math.random() * hidden.length)];
        paint(c, POSES[Math.floor(Math.random() * POSES.length)]);
        c.style.transform = c.dataset.rise;
        if (c.bubble) {{
          var n = Math.floor(Math.random() * PHRASES.length);
          if (n === lastPhrase) n = (n + 1) % PHRASES.length;   // no immediate repeats
          lastPhrase = n;
          c.bubble.textContent = PHRASES[n];
          var bub = c.bubble;
          setTimeout(function () {{ bub.classList.add('show'); }}, 280);
        }}
        setTimeout(function () {{
          c.style.transform = 'translateY(100%)';
          if (c.bubble) c.bubble.classList.remove('show');
        }}, 2600 + Math.random() * 1600);
      }}
    }}
    setTimeout(peek, 2200 + Math.random() * 2400);
  }}
  setTimeout(peek, 1200);
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
