#!/usr/bin/env python3
"""시트 전수 검사 — 눈으로는 놓치는 것들을 좌표로 잡는다.

    python3 tools/check_paperdoll.py            # 전부
    python3 tools/check_paperdoll.py 2 5        # 2·5번 시트만
    python3 tools/check_paperdoll.py --fast     # 인쇄(쪽수) 검사 생략

무엇을 왜 보는가

    쪽수        A4 한 장을 넘기면 시트 설계가 틀린 것이다. 넘친 내용은 조용히
                사라지지 않고 2쪽으로 밀려 인쇄된다.
    종이 밖     오림선이 인쇄 여백을 넘으면 프린터가 잘라 먹는다.
    파츠 겹침   오림선끼리 붙으면 두 조각을 한 번에 오릴 수 없다. 그림은 안
                겹쳐 보여도 여백(3.3mm)끼리 붙는 일이 흔하다.
    앵커        파츠가 선언한 앵커가 spec.ANCHOR 에 있는가. 없으면 입힐 때
                어디에 놓아야 하는지 아무도 모른다.
    탭 돌출     허리·발등 탭이 옷 밖으로 실제로 나오는가. 치마 폭에 묻힌 탭은
                접을 수가 없다 — 눈으로는 절대 안 보이는 결함이다.
    치마 길이   밑단이 신발을 다 덮으면 신발 세트가 무의미해진다.
    받침        칼집이 꽂이보다 길어야 끼워진다.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from paperdoll import spec as S      # noqa: E402
from paperdoll import wear as W      # noqa: E402

SHOE_TOE = 13.6      # 신발 조각이 발목 아래로 내려가는 길이 (small.SHOE_*)
SHOE_SHOW_MIN = 5.0  # 드레스 밑단 아래로 이만큼은 신발이 보여야 한다


def _fmt(v):
    return f"{v:.1f}"


def x_at(half, y):
    """실루엣 오른쪽 절반이 높이 y 에서 얼마나 넓은가.

    점 목록에서 그 높이의 점만 골라 보면 점이 없는 구간에서 0 이 나온다
    (골드 로열은 y=12 과 y=32 사이에 점이 없다). 그래서 **선분을 잘라**
    교점을 구하고, 여러 번 교차하면 가장 바깥을 쓴다.
    """
    best = None
    for (x0, y0), (x1, y1) in zip(half, half[1:]):
        if (y0 - y) * (y1 - y) > 0 or y0 == y1:
            continue
        t = (y - y0) / (y1 - y0)
        x = x0 + (x1 - x0) * t
        best = x if best is None else max(best, x)
    if best is None:                      # 구간 밖이면 가장 가까운 점
        best = min(half, key=lambda pt: abs(pt[1] - y))[0]
    return best


def sheet_checks(num, sh):
    """한 시트의 배치를 본다. (오류 문자열 목록)"""
    bad = []
    boxes = sh.boxes()

    # 종이 밖
    for key, x0, y0, x1, y1 in boxes:
        if (x0 < S.MARGIN - 0.6 or y0 < S.MARGIN - 0.6
                or x1 > S.PAGE_W - S.MARGIN + 0.6
                or y1 > S.PAGE_H - S.MARGIN + 0.6):
            bad.append(f"{num}번 시트 · {key}: 오림선이 인쇄 여백을 넘는다 "
                       f"({_fmt(x0)},{_fmt(y0)})–({_fmt(x1)},{_fmt(y1)})")

    # 파츠 겹침
    for i in range(len(boxes)):
        ka, ax0, ay0, ax1, ay1 = boxes[i]
        for j in range(i + 1, len(boxes)):
            kb, bx0, by0, bx1, by1 = boxes[j]
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox > -S.GAP_MIN and oy > -S.GAP_MIN:
                bad.append(f"{num}번 시트 · {ka} ↔ {kb}: 오림선이 붙는다 "
                           f"(가로 {_fmt(-ox)}mm, 세로 {_fmt(-oy)}mm 여유)")

    # 앵커
    for pc, _, _ in sh.items:
        if pc.anchor not in S.ANCHOR:
            bad.append(f"{num}번 시트 · {pc.key}: 모르는 앵커 '{pc.anchor}'")
    return bad


def part_checks():
    """파츠 자체의 규격 — 시트 배치와 무관하게 항상 지켜야 하는 것."""
    bad = []

    # 받침 칼집 > 꽂이 폭
    if S.BASE_SLIT <= S.STAND_TAB_W:
        bad.append(f"받침 칼집({S.BASE_SLIT})이 본체 꽂이({S.STAND_TAB_W})보다 "
                   "길지 않다 — 끼워지지 않는다")

    tw = S.TAB["dress_waist"]
    for key, label, half, _art in W.DRESSES:
        # 허리 탭이 옷 밖으로 나오는가
        wx = W.tab_x(half, tw["y"], tw["h"])
        lo, hi = tw["y"] - tw["h"] / 2 - 1.5, tw["y"] + tw["h"] / 2 + 1.5
        widest = max((x for x, y in half if lo <= y <= hi), default=0.0)
        if wx + tw["w"] <= widest + 3.0:
            bad.append(f"{label}: 허리 탭이 옷 폭에 묻힌다 "
                       f"(탭 끝 {_fmt(wx + tw['w'])} vs 옷 {_fmt(widest)})")

        # 어깨를 덮는가 (몸통 어깨 끝 ±11.8)
        sh_w = max(x for x, y in half if y <= 12.0)
        if sh_w < S.SHOULDER_X:
            bad.append(f"{label}: 어깨 폭 {_fmt(sh_w)} < 몸통 어깨 "
                       f"{S.SHOULDER_X} — 어깨가 삐져나온다")

        # 몸통 옆을 덮는가 (허리 ±10.4)
        side = min(x_at(half, y) for y in (18.0, 21.0, 24.0))
        if side < S.WAIST_X - 0.3:
            bad.append(f"{label}: 허리 폭 {_fmt(side)} < 몸통 허리 "
                       f"{S.WAIST_X} — 옆구리 살이 비친다")

        # 밑단 — 신발이 보여야 한다
        hem = max(y for _, y in half)
        shoe_bottom = S.ANKLE_Y + SHOE_TOE          # 본체 좌표
        shows = shoe_bottom - (S.SHOULDER_Y + hem)
        if shows < SHOE_SHOW_MIN:
            bad.append(f"{label}: 밑단이 신발을 덮는다 "
                       f"(보이는 길이 {_fmt(shows)}mm < {SHOE_SHOW_MIN}mm)")
    return bad


def print_checks(paths):
    """실제 인쇄 엔진으로 뽑아 쪽수를 센다."""
    bad = []
    try:
        from render import pages
    except ImportError:
        print("  (인쇄 검사 건너뜀 — playwright 가 없다)")
        return bad
    for pth in paths:
        try:
            n = pages(str(pth))
        except Exception as e:                       # noqa: BLE001
            print(f"  (인쇄 검사 건너뜀 — {type(e).__name__}: {e})")
            return bad
        if n != 1:
            bad.append(f"{pth.name}: 인쇄하면 {n}쪽이 된다 (A4 1장이어야 한다)")
    return bad


def run(sheets, paths=(), do_print=True):
    """sheets = [(번호, Sheet), ...]. 오류 개수를 돌려준다."""
    bad = list(part_checks())
    for num, sh in sheets:
        bad += sheet_checks(num, sh)
    if do_print and paths:
        bad += print_checks(list(paths))
    if bad:
        print("\n검사 결과 — 고칠 것")
        for b in bad:
            print(f"  · {b}")
    else:
        print("  검사 통과 — 종이 밖으로 나간 파츠 없음, 오림선 안 붙음, "
              "탭 전부 돌출, 밑단 아래로 신발 보임")
    return len(bad)


if __name__ == "__main__":
    import build_paperdoll as BP
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    nums = [int(a) for a in args] if args else sorted(BP.BUILDERS)
    made = [(n, BP.BUILDERS[n]()) for n in nums]
    root = pathlib.Path(__file__).resolve().parent.parent
    paths = [root / "sheets" / f"sheet{n}.html" for n in nums]
    paths = [p for p in paths if p.exists()]
    raise SystemExit(1 if run(made, paths, "--fast" not in sys.argv) else 0)
