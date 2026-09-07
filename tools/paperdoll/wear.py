#!/usr/bin/env python3
"""드레스와 망토.

앵커는 **어깨 중앙** — 본체 좌표 (0, SHOULDER_Y=38) 에 놓인다. 그래서 이 파일의
y 는 전부 "어깨선에서 아래로 몇 mm" 다.

    허리 24 · 골반 38 · 무릎 80 · 발목 100 · 바닥 111

설계 규칙
    · **밑단은 y=106 을 넘기지 않는다.** 바닥까지 끌리면 신발이 가려져서
      신발 세트를 바꾸는 재미가 사라진다. 발목이 보이는 길이로 끊는다.
    · 몸통 옆은 x=±10.2 이상으로 덮는다. 본체 허리(±10.4)보다 좁으면 살이 비친다.
    · 소매는 어깨 관절(±11.8)을 덮어야 어깨가 삐져나오지 않는다.
    · 조각 반쪽 폭은 27mm 이하 — 한 줄에 3벌이 들어가야 한다.
"""
from . import spec as S
from .svg import (Piece, blob, circ, f, path, rim, smooth, soft,
                  sym, volume)

WAIST = 24.0
HIP = 38.0


# ─────────────────────────────────────────────────────────────
# 공용 장식
# ─────────────────────────────────────────────────────────────
def scallops(x0, x1, y, r, stroke, w=0.28, up=False):
    """레이스 — 작은 반원을 이어 붙인 띠."""
    n = max(1, int(round(abs(x1 - x0) / (r * 2))))
    step = (x1 - x0) / n
    d = [f"M{f(x0)},{f(y)}"]
    for _ in range(n):
        d.append(f"a{f(abs(step) / 2)},{f(r * 0.9)} 0 0 "
                 f"{0 if up else 1} {f(step)},0")
    return path(" ".join(d), stroke=stroke, w=w)


def frill(y, x0, x1, depth, fill, stroke, n=5):
    """프릴 단 — 아래가 물결인 띠."""
    pts = [(x0, y)]
    for i in range(n * 2 + 1):
        t = i / (n * 2)
        pts.append((x0 + (x1 - x0) * t, y + depth * (1.0 if i % 2 else 0.55)))
    pts.append((x1, y))
    return path(smooth(pts, 0.8), fill=fill, stroke=stroke, w=0.28, c=True)


def bow(x, y, sc, main, dark):
    """리본 — 날개 둘 + 매듭."""
    def wing(s):
        return blob([(x, y), (x + s * 3.4 * sc, y - 2.5 * sc),
                     (x + s * 4.4 * sc, y + 0.4 * sc),
                     (x + s * 2.6 * sc, y + 2.2 * sc)],
                    fill=main, stroke=S.INK2, w=0.26)
    knot = blob([(x - 1.3 * sc, y - 1.5 * sc), (x + 1.3 * sc, y - 1.5 * sc),
                 (x + 1.3 * sc, y + 1.5 * sc), (x - 1.3 * sc, y + 1.5 * sc)],
                fill=dark, stroke=S.INK2, w=0.26, t=0.55)
    return [wing(-1), wing(1), knot]


def tails(x, y, sc, main, length=None):
    """리본 꼬리 두 줄."""
    L = length or 14 * sc
    out = []
    for s in (-1, 1):
        out.append(blob([(x + s * 0.8 * sc, y), (x + s * 3.0 * sc, y + L * 0.5),
                         (x + s * 2.0 * sc, y + L), (x + s * 4.6 * sc, y + L)],
                        fill=main, stroke=S.INK2, w=0.24, t=0.8))
    return out


def star(x, y, r, fill, op=None):
    import math
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d = "M" + " L".join(f"{f(px)},{f(py)}" for px, py in pts) + " Z"
    return path(d, fill=fill, c=True, op=op)


def sparkle(x, y, r, fill, op=None):
    """네 갈래 반짝임."""
    d = (f"M{f(x)},{f(y - r)} Q{f(x)},{f(y)} {f(x + r)},{f(y)} "
         f"Q{f(x)},{f(y)} {f(x)},{f(y + r)} Q{f(x)},{f(y)} {f(x - r)},{f(y)} "
         f"Q{f(x)},{f(y)} {f(x)},{f(y - r)} Z")
    return path(d, fill=fill, c=True, op=op)


def flower(x, y, r, petal, center, n=5):
    import math
    out = []
    for i in range(n):
        a = i * 2 * math.pi / n
        out.append(circ(x + r * 0.72 * math.cos(a), y + r * 0.72 * math.sin(a),
                        r * 0.5, fill=petal, c=True))
    out.append(circ(x, y, r * 0.34, fill=center, c=True))
    return out


def pearls(pts, r, fill):
    return [circ(px, py, r, fill=fill, stroke=S.INK2, w=0.16, c=True)
            for px, py in pts]


def arc_pts(x0, y0, x1, y1, sag, n=7):
    """두 점을 잇는 늘어진 곡선 위의 점들 (진주·자수 곡선용)."""
    return [(x0 + (x1 - x0) * (i / (n - 1)),
             y0 + (y1 - y0) * (i / (n - 1))
             + sag * (1 - (2 * (i / (n - 1)) - 1) ** 2))
            for i in range(n)]


# ─────────────────────────────────────────────────────────────
# 드레스 조립
# ─────────────────────────────────────────────────────────────
def tab_x(half, cy, h, pad=0.2):
    """탭을 옆으로 낼 자리 — 그 높이 구간에서 옷이 가장 넓은 x.

    고정값을 쓰면 치마가 퍼지는 드레스에서 탭이 옷 안에 묻혀 버린다.
    (오림선 흰 여백이 3.3mm 라서, 묻힌 탭은 아예 보이지도 않는다.)
    """
    lo, hi = cy - h / 2 - 1.5, cy + h / 2 + 1.5
    xs = [x for x, y in half if lo <= y <= hi]
    if not xs:                      # 구간에 점이 없으면 위아래 점을 보간
        xs = [x for x, y in half if abs(y - cy) < 12]
    return max(xs) + pad


def _dress(key, label, half, art):
    """드레스 한 벌. half 는 오른쪽 절반 실루엣 (목 중앙 → 밑단 중앙)."""
    p = Piece(key, label, "dress", tags=["dress"])
    sil = sym(half)
    d = smooth(sil)
    p.cut(d, sil)

    t = S.TAB["dress_shoulder"]
    for s in (-1, 1):
        p.tab(s * t["x"], t["y"] + 0.4, t["w"], t["h"], "up", name="어깨")
    tw = S.TAB["dress_waist"]
    wx = tab_x(half, tw["y"], tw["h"])
    p.tab(wx, tw["y"], tw["w"], tw["h"], "right", name="허리")
    p.tab(-wx, tw["y"], tw["w"], tw["h"], "left", name="허리")

    if not p.use_art():
        p.art(*art(d))
        p.art(*volume(p, d))
        p.art(path(d, stroke=S.INK, w=0.34))
    return p


# ── 1. 로즈 볼가운 ───────────────────────────────────────────
D1 = [
    (0.0, 6.2), (2.8, 3.2), (5.6, 4.6), (8.4, 1.8), (10.8, 0.8),
    (13.6, 2.6), (15.2, 7.4), (13.2, 11.8), (11.0, 12.6),
    (10.6, 18.0), (10.3, 24.2),
    (14.2, 30.0), (19.0, 44.0), (22.4, 64.0), (24.2, 84.0), (24.4, 96.0),
    (21.6, 102.4), (11.5, 104.4), (0.0, 105.0),
]


def _a1(d):
    bod = sym([(0.0, 6.2), (2.8, 3.2), (5.6, 4.6), (8.4, 1.8), (10.8, 0.8),
               (11.4, 5.0), (10.9, 14.0), (10.4, 24.4), (5.0, 25.0), (0.0, 25.2)])
    over = sym([(0.0, 26.0), (8.0, 27.0), (14.6, 33.0), (19.4, 48.0),
                (21.0, 62.0), (14.0, 66.0), (6.0, 67.6), (0.0, 68.0)])
    a = [path(d, fill=S.C["cream"], c=True),
         blob(bod, fill=S.C["rose"], stroke=S.INK, w=0.3),
         blob(over, fill=S.C["rose3"], stroke=S.INK2, w=0.28)]
    for s in (-1, 1):   # 퍼프 소매
        a.append(blob([(s * 10.6, 1.0), (s * 13.8, 2.6), (s * 15.4, 7.6),
                       (s * 13.2, 11.8), (s * 10.8, 12.4), (s * 11.2, 5.0)],
                      fill=S.C["rose3"], stroke=S.INK, w=0.3))
        a.append(path(smooth([(s * 11.4, 4.0), (s * 13.4, 6.4), (s * 12.6, 10.4)],
                             closed=False), stroke=S.INK2, w=0.24))
    for x in (-13.0, 13.0):
        a.append(path(smooth(arc_pts(x * 0.5, 34.0, x, 64.0, 1.2, 5),
                             closed=False), stroke=S.C["gold"], w=0.3, op=0.55))
    a += [
        path(smooth([(-10.4, 22.4), (0.0, 24.2), (10.4, 22.4),
                     (10.4, 25.6), (0.0, 27.4), (-10.4, 25.6)], 0.7),
             fill=S.C["gold"], stroke=S.C["gold2"], w=0.3, c=True),
        scallops(-21.0, 21.0, 100.6, 2.1, S.C["gold2"], 0.3),
        scallops(-10.0, 10.0, 25.2, 1.3, S.C["gold3"], 0.26),
        *bow(0, 26.6, 1.15, S.C["rose2"], S.C["rose"]),
        *pearls(arc_pts(-6.4, 8.0, 6.4, 8.0, 2.0, 7), 0.62, S.C["gold3"]),
        sparkle(-15.0, 56.0, 1.5, S.C["gold3"]),
        sparkle(13.0, 74.0, 1.7, S.C["gold3"]),
        sparkle(18.0, 40.0, 1.2, S.C["gold3"]),
    ]
    return a


# ── 2. 민트 프릴 ─────────────────────────────────────────────
D2 = [
    (0.0, 4.4), (3.6, 2.6), (7.0, 1.0), (10.8, 0.8),
    (14.0, 3.0), (14.8, 8.6), (12.4, 10.6), (10.6, 13.0),
    (10.3, 24.0),
    (13.2, 29.0), (16.4, 40.0), (18.6, 56.0), (20.4, 74.0), (21.6, 90.0),
    (20.6, 98.4), (11.0, 100.6), (0.0, 101.4),
]


def _a2(d):
    bod = sym([(0.0, 4.4), (3.6, 2.6), (7.0, 1.0), (10.8, 0.8), (11.2, 6.0),
               (10.7, 15.0), (10.3, 24.2), (5.0, 24.8), (0.0, 25.0)])
    a = [path(d, fill=S.C["mint3"], c=True),
         blob(bod, fill=S.C["mint"], stroke=S.INK, w=0.3)]
    for s in (-1, 1):   # 오프숄더 프릴 소매
        a.append(blob([(s * 10.4, 1.2), (s * 14.2, 3.2), (s * 15.0, 8.8),
                       (s * 12.2, 10.8), (s * 10.4, 8.0)],
                      fill=S.C["mint3"], stroke=S.INK, w=0.3))
        a.append(scallops(s * 10.6, s * 14.8, 9.4, 1.2, S.INK2, 0.24))
    a += [frill(30.0, -13.8, 13.8, 5.0, S.C["mint3"], S.INK2, 5),
          frill(52.0, -18.0, 18.0, 5.6, "#e6f4f0", S.INK2, 6),
          frill(76.0, -20.6, 20.6, 6.2, S.C["mint3"], S.INK2, 7),
          path(smooth([(-10.3, 22.6), (0.0, 24.0), (10.3, 22.6),
                       (10.3, 26.4), (0.0, 27.8), (-10.3, 26.4)], 0.7),
               fill=S.C["mint2"], stroke=S.INK2, w=0.28, c=True),
          *bow(0, 25.2, 1.3, S.C["cream"], S.C["mint"]),
          scallops(-6.6, 6.6, 3.4, 1.4, S.C["white"], 0.3),
          *flower(-8.0, 44.0, 2.2, S.C["white"], S.C["gold3"]),
          *flower(9.0, 62.0, 2.4, S.C["white"], S.C["gold3"]),
          *flower(-13.0, 86.0, 2.2, S.C["white"], S.C["gold3"])]
    return a


# ── 3. 라벤더 스타 ───────────────────────────────────────────
D3 = [
    (0.0, 5.2), (3.4, 3.0), (6.8, 1.0), (10.6, 0.6),
    (13.4, 2.4), (14.6, 6.8), (12.6, 9.8), (10.8, 11.2),
    (10.4, 24.0),
    (15.0, 31.0), (20.0, 48.0), (23.0, 70.0), (24.0, 90.0),
    (22.4, 100.4), (12.0, 102.6), (0.0, 103.4),
]


def _a3(d):
    bod = sym([(0.0, 5.2), (3.4, 3.0), (6.8, 1.0), (10.6, 0.6), (11.2, 4.6),
               (10.8, 14.0), (10.4, 24.2), (5.0, 24.8), (0.0, 25.0)])
    tul = sym([(0.0, 27.0), (9.0, 28.4), (15.4, 36.0), (19.6, 54.0),
               (21.4, 74.0), (12.0, 78.0), (5.0, 79.4), (0.0, 79.8)])
    a = [path(d, fill=S.C["lav"], c=True),
         blob(bod, fill=S.C["lav2"], stroke=S.INK, w=0.3),
         blob(tul, fill=S.C["lav3"], stroke=S.INK2, w=0.26, op=0.75)]
    for s in (-1, 1):
        a.append(blob([(s * 10.4, 0.8), (s * 13.6, 2.4), (s * 14.8, 7.0),
                       (s * 12.4, 10.0), (s * 10.6, 8.0)],
                      fill=S.C["lav3"], stroke=S.INK, w=0.3))
    a += [path(smooth([(-10.4, 22.6), (0.0, 24.0), (10.4, 22.6),
                       (10.4, 26.0), (0.0, 27.4), (-10.4, 26.0)], 0.7),
               fill=S.C["gold"], stroke=S.C["gold2"], w=0.3, c=True),
          star(0.0, 24.8, 3.0, S.C["gold3"]),
          scallops(-21.4, 21.4, 98.6, 2.2, S.C["lav3"], 0.3)]
    for x, y, r in ((-14.0, 46.0, 2.0), (10.0, 40.0, 1.7), (17.0, 62.0, 2.2),
                    (-18.0, 72.0, 1.8), (4.0, 86.0, 2.4), (-8.0, 94.0, 1.6),
                    (16.0, 90.0, 1.6), (-4.0, 58.0, 1.4)):
        a.append(star(x, y, r, S.C["gold3"]))
    for x, y, r in ((-6.0, 34.0, 1.8), (12.0, 76.0, 1.9), (-16.0, 88.0, 1.6),
                    (8.0, 54.0, 1.6)):
        a.append(sparkle(x, y, r, S.C["white"]))
    return a


# ── 4. 골드 로열 (긴 소매) ───────────────────────────────────
D4 = [
    (0.0, 3.0), (3.2, 1.6), (7.0, 0.4), (11.0, 0.4),
    (14.8, 3.0), (17.0, 12.0), (18.2, 32.0), (19.6, 52.0),
    (21.4, 72.0), (23.0, 92.0), (22.0, 101.4), (11.5, 103.6), (0.0, 104.4),
]


def _a4(d):
    bod = sym([(0.0, 3.0), (3.2, 1.6), (7.0, 0.4), (11.0, 0.4), (12.4, 4.0),
               (11.6, 14.0), (11.0, 24.4), (5.0, 25.0), (0.0, 25.2)])
    a = [path(d, fill=S.C["cream"], c=True),
         blob(bod, fill=S.C["cream2"], stroke=S.INK, w=0.3)]
    for s in (-1, 1):   # 소매 — 채운 조각으로 그려 치마와 구분한다
        a.append(blob([(s * 11.2, 0.8), (s * 14.8, 3.0), (s * 17.0, 12.0),
                       (s * 18.2, 32.0), (s * 19.4, 52.0), (s * 19.0, 56.4),
                       (s * 13.4, 55.4), (s * 12.6, 34.0), (s * 11.6, 12.0)],
                      fill=S.C["cream"], stroke=S.INK, w=0.3))
        a.append(blob([(s * 13.4, 50.4), (s * 19.2, 51.4), (s * 19.0, 56.6),
                       (s * 13.5, 55.6)], fill=S.C["gold3"], stroke=S.C["gold2"],
                      w=0.28, t=0.5))
    a += [path(smooth([(-11.0, 22.0), (0.0, 23.8), (11.0, 22.0),
                       (11.0, 26.6), (0.0, 28.4), (-11.0, 26.6)], 0.7),
               fill=S.C["gold"], stroke=S.C["gold2"], w=0.3, c=True),
          blob(sym([(0.0, 29.0), (5.6, 30.0), (8.6, 50.0), (10.6, 76.0),
                    (11.4, 98.0), (5.6, 100.4), (0.0, 100.8)]),
               fill=S.C["gold3"], stroke=S.C["gold2"], w=0.28, op=0.5),
          scallops(-6.2, 6.2, 2.6, 1.3, S.C["gold"], 0.3),
          *pearls(arc_pts(-7.0, 8.0, 7.0, 8.0, 2.4, 7), 0.66, S.C["gold3"])]
    for s in (-1, 1):
        for y in (66.0, 84.0):
            a.append(path(smooth([(s * 14.0, y), (s * 16.6, y + 5.0),
                                  (s * 14.4, y + 10.0)], closed=False),
                          stroke=S.C["gold"], w=0.34, op=0.8))
    a.append(scallops(-21.4, 21.4, 99.4, 2.2, S.C["gold2"], 0.32))
    return a


# ── 5. 세이지 플라워 (무릎 아래) ─────────────────────────────
D5 = [
    (0.0, 4.8), (3.4, 2.8), (7.0, 1.0), (10.8, 0.6),
    (13.6, 2.6), (14.4, 7.2), (12.2, 9.6), (10.6, 11.2),
    (10.4, 22.0),
    (12.6, 26.0), (15.6, 40.0), (17.8, 58.0), (19.0, 72.0),
    (18.2, 78.4), (10.0, 80.6), (0.0, 81.4),
]


def _a5(d):
    bod = sym([(0.0, 4.8), (3.4, 2.8), (7.0, 1.0), (10.8, 0.6), (11.2, 5.0),
               (10.8, 13.0), (10.4, 22.2), (5.0, 22.8), (0.0, 23.0)])
    a = [path(d, fill=S.C["sage3"], c=True),
         blob(bod, fill=S.C["sage"], stroke=S.INK, w=0.3)]
    for s in (-1, 1):
        a.append(blob([(s * 10.6, 0.8), (s * 13.8, 2.6), (s * 14.6, 7.4),
                       (s * 12.0, 9.8), (s * 10.6, 7.4)],
                      fill=S.C["sage"], stroke=S.INK, w=0.3))
        a.append(scallops(s * 10.8, s * 14.4, 8.8, 1.2, S.C["white"], 0.24))
    a += [path(smooth([(-10.4, 20.6), (0.0, 22.0), (10.4, 20.6),
                       (10.4, 24.0), (0.0, 25.4), (-10.4, 24.0)], 0.7),
               fill=S.C["leaf"], stroke=S.INK2, w=0.28, c=True),
          *bow(0, 23.2, 1.1, S.C["cream"], S.C["sage2"]),
          scallops(-17.6, 17.6, 76.8, 2.0, S.C["white"], 0.3),
          scallops(-6.4, 6.4, 3.2, 1.3, S.C["white"], 0.28)]
    for x, y in ((-13.0, 44.0), (4.0, 52.0), (-6.0, 74.0), (16.0, 48.0),
                 (9.0, 66.0)):
        a.append(path(smooth([(x, y), (x + 2.4, y + 2.0), (x + 1.0, y + 4.4)],
                             closed=False), stroke=S.C["leaf"], w=0.4, op=0.8))
    for x, y, r in ((-11.0, 34.0, 2.3), (7.0, 42.0, 2.0), (14.0, 60.0, 2.2),
                    (-15.0, 58.0, 2.0), (-3.0, 66.0, 2.4), (11.0, 72.0, 1.8),
                    (-8.0, 48.0, 1.6), (2.0, 32.0, 1.7)):
        a += flower(x, y, r, S.C["rose3"], S.C["gold3"])
    return a


# ── 6. 로즈 머메이드 ─────────────────────────────────────────
D6 = [
    (0.0, 6.0), (3.2, 3.6), (6.6, 1.2), (10.4, 0.8),
    (12.3, 4.2), (11.2, 10.0),
    (10.5, 24.0), (11.2, 38.0), (11.6, 54.0), (11.4, 66.0),
    (13.6, 76.0), (17.6, 88.0), (20.6, 98.0),
    (19.2, 103.0), (10.0, 105.2), (0.0, 106.0),
]


def _a6(d):
    bod = sym([(0.0, 6.0), (3.2, 3.6), (6.6, 1.2), (10.4, 0.8), (12.3, 4.2),
               (11.2, 10.0), (10.5, 24.2), (5.0, 24.8), (0.0, 25.0)])
    a = [path(d, fill=S.C["rose"], c=True),
         blob(bod, fill=S.C["rose2"], stroke=S.INK, w=0.3),
         blob(sym([(0.0, 70.0), (7.0, 71.0), (12.2, 76.0), (17.0, 88.0),
                   (20.0, 98.0), (18.8, 102.6), (9.6, 104.8), (0.0, 105.4)]),
              fill=S.C["rose3"], stroke=S.INK2, w=0.28),
         path(smooth([(-10.5, 22.6), (0.0, 24.0), (10.5, 22.6),
                      (10.5, 26.0), (0.0, 27.4), (-10.5, 26.0)], 0.7),
              fill=S.C["gold"], stroke=S.C["gold2"], w=0.3, c=True),
         scallops(-9.8, 9.8, 2.2, 1.5, S.C["cream"], 0.3),
         *pearls(arc_pts(-6.0, 7.4, 6.0, 7.4, 2.0, 6), 0.6, S.C["cream"])]
    for y in (36.0, 48.0, 60.0):    # 몸판 레이스 — 가로 결
        a.append(scallops(-9.6, 9.6, y, 1.5, S.C["rose3"], 0.28))
    a += [scallops(-19.0, 19.0, 100.6, 2.0, S.C["cream"], 0.3),
          scallops(-11.6, 11.6, 72.0, 1.8, S.C["cream"], 0.3)]
    for x, y, r in ((-7.0, 84.0, 2.2), (8.0, 92.0, 2.0), (-14.0, 96.0, 1.8),
                    (14.0, 78.0, 1.7)):
        a += flower(x, y, r, S.C["cream"], S.C["gold3"])
    return a


DRESSES = [
    ("dress1", "로즈 볼가운", D1, _a1),
    ("dress2", "민트 프릴", D2, _a2),
    ("dress3", "라벤더 스타", D3, _a3),
    ("dress4", "골드 로열", D4, _a4),
    ("dress5", "세이지 플라워", D5, _a5),
    ("dress6", "로즈 머메이드", D6, _a6),
]


def dresses():
    return [_dress(k, lb, half, art) for k, lb, half, art in DRESSES]


# ─────────────────────────────────────────────────────────────
# 망토 — 드레스 위에 덧입힌다. 어깨 탭만 있다.
# ─────────────────────────────────────────────────────────────
def _cape(key, label, half, art):
    p = Piece(key, label, "cape", tags=["cape"])
    sil = sym(half)
    d = smooth(sil)
    p.cut(d, sil)
    for s in (-1, 1):
        p.tab(s * 7.4, 1.2, 6.0, 7.0, "up", name="어깨")
    if not p.use_art():
        p.art(*art(d))
        p.art(*volume(p, d, top=0.26, bottom=0.2))
        p.art(path(d, stroke=S.INK, w=0.34))
    return p


C1 = [
    (0.0, 6.0), (4.0, 3.0), (8.0, 1.0), (12.0, 1.4),
    (14.6, 6.0), (16.0, 20.0), (18.4, 44.0), (21.4, 70.0), (23.6, 92.0),
    (22.0, 100.0), (11.0, 102.4), (0.0, 103.0),
]


def _c1(d):
    a = [path(d, fill=S.C["mint"], c=True),
         blob(sym([(0.0, 12.0), (6.0, 13.0), (9.0, 30.0), (11.0, 60.0),
                   (12.4, 96.0), (6.0, 99.0), (0.0, 99.6)]),
              fill=S.C["cream"], stroke=S.INK2, w=0.26)]
    for s in (-1, 1):
        for y in (26.0, 50.0, 74.0):
            a.append(star(s * 15.0, y, 2.0, S.C["gold3"]))
            a.append(star(s * 8.0, y + 12.0, 1.5, S.C["gold3"]))
    a += [blob(sym([(0.0, 7.4), (4.6, 3.6), (9.0, 1.2), (13.0, 2.0),
                    (14.2, 7.0), (11.0, 11.0), (5.0, 12.4), (0.0, 12.8)]),
               fill=S.C["white"], stroke=S.INK, w=0.3),
          scallops(-12.4, 12.4, 11.4, 1.6, S.INK2, 0.26),
          circ(0, 10.2, 2.0, fill=S.C["gold"], stroke=S.C["gold2"], w=0.3),
          scallops(-21.4, 21.4, 98.4, 2.2, S.C["gold3"], 0.3)]
    return a


C2 = [
    (0.0, 5.6), (4.0, 2.8), (8.2, 1.0), (12.2, 1.6),
    (15.0, 7.0), (17.0, 24.0), (19.6, 50.0), (22.6, 76.0), (24.2, 96.0),
    (22.4, 102.0), (11.2, 104.4), (0.0, 105.0),
]


def _c2(d):
    a = [path(d, fill=S.C["rose"], c=True),
         blob(sym([(0.0, 12.6), (6.4, 13.6), (9.6, 32.0), (11.6, 64.0),
                   (13.0, 98.0), (6.2, 101.0), (0.0, 101.6)]),
              fill=S.C["cream"], stroke=S.INK2, w=0.26)]
    for s in (-1, 1):
        for y, r in ((30.0, 2.4), (54.0, 2.0), (80.0, 2.2)):
            a += flower(s * 16.0, y, r, S.C["cream"], S.C["gold3"])
    a += [blob(sym([(0.0, 7.0), (4.6, 3.4), (9.2, 1.2), (13.2, 2.2),
                    (14.8, 7.4), (11.0, 11.6), (5.0, 13.0), (0.0, 13.4)]),
               fill=S.C["rose3"], stroke=S.INK, w=0.3),
          scallops(-13.0, 13.0, 12.2, 1.6, S.INK2, 0.26),
          *bow(0, 10.6, 1.2, S.C["gold3"], S.C["gold"]),
          scallops(-22.0, 22.0, 100.4, 2.2, S.C["cream"], 0.3)]
    return a


C3 = [
    (0.0, 5.0), (4.2, 2.6), (8.4, 1.0), (12.4, 1.8),
    (15.4, 7.0), (17.4, 20.0), (19.0, 34.0), (18.0, 42.0),
    (10.0, 44.4), (0.0, 45.0),
]


def _c3(d):
    """짧은 퍼 케이프 — 어깨만 덮어서 어떤 드레스에도 얹힌다."""
    # 흰 퍼는 순백으로 칠하면 종이와 구분이 안 된다 — 아주 옅은 따뜻한 색으로.
    a = [path(d, fill="#f4eee6", c=True),
         blob(sym([(0.0, 10.0), (6.0, 11.0), (8.6, 24.0), (9.6, 38.0),
                   (5.0, 40.4), (0.0, 41.0)]),
              fill="#fffaf2", stroke=S.INK2, w=0.26)]
    for y in (16.0, 24.0, 32.0):      # 퍼 결
        a.append(scallops(-16.4, 16.4, y, 2.0, "#ddd2c6", 0.3))
    for s in (-1, 1):
        for y in (20.0, 28.0, 36.0):
            a.append(circ(s * 13.6, y, 1.2, fill="#e6dcd0", c=True, op=0.9))
    a += [scallops(-17.6, 17.6, 40.6, 2.2, "#c9bcae", 0.3),
          scallops(-12.4, 12.4, 11.0, 1.8, "#c9bcae", 0.3),
          *bow(0.0, 8.0, 1.25, S.C["rose3"], S.C["rose"])]
    return a


def capes():
    return [_cape("cape1", "민트 로열 망토", C1, _c1),
            _cape("cape2", "로즈 플라워 망토", C2, _c2),
            _cape("cape3", "퍼 숄더 케이프", C3, _c3)]
