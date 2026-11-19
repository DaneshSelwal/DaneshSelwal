"""Generate the profile banner (light + dark) as animated SVG.

A hyperspectral cube (six spectral bands, the top band classified into land
cover) with one pixel picked out and its conformal prediction set — the
research theme of the profile.
"""
import math, random, os, sys

out = sys.argv[1]
os.makedirs(out, exist_ok=True)

W, H = 1200, 320
N = 9                     # grid cells per side
A = (15, 7.5)             # iso step along i
B = (-15, 7.5)            # iso step along j
GAP = 21                  # vertical gap between band sheets
NB = 6                    # spectral bands
OX, OY = 935, 34          # apex of the top sheet

random.seed(7)
# smooth "land cover" field: nearest of a few seeds (Voronoi parcels)
seeds = [(random.uniform(0, N), random.uniform(0, N), c) for c in
         [0, 1, 2, 3, 1, 2, 4, 0, 3, 2, 1, 4]]
def cls(i, j):
    return min(seeds, key=lambda s: (s[0] - i - .5) ** 2 + (s[1] - j - .5) ** 2)[2]
# per-class reflectance across 6 bands (vegetation peaks in NIR etc.)
refl = {0: [.15, .20, .12, .70, .35, .20],   # crop
        1: [.18, .22, .25, .30, .45, .40],   # soil
        2: [.05, .06, .04, .03, .02, .02],   # water
        3: [.12, .18, .10, .55, .30, .15],   # forest
        4: [.35, .38, .40, .42, .50, .45]}   # built-up

THEMES = {
    "light": dict(bg0="#f6f8fb", bg1="#e9f0fa", dot="#c9d6e8", ink="#0f172a", sub="#475569",
                  accent="#2a78d6", accent2="#0f9d74", pill_bg="#ffffff", pill_bd="#d5e0ee",
                  band="#2a78d6", edge="#ffffff", call_bg="#ffffff", call_bd="#c9d6e8",
                  lc=["#e9b949", "#b07d4f", "#2a78d6", "#1f9e6e", "#9aa5b1"]),
    "dark": dict(bg0="#0d1117", bg1="#111b2e", dot="#1e2a3d", ink="#f1f5f9", sub="#94a3b8",
                 accent="#5aa2f0", accent2="#34d399", pill_bg="#131c2b", pill_bd="#26344a",
                 band="#5aa2f0", edge="#0d1117", call_bg="#131c2b", call_bd="#2b3b54",
                 lc=["#f2c55c", "#c8935f", "#4f97e8", "#34c38f", "#aab4c0"]),
}

def pt(i, j, k):
    return (OX + i * A[0] + j * B[0], OY + k * GAP + i * A[1] + j * B[1])

def poly(i, j, k):
    p = [pt(i, j, k), pt(i + 1, j, k), pt(i + 1, j + 1, k), pt(i, j + 1, k)]
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in p)

def mix(hex1, hex2, t):
    a = [int(hex1[n:n + 2], 16) for n in (1, 3, 5)]
    b = [int(hex2[n:n + 2], 16) for n in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))

def banner(t):
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'role="img" aria-label="Danesh Selwal — Civil Engineering and Machine Learning">')
    s.append(f'''<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg0"]}"/><stop offset="1" stop-color="{t["bg1"]}"/></linearGradient>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{t["dot"]}"/></pattern>
<linearGradient id="fadeR" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".55" stop-color="#fff" stop-opacity="1"/></linearGradient>
<mask id="m"><rect width="{W}" height="{H}" fill="url(#fadeR)"/></mask>
<style>
.f{{font-family:'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif}}
.mono{{font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace}}
</style></defs>''')
    s.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>')
    s.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#dots)" mask="url(#m)" opacity=".9"/>')

    # ---- left: text -------------------------------------------------------
    s.append(f'<g class="f">')
    s.append(f'<text class="in" x="64" y="92" font-size="14" font-weight="700" letter-spacing="3.2" fill="{t["accent"]}">CIVIL ENGINEERING × MACHINE LEARNING</text>')
    s.append(f'<text class="in" style="animation-delay:.15s" x="62" y="160" font-size="62" font-weight="800" fill="{t["ink"]}">Danesh Selwal</text>')
    s.append(f'<text class="in" style="animation-delay:.3s" x="64" y="200" font-size="20" fill="{t["sub"]}">Building models that know when they might be wrong —</text>')
    s.append(f'<text class="in" style="animation-delay:.3s" x="64" y="228" font-size="20" fill="{t["sub"]}">uncertainty quantification for remote sensing and engineering.</text>')
    x = 64
    for k, label in enumerate(["Conformal prediction", "Hyperspectral imaging", "Probabilistic ML"]):
        w = 15 + len(label) * 8.3 + 15
        s.append(f'<g class="in" style="animation-delay:{.45 + .1 * k:.2f}s">'
                 f'<rect x="{x}" y="252" width="{w:.0f}" height="32" rx="16" fill="{t["pill_bg"]}" stroke="{t["pill_bd"]}"/>'
                 f'<circle cx="{x + 15}" cy="268" r="4" fill="{[t["accent"], t["accent2"], "#eb6834"][k]}"/>'
                 f'<text x="{x + 26}" y="273" font-size="14" font-weight="600" fill="{t["ink"]}">{label}</text></g>')
        x += w + 10
    s.append('</g>')

    # ---- right: hyperspectral cube ---------------------------------------
    s.append('<g>')
    for k in range(NB - 1, -1, -1):          # bottom band first
        top = (k == 0)
        s.append(f'<g opacity="{1 if top else .55 + .07 * (NB - k):.2f}">')
        for i in range(N):
            for j in range(N):
                c = cls(i, j)
                if top:
                    col = t["lc"][c]
                else:
                    band = NB - k        # 1..5 for sheets below the top
                    col = mix(t["bg0"], t["band"], .15 + .8 * refl[c][band % 6])
                s.append(f'<polygon points="{poly(i, j, k)}" fill="{col}" stroke="{t["edge"]}" stroke-width=".8"/>')
        s.append('</g>')
        if k == 0:
            pass
    # scanning band highlight: an outline sliding down through the sheets
    hl = " ".join(f"{x:.1f},{y:.1f}" for x, y in [pt(0, 0, 0), pt(N, 0, 0), pt(N, N, 0), pt(0, N, 0)])
    s.append(f'<polygon points="{hl}" fill="none" stroke="{t["accent"]}" stroke-width="2">'
             f'<animateTransform attributeName="transform" type="translate" values="0 {GAP*(NB-1)};0 0;0 0" keyTimes="0;.45;1" dur="5s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.75;1" dur="5s" repeatCount="indefinite"/></polygon>')
    # the picked pixel and its spectrum column
    pi, pj = 5, 2
    s.append(f'<polygon points="{poly(pi, pj, 0)}" fill="none" stroke="{t["ink"]}" stroke-width="2.4">'
             f'<animate attributeName="stroke-opacity" values="1;.25;1" dur="1.8s" repeatCount="indefinite"/></polygon>')
    cx, cy = [sum(v) / 4 for v in zip(*[pt(pi, pj, 0), pt(pi + 1, pj, 0), pt(pi + 1, pj + 1, 0), pt(pi, pj + 1, 0)])]
    s.append('</g>')

    # ---- callout: the prediction set --------------------------------------
    bx, by = 1022, 214
    s.append(f'<path d="M{cx:.1f},{cy:.1f} C {cx + 60:.1f},{cy:.1f} {bx - 40},{by + 26} {bx},{by + 26}" fill="none" '
             f'stroke="{t["sub"]}" stroke-width="1.4" stroke-dasharray="4 4"><animate attributeName="stroke-dashoffset" values="16;0" dur="1.2s" repeatCount="indefinite"/></path>')
    s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.2" fill="{t["ink"]}"/>')
    s.append(f'<g class="f"><rect x="{bx}" y="{by}" width="160" height="66" rx="10" fill="{t["call_bg"]}" stroke="{t["call_bd"]}"/>'
             f'<text x="{bx + 14}" y="{by + 22}" font-size="11" font-weight="700" letter-spacing="1.4" fill="{t["sub"]}">PREDICTION SET</text>'
             f'<text class="mono" x="{bx + 14}" y="{by + 44}" font-size="15" font-weight="700" fill="{t["ink"]}">{{crop, soil}}</text>'
             f'<text x="{bx + 14}" y="{by + 59}" font-size="11.5" fill="{t["accent2"]}">✓ 95% coverage guarantee</text></g>')
    s.append('</svg>')
    return "\n".join(s)

for name, t in THEMES.items():
    open(os.path.join(out, f"banner-{name}.svg"), "w", encoding="utf-8").write(banner(t))
print("ok")
