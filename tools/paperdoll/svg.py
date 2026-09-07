#!/usr/bin/env python3
"""파츠 하나를 SVG 로 뽑는 도구.

## 왜 3겹인가 — 오림선 만드는 법

종이인형 시트는 그림 바깥으로 3mm 쯤 흰 여백이 있고 그 여백 끝에 점선이 있다.
SVG 에는 "도형을 3mm 바깥으로 부풀리기"가 없어서 윤곽선 굵기로 흉내낸다.

    1층  같은 경로를 굵기 6.9mm 회색 **점선**으로 (선이 3.45mm 씩 양쪽으로 번진다)
    2층  같은 경로를 굵기 6.3mm 흰 **실선**으로 덮는다
    3층  그림 (윤곽선 안쪽으로 클립)

1층에서 안쪽으로 번진 회색은 2층이 전부 덮고, 바깥 0.3mm 만 남아 점선 테두리가 된다.
덤으로 이 방법은 **좁은 틈을 알아서 메운다** — 팔과 몸통 사이 2mm 틈은 양쪽 흰 선이
겹쳐 사라지므로, 아이가 겨드랑이를 V자로 파낼 필요가 없다. 파츠를 그릴 때
"틈은 6mm 미만으로" 를 규칙으로 삼는 이유다.

탭도 같은 처리를 받는다. 탭 사각형을 파츠 안쪽으로 FOLD_IN 만큼 밀어 넣으면
1·2층이 겹치면서 오림선이 한 줄로 이어진다 — 그래서 층을 파츠 단위로 묶어
`1층 전부 → 2층 전부 → 그림` 순서로 그린다.

## 밀착 오림선 (tight)

머리 파츠의 **얼굴 창**은 이 3겹을 쓸 수 없다. 얼굴 쪽으로도 3.4mm 가 번지기
때문에, 오린 종이가 이마와 볼을 그만큼 덮어 버린다. 그래서 얼굴 창만은
여백 없이 **선 위를 그대로 오리는** 얇은 점선(`tight`)으로 그린다.
바깥 윤곽은 여백이 있고 안쪽 창은 딱 맞는 것 — 실제 인쇄용 가발 도안이 쓰는 방식이다.

## 수채 느낌 내기 — 그라데이션 + 안쪽 번짐

레퍼런스는 수채/색연필 채색이다. 평면 단색으로 칠하면 아무리 형태가 맞아도
"벡터 클립아트"로 보인다. 벡터로 그 느낌에 다가가는 수단은 셋이다.

    1. **그라데이션** — 살·머리·천을 단색이 아니라 위아래 두 톤으로 채운다.
    2. **안쪽 번짐(rim)** — 도형 윤곽에 굵고 흐린 선을 얹고 도형 안쪽으로
       클립한다. 물감이 종이 가장자리에 고이는 효과가 그대로 난다.
       그림이 이미 실루엣에 클립돼 있으므로 굵은 선의 바깥 절반은 잘려
       나가고 안쪽 절반만 남는다.
    3. **흐린 음영 덩어리(soft)** — 접힌 천, 팔·다리 그늘.

2·3 은 `filter=SOFT` 로 흐리게 만든다. 인쇄는 Chromium 이 래스터로 굽기 때문에
그대로 나온다.

## 수채 원화(래스터)를 끼우는 자리

벡터로 낼 수 있는 한계는 "에어브러시로 칠한 벡터"다. 레퍼런스처럼 물감이
번지고 연필 결이 보이는 그림은 손으로 쓴 SVG 로는 나오지 않는다.
그래서 파츠마다 **그림만 PNG 로 갈아 끼울 수 있게** 해 두었다 —
`art/<파츠키>.png` 가 있으면 벡터 그림 대신 그 이미지를 실루엣에 클립해서 쓴다.
오림선·탭·앵커·배치·검사는 전부 그대로 동작한다.

규격은 `DESIGN.md` 의 「수채 원화로 갈아 끼우기」에 있다.

## 색칠판

색을 채우는 도형에는 `class="c"` 를 붙인다. 색칠판 CSS 가 `.c{fill:#fff}` 로
덮어써서 같은 SVG 가 흑백 선그림이 된다. 눈·입술처럼 색이 곧 표정인 것에는
붙이지 않는다.
"""
from . import spec as S


# ─────────────────────────────────────────────────────────────
# 숫자 · 경로
# ─────────────────────────────────────────────────────────────
def f(v):
    """SVG 에 넣을 숫자 — 소수점 둘째 자리, 꼬리 0 제거."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0", "-") else s


def _bez(p0, p1, p2, p3, t):
    c1 = (p1[0] + (p2[0] - p0[0]) / 6 * t, p1[1] + (p2[1] - p0[1]) / 6 * t)
    c2 = (p2[0] - (p3[0] - p1[0]) / 6 * t, p2[1] - (p3[1] - p1[1]) / 6 * t)
    return f"C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}"


def smooth(pts, t=1.0, closed=True):
    """점을 지나는 부드러운 곡선 (Catmull-Rom → 3차 베지에).

    실루엣을 좌표 몇 개로 잡으면 나머지는 곡선이 알아서 둥글려 준다.
    t 를 낮추면 각이 살고, 높이면 더 출렁인다.
    """
    if closed:
        m = len(pts)
        d = [f"M{f(pts[0][0])},{f(pts[0][1])}"]
        for i in range(m):
            d.append(_bez(pts[(i - 1) % m], pts[i], pts[(i + 1) % m],
                          pts[(i + 2) % m], t))
        d.append("Z")
        return " ".join(d)
    q = [pts[0]] + list(pts) + [pts[-1]]
    d = [f"M{f(pts[0][0])},{f(pts[0][1])}"]
    for i in range(1, len(q) - 2):
        d.append(_bez(q[i - 1], q[i], q[i + 1], q[i + 2], t))
    return " ".join(d)


def mirror(pts):
    """x 부호를 뒤집고 순서를 뒤집는다 — 좌우 대칭 실루엣의 왼쪽 절반."""
    return [(-x, y) for x, y in reversed(pts)]


def sym(right):
    """가운데 축에서 시작·끝나는 오른쪽 절반을 좌우 대칭 폐곡선으로 만든다."""
    return list(right) + mirror(right[1:-1])


def line(x1, y1, x2, y2, stroke=None, w=0.3, dash=None, cap="round"):
    st = stroke or S.INK
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M{f(x1)},{f(y1)} L{f(x2)},{f(y2)}" fill="none" '
            f'stroke="{st}" stroke-width="{f(w)}" stroke-linecap="{cap}"{d}/>')


SOFT = "pdSoft"      # 시트 <defs> 에 한 번 정의되는 흐림 필터
SOFT2 = "pdSoft2"    # 더 넓게 퍼지는 흐림


def defs_common():
    """시트마다 한 번 넣는 공용 defs (흐림 필터)."""
    return (f'<defs>'
            f'<filter id="{SOFT}" x="-30%" y="-30%" width="160%" height="160%">'
            f'<feGaussianBlur stdDeviation="0.55"/></filter>'
            f'<filter id="{SOFT2}" x="-40%" y="-40%" width="180%" height="180%">'
            f'<feGaussianBlur stdDeviation="1.5"/></filter>'
            f'</defs>')


def _stops(stops):
    out = []
    for t in stops:
        o, col = t[0], t[1]
        op = t[2] if len(t) > 2 else None
        so = f' stop-opacity="{f(op)}"' if op is not None else ""
        out.append(f'<stop offset="{f(o)}" stop-color="{col}"{so}/>')
    return "".join(out)


def lg(gid, stops, x1=0.0, y1=0.0, x2=0.0, y2=1.0):
    """선형 그라데이션 (기본 세로). stops = [(offset, color[, opacity]), ...]"""
    return (f'<linearGradient id="{gid}" x1="{f(x1)}" y1="{f(y1)}" '
            f'x2="{f(x2)}" y2="{f(y2)}">{_stops(stops)}</linearGradient>')


def rg(gid, stops, cx=0.5, cy=0.38, r=0.72):
    return (f'<radialGradient id="{gid}" cx="{f(cx)}" cy="{f(cy)}" '
            f'r="{f(r)}">{_stops(stops)}</radialGradient>')


def path(d, fill="none", stroke=None, w=0.3, c=False, dash=None, op=None,
         blur=None, wash=False):
    a = [f'd="{d}"', f'fill="{fill}"']
    if stroke:
        a.append(f'stroke="{stroke}" stroke-width="{f(w)}" '
                 f'stroke-linejoin="round" stroke-linecap="round"')
    if dash:
        a.append(f'stroke-dasharray="{dash}"')
    if op is not None:
        a.append(f'opacity="{f(op)}"')
    if blur:
        a.append(f'filter="url(#{blur})"')
    if wash:
        a.append('class="w"')   # 색칠판에서는 숨긴다 (음영·번짐)
    elif c:
        a.append('class="c"')
    return f'<path {" ".join(a)}/>'


def blob(pts, fill, stroke=None, w=0.3, t=1.0, c=True, op=None, blur=None):
    return path(smooth(pts, t), fill=fill, stroke=stroke, w=w, c=c, op=op,
                blur=blur)


def rim(d, color, w=2.6, op=0.5, blur=None):
    """안쪽 번짐 — 굵고 흐린 윤곽선. 그림이 실루엣에 클립되므로 안쪽만 남는다."""
    return path(d, stroke=color, w=w, op=op, blur=blur or SOFT, wash=True)


def soft(pts, fill, op=0.4, t=1.0, wide=False):
    """흐린 음영 덩어리 — 천 주름, 팔·다리 그늘."""
    return path(smooth(pts, t), fill=fill, op=op,
                blur=SOFT2 if wide else SOFT, wash=True)


def volume(p, d, top=0.30, bottom=0.17, side=0.15, tone="#8a6552"):
    """어떤 파츠에나 얹는 입체감 — 위는 밝게, 아래·오른쪽은 어둡게 + 번짐.

    파츠마다 음영을 손으로 그리지 않아도 천이 부풀어 보인다.
    색칠판에서는 class="w" 라서 전부 사라진다.
    """
    p.add_defs(
        lg(p.g("vv"), [(0.0, "#ffffff", top), (0.32, "#ffffff", 0.0),
                       (0.7, tone, 0.0), (1.0, tone, bottom)]),
        lg(p.g("vh"), [(0.0, "#ffffff", side * 0.7), (0.24, "#ffffff", 0.0),
                       (0.74, tone, 0.0), (1.0, tone, side)],
           x1=0.0, y1=0.0, x2=1.0, y2=0.0),
    )
    return [path(d, fill=f"url(#{p.g('vv')})", wash=True),
            path(d, fill=f"url(#{p.g('vh')})", wash=True),
            rim(d, tone, w=2.2, op=0.22)]


def ell(cx, cy, rx, ry, fill="none", stroke=None, w=0.3, c=True, rot=None, op=None):
    a = [f'cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}"', f'fill="{fill}"']
    if stroke:
        a.append(f'stroke="{stroke}" stroke-width="{f(w)}"')
    if rot:
        a.append(f'transform="rotate({f(rot)} {f(cx)} {f(cy)})"')
    if op is not None:
        a.append(f'opacity="{f(op)}"')
    if c:
        a.append('class="c"')
    return f'<ellipse {" ".join(a)}/>'


def circ(cx, cy, r, fill="none", stroke=None, w=0.3, c=True, op=None):
    return ell(cx, cy, r, r, fill, stroke, w, c, op=op)


def rrect(x, y, w, h, r, fill="none", stroke=None, sw=0.3, c=True):
    a = [f'x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" '
         f'rx="{f(r)}"', f'fill="{fill}"']
    if stroke:
        a.append(f'stroke="{stroke}" stroke-width="{f(sw)}"')
    if c:
        a.append('class="c"')
    return f'<rect {" ".join(a)}/>'


def group(body, tx=0.0, ty=0.0, sc=None, rot=None, op=None, cls=None):
    tr = []
    if tx or ty:
        tr.append(f"translate({f(tx)},{f(ty)})")
    if rot:
        tr.append(f"rotate({f(rot)})")
    if sc:
        tr.append(f"scale({f(sc)})")
    a = []
    if tr:
        a.append(f'transform="{" ".join(tr)}"')
    if op is not None:
        a.append(f'opacity="{f(op)}"')
    if cls:
        a.append(f'class="{cls}"')
    return f'<g {" ".join(a)}>{body}</g>' if a else f"<g>{body}</g>"


# ─────────────────────────────────────────────────────────────
# 파츠
# ─────────────────────────────────────────────────────────────
_uid = [0]


class Piece:
    """오려 쓰는 조각 하나.

    key     파일·검사용 이름
    label   시트에 인쇄할 한글 이름
    anchor  spec.ANCHOR 의 어느 앵커를 원점으로 그렸는가 (검사에 쓰인다)
    """

    def __init__(self, key, label, anchor, tags=(), halo=None):
        _uid[0] += 1
        self.uid = _uid[0]
        self.key = key
        self.label = label
        self.anchor = anchor
        self.tags = list(tags)
        self._defs = []
        # 작은 파츠는 여백을 좁힌다. 신발(폭 10mm)에 3.3mm 여백을 주면
        # 여백이 그림보다 커져서 형태가 뭉개진다.
        self.halo = S.HALO if halo is None else halo
        self._cut = []        # (d, clip?, fill?)
        self._tight = []      # 여백 없이 그 선을 오리는 얇은 점선
        self._clip = []       # 클립에만 넣는 경로 (오림선은 아니다)
        self._fold = []
        self._art = []
        self._slit = []
        self._pts = []        # 경계 상자 계산용
        self.tabs = []        # 검사용 탭 기록

    # ---- 오림선 -------------------------------------------------
    def cut(self, d, pts=(), clip=True, fill=True):
        """오림선 — 3.3mm 흰 여백 + 점선. fill=False 면 열린 경로(테두리만)."""
        self._cut.append((d, clip, fill))
        self._pts += list(pts)
        return self

    def cut_pts(self, pts, t=1.0, clip=True):
        return self.cut(smooth(pts, t), pts, clip)

    def tight(self, d, pts=()):
        """밀착 오림선 — 여백 없이 이 선을 그대로 오린다 (머리 얼굴 창)."""
        self._tight.append(d)
        self._pts += list(pts)
        return self

    def clip(self, d):
        """그림이 삐져나오지 않게 가둘 범위만 추가한다 (오림선에는 안 들어간다)."""
        self._clip.append(d)
        return self

    def cut_ell(self, cx, cy, rx, ry, clip=True):
        d = (f"M{f(cx - rx)},{f(cy)} a{f(rx)},{f(ry)} 0 1 0 {f(2 * rx)},0 "
             f"a{f(rx)},{f(ry)} 0 1 0 {f(-2 * rx)},0 Z")
        return self.cut(d, [(cx - rx, cy - ry), (cx + rx, cy + ry)], clip)

    # ---- 탭 -----------------------------------------------------
    def tab(self, cx, cy, w, h, dir="up", name=""):
        """접어 넘기는 탭. cx,cy 는 접는선의 가운데.

        파츠 안쪽으로 spec.FOLD_IN 만큼 파고들게 그려서 오림선이 이어지게 한다.
        """
        i, r = S.FOLD_IN, min(w, h) * 0.32
        if dir in ("up", "down"):
            s = -1 if dir == "up" else 1
            x0, y0 = cx - w / 2, cy - i * -s if False else cy - (i if s < 0 else h)
            # 위 방향: y = cy+i (안쪽) ~ cy-h (바깥)
            ya, yb = (cy + i, cy - h) if s < 0 else (cy - i, cy + h)
            d = (f"M{f(cx - w / 2)},{f(ya)} L{f(cx - w / 2)},{f(yb + s * -r)} "
                 f"Q{f(cx - w / 2)},{f(yb)} {f(cx - w / 2 + r)},{f(yb)} "
                 f"L{f(cx + w / 2 - r)},{f(yb)} "
                 f"Q{f(cx + w / 2)},{f(yb)} {f(cx + w / 2)},{f(yb + s * -r)} "
                 f"L{f(cx + w / 2)},{f(ya)} Z")
            pts = [(cx - w / 2, min(ya, yb)), (cx + w / 2, max(ya, yb))]
            fold = (cx - w / 2 + 0.4, cy, cx + w / 2 - 0.4, cy)
        else:
            s = 1 if dir == "right" else -1
            xa, xb = cx - s * i, cx + s * w
            d = (f"M{f(xa)},{f(cy - h / 2)} L{f(xb - s * r)},{f(cy - h / 2)} "
                 f"Q{f(xb)},{f(cy - h / 2)} {f(xb)},{f(cy - h / 2 + r)} "
                 f"L{f(xb)},{f(cy + h / 2 - r)} "
                 f"Q{f(xb)},{f(cy + h / 2)} {f(xb - s * r)},{f(cy + h / 2)} "
                 f"L{f(xa)},{f(cy + h / 2)} Z")
            pts = [(min(xa, xb), cy - h / 2), (max(xa, xb), cy + h / 2)]
            fold = (cx, cy - h / 2 + 0.4, cx, cy + h / 2 - 0.4)
        self._cut.append((d, False, True))
        self._pts += pts
        self._fold.append(fold)
        self.tabs.append(dict(name=name or dir, x=cx, y=cy, w=w, h=h, dir=dir))
        return self

    def fold(self, x1, y1, x2, y2):
        self._fold.append((x1, y1, x2, y2))
        return self

    def slit(self, cx, cy, length, horiz=False):
        """가위로 한 번 넣는 칼집 (받침대). 굵은 실선 + 양 끝 표시."""
        self._slit.append((cx, cy, length, horiz))
        if horiz:
            self._pts += [(cx - length / 2, cy), (cx + length / 2, cy)]
        else:
            self._pts += [(cx, cy - length / 2), (cx, cy + length / 2)]
        return self

    # ---- 그림 ---------------------------------------------------
    def art(self, *svg):
        self._art += [s for s in svg if s]
        return self

    def use_art(self, box=None, key=None):
        """`art/<키>.png` 가 있으면 그림을 그 이미지로 대체한다.

        box=(x0,y0,x1,y1) 는 파츠 로컬 좌표(mm)에서 이미지가 놓일 자리다.
        없으면 파츠 경계 상자(오림선 여백 제외)를 쓴다.
        돌려주는 값이 True 면 벡터 그림은 그리지 않는다.
        """
        import base64
        import pathlib as _p
        root = _p.Path(__file__).resolve().parent.parent.parent
        src = root / "art" / f"{key or self.key}.png"
        if not src.exists():
            return False
        if box is None:
            box = self.bbox(halo=False)
        x0, y0, x1, y1 = box
        b64 = base64.b64encode(src.read_bytes()).decode()
        self._art.append(
            f'<image x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" '
            f'height="{f(y1 - y0)}" preserveAspectRatio="none" '
            f'href="data:image/png;base64,{b64}"/>')
        return True

    def add_defs(self, *d):
        """그라데이션 정의. id 는 파츠 uid 로 유일하게 만든다 (self.g("skin"))."""
        self._defs += [x for x in d if x]
        return self

    def g(self, name):
        """이 파츠 전용 그라데이션 id."""
        return f"g{self.uid}{name}"

    # ---- 상자 ---------------------------------------------------
    def bbox(self, halo=True):
        xs = [p[0] for p in self._pts]
        ys = [p[1] for p in self._pts]
        m = (self.halo + 0.9) if halo else 0.9  # 곡선이 점 바깥으로 부푸는 여유
        return (min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m)

    def size(self, halo=True):
        x0, y0, x1, y1 = self.bbox(halo)
        return (x1 - x0, y1 - y0)

    # ---- 출력 ---------------------------------------------------
    def svg(self, worn=False):
        """worn=True 면 오림선·탭·접는선을 빼고 그림만 낸다 — 입혀 본 그림용."""
        cid = f"clip{self.uid}{'w' if worn else ''}"
        a = "".join(f'<path d="{d}"/>' for d, clip, _ in self._cut if clip)
        a += "".join(f'<path d="{d}"/>' for d in self._clip)
        lay1 = "".join(
            f'<path d="{d}" fill="{"#fff" if fl else "none"}" stroke="{S.CUT}" '
            f'stroke-width="{f(self.halo * 2 + 0.3)}" stroke-linejoin="round" '
            f'stroke-linecap="round" stroke-dasharray="2.1 1.5"/>'
            for d, _, fl in self._cut)
        lay2 = "".join(
            f'<path d="{d}" fill="{"#fff" if fl else "none"}" stroke="#fff" '
            f'stroke-width="{f(self.halo * 2 - 0.3)}" stroke-linejoin="round" '
            f'stroke-linecap="round"/>' for d, _, fl in self._cut)
        folds = "".join(line(*fl, stroke=S.FOLD, w=0.32, dash="1.2 1.0")
                        for fl in self._fold)
        slits = "".join(
            (line(cx - L / 2, cy, cx + L / 2, cy, stroke=S.INK, w=0.55, cap="butt")
             if hz else
             line(cx, cy - L / 2, cx, cy + L / 2, stroke=S.INK, w=0.55, cap="butt"))
            for cx, cy, L, hz in self._slit)
        dfs = f'<defs>{"".join(self._defs)}</defs>' if self._defs else ""
        if worn:
            return (f'<g class="pc" data-key="{self.key}">{dfs}'
                    f'<clipPath id="{cid}">{a}</clipPath>'
                    f'<g clip-path="url(#{cid})">{"".join(self._art)}</g></g>')
        tight = "".join(
            f'<path d="{d}" fill="none" stroke="{S.CUT}" stroke-width="0.34" '
            f'stroke-dasharray="1.6 1.1" stroke-linecap="round"/>'
            for d in self._tight)
        return (f'<g class="pc" data-key="{self.key}">{dfs}'
                f'<clipPath id="{cid}">{a}</clipPath>'
                f'{lay1}{lay2}'
                f'<g clip-path="url(#{cid})">{"".join(self._art)}</g>'
                f'{tight}{folds}{slits}</g>')
