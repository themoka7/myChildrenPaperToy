#!/usr/bin/env python3
"""작은 파츠 — 신발 · 양말 · 왕관 · 귀걸이 · 목걸이 · 가방 · 손소품.

## 좌우 한 쌍은 한 덩어리로 배치한다

신발과 양말은 좌·우 두 조각이 한 켤레다. 시트에서 흩어 놓으면 짝을 잃어버리기
때문에 **한 파츠 안에 두 개의 오림선**을 나란히 넣고 이름은 한 번만 쓴다.
사이 간격은 오림선 여백(3.3mm)의 두 배보다 넓어야 두 조각이 붙지 않는다.

## 부착 방식

    신발 · 양말   발등에서 위로 뻗은 탭을 발목 뒤로 접는다
    왕관 · 머리띠 정수리에 걸치는 아치 + 관자놀이 탭 2개
    귀걸이        머리카락 **옆선을 물어 끼우는 고리**. 접는선이 조각 가운데 있다.
                  이 방식이라 머리 모양이 귀를 덮든 말든 상관이 없다.
    목걸이        목 앞 밴드 + 목 옆 탭 2개
    가방 · 소품   손목을 감싸 뒤로 접는 탭 1개
"""
from . import spec as S
from .svg import Piece, blob, circ, ell, f, line, path, rrect, smooth, sym
from .wear import bow, flower, pearls, scallops, sparkle, star

PAIR_DX = 8.4          # 한 켤레의 두 조각 사이 거리 (오림선이 붙지 않는 최소치)


def _mir(pts, s, dx):
    """오른발 도면을 왼발로 뒤집고 dx 만큼 옮긴다."""
    return [(dx + s * x, y) for x, y in pts]


# ─────────────────────────────────────────────────────────────
# 신발 — 앵커는 두 발목 사이 (본체 0, ANKLE_Y)
# 발은 발목에서 x -2.3~+2.2, 발바닥에서 -3.4~+3.0 (발목 중앙 기준)
# ─────────────────────────────────────────────────────────────
def _footwear(key, label, outline, art, tab_y=2.4, tags=("shoe",), pdx=None):
    p = Piece(key, label, "shoe_pair", tags=list(tags), halo=S.HALO_SMALL)
    for s in (-1, 1):
        dx = s * (PAIR_DX if pdx is None else pdx)
        pts = _mir(outline, s, dx)
        p.cut_pts(pts)
        p.tab(dx, tab_y, S.TAB["shoe_ankle"]["w"], S.TAB["shoe_ankle"]["h"],
              "up", name="발등")
        p.art(*art(smooth(pts), s, dx))
    return p


# 발목(폭 4.5)에서 좁고 발(폭 6.4)에서 퍼지게 — 그래야 정면에서도 신발로 읽힌다.
SHOE_FLAT = [(-2.4, 1.8), (0.6, 1.6), (2.9, 2.8), (4.2, 6.4),
             (5.2, 10.8), (4.4, 13.4), (-3.9, 13.6), (-4.9, 10.4),
             (-3.6, 5.8)]
SHOE_POINT = [(-2.4, 1.6), (0.8, 1.4), (3.1, 2.6), (4.8, 6.6),
              (6.2, 11.4), (4.6, 13.6), (-3.9, 13.6), (-4.9, 10.2),
              (-3.6, 5.4)]
SHOE_BOOT = [(-3.4, -6.6), (0.0, -7.6), (3.6, -6.4), (3.8, -1.0),
             (4.2, 4.6), (5.2, 10.6), (4.4, 13.4), (-3.9, 13.6),
             (-4.9, 10.4), (-3.8, 4.0), (-3.4, -1.6)]
SHOE_SANDAL = [(-2.4, 2.4), (0.6, 2.2), (2.9, 3.4), (4.2, 6.8),
               (5.0, 10.8), (4.4, 13.4), (-3.9, 13.6), (-4.9, 10.4),
               (-3.6, 6.2)]


def _shoe_art(main, dark, deco=None, sole=None):
    """신발 그림 — 앞코 이음선과 밑창을 그려야 정면에서도 신발로 읽힌다."""
    def art(d, s, dx):
        a = [path(d, fill=main, c=True),
             # 발등 트인 자리 — 발이 들어가는 곳
             path(smooth([(dx - s * 2.8, 2.6), (dx + s * 0.3, 4.0),
                          (dx + s * 3.2, 3.0)], closed=False),
                  stroke=dark, w=0.38, op=0.75),
             # 앞코 이음선
             path(smooth([(dx - s * 4.4, 8.4), (dx + s * 0.4, 7.0),
                          (dx + s * 4.8, 8.8)], closed=False),
                  stroke=dark, w=0.34, op=0.7),
             # 밑창
             blob([(dx - s * 4.8, 11.0), (dx + s * 0.4, 10.4),
                   (dx + s * 5.1, 11.2), (dx + s * 4.4, 13.7),
                   (dx - s * 3.9, 13.9)], fill=sole or dark, stroke=None,
                  op=0.85),
             path(d, stroke=S.INK, w=0.32)]
        if deco:
            a = a[:3] + deco(s, dx) + a[3:]
        return a
    return art


def shoes(pdx=None):
    out = []

    # 1. 로즈 플랫
    def d1(s, dx):
        return [*bow(dx, 4.6, 0.62, S.C["rose3"], S.C["rose2"]),
                path(smooth([(dx - s * 3.6, 5.6), (dx, 3.8), (dx + s * 4.0, 5.8)],
                            closed=False), stroke=S.C["rose3"], w=0.7)]
    out.append(_footwear("shoe1", "로즈 플랫", SHOE_FLAT,
                         _shoe_art(S.C["rose"], S.C["rose2"], d1), pdx=pdx))

    # 2. 유리 구두
    def d2(s, dx):
        return [sparkle(dx + s * 1.0, 6.4, 1.5, S.C["white"]),
                sparkle(dx - s * 2.0, 9.0, 1.1, S.C["white"]),
                path(smooth([(dx - s * 3.8, 5.4), (dx, 3.4), (dx + s * 4.4, 5.8)],
                            closed=False), stroke=S.C["white"], w=0.8)]
    out.append(_footwear("shoe2", "유리 구두", SHOE_POINT,
                         _shoe_art(S.C["sky"], S.C["sky2"], d2), pdx=pdx))

    # 3. 메리제인
    def d3(s, dx):
        return [path(smooth([(dx - s * 4.0, 5.0), (dx, 4.0), (dx + s * 4.2, 5.2)],
                            closed=False), stroke=S.C["cream"], w=1.0),
                circ(dx + s * 2.6, 4.8, 0.65, fill=S.C["gold3"], c=True),
                scallops(dx - s * 3.4, dx + s * 3.8, 10.4, 1.0, S.C["cream"], 0.26)]
    out.append(_footwear("shoe3", "메리제인", SHOE_FLAT,
                         _shoe_art(S.C["lav"], S.C["lav2"], d3), pdx=pdx))

    # 4. 발레 슈즈
    def d4(s, dx):
        return [path(smooth([(dx - s * 3.6, 4.6), (dx, 3.4), (dx + s * 3.8, 4.8)],
                            closed=False), stroke=S.C["cream"], w=0.7),
                *bow(dx + s * 0.4, 3.0, 0.7, S.C["cream"], S.C["rose3"]),
                path(smooth([(dx - s * 2.6, 6.6), (dx + s * 0.6, 5.6),
                             (dx + s * 3.4, 7.0)], closed=False),
                     stroke=S.C["rose3"], w=0.5)]
    out.append(_footwear("shoe4", "발레 슈즈", SHOE_FLAT,
                         _shoe_art(S.C["rose3"], S.C["rose"], d4), pdx=pdx))

    # 5. 퍼 앵클부츠
    def d5(s, dx):
        return [blob([(dx - s * 4.8, -5.4), (dx, -7.0), (dx + s * 4.8, -5.2),
                      (dx + s * 4.4, -1.0), (dx, 0.2), (dx - s * 4.4, -1.2)],
                     fill=S.C["white"], stroke=S.INK2, w=0.28),
                scallops(dx - s * 4.4, dx + s * 4.6, -1.2, 1.1, S.INK2, 0.24),
                *flower(dx + s * 0.6, 6.4, 1.5, S.C["white"], S.C["gold3"])]
    out.append(_footwear("shoe5", "퍼 앵클부츠", SHOE_BOOT,
                         _shoe_art(S.C["mint"], S.C["mint2"], d5), tab_y=-5.6, pdx=pdx))

    # 6. 골드 샌들
    def d6(s, dx):
        a = []
        for y in (5.2, 7.4, 9.4):
            a.append(path(smooth([(dx - s * 3.8, y - 0.6), (dx, y + 0.8),
                                  (dx + s * 4.0, y - 0.4)], closed=False),
                          stroke=S.C["gold"], w=0.75))
        a.append(star(dx + s * 0.4, 4.0, 1.5, S.C["gold3"]))
        return a
    out.append(_footwear("shoe6", "골드 샌들", SHOE_SANDAL,
                         _shoe_art(S.C["cream2"], S.C["gold2"], d6, S.C["gold2"]), pdx=pdx))
    return out


# ─────────────────────────────────────────────────────────────
# 왕관 · 머리띠 — 정수리에 걸치는 아치. 앵커는 정수리.
# 아치 안쪽 구멍은 오림선 여백 때문에 머리보다 살짝 좁아져서 얹으면 걸린다.
# 그래도 흘러내리지 않게 관자놀이 탭 2개를 뒤로 접는다.
# ─────────────────────────────────────────────────────────────
BAND_OUT = [(-16.8, 13.4), (-14.4, 4.0), (-8.8, -1.4), (0.0, -2.6),
            (8.8, -1.4), (14.4, 4.0), (16.8, 13.4)]
BAND_IN = [(12.6, 13.8), (10.8, 6.0), (6.6, 2.2), (0.0, 1.4),
           (-6.6, 2.2), (-10.8, 6.0), (-12.6, 13.8)]


def _crown(key, label, deco, art):
    p = Piece(key, label, "crown", tags=["crown"], halo=S.HALO_SMALL)
    band = BAND_OUT + BAND_IN
    bd = smooth(band, 0.85)
    p.cut(bd, band)
    if deco is not None:
        p.cut(smooth(deco, 0.85), deco)
    for s in (-1, 1):
        p.tab(s * 14.7, 13.0, 4.6, 5.0, "down", name="관자놀이")
    p.art(*art(bd))
    return p


def crowns():
    out = []

    # 1. 하트 티아라
    deco = [(-7.6, 0.6), (-6.0, -5.0), (-3.0, -8.4), (0.0, -6.2),
            (3.0, -8.4), (6.0, -5.0), (7.6, 0.6), (0.0, 2.6)]
    def a1(bd):
        return [path(bd, fill=S.C["gold"], stroke=S.C["gold2"], w=0.32, c=True),
                blob(deco, fill=S.C["gold"], stroke=S.C["gold2"], w=0.32,
                     t=0.85),
                blob([(-2.6, -4.0), (0.0, -6.0), (2.6, -4.0), (0.0, -0.6)],
                     fill=S.C["rose"], stroke=S.C["rose2"], w=0.28),
                *pearls([(-11.0, 2.6), (-6.0, 0.4), (0.0, 3.4), (6.0, 0.4),
                         (11.0, 2.6)], 0.85, S.C["gold3"])]
    out.append(_crown("crown1", "하트 티아라", deco, a1))

    # 2. 별 왕관
    deco2 = [(-8.6, 1.0), (-8.0, -6.0), (-4.4, -3.4), (0.0, -10.4),
             (4.4, -3.4), (8.0, -6.0), (8.6, 1.0), (0.0, 3.0)]
    def a2(bd):
        return [path(bd, fill=S.C["gold"], stroke=S.C["gold2"], w=0.32, c=True),
                blob(deco2, fill=S.C["gold3"], stroke=S.C["gold2"], w=0.32,
                     t=0.5),
                star(0.0, -6.0, 2.4, S.C["gold"]),
                *pearls([(-9.6, 1.6), (0.0, 2.0), (9.6, 1.6)], 0.9, S.C["white"])]
    out.append(_crown("crown2", "별 왕관", deco2, a2))

    # 3. 진주 머리띠
    def a3(bd):
        return [path(bd, fill=S.C["cream"], stroke=S.INK2, w=0.32, c=True),
                *pearls([(-14.0, 6.6), (-11.4, 1.8), (-6.6, -1.2), (0.0, -2.0),
                         (6.6, -1.2), (11.4, 1.8), (14.0, 6.6)], 1.15,
                        S.C["white"])]
    out.append(_crown("crown3", "진주 머리띠", None, a3))

    # 4. 리본 머리띠 — 리본은 밴드(폭 3.5)보다 커서 오림선에 따로 넣어야 한다.
    #    안 그러면 클립에 잘려 뭉개진다.
    deco4 = [(-14.6, 2.6), (-13.6, -3.8), (-9.4, -5.8), (-5.2, -3.4),
             (-4.2, 2.8), (-9.4, 4.6)]
    def a4(bd):
        return [path(bd, fill=S.C["rose"], stroke=S.C["rose2"], w=0.32, c=True),
                blob(deco4, fill=S.C["rose3"], stroke=S.C["rose2"], w=0.3,
                     t=0.85),
                scallops(2.0, 13.0, 1.2, 1.4, S.C["rose3"], 0.3),
                *bow(-9.4, -0.6, 1.35, S.C["rose3"], S.C["rose2"])]
    out.append(_crown("crown4", "리본 머리띠", deco4, a4))

    # 5. 꽃 화관
    def a5(bd):
        a = [path(bd, fill=S.C["sage"], stroke=S.C["sage2"], w=0.32, c=True)]
        for x, y, r, pet in ((-13.0, 7.0, 2.1, S.C["rose3"]),
                             (-8.0, 0.6, 2.4, S.C["white"]),
                             (-2.0, -1.6, 2.0, S.C["rose"]),
                             (4.0, -1.0, 2.4, S.C["white"]),
                             (9.4, 1.6, 2.1, S.C["rose3"]),
                             (13.4, 7.4, 1.9, S.C["white"])):
            a += flower(x, y, r, pet, S.C["gold3"])
        return a
    out.append(_crown("crown5", "꽃 화관", None, a5))
    return out


# ─────────────────────────────────────────────────────────────
# 귀걸이 — 머리카락 옆선을 물어 끼우는 고리. 좌·우 두 조각이 한 쌍.
# 조각 가운데 접는선이 있고, 접으면 위쪽 절반이 머리 뒤로 간다.
# ─────────────────────────────────────────────────────────────
EAR_DX = 8.0


def _earrings(key, label, drop, art, edx=None):
    p = Piece(key, label, "earring", tags=["earring"], halo=S.HALO_SMALL)
    for s in (-1, 1):
        dx = s * (EAR_DX if edx is None else edx)
        # 고리 — 위로 뻗은 띠. 가운데 접는선.
        p.cut(f"M{f(dx - 1.7)},{f(1.0)} L{f(dx - 1.7)},{f(-6.4)} "
              f"Q{f(dx - 1.7)},{f(-7.8)} {f(dx)},{f(-7.8)} "
              f"Q{f(dx + 1.7)},{f(-7.8)} {f(dx + 1.7)},{f(-6.4)} "
              f"L{f(dx + 1.7)},{f(1.0)} Z",
              [(dx - 1.7, -7.8), (dx + 1.7, 1.0)])
        p.fold(dx - 1.7, -3.6, dx + 1.7, -3.6)
        pts = [(dx + x, y) for x, y in drop]
        p.cut_pts(pts)
        p.art(*art(smooth(pts), s, dx))
    return p


def earrings(edx=None):
    out = []
    # 귀 옆에 걸리는 크기 — 5~6mm. 이보다 크면 볼을 덮는다.
    D_ROUND = [(-2.6, 0.8), (0.0, -1.0), (2.6, 0.8), (2.7, 3.5),
               (0.0, 5.0), (-2.7, 3.5)]
    D_DROP = [(-2.1, 0.3), (0.0, -1.1), (2.1, 0.3), (1.8, 3.3),
              (0.0, 5.9), (-1.8, 3.3)]
    D_WIDE = [(-3.0, 0.6), (0.0, -1.0), (3.0, 0.6), (2.6, 3.0),
              (0.0, 4.6), (-2.6, 3.0)]

    def mk(key, label, drop, fn):
        return _earrings(key, label, drop, fn, edx)

    def a1(d, s, dx):     # 진주
        return [path(d, fill=S.C["white"], stroke=S.INK2, w=0.3),
                circ(dx, 2.6, 1.45, fill="#ffffff", stroke=S.INK2, w=0.26),
                circ(dx - 0.55, 2.1, 0.45, fill="#ffffff", c=False)]
    out.append(mk("ear1", "진주", D_ROUND, a1))

    def a2(d, s, dx):     # 하트
        return [path(d, fill=S.C["rose"], stroke=S.C["rose2"], w=0.3, c=True),
                blob([(dx - 1.6, 1.3), (dx, 0.0), (dx + 1.6, 1.3), (dx, 3.8)],
                     fill=S.C["rose3"], stroke=S.C["rose2"], w=0.26)]
    out.append(mk("ear2", "하트", D_ROUND, a2))

    def a3(d, s, dx):     # 별
        return [path(d, fill=S.C["gold"], stroke=S.C["gold2"], w=0.3, c=True),
                star(dx, 2.2, 1.85, S.C["gold3"])]
    out.append(mk("ear3", "별", D_WIDE, a3))

    def a4(d, s, dx):     # 물방울
        return [path(d, fill=S.C["sky"], stroke=S.C["sky2"], w=0.3, c=True),
                blob([(dx - 1.1, 1.2), (dx, -0.3), (dx + 1.1, 1.2), (dx, 4.7)],
                     fill=S.C["white"], stroke=S.C["sky2"], w=0.26),
                sparkle(dx - 0.4, 1.6, 0.75, "#ffffff", 0.9)]
    out.append(mk("ear4", "물방울", D_DROP, a4))

    def a5(d, s, dx):     # 꽃
        return [path(d, fill=S.C["sage3"], stroke=S.C["sage2"], w=0.3, c=True),
                *flower(dx, 2.3, 1.85, S.C["white"], S.C["gold3"])]
    out.append(mk("ear5", "꽃", D_WIDE, a5))

    def a6(d, s, dx):     # 리본
        return [path(d, fill=S.C["lav3"], stroke=S.C["lav2"], w=0.3, c=True),
                *bow(dx, 2.3, 0.58, S.C["lav"], S.C["lav2"])]
    out.append(mk("ear6", "리본", D_WIDE, a6))
    return out


# ─────────────────────────────────────────────────────────────
# 목걸이 — 목 앞 밴드 + 목 옆 탭 2개. 앵커는 목 (본체 0, SHOULDER_Y-4)
# ─────────────────────────────────────────────────────────────
def _necklace(key, label, art, pendant):
    p = Piece(key, label, "necklace", tags=["necklace"], halo=S.HALO_SMALL)
    band = sym([(0.0, -0.6), (2.8, -0.4), (5.0, 0.4), (5.2, 2.8),
                (2.8, 3.4), (0.0, 3.6)])
    p.cut_pts(band, 0.8)
    if pendant:
        p.cut_pts([(x, y) for x, y in pendant], 0.9)
    t = S.TAB["necklace_side"]
    p.tab(5.1, t["y"], t["w"], t["h"], "right", name="목 옆")
    p.tab(-5.1, t["y"], t["w"], t["h"], "left", name="목 옆")
    p.art(*art(smooth(band, 0.8)))
    return p


def necklaces():
    out = []
    P_DROP = [(-2.2, 2.4), (0.0, 1.4), (2.2, 2.4), (2.6, 6.4),
              (0.0, 9.4), (-2.6, 6.4)]
    P_WIDE = [(-3.2, 2.2), (0.0, 1.2), (3.2, 2.2), (3.0, 6.0),
              (0.0, 7.8), (-3.0, 6.0)]

    def a1(bd):
        return [path(bd, fill=S.C["gold"], stroke=S.C["gold2"], w=0.3, c=True),
                blob(P_DROP, fill=S.C["rose"], stroke=S.C["gold2"], w=0.28,
                     t=0.9),
                sparkle(-0.6, 4.6, 1.0, "#ffffff", 0.85)]
    out.append(_necklace("neck1", "루비 펜던트", a1, P_DROP))

    def a2(bd):
        return [path(bd, fill=S.C["white"], stroke=S.INK2, w=0.3, c=True),
                *pearls([(-4.2, 1.6), (-1.4, 2.6), (1.4, 2.6), (4.2, 1.6)],
                        1.0, "#ffffff")]
    out.append(_necklace("neck2", "진주 초커", a2, None))

    def a3(bd):
        return [path(bd, fill=S.C["mint"], stroke=S.C["mint2"], w=0.3, c=True),
                blob(P_WIDE, fill=S.C["gold3"], stroke=S.C["gold2"], w=0.28,
                     t=0.9),
                star(0.0, 4.4, 2.0, S.C["gold"])]
    out.append(_necklace("neck3", "별 목걸이", a3, P_WIDE))

    def a4(bd):
        return [path(bd, fill=S.C["rose3"], stroke=S.C["rose"], w=0.3, c=True),
                *flower(0.0, 4.4, 2.6, S.C["white"], S.C["gold3"])]
    out.append(_necklace("neck4", "꽃 목걸이", a4, P_WIDE))
    return out


# ─────────────────────────────────────────────────────────────
# 가방 · 손소품 — 손목을 감싸 뒤로 접는 탭 1개. 앵커는 손.
# ─────────────────────────────────────────────────────────────
def _handheld(key, label, outline, art, tab=None, tags=("prop",), t=1.0):
    """tab=(y, 방향) — 손이 잡는 자리. 가방은 위(손목에 걸고), 부채·봉은 아래(손잡이)."""
    p = Piece(key, label, "prop", tags=list(tags), halo=2.4)
    p.cut_pts(outline, t)
    tw = S.TAB["prop_wrist"]
    ty, tdir = tab or (min(y for _, y in outline) + 1.2, "up")
    p.tab(0.0, ty, tw["w"], tw["h"], tdir, name="손목")
    p.art(*art(smooth(outline, t)))
    return p


def bags():
    out = []
    B_ROUND = [(-4.6, 0.0), (0.0, -1.6), (4.6, 0.0), (5.4, 5.0),
               (3.4, 9.4), (0.0, 10.2), (-3.4, 9.4), (-5.4, 5.0)]
    B_SQ = [(-4.4, -0.6), (4.4, -0.6), (5.0, 4.0), (4.6, 9.2),
            (0.0, 9.8), (-4.6, 9.2), (-5.0, 4.0)]

    def a1(d):
        return [path(d, fill=S.C["rose"], stroke=S.INK, w=0.32, c=True),
                path(smooth([(-3.4, 0.4), (0.0, -4.4), (3.4, 0.4)], closed=False),
                     stroke=S.C["gold"], w=0.55),
                *bow(0.0, 3.6, 0.85, S.C["rose3"], S.C["rose2"])]
    out.append(_handheld("bag1", "로즈 손가방", B_ROUND, a1, tags=("bag",)))

    def a2(d):
        return [path(d, fill=S.C["mint"], stroke=S.INK, w=0.32, c=True),
                path(smooth([(-4.9, 2.0), (0.0, 3.0), (4.9, 2.0)], closed=False),
                     stroke=S.C["mint2"], w=0.4),
                scallops(-4.6, 4.8, 6.4, 1.2, S.C["white"], 0.28),
                *flower(0.0, 4.8, 1.9, S.C["white"], S.C["gold3"])]
    out.append(_handheld("bag2", "민트 가방", B_SQ, a2, tags=("bag",)))

    def a3(d):
        return [path(d, fill=S.C["gold3"], stroke=S.INK, w=0.32, c=True),
                path(smooth([(-3.4, 0.4), (0.0, -4.2), (3.4, 0.4)], closed=False),
                     stroke=S.C["gold2"], w=0.55),
                star(0.0, 4.4, 2.6, S.C["gold"]),
                sparkle(-2.8, 7.4, 1.1, S.C["white"])]
    out.append(_handheld("bag3", "골드 파티백", B_ROUND, a3, tags=("bag",)))

    def a4(d):
        return [path(d, fill=S.C["lav"], stroke=S.INK, w=0.32, c=True),
                path(smooth([(-4.9, 1.8), (0.0, 2.8), (4.9, 1.8)], closed=False),
                     stroke=S.C["lav2"], w=0.4),
                *pearls([(-2.6, 5.2), (0.0, 4.4), (2.6, 5.2)], 0.85,
                        S.C["white"]),
                scallops(-4.8, 5.0, 7.8, 1.2, S.C["lav3"], 0.28)]
    out.append(_handheld("bag4", "라벤더 파우치", B_SQ, a4, tags=("bag",)))
    return out


def props():
    out = []

    # 부채
    FAN = [(-8.0, 2.0), (-6.0, -4.6), (0.0, -7.4), (6.0, -4.6), (8.0, 2.0),
           (4.0, 4.6), (0.0, 5.2), (-4.0, 4.6)]

    def a1(d):
        a = [path(d, fill=S.C["rose3"], stroke=S.INK, w=0.32, c=True)]
        for x in (-5.2, -2.6, 0.0, 2.6, 5.2):
            a.append(path(smooth([(x * 0.28, 4.4), (x * 0.7, -1.0),
                                  (x, -5.6)], closed=False),
                          stroke=S.C["rose"], w=0.34, op=0.9))
        a.append(scallops(-7.6, 7.6, -3.2, 1.5, S.C["rose"], 0.3))
        return a
    out.append(_handheld("prop1", "레이스 부채", FAN, a1, (4.2, "down")))

    # 꽃다발
    BQ = [(-5.4, 0.0), (0.0, -3.0), (5.4, 0.0), (4.0, 6.0), (2.0, 13.0),
          (0.0, 14.0), (-2.0, 13.0), (-4.0, 6.0)]

    def a2(d):
        a = [path(d, fill=S.C["sage3"], stroke=S.INK, w=0.32, c=True)]
        for x, y, r, pet in ((-2.8, 1.0, 2.1, S.C["rose"]),
                             (2.8, 0.6, 2.1, S.C["white"]),
                             (0.0, -1.4, 2.3, S.C["rose3"])):
            a += flower(x, y, r, pet, S.C["gold3"])
        a += [path(smooth([(-1.6, 4.0), (0.0, 9.0), (1.4, 13.4)], closed=False),
                   stroke=S.C["leaf"], w=0.5),
              *bow(0.0, 7.0, 0.8, S.C["cream"], S.C["sage2"])]
        return a
    out.append(_handheld("prop2", "꽃다발", BQ, a2, (12.8, "down")))

    # 요술봉
    WAND = [(-2.4, -6.0), (0.0, -8.6), (2.4, -6.0), (1.4, 2.0), (1.2, 14.0),
            (0.0, 15.0), (-1.2, 14.0), (-1.4, 2.0)]

    def a3(d):
        return [path(d, fill=S.C["gold3"], stroke=S.INK, w=0.32, c=True),
                star(0.0, -5.0, 4.4, S.C["gold"]),
                star(0.0, -5.0, 2.2, S.C["gold3"]),
                path(smooth([(0.0, 1.0), (0.0, 13.6)], closed=False),
                     stroke=S.C["gold"], w=0.5, op=0.7),
                sparkle(3.6, -8.0, 1.3, S.C["gold3"])]
    out.append(_handheld("prop3", "요술봉", WAND, a3, (13.8, "down"), t=0.6))

    # 파라솔
    UMB = [(-9.0, 1.0), (-7.0, -6.0), (0.0, -9.4), (7.0, -6.0), (9.0, 1.0),
           (4.6, 2.4), (0.0, 3.0), (-4.6, 2.4)]

    def a4(d):
        a = [path(d, fill=S.C["lav3"], stroke=S.INK, w=0.32, c=True)]
        for i, x in enumerate((-6.0, -2.0, 2.0, 6.0)):
            a.append(blob([(x - 2.0, 1.6), (x, -7.6), (x + 2.0, 1.6),
                           (x, 2.6)], fill=S.C["lav"] if i % 2 else S.C["white"],
                          stroke=None, op=0.85))
        a += [path(d, stroke=S.INK, w=0.32),
              scallops(-8.6, 8.6, 1.4, 1.5, S.C["lav2"], 0.3),
              circ(0.0, -9.0, 1.1, fill=S.C["gold"], stroke=S.C["gold2"], w=0.26)]
        return a
    out.append(_handheld("prop4", "레이스 파라솔", UMB, a4, (2.2, "down")))
    return out
