"""Build the project preview images for the profile README.

    python3 scripts/make_project_images.py assets/projects [download_dir]

* Research projects: real figures fetched from the project repositories,
  trimmed and framed on a dark "space" card (PNG, needs Pillow).
* Projects without figures (apps, agent tools): drawn cover art (SVG).
"""
import os, random, sys, urllib.request

out = sys.argv[1] if len(sys.argv) > 1 else "assets/projects"
dl = sys.argv[2] if len(sys.argv) > 2 else os.path.join(out, "_downloads")
os.makedirs(out, exist_ok=True)
os.makedirs(dl, exist_ok=True)

W, H = 800, 420
SPACE0, SPACE1 = "#03040f", "#120c38"
VIOLET, CYAN, PINK, GOLD, GREEN = "#8b7bff", "#5ee7ff", "#ff7ad9", "#ffd27a", "#5dffa8"
INK, SOFT = "#f4f2ff", "#b9b4e6"
SANS = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
RAW = "https://raw.githubusercontent.com/DaneshSelwal/"


# ---------------------------------------------------------------- figures ---
def figures():
    from PIL import Image, ImageChops, ImageDraw, ImageFilter

    def get(name, path):
        f = os.path.join(dl, name)
        if not os.path.exists(f):
            urllib.request.urlretrieve(RAW + path.replace(" ", "%20"), f)
        return Image.open(f).convert("RGB")

    def trim(im, pad=6):
        bb = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
        return im.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad)))

    def strip_title(im, frac):
        return im.crop((0, int(im.height * frac), im.width, im.height))

    def canvas():
        c = Image.new("RGB", (W * 2, H * 2), SPACE0)
        g = Image.new("RGB", (W * 2, H * 2), SPACE1)
        mask = Image.linear_gradient("L").rotate(90).resize((W * 2, H * 2))
        c = Image.composite(g, c, mask)
        random.seed(len(os.listdir(out)))
        d = ImageDraw.Draw(c)
        for _ in range(140):
            x, y, r = random.uniform(0, W * 2), random.uniform(0, H * 2), random.choice([1, 1.5, 2, 3])
            v = random.randint(140, 255)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(v, v, 255))
        return c

    def frame(panels, name, gap=18):
        c = canvas()
        # place panels side by side inside a white rounded sheet
        aw, ah = W * 2 - 120, H * 2 - 120
        tw = sum(p.width * 1000 / p.height for p in panels) + gap * (len(panels) - 1)
        s = min(ah / 1000, (aw - 48) / tw)
        ps = [p.resize((int(p.width * 1000 / p.height * s), int(1000 * s)), Image.LANCZOS) for p in panels]
        sw = sum(p.width for p in ps) + gap * (len(ps) - 1) + 48
        sh = ps[0].height + 48
        x0, y0 = (W * 2 - sw) // 2, (H * 2 - sh) // 2
        glow = Image.new("L", c.size, 0)
        ImageDraw.Draw(glow).rounded_rectangle((x0 - 6, y0 - 6, x0 + sw + 6, y0 + sh + 6), 34, fill=150)
        glow = glow.filter(ImageFilter.GaussianBlur(22))
        c = Image.composite(Image.new("RGB", c.size, (139, 123, 255)), c, glow)
        sheet = Image.new("L", c.size, 0)
        ImageDraw.Draw(sheet).rounded_rectangle((x0, y0, x0 + sw, y0 + sh), 28, fill=255)
        c = Image.composite(Image.new("RGB", c.size, "white"), c, sheet)
        x = x0 + 24
        for p in ps:
            c.paste(p, (x, y0 + 24))
            x += p.width + gap
        ImageDraw.Draw(c).rounded_rectangle((2, 2, W * 2 - 3, H * 2 - 3), 44, outline=(139, 123, 255), width=4)
        corner = Image.new("L", c.size, 0)
        ImageDraw.Draw(corner).rounded_rectangle((0, 0, W * 2 - 1, H * 2 - 1), 44, fill=255)
        c = c.convert("RGBA"); c.putalpha(corner)
        c.resize((W, H), Image.LANCZOS).save(os.path.join(out, name), optimize=True)

    # DIAS hyperspectral: scene, ground truth, model map
    sv = "DIAS-65Band-Hyperspectral-UQ/main/baseline/results/scene_visualizations/"
    frame([trim(strip_title(get(f"dias_{k}.png", sv + f), .07)) for k, f in
           [("rgb", "scene_rgb.png"), ("gt", "ground_truth_label_map.png"), ("gfnet", "GFNet_initial_classification.png")]],
          "dias.png")

    # 6-band overview: scene, truth, one model (cut out of the 5-panel figure)
    ov = get("six.png", "Classification_Uncertainty_Quantification_Analysis/main/Classification/baseline/results/"
                        "scene_visualizations/combined_initial_classification_overview.png")
    body = ov.crop((0, int(ov.height * .03), ov.width, int(ov.height * .80)))
    cols = [i for i in range(body.width) if min(body.crop((i, body.height // 3, i + 1, 2 * body.height // 3)).convert("L").getdata()) < 235]
    runs, start = [], cols[0]
    for a, b in zip(cols, cols[1:] + [None]):
        if b is None or b - a > 8:
            runs.append((start, a)); start = b
    runs = [r for r in runs if r[1] - r[0] > body.width * .1]
    pick = [runs[i] for i in (0, 1, 3)] if len(runs) >= 4 else runs[:3]
    frame([trim(body.crop((a, 0, b + 1, body.height))) for a, b in pick], "classification.png")

    # Singrauli LULC: the three classified maps + legend
    lu = get("lulc.png", "LULC_Classification_Singrauli_region/updated_version1/Results/Comparison Results/Classified Images.png")
    frame([trim(strip_title(lu, .08))], "lulc.png")


# ----------------------------------------------------------------- covers ---
def stars(n, seed, ymax=H):
    random.seed(seed)
    s = []
    for _ in range(n):
        x, y, r = random.uniform(0, W), random.uniform(0, ymax), random.choice([.6, .8, 1, 1.4])
        tw = (f'<animate attributeName="opacity" values=".2;1;.2" dur="{random.uniform(2, 5):.1f}s" '
              f'repeatCount="indefinite"/>') if random.random() < .3 else ""
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" opacity="{random.uniform(.3, .85):.2f}">{tw}</circle>')
    return "".join(s)


def svg(name, label, body, seed, accent=VIOLET):
    return name, f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
<defs><radialGradient id="bg" cx=".7" cy=".3" r="1"><stop offset="0" stop-color="{SPACE1}"/><stop offset="1" stop-color="{SPACE0}"/></radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="haze" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
<clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath></defs>
<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#bg)"/>
<g filter="url(#haze)"><ellipse cx="600" cy="120" rx="200" ry="110" fill="{accent}" opacity=".35"/><ellipse cx="160" cy="360" rx="200" ry="80" fill="#00b4d8" opacity=".18"/></g>
{stars(90, seed)}{body}</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="{accent}" stroke-opacity=".5" stroke-width="2"/>
</svg>'''


def chip(x, y, text, col, size=15):
    w = len(text) * size * .56 + 30
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{size + 17}" rx="{(size + 17) / 2}" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".75"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + size + 4}" font-family="{SANS}" font-size="{size}" font-weight="600" fill="{INK}" text-anchor="middle">{text}</text>'), w


def mytube():
    # phone mockup in the app's own "Midnight Vinyl" palette
    BG, SURF, ACC, ACC2, TXT, TXT2 = "#0D0B0F", "#161218", "#B08DFF", "#FFD98E", "#F2EEF8", "#9A8FAA"
    px, py, pw, ph = 70, 34, 210, 352
    vx, vy = px + pw / 2, py + 138
    b = [f'<defs><radialGradient id="vinyl" r=".5"><stop offset="0" stop-color="#2a2232"/><stop offset=".97" stop-color="#0a080c"/><stop offset="1" stop-color="#55505c"/></radialGradient>'
         f'<radialGradient id="mesh" cx=".5" cy=".3" r=".8"><stop offset="0" stop-color="{ACC}" stop-opacity=".55"><animate attributeName="stop-opacity" values=".55;.25;.55" dur="4s" repeatCount="indefinite"/></stop>'
         f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>'
         f'<clipPath id="scr"><rect x="{px + 8}" y="{py + 8}" width="{pw - 16}" height="{ph - 16}" rx="26"/></clipPath></defs>',
         f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="34" fill="#1b1720" stroke="#4a3f55" stroke-width="2"/>',
         f'<g clip-path="url(#scr)"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{BG}"/><rect x="{px}" y="{py}" width="{pw}" height="{ph * .7}" fill="url(#mesh)"/>',
         f'<text x="{vx}" y="{py + 38}" font-family="{SANS}" font-size="10" letter-spacing="2" fill="{TXT2}" text-anchor="middle">NOW PLAYING</text>',
         f'<g><circle cx="{vx}" cy="{vy}" r="72" fill="url(#vinyl)"/>'
         + "".join(f'<circle cx="{vx}" cy="{vy}" r="{r}" fill="none" stroke="#ffffff" stroke-opacity=".06"/>' for r in range(30, 70, 6)) +
         f'<path d="M{vx - 60},{vy - 30} A68,68 0 0 1 {vx - 20},{vy - 66}" stroke="#ffffff" stroke-opacity=".18" stroke-width="5" fill="none"/>'
         f'<circle cx="{vx}" cy="{vy}" r="24" fill="{ACC}"/><circle cx="{vx}" cy="{vy}" r="4" fill="{BG}"/>'
         f'<animateTransform attributeName="transform" type="rotate" from="0 {vx} {vy}" to="360 {vx} {vy}" dur="6s" repeatCount="indefinite"/></g>',
         f'<text x="{vx}" y="{py + 245}" font-family="Georgia,serif" font-size="17" fill="{TXT}" text-anchor="middle">Midnight Vinyl</text>',
         f'<text x="{vx}" y="{py + 263}" font-family="{SANS}" font-size="11" fill="{TXT2}" text-anchor="middle">your local library</text>',
         f'<rect x="{px + 28}" y="{py + 280}" width="{pw - 56}" height="3" rx="1.5" fill="#2A2432"/>'
         f'<rect x="{px + 28}" y="{py + 280}" width="60" height="3" rx="1.5" fill="{ACC}"><animate attributeName="width" values="20;{pw - 56};20" dur="14s" repeatCount="indefinite"/></rect>',
         f'<g fill="{TXT}"><path d="M{vx - 50},{py + 302} l-12,8 l12,8z M{vx - 62},{py + 302} l-12,8 l12,8z"/>'
         f'<circle cx="{vx}" cy="{py + 310}" r="17" fill="{ACC}"/><rect x="{vx - 6}" y="{py + 302}" width="4" height="16" fill="{BG}"/><rect x="{vx + 2}" y="{py + 302}" width="4" height="16" fill="{BG}"/>'
         f'<path d="M{vx + 50},{py + 302} l12,8 l-12,8z M{vx + 62},{py + 302} l12,8 l-12,8z"/></g></g>',
         f'<rect x="{px + 80}" y="{py + 14}" width="50" height="6" rx="3" fill="#000"/>']
    # floating notes
    for n, (x, y, c) in enumerate([(320, 120, ACC), (300, 250, ACC2), (350, 320, CYAN)]):
        b.append(f'<g fill="{c}" filter="url(#glow)" opacity=".85"><circle cx="{x}" cy="{y}" r="7"/><rect x="{x + 5}" y="{y - 30}" width="2.5" height="30"/>'
                 f'<path d="M{x + 7},{y - 30} q12,4 10,16 q-3,-8 -10,-8z"/>'
                 f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -12;0 0" dur="{3 + n}s" repeatCount="indefinite"/></g>')
    b.append(f'<text x="420" y="118" font-family="Georgia,serif" font-size="40" fill="{INK}">MyTube Music</text>')
    b.append(f'<text x="422" y="148" font-family="{SANS}" font-size="17" fill="{SOFT}">my own Android music player</text>')
    y = 180
    for row in [[("Jetpack Compose", ACC), ("Material 3", CYAN)], [("Synced lyrics", ACC2), ("Shake to skip", PINK)], [("Vinyl animation", GREEN), ("Sleep timer", VIOLET)]]:
        x = 422
        for t, c in row:
            s, w = chip(x, y, t, c)
            b.append(s); x += w + 10
        y += 46
    b.append(f'<text x="422" y="352" font-family="{SANS}" font-size="14" fill="{SOFT}" opacity=".85">Kotlin · Android 8.0+</text>')
    return svg("mytube.svg", "MyTube Music: an Android music player app with a spinning vinyl, synced lyrics and shake to skip", "".join(b), 31, ACC)


def helios():
    b = [f'<circle cx="640" cy="90" r="46" fill="{GOLD}" filter="url(#glow)"><animate attributeName="r" values="44;50;44" dur="4s" repeatCount="indefinite"/></circle>',
         f'<circle cx="640" cy="90" r="80" fill="{GOLD}" opacity=".12"/>']
    # ground
    b.append(f'<path d="M0,300 Q400,270 800,300 L800,420 L0,420z" fill="#0b0920"/>')
    for r in range(4):
        y = 300 + r * 26
        for c in range(7):
            x = 70 + c * 90 + r * 18
            b.append(f'<polygon points="{x},{y} {x + 70},{y} {x + 60},{y + 18} {x - 10},{y + 18}" fill="#2a3a8f" stroke="{CYAN}" stroke-opacity=".6"/>'
                     f'<line x1="{x + 35}" y1="{y}" x2="{x + 25}" y2="{y + 18}" stroke="{CYAN}" stroke-opacity=".35"/>')
    # sun glint sweeping over panels
    b.append(f'<rect x="-120" y="296" width="70" height="124" fill="#fff" opacity=".12" transform="skewX(-20)">'
             f'<animate attributeName="x" values="-120;900" dur="5s" repeatCount="indefinite"/></rect>')
    # battery
    b.append(f'<g transform="translate(690 214)"><rect width="70" height="56" rx="6" fill="#141236" stroke="{GREEN}" stroke-width="2"/>'
             f'<rect x="70" y="20" width="6" height="16" fill="{GREEN}"/><rect x="6" y="6" width="20" height="44" rx="3" fill="{GREEN}">'
             f'<animate attributeName="width" values="10;58;10" dur="6s" repeatCount="indefinite"/></rect></g>')
    # AI agent crew with speech bubbles
    for n, (x, col, txt) in enumerate([(90, CYAN, "RFI-012"), (210, PINK, "Approved ✓"), (330, GOLD, "Site diary"), (450, VIOLET, "Meeting 9:00")]):
        y = 205 + (n % 2) * 26
        b.append(f'<g><circle cx="{x}" cy="{y}" r="17" fill="{col}" fill-opacity=".18" stroke="{col}" stroke-width="2"/>'
                 f'<circle cx="{x - 6}" cy="{y - 2}" r="2.5" fill="{col}"/><circle cx="{x + 6}" cy="{y - 2}" r="2.5" fill="{col}"/>'
                 f'<path d="M{x - 6},{y + 6} q6,5 12,0" stroke="{col}" stroke-width="2" fill="none"/>'
                 f'<g opacity="0"><rect x="{x - 48}" y="{y - 62}" width="96" height="30" rx="12" fill="#ffffff" fill-opacity=".1" stroke="{col}"/>'
                 f'<text x="{x}" y="{y - 42}" font-family="{SANS}" font-size="13" fill="{INK}" text-anchor="middle">{txt}</text>'
                 f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.08;.3;.38;1" dur="6s" begin="{n * 1.5}s" repeatCount="indefinite"/></g></g>')
    b.append(f'<text x="40" y="60" font-family="{SANS}" font-size="32" font-weight="800" fill="{INK}">HELIOS</text>')
    b.append(f'<text x="40" y="88" font-family="{SANS}" font-size="16" fill="{SOFT}">a solar + battery project run by a crew of AI agents</text>')
    b.append(f'<text x="40" y="112" font-family="{MONO}" font-size="12" fill="{GREEN}" letter-spacing="1">● 100 MW SOLAR · 100 MWh STORAGE · DAY BY DAY</text>')
    return svg("helios.svg", "HELIOS: a simulated solar and battery project where every team member is an AI agent", "".join(b), 41, GOLD)


def colab():
    b = []
    # agent (left)
    b.append(f'<g transform="translate(150 215)"><circle r="62" fill="{VIOLET}" fill-opacity=".15" stroke="{VIOLET}" stroke-width="2"/>'
             f'<rect x="-34" y="-26" width="68" height="50" rx="14" fill="#1a1450" stroke="{CYAN}" stroke-width="2"/>'
             f'<circle cx="-13" cy="-2" r="6" fill="{CYAN}"><animate attributeName="r" values="6;2;6" dur="3s" repeatCount="indefinite"/></circle>'
             f'<circle cx="13" cy="-2" r="6" fill="{CYAN}"><animate attributeName="r" values="6;2;6" dur="3s" repeatCount="indefinite"/></circle>'
             f'<line x1="0" y1="-26" x2="0" y2="-42" stroke="{CYAN}" stroke-width="2"/><circle cy="-46" r="5" fill="{PINK}" filter="url(#glow)"/>'
             f'<text y="96" font-family="{SANS}" font-size="16" fill="{SOFT}" text-anchor="middle">AI agent</text></g>')
    # beam
    b.append(f'<path d="M220,215 C330,150 430,280 540,215" stroke="{CYAN}" stroke-width="2.5" fill="none" stroke-dasharray="8 8" opacity=".8">'
             f'<animate attributeName="stroke-dashoffset" values="32;0" dur="1s" repeatCount="indefinite"/></path>')
    for n in range(3):
        b.append(f'<circle r="5" fill="{GOLD}" filter="url(#glow)"><animateMotion dur="2.4s" begin="{n * .8}s" repeatCount="indefinite" path="M220,215 C330,150 430,280 540,215"/></circle>')
    # notebook in a cloud (right)
    b.append(f'<g transform="translate(560 120)"><path d="M30,60 a40,40 0 0 1 70,-30 a50,50 0 0 1 90,20 a35,35 0 0 1 10,70 h-170 a30,30 0 0 1 0,-60z" fill="#ffffff" fill-opacity=".07" stroke="{SOFT}" stroke-opacity=".6" stroke-width="2"/>'
             f'<rect x="20" y="70" width="180" height="140" rx="12" fill="#0f0c2e" stroke="{GOLD}" stroke-width="2"/>')
    for i, w in enumerate([120, 90, 140, 70]):
        y = 92 + i * 28
        b.append(f'<text x="34" y="{y + 5}" font-family="{MONO}" font-size="12" fill="{SOFT}">[{i + 1}]</text>'
                 f'<rect x="62" y="{y - 6}" width="{w}" height="12" rx="4" fill="{[CYAN, PINK, GREEN, VIOLET][i]}" opacity=".7">'
                 f'<animate attributeName="opacity" values=".25;.9;.25" dur="2.4s" begin="{i * .6}s" repeatCount="indefinite"/></rect>')
    b.append(f'<text x="110" y="240" font-family="{SANS}" font-size="16" fill="{SOFT}" text-anchor="middle">Colab · Kaggle GPUs</text></g>')
    b.append(f'<text x="40" y="58" font-family="{SANS}" font-size="28" font-weight="800" fill="{INK}">Agents that run notebooks in the cloud</text>')
    return svg("agents.svg", "An AI agent sending notebook cells to run on Google Colab and Kaggle GPUs", "".join(b), 51, CYAN)


def regression():
    random.seed(4)
    xs = [40 + i * 22 for i in range(33)]
    import math
    f = lambda x: 250 - 90 * math.sin((x - 40) / 120) - (x - 40) * .12
    up = " ".join(f"{x},{f(x) - 30 - (x - 40) * .05:.1f}" for x in xs)
    lo = " ".join(f"{x},{f(x) + 30 + (x - 40) * .05:.1f}" for x in reversed(xs))
    b = [f'<polygon points="{up} {lo}" fill="{VIOLET}" fill-opacity=".25" stroke="{VIOLET}" stroke-opacity=".5"/>',
         f'<polyline points="{" ".join(f"{x},{f(x):.1f}" for x in xs)}" fill="none" stroke="{CYAN}" stroke-width="3" filter="url(#glow)"/>']
    for x in xs:
        y = f(x) + random.gauss(0, 18 + (x - 40) * .03)
        b.append(f'<circle cx="{x}" cy="{y:.1f}" r="4" fill="{GOLD}" opacity=".9"/>')
    b.append(f'<circle r="7" fill="#fff" filter="url(#glow)"><animateMotion dur="7s" repeatCount="indefinite" path="M{" L".join(f"{x},{f(x):.1f}" for x in xs)}"/></circle>')
    b.append(f'<text x="40" y="58" font-family="{SANS}" font-size="28" font-weight="800" fill="{INK}">Predictions with an honest range</text>')
    b.append(f'<text x="42" y="86" font-family="{SANS}" font-size="16" fill="{SOFT}">not just “the answer is 42”, but “42, give or take 5”</text>')
    return svg("regression.svg", "A prediction line with a shaded band showing how uncertain each prediction is", "".join(b), 61, VIOLET)


def quake():
    import math
    def wave(seed, amp, ph):
        random.seed(seed)
        pts = []
        for i in range(0, 761, 4):
            env = math.exp(-((i - 330) / 150) ** 2)
            pts.append(f"{20 + i},{225 + amp * env * math.sin(i / 7 + ph) * (0.6 + random.random() * .4):.1f}")
        return " ".join(pts)
    b = [f'<line x1="20" y1="225" x2="780" y2="225" stroke="{SOFT}" stroke-opacity=".25"/>',
         f'<polyline points="{wave(1, 120, 0)}" fill="none" stroke="{CYAN}" stroke-width="2" opacity=".9" filter="url(#glow)"/>',
         f'<polyline points="{wave(2, 95, .6)}" fill="none" stroke="{PINK}" stroke-width="2" opacity=".75"/>',
         f'<rect x="20" y="90" width="4" height="270" fill="{GOLD}" filter="url(#glow)"><animate attributeName="x" values="20;780" dur="6s" repeatCount="indefinite"/></rect>',
         f'<text x="40" y="58" font-family="{SANS}" font-size="28" font-weight="800" fill="{INK}">AI that imagines earthquakes</text>',
         f'<text x="42" y="388" font-family="{SANS}" font-size="15" fill="{CYAN}">— recorded</text>'
         f'<text x="160" y="388" font-family="{SANS}" font-size="15" fill="{PINK}">— generated by the GAN</text>']
    return svg("quake.svg", "Two earthquake ground-motion waves: one recorded, one generated by an AI model", "".join(b), 71, PINK)


def crew():
    w, h = 900, 190
    def pilot(x, col, name, sub, seed):
        return (f'<g transform="translate({x} 100)"><circle r="44" fill="{col}" fill-opacity=".14" stroke="{col}" stroke-width="2"/>'
                f'<ellipse rx="66" ry="16" fill="none" stroke="{col}" stroke-opacity=".5" transform="rotate(-15)"/>'
                f'<circle r="5" fill="#fff" filter="url(#glow)"><animateMotion dur="{4 + seed}s" repeatCount="indefinite" path="M-66,0 a66,16 0 1,0 132,0 a66,16 0 1,0 -132,0" /></circle>'
                f'<path d="M-18,-6 a18,18 0 0 1 36,0 v12 a8,8 0 0 1 -8,8 h-20 a8,8 0 0 1 -8,-8z" fill="#1a1450" stroke="{col}" stroke-width="2"/>'
                f'<rect x="-12" y="-8" width="24" height="12" rx="6" fill="{col}" opacity=".85"/>'
                f'<text x="90" y="-4" font-family="{SANS}" font-size="26" font-weight="800" fill="{INK}">{name}</text>'
                f'<text x="90" y="22" font-family="{SANS}" font-size="15" fill="{SOFT}">{sub}</text></g>')
    body = (pilot(90, CYAN, "agy", "Google Antigravity CLI", 0) + pilot(500, GOLD, "Claude Code", "Anthropic's coding agent", 1))
    return "crew.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="My favourite AI co-pilots: agy (Google Antigravity CLI) and Claude Code">
<defs><linearGradient id="bg" x1="0" x2="1"><stop offset="0" stop-color="{SPACE1}"/><stop offset="1" stop-color="{SPACE0}"/></linearGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="c"><rect width="{w}" height="{h}" rx="18"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#bg)"/>{stars(60, 81, h)}</g>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" fill="none" stroke="{VIOLET}" stroke-opacity=".5" stroke-width="2"/>
<text x="{w / 2}" y="30" font-family="{SANS}" font-size="13" letter-spacing="3" fill="{SOFT}" text-anchor="middle">MY FAVOURITE AI CO-PILOTS</text>
{body}
<text x="{w / 2}" y="174" font-family="{SANS}" font-size="13" font-style="italic" fill="{SOFT}" text-anchor="middle" opacity=".85">most of the projects below were built side by side with these two</text>
</svg>'''


for name, text in [mytube(), helios(), colab(), regression(), quake(), crew()]:
    open(os.path.join(out, name), "w", encoding="utf-8").write(text)
if "--no-figures" not in sys.argv:
    figures()
print("ok")
