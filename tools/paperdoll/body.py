#!/usr/bin/env python3
"""공주 본체 — 세트의 기준 조각.

이 인형은 **1명뿐**이다. 1번 시트에 같은 인형이 4장 인쇄되는 것은
네 벌을 동시에 입혀 세워 두고 놀 수 있게 하려는 것이고, 그림은 하나다.
그래서 이 파일의 치수가 바뀌면 드레스·머리·신발이 전부 어긋난다 —
치수는 반드시 `spec.py` 를 통해서만 만진다.

실루엣 규칙
    · 팔은 몸통에 **붙여** 내린다. 오림선이 어깨 → 손 → 허벅지로 한 줄로
      흐르므로 아이가 겨드랑이를 V자로 파낼 일이 없다. 팔과 몸통의 구분은
      잔선으로만 보여 준다.
    · 두 다리 사이도 오리지 않는다. 발 아래 발판이 어차피 둘을 잇는다.
    · 발판은 **발보다 먼저** 그린다. 그래야 발이 발판 앞에 서 있는 것으로 보인다.
"""
from . import spec as S
from .svg import (Piece, blob, circ, ell, f, line, path, smooth, sym)

# ─────────────────────────────────────────────────────────────
# 실루엣 — 오른쪽 절반 (정수리 → 발밑 가운데). 왼쪽은 좌우 대칭.
# ─────────────────────────────────────────────────────────────
HALF = [
    (0.0, 0.0),          # 정수리
    (8.0, 0.8),
    (13.0, 4.6),
    (15.4, 12.4),
    (15.0, 19.6),        # 귀 높이
    (13.2, 26.6),
    (9.8, 31.6),         # 턱 옆
    (5.4, 33.8),         # 턱 → 목
    (4.8, 36.0),         # 목
    (5.6, 37.6),
    (9.2, 38.6),         # 어깨선
    (11.8, 40.0),        # 어깨 끝
    (14.4, 44.6),        # 팔 바깥
    (16.0, 58.0),
    (16.6, 72.0),
    (16.2, 84.0),
    (15.5, 91.0),
    (14.6, 96.4),        # 손등
    (12.2, 98.8),        # 손끝
    (12.0, 101.0),       # 허벅지로 합류
    (11.3, 110.0),
    (10.2, 118.0),       # 무릎
    (9.2, 128.0),
    (7.4, 138.0),        # 발목
    (8.6, 144.0),
    (9.0, 147.6),
    (8.2, 149.4),        # 발바닥
    (4.4, 150.2),
    (0.0, 150.4),
]

SIL = sym(HALF)
SIL_D = smooth(SIL)

# 발판 + 받침에 꽂는 돌기. 본체와 한 덩어리로 오린다.
PLATE_D = (
    "M-14,151.4 C-14,149.2 -7.6,148.4 0,148.4 C7.6,148.4 14,149.2 14,151.4 "
    "L14,155.4 C14,157.8 11.6,158.2 9.2,158.2 L5.6,158.2 "
    "L5.6,163 C5.6,165 4.2,165.4 3,165.4 L-3,165.4 "
    "C-4.2,165.4 -5.6,165 -5.6,163 L-5.6,158.2 L-9.2,158.2 "
    "C-11.6,158.2 -14,157.8 -14,155.4 Z"
)

# 베이스 머리 — 뒤로 넘긴 긴 머리. 어떤 가발을 씌워도 덮이도록 머리
# 실루엣 안쪽에만 있고, 귀(y=20.5)는 드러난다.
BASE_HAIR = sym([
    (0.0, -0.8), (8.4, 0.0), (13.4, 4.0), (15.5, 11.6), (15.1, 18.4),
    (13.4, 14.8), (11.0, 10.6), (7.0, 8.8), (3.2, 9.6), (0.0, 10.6),
])


def _face():
    """얼굴 — 7살, 큰 눈. 눈·입술은 색칠판에서도 남아야 해서 c 를 뺀다."""
    a = []
    for s in (-1, 1):
        ex, ey = s * S.EYE_X, S.EYE_Y
        a += [
            # 눈썹 — 가늘고 높게. 굵으면 화난 얼굴이 된다.
            path(smooth([(ex - 2.6 * s, ey - 6.9), (ex - 0.1 * s, ey - 7.6),
                         (ex + 2.4 * s, ey - 7.0)], closed=False),
                 stroke="#b08d78", w=0.3),
            # 흰자 · 동공 · 하이라이트
            ell(ex, ey, 3.0, 3.6, fill="#fffdfb", c=False),
            ell(ex, ey + 0.3, 2.6, 3.15, fill=S.EYE, c=False),
            circ(ex - 0.9 * s, ey - 1.0, 0.98, fill="#ffffff", c=False),
            circ(ex + 1.0 * s, ey + 1.6, 0.44, fill="#ffffff", c=False, op=0.85),
            # 위 속눈썹
            path(smooth([(ex - 3.2 * s, ey - 2.0), (ex - 0.3 * s, ey - 3.7),
                         (ex + 3.0 * s, ey - 2.1)], closed=False),
                 stroke=S.INK, w=0.6),
            line(ex + 3.1 * s, ey - 2.2, ex + 4.4 * s, ey - 3.2, S.INK, 0.38),
            line(ex + 3.3 * s, ey - 0.8, ex + 4.7 * s, ey - 1.2, S.INK, 0.34),
            # 볼
            ell(s * 9.8, 25.2, 2.9, 1.8, fill=S.BLUSH, op=0.48),
            # 귀
            ell(s * S.EAR_X, S.EAR_Y, 1.85, 2.6, fill=S.SKIN, stroke=S.INK,
                w=0.28, c=False),
            path(smooth([(s * 14.0, 18.1), (s * 13.3, 19.8), (s * 13.9, 21.2)],
                        closed=False), stroke=S.INK2, w=0.26),
        ]
    a += [
        # 코 — 아주 작게
        path(smooth([(-0.65, 24.6), (0.0, 25.2), (0.65, 24.6)], closed=False),
             stroke="#cf9884", w=0.36),
        # 입
        path(smooth([(-2.3, 28.0), (0.0, 29.9), (2.3, 28.0)], closed=False),
             stroke=S.LIP, w=0.55),
        path(smooth([(-1.1, 29.0), (0.0, 29.5), (1.1, 29.0)], closed=False),
             stroke=S.LIP, w=0.34, op=0.55),
        # 턱 아래 · 목 음영
        path(smooth([(-4.3, 34.0), (0.0, 35.6), (4.3, 34.0)], closed=False),
             stroke=S.SKIN_SH, w=0.9, op=0.85),
    ]
    return a


def _hair_base():
    lo, dk, hi = S.HAIR["brown"]
    return [
        blob(BASE_HAIR, fill=lo, stroke=S.INK, w=0.32),
        path(smooth([(-10.6, 7.2), (-5.2, 3.4), (2.0, 2.2)], closed=False),
             stroke=hi, w=0.5, op=0.6),
        path(smooth([(-13.0, 11.0), (-7.0, 5.4), (1.6, 3.6)], closed=False),
             stroke=hi, w=0.36, op=0.45),
        path(smooth([(12.2, 8.6), (7.6, 4.2), (1.8, 2.6)], closed=False),
             stroke=dk, w=0.42, op=0.4),
    ]


def _underwear():
    """속옷 — 크림색 캐미솔 + 팬티. 그림은 실루엣에 클립되므로 넉넉히 그린다."""
    cami = sym([(0.0, 45.2), (4.6, 43.0), (7.8, 41.6), (9.2, 45.0),
                (9.8, 50.0), (10.1, 56.6), (5.2, 57.8), (0.0, 58.2)])
    # 팬티는 다리가 트인 모양 — 옆은 짧고 가운데가 내려온다
    pants = sym([(0.0, 75.6), (5.4, 76.2), (9.8, 78.2), (10.6, 81.6),
                 (7.0, 84.6), (3.0, 87.4), (0.0, 88.0)])
    a = [blob(cami, fill=S.C["cream"], stroke=S.INK, w=0.3),
         blob(pants, fill=S.C["cream"], stroke=S.INK, w=0.3)]
    for s in (-1, 1):
        a.append(line(s * 5.8, 42.6, s * 7.6, 38.8, S.INK, 0.3))
    # 레이스 — 작은 반원을 이어 붙인다
    r, x0, x1, y = 1.0, -9.6, 9.6, 57.2
    n = int((x1 - x0) / (r * 2))
    d = [f"M{f(x0)},{f(y)}"]
    for _ in range(n):
        d.append(f"a{f(r)},{f(r * 0.8)} 0 0 0 {f(r * 2)},0")
    a.append(path(" ".join(d), stroke=S.INK2, w=0.28))
    a += [
        path(smooth([(-1.9, 45.0), (0.0, 46.2), (1.9, 45.0), (0.0, 44.0)]),
             fill=S.C["rose3"], stroke=S.INK2, w=0.26, c=True),
        circ(0, 45.1, 0.5, fill=S.C["rose"], c=True),
        path(smooth([(-1.5, 77.6), (0.0, 78.5), (1.5, 77.6)], closed=False),
             stroke=S.INK2, w=0.26),
    ]
    return a


def _limbs():
    """팔·다리·몸통 잔선 — 오리는 선이 아니라 형태를 읽히게 하는 선."""
    a = []
    for s in (-1, 1):
        a += [
            # 몸통 옆선 (팔보다 안쪽에 있어 팔과 구분된다)
            path(smooth([(s * 11.0, 40.4), (s * 10.6, 47.0), (s * 10.4, 62.0),
                         (s * 11.9, 76.0), (s * 11.9, 86.0), (s * 11.8, 98.0)],
                        closed=False), stroke=S.INK2, w=0.28),
            # 팔 안쪽
            path(smooth([(s * 13.0, 44.4), (s * 13.4, 58.0), (s * 13.8, 72.0),
                         (s * 13.9, 85.0), (s * 13.6, 92.0)], closed=False),
                 stroke=S.INK, w=0.3),
            # 손목 · 손가락
            line(s * 13.5, 92.6, s * 16.1, 91.6, S.INK2, 0.3),
            path(smooth([(s * 14.1, 94.8), (s * 15.4, 95.6)], closed=False),
                 stroke=S.INK2, w=0.24),
            path(smooth([(s * 13.8, 96.6), (s * 15.1, 97.3)], closed=False),
                 stroke=S.INK2, w=0.24),
            # 다리 안쪽
            path(smooth([(s * 1.8, 87.6), (s * 3.4, 98.0), (s * 3.9, 112.0),
                         (s * 3.6, 126.0), (s * 3.2, 135.0), (s * 2.5, 143.0),
                         (s * 1.8, 149.8)], closed=False),
                 stroke=S.INK, w=0.3),
            # 무릎 · 발목
            path(smooth([(s * 5.0, 118.4), (s * 7.0, 119.4), (s * 9.2, 118.2)],
                        closed=False), stroke=S.INK2, w=0.24, op=0.75),
            path(smooth([(s * 3.3, 139.2), (s * 5.3, 140.0), (s * 7.3, 138.8)],
                        closed=False), stroke=S.INK2, w=0.26),
            # 어깨 음영
            path(smooth([(s * 8.6, 39.2), (s * 11.0, 41.2), (s * 12.0, 44.8)],
                        closed=False), stroke=S.SKIN_SH, w=0.85, op=0.8),
        ]
    return a


def _plate():
    """발판 — 발보다 먼저 그린다 (발이 앞에 서 있는 것으로 보이도록)."""
    return [
        path(PLATE_D, fill=S.C["cream2"], stroke=S.INK, w=0.32, c=True),
        path("M-13.6,151.4 C-13.6,149.5 -7.6,148.8 0,148.8 C7.6,148.8 13.6,149.5 "
             "13.6,151.4 C9,153 -9,153 -13.6,151.4 Z",
             fill="#fffaf0", c=True, op=0.95),
        path(smooth([(-13.6, 151.4), (-7.5, 152.9), (0.0, 153.2),
                     (7.5, 152.9), (13.6, 151.4)], closed=False),
             stroke=S.INK2, w=0.3),
        line(-5.6, 158.2, 5.6, 158.2, S.INK2, 0.28),
    ]


def body():
    """공주 본체 1조각 (앵커: 정수리)."""
    p = Piece("body", "공주", "body")
    p.cut(SIL_D, SIL)
    p.cut(PLATE_D, [(-14.0, S.STAND_PLATE_TOP), (14.0, S.BODY_BOTTOM)])
    p.art(*_plate())
    p.art(path(SIL_D, fill=S.SKIN, c=True),
          path(SIL_D, stroke=S.INK, w=0.36))
    p.art(*_hair_base(), *_underwear(), *_limbs(), *_face())
    return p


def base():
    """세우는 받침 — 타원에 칼집을 넣어 본체 꽂이를 끼운다."""
    p = Piece("base", "받침", "body")
    w, h = S.BASE_W, S.BASE_H
    p.cut_ell(0, 0, w / 2, h / 2)
    p.slit(0, 0.6, S.BASE_SLIT)
    p.art(
        ell(0, 0, w / 2, h / 2, fill=S.C["cream2"], stroke=S.INK, w=0.34),
        ell(0, -0.6, w / 2 - 2.2, h / 2 - 2.0, fill="#fffaf0", op=0.85),
        ell(0, -0.6, w / 2 - 2.2, h / 2 - 2.0, stroke=S.INK2, w=0.28, c=False),
    )
    return p
