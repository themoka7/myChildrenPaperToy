#!/usr/bin/env python3
"""시트 조립 — A4 한 장에 파츠를 앉히고, 앉힌 자리를 기록해 둔다.

기록해 두는 이유: 오림선끼리 붙었는지, 종이 밖으로 나갔는지를
`check_paperdoll.py` 가 사람 눈이 아니라 좌표로 검사하기 때문이다.
파츠를 하나 더 끼워 넣다가 조용히 겹치는 사고를 막는 장치다.
"""
from . import spec as S
from .svg import f, group, line, path, smooth


class Sheet:
    def __init__(self, num, title, sub, big=False):
        self.num = num
        self.title = title
        self.sub = sub
        self.big = big
        self.items = []      # (piece, x, y)
        self.extra = []      # 머리글·설명 등 시트 고정 요소

    # ---- 배치 ---------------------------------------------------
    def put(self, piece, x, y, label=None, label_dy=2.6):
        """파츠의 앵커를 (x,y) 에 놓는다. label=False 면 이름을 안 쓴다."""
        self.items.append((piece, x, y))
        if label is not False:
            x0, y0, x1, y1 = piece.bbox()
            txt = label if isinstance(label, str) else piece.label
            self.extra.append(self._text(x + (x0 + x1) / 2, y + y1 + label_dy,
                                         txt, 3.0, S.LABEL, weight=600))
        return piece

    def row(self, pieces, cy, x0=None, x1=None, labels=True):
        """가로로 균등 배치. 이름은 줄에서 가장 아래인 파츠에 맞춰 한 줄로 쓴다."""
        x0 = S.MARGIN if x0 is None else x0
        x1 = S.PAGE_W - S.MARGIN if x1 is None else x1
        n = len(pieces)
        cw = (x1 - x0) / n
        base = max(pc.bbox()[3] for pc in pieces) + cy
        for i, pc in enumerate(pieces):
            bx0, _, bx1, by1 = pc.bbox()
            cx = x0 + cw * (i + 0.5)
            self.put(pc, cx - (bx0 + bx1) / 2, cy,
                     label=None if labels else False,
                     label_dy=base - (cy + by1) + 2.8)
        return cw

    # ---- 글자 ---------------------------------------------------
    @staticmethod
    def _text(x, y, s, size, fill, weight=400, anchor="middle", family=None,
              spacing=None, op=None):
        fam = family or "'Malgun Gothic','Apple SD Gothic Neo','Noto Sans KR',sans-serif"
        a = [f'x="{f(x)}" y="{f(y)}"', f'font-size="{f(size)}"',
             f'fill="{fill}"', f'font-weight="{weight}"',
             f'text-anchor="{anchor}"', f'font-family="{fam}"']
        if spacing:
            a.append(f'letter-spacing="{f(spacing)}"')
        if op is not None:
            a.append(f'opacity="{f(op)}"')
        return f'<text {" ".join(a)}>{s}</text>'

    def text(self, *a, **k):
        self.extra.append(self._text(*a, **k))

    # ---- 머리글 -------------------------------------------------
    def header(self):
        cx = S.PAGE_W / 2
        if self.big:
            g = [
                self._text(cx, S.MARGIN + 12.5, "Princess", 11.5, S.C["rose2"],
                           weight=700, family="Georgia,'Times New Roman',serif",
                           spacing=0.6),
                self._text(cx, S.MARGIN + 22.5, "Dress-Up", 11.5, S.C["mint2"],
                           weight=700, family="Georgia,'Times New Roman',serif",
                           spacing=0.6),
                self._text(cx, S.MARGIN + 30.5, "공주 옷입히기 · 1. 공주", 3.6,
                           S.LABEL, weight=700, spacing=0.4),
            ]
            # 좌우 장식
            for s in (-1, 1):
                bx = cx + s * 40
                g.append(path(smooth([(bx, S.MARGIN + 15), (bx + s * 7, S.MARGIN + 11),
                                      (bx + s * 14, S.MARGIN + 16)], closed=False),
                              stroke=S.C["sage"], w=0.6))
                g.append(f'<circle cx="{f(bx + s * 16.5)}" cy="{f(S.MARGIN + 14)}" '
                         f'r="1.5" fill="{S.C["rose"]}" class="c"/>')
            return "".join(g)
        y = S.MARGIN + 6.2
        return "".join([
            self._text(S.MARGIN + 1, y, f"{S.SET_TITLE} · {self.num}. {self.title}",
                       4.4, S.C["rose2"], weight=700, anchor="start"),
            self._text(S.PAGE_W - S.MARGIN - 1, y, self.sub, 3.1, S.LABEL,
                       anchor="end"),
            line(S.MARGIN, S.MARGIN + 9.4, S.PAGE_W - S.MARGIN, S.MARGIN + 9.4,
                 S.C["rose3"], 0.8),
        ])

    def footer(self, msg):
        self.extra.append(self._text(
            S.PAGE_W / 2, S.PAGE_H - S.MARGIN - 1.4, msg, 3.0, S.LABEL))

    # ---- 출력 ---------------------------------------------------
    def svg(self):
        body = [self.header()]
        for pc, x, y in self.items:
            body.append(group(pc.svg(), tx=x, ty=y))
        body += self.extra
        return (f'<svg class="sheet" xmlns="http://www.w3.org/2000/svg" '
                f'width="{f(S.PAGE_W)}mm" height="{f(S.PAGE_H)}mm" '
                f'viewBox="0 0 {f(S.PAGE_W)} {f(S.PAGE_H)}">'
                f'{"".join(body)}</svg>')

    def boxes(self):
        """(이름, x0,y0,x1,y1) — 오림선까지 포함한 실제 종이 자리."""
        out = []
        for pc, x, y in self.items:
            bx0, by0, bx1, by1 = pc.bbox()
            out.append((pc.key, bx0 + x, by0 + y, bx1 + x, by1 + y))
        return out
