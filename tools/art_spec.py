#!/usr/bin/env python3
"""수채 원화(PNG)를 그릴 때 필요한 규격표를 뽑는다.

    python3 tools/art_spec.py            # 표를 화면에 출력
    python3 tools/art_spec.py --md       # art/SPEC.md 로 저장
    python3 tools/art_spec.py --guide    # art/guide/<키>.png — 실루엣 안내선 그림

`art/<파츠키>.png` 를 놓으면 빌더가 벡터 그림 대신 그 이미지를 파츠 실루엣에
클립해서 쓴다 (`Piece.use_art`). 오림선·탭·앵커·배치·검사는 그대로 동작한다.

규격
    · 이미지는 아래 표의 **파츠 상자(mm)** 를 정확히 채운다. 그 상자가
      파츠 로컬 좌표라서, 어긋나면 옷이 몸에서 밀린다.
    · 600dpi 기준 픽셀 크기를 함께 적어 둔다. 300dpi 로 그리면 절반.
    · 배경은 투명(알파). 실루엣 밖은 어차피 잘리지만, 알파가 없으면
      오림선 여백이 색으로 덮인다.
    · 오림선·탭·접는선은 **그리지 않는다.** 빌더가 얹는다.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from paperdoll import body as B          # noqa: E402
from paperdoll import hair as HR         # noqa: E402
from paperdoll import small as SM        # noqa: E402
from paperdoll import spec as S          # noqa: E402
from paperdoll import wear as W          # noqa: E402
from paperdoll.svg import defs_common, group  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
DPI = 600


def all_parts():
    out = [(B.body(), "본체"), (B.base(), "받침")]
    out += [(p, "머리") for p in HR.hairs()]
    out += [(p, "드레스") for p in W.dresses()]
    out += [(p, "망토") for p in W.capes()]
    out += [(p, "신발(한 켤레)") for p in SM.shoes()]
    out += [(p, "왕관·머리띠") for p in SM.crowns()]
    out += [(p, "귀걸이(한 쌍)") for p in SM.earrings()]
    out += [(p, "목걸이") for p in SM.necklaces()]
    out += [(p, "가방") for p in SM.bags()]
    out += [(p, "손소품") for p in SM.props()]
    return out


def rows():
    for p, kind in all_parts():
        x0, y0, x1, y1 = p.bbox(halo=False)
        w, h = x1 - x0, y1 - y0
        yield dict(key=p.key, label=p.label, kind=kind, anchor=p.anchor,
                   x0=x0, y0=y0, w=w, h=h,
                   px=round(w / 25.4 * DPI), py=round(h / 25.4 * DPI))


def table():
    lines = [f"{'파츠':22} {'이름':16} {'상자 mm':>18}  {'600dpi px':>13}  앵커",
             "-" * 88]
    for r in rows():
        lines.append(
            f"{r['key']:22} {r['label']:16} "
            f"{r['w']:6.1f} × {r['h']:6.1f}  {r['px']:5d} × {r['py']:5d}  "
            f"{r['anchor']}")
    return "\n".join(lines)


def md():
    out = ["# 수채 원화 규격", "",
           f"`art/<파츠키>.png` 를 놓으면 그 파츠의 그림이 이미지로 바뀐다.",
           "오림선·탭·앵커·배치·검사는 그대로 동작한다.", "",
           "- 이미지는 **파츠 상자**를 정확히 채운다 (가로세로 비율 고정 안 함).",
           "- 배경은 투명(알파). 오림선·탭·접는선은 그리지 않는다.",
           f"- px 는 {DPI}dpi 기준. 300dpi 면 절반.", "",
           "| 파츠 키 | 이름 | 종류 | 상자 (mm) | 600dpi (px) | 앵커 |",
           "|---|---|---|---|---|---|"]
    for r in rows():
        out.append(f"| `{r['key']}` | {r['label']} | {r['kind']} | "
                   f"{r['w']:.1f} × {r['h']:.1f} | {r['px']} × {r['py']} | "
                   f"{r['anchor']} |")
    out += ["", "## 파츠 로컬 좌표", "",
            "각 상자의 왼쪽 위 모서리는 파츠 로컬 좌표에서 아래 위치다.", "",
            "| 파츠 키 | 상자 왼쪽위 (x, y) |", "|---|---|"]
    for r in rows():
        out.append(f"| `{r['key']}` | ({r['x0']:.1f}, {r['y0']:.1f}) |")
    out += ["", "앵커가 본체 좌표의 어디에 놓이는지는 `DESIGN.md` 2장에 있다."]
    return "\n".join(out) + "\n"


def guides():
    """실루엣만 그린 안내 그림 — 이 위에 채색하면 상자가 자동으로 맞는다."""
    out = ROOT / "art" / "guide"
    out.mkdir(parents=True, exist_ok=True)
    from render import shot
    tmp = ROOT / "art" / "guide" / "_tmp.html"
    made = []
    for p, _ in all_parts():
        x0, y0, x1, y1 = p.bbox(halo=False)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'width="{(x1 - x0) * 8}" height="{(y1 - y0) * 8}" '
               f'viewBox="{x0} {y0} {x1 - x0} {y1 - y0}">{defs_common()}'
               f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" '
               f'height="{y1 - y0}" fill="#fff"/>{group(p.svg(worn=True))}</svg>')
        tmp.write_text(f'<body style="margin:0;width:max-content">{svg}</body>',
                       encoding="utf-8")
        shot(str(tmp), png=str(out / f"{p.key}.png"), scale=1.0)
        made.append(p.key)
    tmp.unlink(missing_ok=True)
    return made


if __name__ == "__main__":
    if "--md" in sys.argv:
        (ROOT / "art").mkdir(exist_ok=True)
        (ROOT / "art" / "SPEC.md").write_text(md(), encoding="utf-8")
        print("art/SPEC.md")
    elif "--guide" in sys.argv:
        print(f"art/guide/ — {len(guides())}장")
    else:
        print(table())
