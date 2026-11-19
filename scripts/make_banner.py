"""Generate the sci-fi profile graphics (animated SVG, no external assets).

    python3 scripts/make_banner.py assets

Writes:
  banner.svg          HUD banner: glitching name, scanlines, holographic
                      hyperspectral cube, targeting reticle, readout panel
  header-<id>.svg     HUD section headers
  footer.svg          "end of transmission" footer
"""
import os, random, sys

out = sys.argv[1] if len(sys.argv) > 1 else "assets"
os.makedirs(out, exist_ok=True)

CYAN, MAG, GRN, AMB = "#00e5ff", "#ff3df2", "#39ff88", "#ffb84d"
BG0, BG1, INK, DIM = "#05070d", "#0b1324", "#e6f7ff", "#7f93ad"
MONO = "'SFMono-Regular','JetBrains Mono',Consolas,'Liberation Mono',Menlo,monospace"
SANS = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"

GLOW = f"""<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
  <feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="glow2" x="-30%" y="-30%" width="160%" height="160%">
  <feGaussianBlur stdDeviation="1.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>"""


def brackets(w, h, inset=14, ln=26, col=CYAN):
    p = []
    for x, y, dx, dy in [(inset, inset, 1, 1), (w - inset, inset, -1, 1),
                         (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1)]:
        p.append(f'<path d="M{x},{y + dy * ln} L{x},{y} L{x + dx * ln},{y}" fill="none" stroke="{col}" stroke-width="2"/>')
    return "".join(p)


# --------------------------------------------------------------------------
# banner
# --------------------------------------------------------------------------
W, H = 1200, 340
N, A, B, GAP, NB = 9, (15, 7.5), (-15, 7.5), 21, 6
OX, OY = 880, 74
random.seed(7)
seeds = [(random.uniform(0, N), random.uniform(0, N), c) for c in [0, 1, 2, 3, 1, 2, 4, 0, 3, 2, 1, 4]]
LC = ["#ffd34d", "#ff8a3d", "#00b3ff", "#39ff88", "#a0a8ff"]   # crop soil water forest built
REFL = {0: [.15, .20, .12, .70, .35, .20], 1: [.18, .22, .25, .30, .45, .40],
        2: [.05, .06, .04, .03, .02, .02], 3: [.12, .18, .10, .55, .30, .15],
        4: [.35, .38, .40, .42, .50, .45]}


def cls(i, j):
    return min(seeds, key=lambda s: (s[0] - i - .5) ** 2 + (s[1] - j - .5) ** 2)[2]


def pt(i, j, k):
    return (OX + i * A[0] + j * B[0], OY + k * GAP + i * A[1] + j * B[1])


def poly(i, j, k):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in
                    [pt(i, j, k), pt(i + 1, j, k), pt(i + 1, j + 1, k), pt(i, j + 1, k)])


def banner():
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Danesh Selwal. Civil engineering times machine learning. Building models that know when they might be wrong.">']
    s.append(f'''<defs>{GLOW}
<radialGradient id="bg" cx=".72" cy=".45" r=".9"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/></radialGradient>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#ffffff" opacity=".035"/></pattern>
<linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}" stop-opacity=".10"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
<linearGradient id="floorfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>
<mask id="floormask"><rect x="0" y="230" width="{W}" height="110" fill="url(#floorfade)"/></mask>
<clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>''')
    s.append('<g clip-path="url(#card)">')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    # stars
    random.seed(3)
    for _ in range(70):
        x, y, r = random.uniform(0, W), random.uniform(0, 230), random.choice([.6, .8, 1.1])
        tw = f'<animate attributeName="opacity" values=".2;1;.2" dur="{random.uniform(2, 5):.1f}s" begin="{random.uniform(0, 3):.1f}s" repeatCount="indefinite"/>' if random.random() < .3 else ""
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#cfe9ff" opacity=".55">{tw}</circle>')

    # perspective floor grid
    g = [f'<g mask="url(#floormask)" stroke="{CYAN}" stroke-width="1" opacity=".22">']
    vpx, vpy = 600, 228
    for x in range(-1200, 2401, 80):
        g.append(f'<line x1="{vpx}" y1="{vpy}" x2="{x}" y2="{H}"/>')
    y, step = 236, 3
    while y < H:
        g.append(f'<line x1="0" y1="{y:.1f}" x2="{W}" y2="{y:.1f}"/>')
        step *= 1.38
        y += step
    g.append('</g>')
    s += g

    # holographic cube
    s.append('<g filter="url(#glow2)">')
    for k in range(NB - 1, -1, -1):
        top = k == 0
        s.append(f'<g opacity="{1 if top else .30 + .06 * (NB - k):.2f}">')
        for i in range(N):
            for j in range(N):
                c = cls(i, j)
                if top:
                    s.append(f'<polygon points="{poly(i, j, k)}" fill="{LC[c]}" fill-opacity=".78" stroke="{BG0}" stroke-width=".9"/>')
                else:
                    a = .08 + .55 * REFL[c][(NB - k) % 6]
                    s.append(f'<polygon points="{poly(i, j, k)}" fill="{CYAN}" fill-opacity="{a:.2f}" stroke="{CYAN}" stroke-opacity=".35" stroke-width=".6"/>')
        s.append('</g>')
    # outline of the stack (vertical edges)
    for (i, j) in [(0, 0), (N, 0), (N, N), (0, N)]:
        x0, y0 = pt(i, j, 0)
        x1, y1 = pt(i, j, NB - 1)
        s.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{CYAN}" stroke-opacity=".55" stroke-dasharray="3 3"/>')
    s.append('</g>')
    # band sweep through the sheets
    hl = " ".join(f"{x:.1f},{y:.1f}" for x, y in [pt(0, 0, 0), pt(N, 0, 0), pt(N, N, 0), pt(0, N, 0)])
    s.append(f'<polygon points="{hl}" fill="{CYAN}" fill-opacity=".06" stroke="{CYAN}" stroke-width="2" filter="url(#glow)">'
             f'<animateTransform attributeName="transform" type="translate" values="0 {GAP * (NB - 1)};0 0;0 0" keyTimes="0;.45;1" dur="4.5s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.75;1" dur="4.5s" repeatCount="indefinite"/></polygon>')

    # targeting reticle on one pixel
    pi, pj = 5, 2
    cx, cy = [sum(v) / 4 for v in zip(pt(pi, pj, 0), pt(pi + 1, pj, 0), pt(pi + 1, pj + 1, 0), pt(pi, pj + 1, 0))]
    s.append(f'<g filter="url(#glow)" stroke="{MAG}" fill="none">'
             f'<polygon points="{poly(pi, pj, 0)}" stroke-width="2"><animate attributeName="stroke-opacity" values="1;.3;1" dur="1.2s" repeatCount="indefinite"/></polygon>'
             f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="17" stroke-width="1.4" stroke-dasharray="6 5">'
             f'<animateTransform attributeName="transform" type="rotate" from="0 {cx:.1f} {cy:.1f}" to="360 {cx:.1f} {cy:.1f}" dur="6s" repeatCount="indefinite"/></circle>'
             f'<path d="M{cx - 26:.1f},{cy:.1f}h8 M{cx + 18:.1f},{cy:.1f}h8 M{cx:.1f},{cy - 26:.1f}v8 M{cx:.1f},{cy + 18:.1f}v8" stroke-width="1.6"/></g>')

    # readout panel
    bx, by, bw, bh = 1028, 128, 152, 168
    s.append(f'<path d="M{cx + 17:.1f},{cy:.1f} L{bx - 24},{cy:.1f} L{bx},{by + 18}" fill="none" stroke="{MAG}" stroke-width="1.2" stroke-dasharray="4 3" opacity=".9">'
             f'<animate attributeName="stroke-dashoffset" values="14;0" dur="1s" repeatCount="indefinite"/></path>')
    s.append(f'<g font-family="{MONO}">'
             f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="6" fill="{BG0}" fill-opacity=".82" stroke="{MAG}" stroke-opacity=".7"/>'
             f'<rect x="{bx}" y="{by}" width="{bw}" height="20" rx="6" fill="{MAG}" fill-opacity=".18"/>'
             f'<text x="{bx + 10}" y="{by + 14}" font-size="10.5" font-weight="700" letter-spacing="1.5" fill="{MAG}">TARGET // PX[5,2]</text>'
             f'<text x="{bx + 10}" y="{by + 40}" font-size="10" letter-spacing="1.2" fill="{DIM}">PREDICTION SET</text>'
             f'<text x="{bx + 10}" y="{by + 60}" font-size="15" font-weight="700" fill="{INK}" filter="url(#glow2)">{{crop, soil}}</text>'
             f'<text x="{bx + 10}" y="{by + 82}" font-size="10" letter-spacing="1.2" fill="{DIM}">COVERAGE</text>'
             f'<text x="{bx + 10}" y="{by + 99}" font-size="13" font-weight="700" fill="{GRN}">≥ 0.95  ✓ LOCKED</text>'
             f'<text x="{bx + 10}" y="{by + 120}" font-size="10" letter-spacing="1.2" fill="{DIM}">SPECTRUM</text>')
    # animated spectrum bars
    base = [.25, .32, .22, .85, .55, .35, .3, .62, .45, .28, .5, .38]
    for n, v in enumerate(base):
        x = bx + 10 + n * 11
        h1, h2 = 30 * v, 30 * min(1, v * 1.25 + .08)
        s.append(f'<rect x="{x}" y="{by + 158 - h1:.1f}" width="7" height="{h1:.1f}" fill="{CYAN}" opacity=".85">'
                 f'<animate attributeName="height" values="{h1:.1f};{h2:.1f};{h1:.1f}" dur="{1.4 + n % 4 * .3:.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y" values="{by + 158 - h1:.1f};{by + 158 - h2:.1f};{by + 158 - h1:.1f}" dur="{1.4 + n % 4 * .3:.1f}s" repeatCount="indefinite"/></rect>')
    s.append('</g>')

    # left: HUD text
    s.append(f'<g font-family="{MONO}">')
    s.append(f'<text x="60" y="45" font-size="13" letter-spacing="1.5" fill="{DIM}">'
             f'<tspan fill="{GRN}">◉<animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></tspan> CURRENTLY  //  '
             f'<tspan fill="{GRN}" font-weight="700">GRADUATE ENGINEER TRAINEE @ L&amp;T RENEWABLES</tspan>  ·  TASHKENT</text>')
    s.append(f'<text x="1160" y="44" font-size="12" letter-spacing="2" fill="{DIM}" text-anchor="end">α = 0.05  ·  TARGET 95%</text>')
    s.append(f'<text x="62" y="104" font-size="13" font-weight="700" letter-spacing="3.5" fill="{CYAN}">CIVIL ENGINEERING × MACHINE LEARNING</text>')
    name = "DANESH SELWAL"
    attrs = f'x="58" y="168" font-size="54" font-weight="800" letter-spacing="3"'
    jit = 'values="0 0;0 0;4 -1;-3 1;2 0;0 0" keyTimes="0;.86;.89;.92;.95;1" dur="4s" repeatCount="indefinite"'
    s.append(f'<text {attrs} fill="{MAG}" opacity=".75"><animateTransform attributeName="transform" type="translate" {jit}/>{name}</text>')
    s.append(f'<text {attrs} fill="{CYAN}" opacity=".75"><animateTransform attributeName="transform" type="translate" '
             f'values="0 0;0 0;-4 1;3 -1;-2 0;0 0" keyTimes="0;.86;.89;.92;.95;1" dur="4s" repeatCount="indefinite"/>{name}</text>')
    s.append(f'<text {attrs} fill="{INK}" filter="url(#glow2)">{name}</text>')
    s.append(f'<text x="62" y="208" font-size="16" fill="{INK}" opacity=".88"><tspan fill="{CYAN}">&gt;</tspan> building models that know when they might be wrong</text>')
    s.append(f'<text x="62" y="234" font-size="16" fill="{INK}" opacity=".88"><tspan fill="{CYAN}">&gt;</tspan> uncertainty quantification · remote sensing · engineering'
             f'<tspan fill="{CYAN}">▌<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/></tspan></text>')
    x = 62
    for k, (label, col) in enumerate([("CONFORMAL PREDICTION", CYAN), ("HYPERSPECTRAL", GRN), ("PROBABILISTIC ML", MAG)]):
        w = len(label) * 8.1 + 30
        s.append(f'<g><rect x="{x}" y="258" width="{w:.0f}" height="28" rx="3" fill="{col}" fill-opacity=".08" stroke="{col}" stroke-opacity=".75"/>'
                 f'<text x="{x + w / 2:.0f}" y="276.5" font-size="11.5" font-weight="700" letter-spacing="1.5" fill="{col}" text-anchor="middle">{label}</text></g>')
        x += w + 10
    s.append(f'<text x="60" y="318" font-size="11" letter-spacing="2" fill="{DIM}">BANDS 65  ·  CLASSES 8  ·  BACKBONES 11  ·  UQ METHODS 11</text>')
    s.append('</g>')

    # scanlines + sweep + frame
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append(f'<rect x="0" y="-80" width="{W}" height="80" fill="url(#sweep)">'
             f'<animate attributeName="y" values="-80;{H}" dur="5s" repeatCount="indefinite"/></rect>')
    s.append('</g>')
    s.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{CYAN}" stroke-opacity=".35"/>')
    s.append(brackets(W, H))
    s.append('</svg>')
    return "\n".join(s)


# --------------------------------------------------------------------------
# section headers + footer
# --------------------------------------------------------------------------
def header(num, title, tag, col):
    w, h = 900, 52
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">
<defs>{GLOW}<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{col}" stop-opacity=".9"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="8" fill="{BG0}" stroke="{col}" stroke-opacity=".35"/>
<g font-family="{MONO}">
<text x="20" y="32" font-size="13" font-weight="700" letter-spacing="2" fill="{DIM}">{num} //</text>
<text x="78" y="33" font-size="19" font-weight="800" letter-spacing="3" fill="{col}" filter="url(#glow2)">{title}</text>
<text x="{w - 20}" y="31" font-size="11.5" font-weight="700" letter-spacing="2" fill="{col}" text-anchor="end">[ {tag} ]</text>
</g>
<rect x="{100 + len(title) * 14.5:.0f}" y="25" width="{w - 230 - len(title) * 14.5 - len(tag) * 8:.0f}" height="1.5" fill="url(#ln)"/>
<circle cx="0" cy="25.75" r="3" fill="{col}" filter="url(#glow)"><animate attributeName="cx" values="{100 + len(title) * 14.5:.0f};{w - 140 - len(tag) * 8:.0f}" dur="2.6s" repeatCount="indefinite"/>
<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.8;1" dur="2.6s" repeatCount="indefinite"/></circle>
{brackets(w, h, inset=6, ln=10, col=col)}
</svg>'''


def footer():
    w, h = 900, 76
    dots = "".join(f'<circle cx="{410 + 20 * n}" cy="22" r="3.5" fill="{c}" filter="url(#glow)"><animate attributeName="opacity" values=".2;1;.2" dur="1.5s" begin="{n * .25}s" repeatCount="indefinite"/></circle>'
                   for n, c in enumerate([CYAN, MAG, GRN, AMB, CYAN]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="End of transmission">
<defs>{GLOW}</defs>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="8" fill="{BG0}" stroke="{CYAN}" stroke-opacity=".35"/>
{dots}
<g font-family="{MONO}" text-anchor="middle">
<text x="{w / 2}" y="46" font-size="12.5" font-weight="700" letter-spacing="4" fill="{CYAN}" filter="url(#glow2)">END OF TRANSMISSION</text>
<text x="{w / 2}" y="64" font-size="11" letter-spacing="1" fill="{DIM}">predictions are easy. knowing when to trust them is the interesting part.</text>
</g>
{brackets(w, h, inset=6, ln=10)}
</svg>'''


HEADERS = [("about", "01", "ABOUT", "IDENTITY", CYAN),
           ("focus", "02", "RESEARCH VECTORS", "3 ACTIVE", GRN),
           ("work", "03", "MISSION LOG", "FEATURED", MAG),
           ("toolbox", "04", "ARSENAL", "LOADED", AMB),
           ("telemetry", "05", "TELEMETRY", "LIVE", CYAN)]

open(os.path.join(out, "banner.svg"), "w", encoding="utf-8").write(banner())
for key, num, title, tag, col in HEADERS:
    open(os.path.join(out, f"header-{key}.svg"), "w", encoding="utf-8").write(header(num, title, tag, col))
open(os.path.join(out, "footer.svg"), "w", encoding="utf-8").write(footer())
print("ok")
