#!/usr/bin/env python3
"""입혀 본 그림 — 파츠를 앵커대로 얹어서 한 명을 완성한다.

이게 이 세트의 **검증 장치**다. 드레스 어깨선이 본체 어깨선과 어긋나 있거나
신발이 발에서 떠 있으면 시트에서는 안 보이지만 여기서는 바로 드러난다.
`spec.ANCHOR` 를 그대로 쓰기 때문에, 그림이 맞으면 도면이 맞는 것이다.

겹치는 순서는 실제로 입히는 순서와 같다.

    본체 → 머리 → 드레스 → 망토 → 신발 → 목걸이 → 귀걸이 → 왕관 → 손소품
"""
from . import body as B
from . import hair as HR
from . import small as SM
from . import spec as S
from . import wear as W
from .svg import group

# 얹는 순서 (뒤로 갈수록 위에 온다)
ORDER = ["body", "hair", "dress", "cape", "shoe", "necklace", "earring",
         "crown", "prop"]


def _pick(items, name):
    if name is None:
        return None
    for it in items:
        if it.key == name or it.label == name:
            return it
    raise KeyError(f"그런 파츠가 없다: {name}")


def dressed(hair=None, dress=None, shoe=None, crown=None, earring=None,
            necklace=None, cape=None, prop=None, stand=True):
    """파츠 이름(key)을 받아 입혀 놓은 SVG 조각과 경계 상자를 돌려준다."""
    parts = {
        "body": B.body(),
        "hair": _pick(HR.hairs(), hair),
        "dress": _pick(W.dresses(), dress),
        "cape": _pick(W.capes(), cape),
        # 신발은 시트에서는 8.4mm 떨어져 인쇄되지만, 신길 때는 두 발 위치로 모은다
        "shoe": _pick(SM.shoes(pdx=S.FOOT_CX), shoe),
        "crown": _pick(SM.crowns(), crown),
        # 귀걸이는 머리카락 옆선에 걸리므로 귀보다 조금 바깥에 놓인다
        "earring": _pick(SM.earrings(edx=S.EAR_X + 3.0), earring),
        "necklace": _pick(SM.necklaces(), necklace),
        "prop": _pick(SM.props(), prop),
    }
    out = []
    for name in ORDER:
        pc = parts[name]
        if pc is None:
            continue
        ax, ay = S.ANCHOR[pc.anchor]
        out.append(group(pc.svg(worn=True), tx=ax, ty=ay))
    if stand:
        base = B.base()
        out.insert(0, group(base.svg(worn=True), tx=0.0,
                            ty=S.BODY_BOTTOM - S.BASE_H / 2 + 1.0))
    box = (-26.0, -18.0, 26.0, S.BODY_BOTTOM + 6.0)
    return "".join(out), box


def figure(picks, scale=1.0, gap=6.0):
    """여러 명을 나란히 세운 SVG 조각. picks 는 dressed() 인자 dict 목록."""
    out, x = [], 0.0
    for kw in picks:
        g, (x0, y0, x1, y1) = dressed(**kw)
        out.append(group(g, tx=x - x0 * scale, ty=-y0 * scale, sc=scale)
                   if scale != 1.0 else group(g, tx=x - x0, ty=-y0))
        x += (x1 - x0) * scale + gap
    h = (S.BODY_BOTTOM + 24.0) * scale
    return "".join(out), (x - gap, h)


# 안내 페이지·6번 시트에 쓰는 예시 네 명
SAMPLES = [
    dict(hair="hair1", dress="dress1", shoe="shoe2", crown="crown1",
         earring="ear1", necklace="neck1"),
    dict(hair="hair2", dress="dress3", shoe="shoe3", crown="crown2",
         earring="ear3", prop="prop3"),
    dict(hair="hair5", dress="dress4", shoe="shoe6", crown="crown3",
         earring="ear4", necklace="neck2", cape="cape1"),
    dict(hair="hair6", dress="dress5", shoe="shoe1", crown="crown5",
         earring="ear5", necklace="neck4", prop="prop2"),
]
