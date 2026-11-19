"""Generate the space-themed profile graphics (animated SVG, no external assets).

    python3 scripts/make_banner.py assets

Writes banner.svg, header-<id>.svg and footer.svg.
"""
import os, random, sys

out = sys.argv[1] if len(sys.argv) > 1 else "assets"
os.makedirs(out, exist_ok=True)

SPACE0, SPACE1 = "#03040f", "#0d0b2b"
VIOLET, CYAN, PINK, GOLD = "#8b7bff", "#5ee7ff", "#ff7ad9", "#ffd27a"
INK, SOFT = "#f4f2ff", "#b9b4e6"
GREEN = "#5dffa8"
SANS = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

GLOW = """<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="haze" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="38"/></filter>"""


def stars(w, h, n, seed, ymax=None):
    random.seed(seed)
    s = []
    for _ in range(n):
        x, y = random.uniform(0, w), random.uniform(0, ymax or h)
        r = random.choice([.5, .7, .7, .9, 1.2, 1.6])
        col = random.choice(["#ffffff", "#ffffff", "#dcd6ff", "#c9f6ff"])
        tw = (f'<animate attributeName="opacity" values=".15;1;.15" dur="{random.uniform(2, 6):.1f}s" '
              f'begin="{random.uniform(0, 4):.1f}s" repeatCount="indefinite"/>') if random.random() < .35 else ""
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{col}" opacity="{random.uniform(.35, .9):.2f}">{tw}</circle>')
    return "".join(s)


def shooting(x, y, dx, dy, dur, begin):
    return (f'<line x1="0" y1="0" x2="-70" y2="-22" stroke="url(#trail)" stroke-width="2" stroke-linecap="round" opacity="0">'
            f'<animateTransform attributeName="transform" type="translate" values="{x} {y};{x + dx} {y + dy}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;.08;.25;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></line>')


def planet_defs():
    return f"""<radialGradient id="pl" cx=".35" cy=".3" r=".85"><stop offset="0" stop-color="#b6a8ff"/>
<stop offset=".45" stop-color="#5b45d6"/><stop offset="1" stop-color="#160f45"/></radialGradient>
<radialGradient id="atmo" cx=".5" cy=".5" r=".5"><stop offset=".78" stop-color="{CYAN}" stop-opacity="0"/>
<stop offset=".88" stop-color="{CYAN}" stop-opacity=".35"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<linearGradient id="ring" x1="0" x2="1"><stop offset="0" stop-color="{PINK}" stop-opacity=".2"/>
<stop offset=".5" stop-color="{GOLD}" stop-opacity=".9"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".2"/></linearGradient>
<linearGradient id="trail" x1="0" x2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>"""


def banner():
    W, H = 1200, 330
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Danesh Selwal. Civil engineer exploring AI and machine learning. Currently Graduate Engineer Trainee at L&amp;T Renewables, Tashkent.">']
    s.append(f'''<defs>{GLOW}{planet_defs()}
<radialGradient id="bg" cx=".7" cy=".4" r="1"><stop offset="0" stop-color="{SPACE1}"/><stop offset="1" stop-color="{SPACE0}"/></radialGradient>
<linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#d9d2ff"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>''')
    s.append('<g clip-path="url(#card)">')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    # nebula clouds
    s.append(f'<g filter="url(#haze)"><ellipse cx="820" cy="120" rx="230" ry="110" fill="#6d3cff" opacity=".38"/>'
             f'<ellipse cx="1080" cy="260" rx="200" ry="90" fill="#00b4d8" opacity=".22"/>'
             f'<ellipse cx="560" cy="300" rx="260" ry="70" fill="#ff4fd8" opacity=".14"/>'
             f'<ellipse cx="120" cy="40" rx="200" ry="80" fill="#3a2bd1" opacity=".22"/></g>')
    s.append(stars(W, H, 150, 11))
    s.append(shooting(380, 20, 520, 165, 7, 1.5) + shooting(900, 10, 420, 135, 9, 5))

    # neural-network constellation: signals travel between the "stars"
    layers = [(690, [85, 165, 245]), (770, [60, 125, 195, 265]), (850, [110, 220])]
    nodes = [(x, y) for x, ys in layers for y in ys]
    edges = [((x1, y1), (x2, y2)) for (x1, ys1), (x2, ys2) in zip(layers, layers[1:]) for y1 in ys1 for y2 in ys2]
    s.append('<g stroke="#a99cff" stroke-width=".8" opacity=".35">' +
             "".join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>' for a, b in edges) + '</g>')
    random.seed(5)
    for n, (a, b) in enumerate(random.sample(edges, 8)):
        col = [CYAN, PINK, GOLD][n % 3]
        s.append(f'<circle r="2.4" fill="{col}" filter="url(#glow)"><animateMotion path="M{a[0]},{a[1]} L{b[0]},{b[1]}" '
                 f'dur="{1.6 + n % 3 * .5:.1f}s" begin="{n * .45:.2f}s" repeatCount="indefinite"/></circle>')
    for n, (x, y) in enumerate(nodes):
        s.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#fff" filter="url(#glow)">'
                 f'<animate attributeName="r" values="3.2;4.6;3.2" dur="{2.2 + n % 4 * .4:.1f}s" repeatCount="indefinite"/></circle>')

    # ringed planet with an orbiting moon
    cx, cy, r = 1040, 168, 86
    ring = f'translate({cx} {cy}) rotate(-16)'
    s.append(f'<g transform="{ring}"><ellipse rx="158" ry="30" fill="none" stroke="url(#ring)" stroke-width="7" opacity=".45"/></g>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 1.28:.0f}" fill="url(#atmo)"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#pl)"/>')
    s.append(f'<g opacity=".18" stroke="#fff" fill="none" stroke-width="5">'
             f'<path d="M{cx - 80},{cy - 25} q80,-14 160,6"/><path d="M{cx - 84},{cy + 12} q84,-10 168,4"/><path d="M{cx - 70},{cy + 45} q70,-8 140,2"/></g>')
    s.append(f'<g transform="{ring}"><path d="M-158,0 A158,30 0 0 0 158,0" fill="none" stroke="url(#ring)" stroke-width="7"/>'
             f'<path d="M-140,0 A140,25 0 0 0 140,0" fill="none" stroke="{GOLD}" stroke-opacity=".35" stroke-width="2"/></g>')
    s.append(f'<circle r="7" fill="#e9e6ff" filter="url(#glow)"><animateMotion dur="12s" repeatCount="indefinite" '
             f'path="M{cx - 150},{cy - 70} a150,60 0 1,0 300,0 a150,60 0 1,0 -300,0"/></circle>')

    # text
    s.append(f'<g font-family="{SANS}">')
    s.append(f'<g font-family="{MONO}" font-size="13" letter-spacing=".6">'
             f'<rect x="60" y="30" width="470" height="28" rx="14" fill="#ffffff" fill-opacity=".06" stroke="{VIOLET}" stroke-opacity=".55"/>'
             f'<circle cx="78" cy="44" r="4.5" fill="#5dffa8"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>'
             f'<text x="92" y="48.5" fill="{SOFT}">CURRENTLY · <tspan fill="{INK}" font-weight="700">Graduate Engineer Trainee @ L&amp;T Renewables</tspan></text></g>')
    s.append(f'<text x="60" y="146" font-size="64" font-weight="800" fill="url(#name)" filter="url(#glow)">Danesh Selwal</text>')
    s.append(f'<text x="62" y="190" font-size="21" fill="{INK}" opacity=".92">Civil engineer exploring the universe of</text>')
    s.append(f'<text x="62" y="218" font-size="21" fill="{INK}" opacity=".92"><tspan fill="{CYAN}" font-weight="700">AI</tspan> &amp; '
             f'<tspan fill="{PINK}" font-weight="700">machine learning</tspan> ✦</text>')
    x = 62
    for label, col in [("Artificial Intelligence", CYAN), ("Machine Learning", VIOLET), ("Earth from space", PINK)]:
        w = len(label) * 8.4 + 34
        s.append(f'<rect x="{x}" y="246" width="{w:.0f}" height="32" rx="16" fill="{col}" fill-opacity=".10" stroke="{col}" stroke-opacity=".7"/>'
                 f'<circle cx="{x + 16}" cy="262" r="3.5" fill="{col}"/>'
                 f'<text x="{x + 27}" y="267" font-size="14" font-weight="600" fill="{INK}">{label}</text>')
        x += w + 10
    s.append(f'<text x="62" y="306" font-size="13" fill="{SOFT}" opacity=".85">Tashkent, Uzbekistan</text>')
    s.append('</g></g>')
    s.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{VIOLET}" stroke-opacity=".35"/>')
    s.append('</svg>')
    return "\n".join(s)


def header(title, sub, col, seed):
    w, h = 900, 58
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">
<defs>{GLOW}<linearGradient id="hb" x1="0" x2="1"><stop offset="0" stop-color="#120c38"/><stop offset="1" stop-color="{SPACE0}"/></linearGradient>
<radialGradient id="mini" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="{col}"/><stop offset="1" stop-color="#1a1250"/></radialGradient>
<clipPath id="c"><rect width="{w}" height="{h}" rx="14"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#hb)"/>{stars(w, h, 45, seed)}</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{col}" stroke-opacity=".45"/>
<g transform="rotate(-18 36 29)"><ellipse cx="36" cy="29" rx="19" ry="5" fill="none" stroke="{col}" stroke-opacity=".45" stroke-width="1.5"/></g>
<circle cx="36" cy="29" r="10" fill="url(#mini)"/>
<g transform="rotate(-18 36 29)"><path d="M17,29 A19,5 0 0 0 55,29" fill="none" stroke="{col}" stroke-width="1.8"/></g>
<circle r="2.2" fill="#fff" filter="url(#glow)"><animateMotion dur="4s" repeatCount="indefinite" path="M12,29 a24,9 0 1,0 48,0 a24,9 0 1,0 -48,0"/></circle>
<text x="70" y="37" font-family="{SANS}" font-size="22" font-weight="800" fill="{INK}">{title}</text>
<text x="{w - 24}" y="35" font-family="{SANS}" font-size="14" font-style="italic" fill="{col}" text-anchor="end">{sub}</text>
</svg>'''


def footer():
    w, h = 900, 130
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Thanks for stopping by. Keep exploring.">
<defs>{GLOW}{planet_defs()}<clipPath id="c"><rect width="{w}" height="{h}" rx="16"/></clipPath>
<radialGradient id="hz" cx=".5" cy="1" r=".8"><stop offset="0" stop-color="#6d3cff" stop-opacity=".55"/><stop offset="1" stop-color="{SPACE0}" stop-opacity="0"/></radialGradient></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{SPACE0}"/><rect width="{w}" height="{h}" fill="url(#hz)"/>
{stars(w, h, 70, 23, ymax=95)}{shooting(150, 10, 380, 120, 8, 2)}
<circle cx="{w / 2}" cy="{h + 535}" r="560" fill="url(#pl)"/>
<circle cx="{w / 2}" cy="{h + 535}" r="563" fill="none" stroke="{CYAN}" stroke-opacity=".6" stroke-width="2" filter="url(#glow)"/></g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="none" stroke="{VIOLET}" stroke-opacity=".35"/>
<text x="{w / 2}" y="46" font-family="{SANS}" font-size="20" font-weight="700" fill="{INK}" text-anchor="middle" filter="url(#glow)">Thanks for stopping by ✦ keep exploring</text>
<text x="{w / 2}" y="72" font-family="{SANS}" font-size="14" font-style="italic" fill="{SOFT}" text-anchor="middle">built on curiosity, one model at a time</text>
</svg>'''


HEADERS = [("about", "About me", "the person behind the telescope", CYAN, 1),
           ("explore", "What I explore", "where curiosity takes me", VIOLET, 2),
           ("current", "Currently working on", "missions in progress", GREEN, 5),
           ("pinned", "Pinned projects", "flagship missions", PINK, 3),
           ("built", "Other things I have built", "side quests", CYAN, 6),
           ("toolkit", "Toolkit", "what is on board", GOLD, 4)]

open(os.path.join(out, "banner.svg"), "w", encoding="utf-8").write(banner())
for key, title, sub, col, seed in HEADERS:
    open(os.path.join(out, f"header-{key}.svg"), "w", encoding="utf-8").write(header(title, sub, col, seed))
open(os.path.join(out, "footer.svg"), "w", encoding="utf-8").write(footer())
print("ok")
