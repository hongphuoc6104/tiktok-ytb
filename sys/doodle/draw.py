"""Doodle illustration engine for the prehistory channel (no AI image service).

A scene is a dict: {"bg": name, "items": [[kind, x, y, scale, {opts}], ...]} in a
1920x1080 canvas (x, y = anchor, usually the feet/base). Every stroke is slightly
jittered with a per-image seed so drawings look hand-inked but stay reproducible.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080
INK = (28, 26, 24)
CREAM = (247, 241, 226)
SKIN = (255, 255, 255)
FUR = (140, 92, 52)
FUR_D = (104, 66, 36)
HAIR = (88, 56, 30)
BONE = (244, 236, 214)
GROUND = (222, 206, 170)
GRASS = (170, 180, 110)


class Pen:
    def __init__(self, img, seed):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.r = random.Random(seed)

    def j(self, v=3.0):
        return self.r.uniform(-v, v)

    def line(self, pts, w=6, color=INK, jitter=2.5):
        pts = [(x + self.j(jitter), y + self.j(jitter)) for x, y in pts]
        self.d.line(pts, fill=color, width=int(w), joint='curve')
        for x, y in (pts[0], pts[-1]):
            self.d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=color)

    def curve(self, pts, w=6, color=INK, n=24, jitter=1.5):
        """Catmull-Rom through control points."""
        if len(pts) < 3:
            return self.line(pts, w, color, jitter)
        out = []
        p = [pts[0]] + list(pts) + [pts[-1]]
        for i in range(1, len(p) - 2):
            for t in range(n):
                t /= n
                a = [0.5 * (2 * p[i][k] + (-p[i - 1][k] + p[i + 1][k]) * t
                            + (2 * p[i - 1][k] - 5 * p[i][k] + 4 * p[i + 1][k] - p[i + 2][k]) * t * t
                            + (-p[i - 1][k] + 3 * p[i][k] - 3 * p[i + 1][k] + p[i + 2][k]) * t ** 3) for k in (0, 1)]
                out.append(tuple(a))
        out.append(pts[-1])
        self.line(out, w, color, jitter)

    def poly(self, pts, fill, w=6, outline=INK, jitter=2.0):
        pts = [(x + self.j(jitter), y + self.j(jitter)) for x, y in pts]
        self.d.polygon(pts, fill=fill)
        if outline:
            self.d.line(pts + [pts[0]], fill=outline, width=int(w), joint='curve')

    def circle(self, cx, cy, r, fill=None, w=6, outline=INK):
        n = 36
        pts = [(cx + (r + self.j(1.2)) * math.cos(2 * math.pi * i / n), cy + (r + self.j(1.2)) * math.sin(2 * math.pi * i / n)) for i in range(n)]
        if fill:
            self.d.polygon(pts, fill=fill)
        if outline:
            self.d.line(pts + [pts[0]], fill=outline, width=int(w), joint='curve')

    def oval(self, box, fill):
        self.d.ellipse(box, fill=fill)


# ------------------------------------------------------------------ backgrounds
SKIES = {
    'day': [(214, 233, 240), (240, 238, 222)],
    'dawn': [(247, 196, 150), (250, 232, 200)],
    'dusk': [(233, 150, 110), (247, 205, 160)],
    'night': [(28, 36, 64), (58, 66, 98)],
    'rain': [(150, 158, 165), (196, 199, 196)],
    'winter': [(200, 212, 222), (236, 238, 238)],
    'cream': [CREAM, CREAM],
}


def gradient(img, top, bottom, y0=0, y1=H):
    d = ImageDraw.Draw(img)
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        d.line([(0, y), (W, y)], fill=tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3)))


def background(pen, name):
    img = pen.img
    sky, _, ground = (name.split(':') + ['', ''])[:3]
    kind = sky or 'cream'
    if kind == 'paper':
        gradient(img, CREAM, CREAM)
        return
    if kind == 'cave':
        gradient(img, (70, 58, 50), (110, 92, 76))
        pen.poly([(0, 1080), (0, 0), (1920, 0), (1920, 1080), (1700, 1080), (1650, 300), (960, 120), (270, 300), (220, 1080)],
                 fill=(52, 42, 36), w=8)
        gradient_floor(pen, (120, 100, 80), 860)
        return
    if kind == 'city':
        gradient(img, *SKIES['day'])
        for i, (x, h) in enumerate([(0, 420), (260, 520), (520, 360), (760, 600), (1040, 450), (1300, 560), (1560, 400), (1760, 500)]):
            c = [(196, 202, 210), (178, 186, 196), (206, 200, 190)][i % 3]
            pen.poly([(x, 820), (x, 820 - h), (x + 240, 820 - h), (x + 240, 820)], fill=c, w=5)
            for wy in range(820 - h + 40, 800, 70):
                for wx in (x + 40, x + 140):
                    pen.poly([(wx, wy), (wx + 50, wy), (wx + 50, wy + 36), (wx, wy + 36)], fill=(235, 238, 240), w=3, jitter=1)
        gradient_floor(pen, (150, 150, 150), 820, road=True)
        return
    gradient(img, *SKIES.get(kind, SKIES['day']), 0, 760)
    if kind == 'night':
        for _ in range(60):
            x, y = pen.r.uniform(0, W), pen.r.uniform(0, 620)
            pen.oval([x - 2, y - 2, x + 2, y + 2], fill=(240, 236, 210))
        pen.circle(1580, 170, 60, fill=(245, 238, 200), w=4)
    if kind in ('day', 'winter'):
        pen.circle(1640, 180, 70, fill=(250, 214, 110) if kind == 'day' else (245, 240, 220), w=5)
    if kind == 'dawn':
        pen.circle(960, 760, 150, fill=(250, 200, 90), w=5)
    hills = [(0, 700), (300, 640), (620, 690), (980, 620), (1320, 680), (1640, 630), (1920, 690)]
    col = {'night': (40, 52, 60), 'winter': (232, 236, 238), 'rain': (140, 150, 130)}.get(kind, (196, 196, 150))
    pen.poly(hills + [(1920, 1080), (0, 1080)], fill=col, w=6)
    gcol = {'night': (48, 60, 62), 'winter': (245, 247, 248), 'rain': (160, 165, 140), 'dawn': (214, 190, 150)}.get(kind, GROUND)
    pen.poly([(0, 760), (1920, 760), (1920, 1080), (0, 1080)], fill=gcol, w=0, outline=None)
    pen.line([(0, 760), (1920, 760)], w=5)
    if kind == 'rain':
        for _ in range(170):
            x, y = pen.r.uniform(0, W), pen.r.uniform(0, H)
            pen.d.line([(x, y), (x - 14, y + 44)], fill=(90, 110, 140), width=3)
    if kind == 'winter':
        for _ in range(140):
            x, y = pen.r.uniform(0, W), pen.r.uniform(0, H)
            pen.oval([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255))


def gradient_floor(pen, color, y, road=False):
    pen.poly([(0, y), (W, y), (W, H), (0, H)], fill=color, w=5)
    if road:
        for x in range(40, W, 260):
            pen.poly([(x, 960), (x + 140, 960), (x + 140, 976), (x, 976)], fill=(245, 245, 245), w=0, outline=None)


# ------------------------------------------------------------------ figures
def figure(pen, x, y, s=1.0, pose='stand', face='smile', hair=HAIR, tunic=FUR, necklace=True, modern=None, flip=False, prop=None):
    """Stick figure standing on (x, y). modern = shirt color for the present-day 'you'."""
    f = -1 if flip else 1
    hr = 62 * s
    lw = 7 * s
    if pose == 'sleep':
        # lying on the ground, head left
        hx, hy = x - 150 * s * f, y - hr
        pen.line([(hx + (hr + 5) * f, y - 30 * s), (x + 140 * s * f, y - 30 * s)], w=lw)
        pen.poly([(hx + hr * f, y - 70 * s), (x + 80 * s * f, y - 70 * s), (x + 90 * s * f, y - 5 * s), (hx + hr * f, y - 5 * s)],
                 fill=(modern or tunic), w=lw * .8)
        pen.circle(hx, hy, hr, fill=SKIN, w=lw)
        eyes_closed(pen, hx, hy, s)
        zz(pen, hx + 60 * s * f, hy - 110 * s, s)
        return
    sit = pose in ('sit', 'ride')
    hip = (x, y - (95 if sit else 190) * s)
    neck = (x, hip[1] - 150 * s)
    head = (x, neck[1] - hr + 6 * s)
    # legs
    if pose == 'ride':
        pen.line([hip, (x + 70 * s * f, y - 40 * s), (x + 80 * s * f, y + 30 * s)], w=lw)
    elif sit:
        pen.line([hip, (x + 90 * s * f, y - 20 * s), (x + 70 * s * f, y)], w=lw)
        pen.line([hip, (x + 60 * s * f, y - 10 * s), (x + 30 * s * f, y)], w=lw)
    elif pose == 'walk':
        pen.line([hip, (x - 45 * s * f, y)], w=lw)
        pen.line([hip, (x + 55 * s * f, y)], w=lw)
    else:
        pen.line([hip, (x - 30 * s, y)], w=lw)
        pen.line([hip, (x + 30 * s, y)], w=lw)
    # body / clothes
    if modern:
        pen.poly([(x - 48 * s, neck[1] + 10 * s), (x + 48 * s, neck[1] + 10 * s), (x + 42 * s, hip[1] + 10 * s), (x - 42 * s, hip[1] + 10 * s)],
                 fill=modern, w=lw * .8)
    else:
        pen.line([neck, hip], w=lw)
        pen.poly([(x - 20 * s * f, neck[1] + 8 * s), (x + 40 * s * f, neck[1] + 40 * s), (x + 55 * s * f, hip[1] + 45 * s),
                  (x + 15 * s * f, hip[1] + 30 * s), (x - 20 * s * f, hip[1] + 55 * s), (x - 50 * s * f, hip[1] + 35 * s), (x - 42 * s * f, neck[1] + 40 * s)],
                 fill=tunic, w=lw * .8)
    # arms
    sh = (x, neck[1] + 25 * s)
    arms = {
        'stand': [[(x - 70 * s, sh[1] + 110 * s)], [(x + 70 * s, sh[1] + 110 * s)]],
        'walk': [[(x - 60 * s * f, sh[1] + 100 * s)], [(x + 75 * s * f, sh[1] + 90 * s)]],
        'point': [[(x - 60 * s * f, sh[1] + 110 * s)], [(x + 90 * s * f, sh[1] - 20 * s), (x + 150 * s * f, sh[1] - 60 * s)]],
        'arms_up': [[(x - 70 * s, sh[1] - 60 * s), (x - 100 * s, sh[1] - 130 * s)], [(x + 70 * s, sh[1] - 60 * s), (x + 100 * s, sh[1] - 130 * s)]],
        'carry': [[(x - 40 * s, sh[1] + 70 * s), (x + 30 * s * f, sh[1] + 95 * s)], [(x + 40 * s, sh[1] + 70 * s), (x + 60 * s * f, sh[1] + 95 * s)]],
        'think': [[(x - 60 * s * f, sh[1] + 110 * s)], [(x + 60 * s * f, sh[1] + 60 * s), (x + 25 * s * f, head[1] + 45 * s)]],
        'sit': [[(x - 55 * s * f, sh[1] + 100 * s)], [(x + 75 * s * f, sh[1] + 80 * s)]],
        'ride': [[(x + 60 * s * f, sh[1] + 40 * s), (x + 120 * s * f, sh[1] + 20 * s)], [(x + 70 * s * f, sh[1] + 50 * s), (x + 125 * s * f, sh[1] + 30 * s)]],
        'spear': [[(x - 60 * s * f, sh[1] + 110 * s)], [(x + 55 * s * f, sh[1] + 60 * s), (x + 80 * s * f, sh[1] + 20 * s)]],
    }.get(pose, None) or [[(x - 70 * s, sh[1] + 110 * s)], [(x + 70 * s, sh[1] + 110 * s)]]
    for a in arms:
        pen.line([sh] + a, w=lw)
    hand = arms[1][-1]
    if necklace and not modern:
        for k in range(-3, 4):
            bx, by = x + k * 13 * s, neck[1] + 6 * s + abs(k) * -2 * s + 6 * s
            pen.circle(bx, by, 5.5 * s, fill=BONE, w=2.5 * s)
    # head
    pen.circle(head[0], head[1], hr, fill=SKIN, w=lw)
    if hair:
        hairdo(pen, head[0], head[1], hr, s, hair, short=bool(modern))
    face_draw(pen, head[0], head[1], s, face, f)
    if prop:
        props_in_hand(pen, prop, hand, s, f)
    return hand


def hairdo(pen, cx, cy, r, s, color, short=False):
    """A messy tuft on the crown (not a halo): filled jagged cap + a few loose strokes."""
    top = cy - r
    if short:
        pts = [(cx - r * .95, cy - r * .25)]
        for k in range(9):
            a = math.pi * (1.05 + .9 * k / 8)
            rr = r * (1.08 if k % 2 else 1.0)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        pts.append((cx + r * .95, cy - r * .25))
        pen.poly(pts, fill=color, w=3 * s, outline=color)
        return
    pts = [(cx - r * .8, cy - r * .45)]
    n = 11
    for k in range(n):
        a = math.pi * (1.12 + .76 * k / (n - 1))
        rr = r * (1.42 + pen.r.uniform(-.08, .12) if k % 2 else 1.04)
        pts.append((cx + rr * math.cos(a) + pen.r.uniform(-6, 6) * s, cy + rr * math.sin(a)))
    pts.append((cx + r * .8, cy - r * .45))
    pts.append((cx + r * .3, cy - r * .7))
    pts.append((cx - r * .3, cy - r * .72))
    pen.poly(pts, fill=color, w=4 * s, outline=(60, 38, 20))
    for k in range(3):
        bx = cx + (k - 1) * r * .45
        pen.line([(bx, top + 4 * s), (bx + (k - 1) * 18 * s, top - 34 * s)], w=6 * s, color=(60, 38, 20), jitter=1)


def eyes_closed(pen, cx, cy, s):
    for dx in (-22, 22):
        pen.d.arc([cx + dx * s - 11 * s, cy - 12 * s, cx + dx * s + 11 * s, cy + 4 * s], 20, 160, fill=INK, width=int(4 * s))


def zz(pen, x, y, s):
    for i, k in enumerate((1.0, .8, .6)):
        xx, yy, z = x + i * 34 * s, y - i * 40 * s, 22 * s * k
        pen.line([(xx, yy), (xx + z, yy), (xx, yy + z), (xx + z, yy + z)], w=4 * s, jitter=.5)


def face_draw(pen, cx, cy, s, face, f=1):
    if face == 'sleep':
        eyes_closed(pen, cx, cy, s)
        return
    ey = cy - 6 * s
    for dx in (-21, 21):
        rx, ry = (8, 12) if face != 'wow' else (9, 14)
        pen.oval([cx + dx * s - rx * s, ey - ry * s, cx + dx * s + rx * s, ey + ry * s], fill=INK)
    my = cy + 26 * s
    if face == 'smile':
        pen.d.arc([cx - 22 * s, my - 22 * s, cx + 22 * s, my + 8 * s], 20, 160, fill=INK, width=int(5 * s))
    elif face == 'wow':
        pen.circle(cx, my + 4 * s, 10 * s, fill=INK, w=3 * s)
    elif face == 'sad':
        pen.d.arc([cx - 20 * s, my - 2 * s, cx + 20 * s, my + 24 * s], 200, 340, fill=INK, width=int(5 * s))
    elif face == 'tired':
        pen.line([(cx - 18 * s, my + 6 * s), (cx + 18 * s, my + 2 * s)], w=5 * s)
        for dx in (-21, 21):
            pen.line([(cx + dx * s - 12 * s, ey - 16 * s), (cx + dx * s + 12 * s, ey - 12 * s)], w=4 * s)
    else:
        pen.line([(cx - 14 * s, my + 4 * s), (cx + 14 * s, my + 4 * s)], w=5 * s)


def props_in_hand(pen, prop, hand, s, f):
    hx, hy = hand
    if prop == 'spear':
        pen.line([(hx - 20 * s * f, hy + 240 * s), (hx + 25 * s * f, hy - 200 * s)], w=7 * s, color=(120, 80, 40))
        pen.poly([(hx + 25 * s * f, hy - 200 * s), (hx + 12 * s * f, hy - 250 * s), (hx + 45 * s * f, hy - 230 * s)], fill=(150, 150, 150), w=4 * s)
    elif prop == 'basket':
        basket(pen, hx, hy + 70 * s, .8 * s, full=True)
    elif prop == 'torch':
        pen.line([(hx, hy + 60 * s), (hx, hy - 60 * s)], w=8 * s, color=(120, 80, 40))
        flame(pen, hx, hy - 60 * s, .45 * s)
    elif prop == 'phone':
        pen.poly([(hx - 18 * s, hy - 30 * s), (hx + 18 * s, hy - 30 * s), (hx + 18 * s, hy + 30 * s), (hx - 18 * s, hy + 30 * s)], fill=(60, 60, 70), w=4 * s)
    elif prop == 'stone':
        stone_tool(pen, hx, hy, .5 * s)
    elif prop == 'fish':
        fish(pen, hx + 30 * s * f, hy + 10 * s, .6 * s)


# ------------------------------------------------------------------ props
def flame(pen, x, y, s=1.0):
    pen.poly([(x - 60 * s, y), (x - 50 * s, y - 90 * s), (x - 10 * s, y - 60 * s), (x, y - 160 * s), (x + 20 * s, y - 70 * s),
              (x + 55 * s, y - 110 * s), (x + 60 * s, y)], fill=(245, 150, 60), w=5 * s)
    pen.poly([(x - 30 * s, y), (x - 20 * s, y - 55 * s), (x, y - 90 * s), (x + 20 * s, y - 50 * s), (x + 30 * s, y)], fill=(252, 214, 90), w=3 * s)


def fire(pen, x, y, s=1.0, lit=True):
    for a in (-.35, .35):
        pen.line([(x - 110 * s * math.cos(a), y + 10 * s), (x + 110 * s * math.cos(a), y - 40 * s * (1 if a > 0 else -.2))], w=22 * s, color=(120, 76, 40))
    for k in range(-3, 4):
        pen.circle(x + k * 40 * s, y + 22 * s, 16 * s, fill=(150, 150, 140), w=3 * s)
    if lit:
        flame(pen, x, y - 10 * s, s)
    else:
        for _ in range(3):
            sx = x + pen.r.uniform(-30, 30) * s
            pen.curve([(sx, y - 20 * s), (sx + 15 * s, y - 70 * s), (sx - 10 * s, y - 120 * s)], w=4 * s, color=(140, 140, 140))


def basket(pen, x, y, s=1.0, full=False):
    pen.poly([(x - 80 * s, y - 90 * s), (x + 80 * s, y - 90 * s), (x + 60 * s, y), (x - 60 * s, y)], fill=(196, 150, 90), w=5 * s)
    for k in range(1, 4):
        yy = y - 90 * s + k * 22 * s
        pen.line([(x - 78 * s + k * 5 * s, yy), (x + 78 * s - k * 5 * s, yy)], w=3 * s, color=(120, 80, 40))
    if full:
        for i in range(9):
            bx, by = x + (i % 5 - 2) * 26 * s, y - 100 * s - (i // 5) * 22 * s
            pen.circle(bx, by, 14 * s, fill=[(190, 50, 70), (90, 60, 140), (230, 160, 40)][i % 3], w=3 * s)


def tree(pen, x, y, s=1.0, kind='acacia'):
    pen.poly([(x - 18 * s, y), (x - 10 * s, y - 260 * s), (x + 10 * s, y - 260 * s), (x + 18 * s, y)], fill=(130, 90, 55), w=5 * s)
    if kind == 'acacia':
        pen.poly([(x - 220 * s, y - 250 * s), (x - 150 * s, y - 330 * s), (x + 160 * s, y - 340 * s), (x + 230 * s, y - 260 * s)], fill=(120, 150, 80), w=5 * s)
    else:
        pen.circle(x, y - 330 * s, 130 * s, fill=(110, 150, 90), w=5 * s)


def bush(pen, x, y, s=1.0, berries=True):
    for dx, dy, r in ((-60, -50, 60), (0, -80, 75), (60, -50, 60)):
        pen.circle(x + dx * s, y + dy * s, r * s, fill=(100, 140, 80), w=5 * s)
    if berries:
        for _ in range(12):
            pen.circle(x + pen.r.uniform(-100, 100) * s, y + pen.r.uniform(-130, -30) * s, 9 * s, fill=(190, 40, 60), w=2 * s)


def deer(pen, x, y, s=1.0):
    pen.poly([(x - 110 * s, y - 170 * s), (x + 90 * s, y - 175 * s), (x + 100 * s, y - 110 * s), (x - 110 * s, y - 105 * s)], fill=(190, 130, 80), w=5 * s)
    for lx in (-90, -60, 60, 85):
        pen.line([(x + lx * s, y - 110 * s), (x + lx * s, y)], w=6 * s)
    pen.line([(x + 90 * s, y - 170 * s), (x + 140 * s, y - 240 * s)], w=18 * s, color=(190, 130, 80))
    pen.circle(x + 155 * s, y - 250 * s, 28 * s, fill=(190, 130, 80), w=5 * s)
    pen.line([(x + 150 * s, y - 275 * s), (x + 130 * s, y - 330 * s), (x + 110 * s, y - 345 * s)], w=5 * s)
    pen.line([(x + 165 * s, y - 275 * s), (x + 190 * s, y - 330 * s), (x + 215 * s, y - 340 * s)], w=5 * s)
    pen.oval([x + 158 * s, y - 258 * s, x + 168 * s, y - 248 * s], fill=INK)


def mammoth(pen, x, y, s=1.0):
    pen.poly([(x - 230 * s, y - 120 * s), (x - 200 * s, y - 330 * s), (x + 50 * s, y - 380 * s), (x + 200 * s, y - 300 * s),
              (x + 230 * s, y - 120 * s)], fill=(120, 80, 50), w=6 * s)
    for lx in (-190, -110, 110, 190):
        pen.poly([(x + lx * s - 28 * s, y - 130 * s), (x + lx * s + 28 * s, y - 130 * s), (x + lx * s + 26 * s, y), (x + lx * s - 26 * s, y)], fill=(110, 72, 44), w=5 * s)
    pen.curve([(x + 210 * s, y - 250 * s), (x + 280 * s, y - 150 * s), (x + 270 * s, y - 40 * s), (x + 240 * s, y - 20 * s)], w=26 * s, color=(110, 72, 44))
    pen.curve([(x + 200 * s, y - 180 * s), (x + 300 * s, y - 130 * s), (x + 360 * s, y - 190 * s)], w=14 * s, color=BONE)
    pen.oval([x + 150 * s, y - 280 * s, x + 164 * s, y - 266 * s], fill=INK)


def hut(pen, x, y, s=1.0):
    pts = [(x - 230 * s, y)] + [(x + 230 * s * math.cos(a), y - 260 * s * math.sin(a)) for a in [math.pi * k / 10 for k in range(10, -1, -1)]]
    pen.poly(pts, fill=(160, 130, 80), w=6 * s)
    for k in range(-4, 5):
        pen.line([(x + k * 50 * s, y), (x + k * 18 * s, y - 250 * s)], w=4 * s, color=(110, 80, 45))
    pen.poly([(x - 60 * s, y), (x - 50 * s, y - 120 * s), (x + 50 * s, y - 120 * s), (x + 60 * s, y)], fill=(60, 45, 35), w=5 * s)


def cave_mouth(pen, x, y, s=1.0):
    pen.poly([(x - 380 * s, y), (x - 330 * s, y - 380 * s), (x, y - 470 * s), (x + 330 * s, y - 380 * s), (x + 380 * s, y)], fill=(150, 140, 125), w=7 * s)
    pen.poly([(x - 220 * s, y), (x - 170 * s, y - 250 * s), (x, y - 300 * s), (x + 170 * s, y - 250 * s), (x + 220 * s, y)], fill=(45, 38, 34), w=6 * s)


def river(pen, y=900):
    pen.poly([(0, y - 40), (600, y - 70), (1200, y - 30), (1920, y - 60), (1920, y + 60), (1200, y + 90), (600, y + 50), (0, y + 70)],
             fill=(130, 180, 215), w=6)
    for _ in range(14):
        x = pen.r.uniform(80, 1840)
        pen.line([(x, y + pen.r.uniform(-20, 30)), (x + 60, y + pen.r.uniform(-20, 30))], w=4, color=(245, 250, 255))


def stone_tool(pen, x, y, s=1.0):
    pen.poly([(x, y - 120 * s), (x + 55 * s, y - 20 * s), (x + 30 * s, y + 40 * s), (x - 30 * s, y + 40 * s), (x - 55 * s, y - 20 * s)], fill=(160, 160, 155), w=5 * s)
    for k in range(3):
        pen.line([(x - 30 * s + k * 20 * s, y - 50 * s + k * 10 * s), (x - 10 * s + k * 20 * s, y + 20 * s)], w=3 * s, color=(110, 110, 105))


def fish(pen, x, y, s=1.0):
    pen.poly([(x - 70 * s, y), (x - 20 * s, y - 35 * s), (x + 50 * s, y - 20 * s), (x + 70 * s, y), (x + 50 * s, y + 20 * s), (x - 20 * s, y + 35 * s)], fill=(150, 170, 190), w=4 * s)
    pen.poly([(x + 60 * s, y), (x + 110 * s, y - 35 * s), (x + 110 * s, y + 35 * s)], fill=(150, 170, 190), w=4 * s)
    pen.oval([x - 45 * s, y - 10 * s, x - 33 * s, y + 2 * s], fill=INK)


def bones(pen, x, y, s=1.0, skull=True):
    for a in (-.4, .3):
        dx, dy = 110 * s * math.cos(a), 110 * s * math.sin(a)
        pen.line([(x - dx, y - dy), (x + dx, y + dy)], w=18 * s, color=BONE)
        for ex, ey in ((x - dx, y - dy), (x + dx, y + dy)):
            pen.circle(ex, ey, 16 * s, fill=BONE, w=4 * s)
    if skull:
        pen.circle(x, y - 90 * s, 60 * s, fill=BONE, w=5 * s)
        for dx in (-22, 22):
            pen.oval([x + dx * s - 14 * s, y - 100 * s, x + dx * s + 14 * s, y - 76 * s], fill=INK)


def clock(pen, x, y, s=1.0, hh=8, mm=0):
    pen.circle(x, y, 110 * s, fill=(255, 255, 255), w=8 * s)
    for k in range(12):
        a = 2 * math.pi * k / 12
        pen.line([(x + 90 * s * math.cos(a), y + 90 * s * math.sin(a)), (x + 100 * s * math.cos(a), y + 100 * s * math.sin(a))], w=5 * s, jitter=.5)
    for L, ang in ((55, (hh % 12 + mm / 60) / 12), (85, mm / 60)):
        a = 2 * math.pi * ang - math.pi / 2
        pen.line([(x, y), (x + L * s * math.cos(a), y + L * s * math.sin(a))], w=8 * s, jitter=.5)


def motorbike(pen, x, y, s=1.0, rider=None):
    for wx in (-90, 90):
        pen.circle(x + wx * s, y - 45 * s, 45 * s, fill=(60, 60, 60), w=6 * s)
        pen.circle(x + wx * s, y - 45 * s, 16 * s, fill=(200, 200, 200), w=3 * s)
    pen.poly([(x - 90 * s, y - 60 * s), (x - 40 * s, y - 120 * s), (x + 60 * s, y - 120 * s), (x + 110 * s, y - 70 * s), (x + 20 * s, y - 55 * s)], fill=rider or (200, 70, 60), w=5 * s)
    pen.line([(x + 60 * s, y - 120 * s), (x + 80 * s, y - 175 * s), (x + 110 * s, y - 180 * s)], w=6 * s)


def bed(pen, x, y, s=1.0):
    pen.poly([(x - 260 * s, y - 120 * s), (x + 260 * s, y - 120 * s), (x + 260 * s, y - 40 * s), (x - 260 * s, y - 40 * s)], fill=(240, 240, 250), w=6 * s)
    pen.poly([(x - 60 * s, y - 150 * s), (x + 260 * s, y - 150 * s), (x + 260 * s, y - 110 * s), (x - 60 * s, y - 110 * s)], fill=(120, 160, 210), w=5 * s)
    pen.poly([(x - 250 * s, y - 170 * s), (x - 140 * s, y - 170 * s), (x - 140 * s, y - 120 * s), (x - 250 * s, y - 120 * s)], fill=(255, 255, 255), w=5 * s)
    for lx in (-250, 250):
        pen.line([(x + lx * s, y - 40 * s), (x + lx * s, y)], w=8 * s)


def fridge(pen, x, y, s=1.0):
    pen.poly([(x - 110 * s, y), (x - 110 * s, y - 420 * s), (x + 110 * s, y - 420 * s), (x + 110 * s, y)], fill=(236, 240, 244), w=7 * s)
    pen.line([(x - 110 * s, y - 280 * s), (x + 110 * s, y - 280 * s)], w=6 * s)
    for yy in (-350, -200):
        pen.line([(x + 80 * s, y + yy * s), (x + 80 * s, y + (yy + 50) * s)], w=8 * s)


def desk(pen, x, y, s=1.0):
    pen.poly([(x - 260 * s, y - 250 * s), (x + 260 * s, y - 250 * s), (x + 260 * s, y - 225 * s), (x - 260 * s, y - 225 * s)], fill=(190, 150, 110), w=5 * s)
    for lx in (-240, 240):
        pen.line([(x + lx * s, y - 225 * s), (x + lx * s, y)], w=8 * s)
    pen.poly([(x - 110 * s, y - 430 * s), (x + 110 * s, y - 430 * s), (x + 110 * s, y - 290 * s), (x - 110 * s, y - 290 * s)], fill=(60, 70, 90), w=6 * s)
    pen.line([(x, y - 290 * s), (x, y - 250 * s)], w=8 * s)


def bubble(pen, x, y, s=1.0, inner=None):
    pen.circle(x, y, 150 * s, fill=(255, 255, 255), w=6 * s)
    for k, r in ((1, 22), (2, 14)):
        pen.circle(x - 120 * s - k * 40 * s, y + 140 * s + k * 38 * s, r * s, fill=(255, 255, 255), w=5 * s)
    if inner:
        draw_item(pen, inner[0], x + inner[1] * s, y + inner[2] * s, inner[3] * s, inner[4] if len(inner) > 4 else {})


def question(pen, x, y, s=1.0):
    pen.curve([(x - 45 * s, y - 120 * s), (x - 20 * s, y - 165 * s), (x + 40 * s, y - 160 * s), (x + 50 * s, y - 100 * s), (x, y - 60 * s), (x, y - 20 * s)], w=18 * s)
    pen.circle(x, y + 25 * s, 12 * s, fill=INK, w=4 * s)


def calendar(pen, x, y, s=1.0, filled=3, total=7):
    for k in range(total):
        cx = x + (k - total / 2) * 105 * s
        pen.poly([(cx, y - 100 * s), (cx + 90 * s, y - 100 * s), (cx + 90 * s, y), (cx, y)], fill=(250, 110, 90) if k < filled else (255, 255, 255), w=5 * s)


def bars(pen, x, y, s=1.0, a=0.45, b=1.0, ca=(120, 170, 110), cb=(210, 110, 90)):
    for k, (v, c) in enumerate(((a, ca), (b, cb))):
        bx = x + (k - 1) * 200 * s + 30 * s
        pen.poly([(bx, y), (bx, y - 420 * s * v), (bx + 140 * s, y - 420 * s * v), (bx + 140 * s, y)], fill=c, w=6 * s)
    pen.line([(x - 220 * s, y), (x + 260 * s, y)], w=7 * s)


def skeleton_pair(pen, x, y, s=1.0):
    for k, (h, c) in enumerate(((1.0, (70, 62, 54)), (.82, (120, 96, 72)))):
        bx = x + (k * 2 - 1) * 180 * s
        hh = 520 * s * h
        pen.circle(bx, y - hh, 45 * s * h, fill=c, w=5 * s)
        pen.line([(bx, y - hh + 45 * s * h), (bx, y - hh * .42)], w=10 * s, color=c)
        for r in range(4):
            yy = y - hh + (90 + r * 36) * s * h
            pen.line([(bx - 55 * s * h, yy), (bx + 55 * s * h, yy)], w=7 * s, color=c)
        pen.line([(bx, y - hh * .42), (bx - 45 * s * h, y)], w=10 * s, color=c)
        pen.line([(bx, y - hh * .42), (bx + 45 * s * h, y)], w=10 * s, color=c)


def map_route(pen, x, y, s=1.0):
    pen.poly([(x - 380 * s, y - 260 * s), (x + 380 * s, y - 260 * s), (x + 380 * s, y + 220 * s), (x - 380 * s, y + 220 * s)], fill=(240, 226, 190), w=6 * s)
    pts = [(x - 300 * s, y + 150 * s), (x - 150 * s, y + 40 * s), (x, y + 90 * s), (x + 150 * s, y - 60 * s), (x + 290 * s, y - 170 * s)]
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        for t in range(0, 10, 2):
            t0, t1 = t / 10, (t + 1) / 10
            pen.line([(ax + (bx - ax) * t0, ay + (by - ay) * t0), (ax + (bx - ax) * t1, ay + (by - ay) * t1)], w=6 * s, color=(170, 60, 50), jitter=.5)
    pen.circle(*pts[0], 18 * s, fill=(60, 120, 170), w=4 * s)
    pen.circle(*pts[-1], 18 * s, fill=(170, 60, 50), w=4 * s)


def handprints(pen, x, y, s=1.0):
    for k in range(3):
        hx, hy = x + (k - 1) * 170 * s, y + (k % 2) * 60 * s
        pen.circle(hx, hy, 45 * s, fill=(190, 80, 50), w=0, outline=None)
        for f in range(5):
            a = math.pi * (1.1 + .2 * f)
            pen.line([(hx, hy), (hx + 85 * s * math.cos(a), hy + 85 * s * math.sin(a))], w=20 * s, color=(190, 80, 50), jitter=1)


def footprints(pen, x, y, s=1.0, n=6):
    for k in range(n):
        fx, fy = x + k * 90 * s, y + (k % 2) * 40 * s
        pen.oval([fx - 18 * s, fy - 30 * s, fx + 18 * s, fy + 30 * s], fill=(150, 120, 90))


def flute(pen, x, y, s=1.0):
    pen.line([(x - 150 * s, y + 20 * s), (x + 150 * s, y - 20 * s)], w=26 * s, color=BONE)
    for k in range(-2, 3):
        pen.oval([x + k * 45 * s - 7 * s, y - k * 6 * s - 7 * s, x + k * 45 * s + 7 * s, y - k * 6 * s + 7 * s], fill=INK)


def notes(pen, x, y, s=1.0):
    for k in range(3):
        nx, ny = x + k * 70 * s, y - k * 40 * s
        pen.oval([nx - 20 * s, ny - 14 * s, nx + 20 * s, ny + 14 * s], fill=INK)
        pen.line([(nx + 18 * s, ny), (nx + 18 * s, ny - 90 * s)], w=6 * s, jitter=.5)


def wheat(pen, x, y, s=1.0):
    for k in range(-3, 4):
        bx = x + k * 50 * s
        pen.line([(bx, y), (bx + 10 * s, y - 260 * s)], w=5 * s, color=(170, 140, 60))
        for g in range(5):
            gy = y - 170 * s - g * 18 * s
            pen.oval([bx - 12 * s, gy - 10 * s, bx + 4 * s, gy + 8 * s], fill=(214, 176, 80))
            pen.oval([bx + 10 * s, gy - 10 * s, bx + 26 * s, gy + 8 * s], fill=(214, 176, 80))


def arrow(pen, x1, y1, x2, y2, s=1.0, color=(200, 60, 50)):
    pen.curve([(x1, y1), ((x1 + x2) / 2, min(y1, y2) - 60 * s), (x2, y2)], w=9 * s, color=color)
    a = math.atan2(y2 - y1, x2 - x1)
    for d in (2.5, -2.5):
        pen.line([(x2, y2), (x2 - 40 * s * math.cos(a + d / 6), y2 - 40 * s * math.sin(a + d / 6))], w=9 * s, color=color)


KINDS = {
    'fire': lambda p, x, y, s, o: fire(p, x, y, s, o.get('lit', True)),
    'basket': lambda p, x, y, s, o: basket(p, x, y, s, o.get('full', False)),
    'tree': lambda p, x, y, s, o: tree(p, x, y, s, o.get('kind', 'acacia')),
    'bush': lambda p, x, y, s, o: bush(p, x, y, s, o.get('berries', True)),
    'deer': lambda p, x, y, s, o: deer(p, x, y, s),
    'mammoth': lambda p, x, y, s, o: mammoth(p, x, y, s),
    'hut': lambda p, x, y, s, o: hut(p, x, y, s),
    'cave': lambda p, x, y, s, o: cave_mouth(p, x, y, s),
    'river': lambda p, x, y, s, o: river(p, y),
    'stone': lambda p, x, y, s, o: stone_tool(p, x, y, s),
    'fish': lambda p, x, y, s, o: fish(p, x, y, s),
    'bones': lambda p, x, y, s, o: bones(p, x, y, s, o.get('skull', True)),
    'clock': lambda p, x, y, s, o: clock(p, x, y, s, o.get('h', 8), o.get('m', 0)),
    'moto': lambda p, x, y, s, o: motorbike(p, x, y, s, o.get('color')),
    'bed': lambda p, x, y, s, o: bed(p, x, y, s),
    'fridge': lambda p, x, y, s, o: fridge(p, x, y, s),
    'desk': lambda p, x, y, s, o: desk(p, x, y, s),
    'bubble': lambda p, x, y, s, o: bubble(p, x, y, s, o.get('inner')),
    'question': lambda p, x, y, s, o: question(p, x, y, s),
    'calendar': lambda p, x, y, s, o: calendar(p, x, y, s, o.get('filled', 3), o.get('total', 7)),
    'bars': lambda p, x, y, s, o: bars(p, x, y, s, o.get('a', .45), o.get('b', 1.0)),
    'skeletons': lambda p, x, y, s, o: skeleton_pair(p, x, y, s),
    'map': lambda p, x, y, s, o: map_route(p, x, y, s),
    'hands': lambda p, x, y, s, o: handprints(p, x, y, s),
    'feet': lambda p, x, y, s, o: footprints(p, x, y, s, o.get('n', 6)),
    'flute': lambda p, x, y, s, o: flute(p, x, y, s),
    'notes': lambda p, x, y, s, o: notes(p, x, y, s),
    'wheat': lambda p, x, y, s, o: wheat(p, x, y, s),
    'flame': lambda p, x, y, s, o: flame(p, x, y, s),
    'arrow': lambda p, x, y, s, o: arrow(p, x, y, o['to'][0], o['to'][1], s),
}

PEOPLE = {
    # mascot: the channel's canonical character
    'mascot': dict(),
    'man': dict(hair=(40, 30, 25), tunic=(120, 100, 70), necklace=False),
    'woman': dict(hair=(60, 40, 30), tunic=(150, 110, 80), necklace=False),
    'elder': dict(hair=(200, 200, 200), tunic=(110, 90, 70), necklace=False),
    'kid': dict(hair=(70, 45, 25), tunic=(160, 120, 70), necklace=False),
    'you': dict(hair=(25, 25, 25), modern=(90, 140, 200), necklace=False),
    'worker': dict(hair=(25, 25, 25), modern=(230, 230, 235), necklace=False),
}


def draw_item(pen, kind, x, y, s, o):
    if kind in PEOPLE:
        kw = dict(PEOPLE[kind])
        kw.update({k: v for k, v in o.items() if k in ('pose', 'face', 'flip', 'prop')})
        if kind == 'kid':
            s *= .62
        figure(pen, x, y, s, **kw)
    elif kind in KINDS:
        KINDS[kind](pen, x, y, s, o)
    else:
        raise ValueError(f'unknown item {kind}')


def render(scene, out, seed=0):
    img = Image.new('RGB', (W, H), CREAM)
    pen = Pen(img, seed)
    background(pen, scene.get('bg', 'cream'))
    for it in scene.get('items', []):
        kind, x, y = it[0], it[1], it[2]
        s = it[3] if len(it) > 3 else 1.0
        o = it[4] if len(it) > 4 else {}
        draw_item(pen, kind, x, y, s, o)
    # soft paper grain
    img = img.filter(ImageFilter.SMOOTH)
    img.save(out, quality=92)
    return out
