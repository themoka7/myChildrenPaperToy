#!/usr/bin/env python3
"""공주 옷입히기 세트 — 시트 6장과 안내 페이지를 만든다.

    python3 tools/build_paperdoll.py            # 전부 다시 생성
    python3 tools/build_paperdoll.py 2 3        # 2·3번 시트만
    python3 tools/build_paperdoll.py --no-check # 인쇄 검사 건너뛰기 (빠르다)

`sheets/*.html` 과 `index.html` 은 **전부 생성물**이다. 직접 고치지 말 것 —
다시 빌드하면 덮어쓴다. 고칠 곳은 `tools/paperdoll/` 안이다.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from paperdoll import body as B          # noqa: E402
from paperdoll import compose as CP      # noqa: E402
from paperdoll import hair as HR         # noqa: E402
from paperdoll import small as SM        # noqa: E402
from paperdoll import spec as S          # noqa: E402
from paperdoll import wear as W          # noqa: E402
from paperdoll.sheets import Sheet       # noqa: E402
from paperdoll.svg import group          # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────
# HTML 껍데기
# ─────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
  @page {{ size: A4 portrait; margin: 0; }}
  *{{ box-sizing:border-box; }}
  html,body{{ margin:0; padding:0; }}
  body{{
    font-family:"Malgun Gothic","Apple SD Gothic Neo","Noto Sans KR",sans-serif;
    background:#efe7e2; color:#4b3f3a;
    -webkit-print-color-adjust:exact; print-color-adjust:exact;
  }}
  .bar{{
    position:sticky; top:0; z-index:9; display:flex; gap:14px; align-items:center;
    background:#5c4b45; color:#fff; padding:10px 16px; font-size:14px;
  }}
  .bar b{{ font-size:15px; }}
  .bar .sp{{ flex:1; }}
  .bar a{{ color:#ffd9b0; text-decoration:none; font-weight:700; }}
  .bar button{{
    font:inherit; font-weight:700; cursor:pointer; border:0; border-radius:8px;
    padding:8px 15px; background:#f4aebb; color:#4b3f3a;
  }}
  .bar label{{ display:flex; gap:6px; align-items:center; cursor:pointer; }}
  .page{{
    width:210mm; height:297mm; margin:16px auto; background:#fff;
    box-shadow:0 2px 14px rgba(0,0,0,.18); overflow:hidden;
  }}
  svg.sheet{{ display:block; }}
  /* 색칠판 — 색을 채우는 도형만 비운다. 눈·입술은 그대로 남는다. */
  body.line .c{{ fill:#fff !important; }}
  body.line .sheet text{{ fill:#9b9b9b !important; }}
  @media print{{
    .bar{{ display:none; }}
    body{{ background:#fff; }}
    .page{{ margin:0; box-shadow:none; }}
  }}
</style>
</head>
<body>
<div class="bar">
  <b>{title}</b>
  <label><input type="checkbox" id="ln"> 색칠판 (색 없이)</label>
  <span class="sp"></span>
  <a href="../index.html">← 세트 안내</a>
  <button onclick="print()">인쇄</button>
</div>
<div class="page">{svg}</div>
<script>
  ln.onchange = e => document.body.classList.toggle('line', e.target.checked);
</script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────
# 시트 1 — 공주 본체 4명 + 받침 4개
# ─────────────────────────────────────────────────────────────
def sheet1():
    sh = Sheet(1, "공주", "본체 4명 + 받침 4개", big=True)
    for i in range(4):
        cx = S.MARGIN + 194 / 4 * (i + 0.5)
        sh.put(B.body(), cx, 50.0, label=False)
    sh.row([B.base() for _ in range(4)], 243.0, labels=False)
    sh.text(S.PAGE_W / 2, 268.0,
            "받침 가운데 굵은 선은 가위로 칼집만 넣고, 공주 발밑 꽂이를 끼워 세운다.",
            3.2, S.LABEL)
    sh.footer("입히는 순서 ─ 공주 → 머리 → 드레스 → 신발 → 왕관 · 귀걸이 · 목걸이")
    return sh


# ─────────────────────────────────────────────────────────────
# 시트 2 — 드레스 6벌
# ─────────────────────────────────────────────────────────────
def sheet2():
    sh = Sheet(2, "드레스", "6벌 · 어깨 탭 2 + 허리 탭 2")
    ds = W.dresses()
    for r in range(2):
        sh.row(ds[r * 3:r * 3 + 3], 34.0 + r * 128.0)
    sh.footer("어깨 탭은 어깨 위로, 허리 탭은 옆구리를 감싸 뒤로 접는다.")
    return sh


# ─────────────────────────────────────────────────────────────
# 시트 3 — 머리 6가지
# ─────────────────────────────────────────────────────────────
def sheet3():
    sh = Sheet(3, "머리", "6가지 · 정수리 탭 2")
    hs = HR.hairs()
    for r in range(2):
        sh.row(hs[r * 3:r * 3 + 3], 40.0 + r * 118.0)
    sh.text(S.PAGE_W / 2, 272.0,
            "얼굴 창(가운데 얇은 점선)은 여백 없이 선 위를 그대로 오린다 — 어른이 오려 주세요.",
            3.2, S.LABEL)
    sh.footer("정수리 탭 2개를 공주 머리 뒤로 넘겨 접으면 고정된다.")
    return sh


# ─────────────────────────────────────────────────────────────
# 시트 4 — 왕관·머리띠 5 + 귀걸이 6쌍 + 목걸이 4
# ─────────────────────────────────────────────────────────────
def sheet4():
    sh = Sheet(4, "왕관 · 귀걸이 · 목걸이", "왕관·머리띠 5 + 귀걸이 6쌍 + 목걸이 4")
    sh.text(S.MARGIN + 1, 28.0, "왕관 · 머리띠 — 정수리에 걸치고 관자놀이 탭을 뒤로 접는다",
            3.5, S.C["rose2"], weight=700, anchor="start")
    cr = SM.crowns()
    sh.row(cr[:3], 50.0)
    sh.row(cr[3:], 96.0, x0=42.0, x1=168.0)
    sh.text(S.MARGIN + 1, 132.0, "귀걸이 — 머리카락 옆선을 물려 끼운다 (조각 가운데가 접는선)",
            3.5, S.C["rose2"], weight=700, anchor="start")
    ea = SM.earrings()
    sh.row(ea[:3], 152.0)
    sh.row(ea[3:], 188.0)
    sh.text(S.MARGIN + 1, 216.0, "목걸이 — 목 옆 탭 2개를 뒤로 접는다",
            3.5, S.C["rose2"], weight=700, anchor="start")
    sh.row(SM.necklaces(), 240.0)
    sh.footer("전부 작은 조각이다 — 어른이 오려서 세트별로 지퍼백에 담아 두면 잃어버리지 않는다.")
    return sh


# ─────────────────────────────────────────────────────────────
# 시트 5 — 신발 6켤레 + 가방 4 + 손소품 4
# ─────────────────────────────────────────────────────────────
def sheet5():
    sh = Sheet(5, "신발 · 가방 · 소품", "신발 6켤레 + 가방 4 + 손소품 4")
    sh.text(S.MARGIN + 1, 28.0, "신발 — 좌·우 두 조각이 한 켤레. 발등 탭을 발목 뒤로 접는다",
            3.5, S.C["rose2"], weight=700, anchor="start")
    ss = SM.shoes()
    sh.row(ss[:3], 44.0)
    sh.row(ss[3:], 96.0)
    sh.text(S.MARGIN + 1, 138.0, "가방 — 손잡이 위 탭을 손목에 걸어 뒤로 접는다",
            3.5, S.C["rose2"], weight=700, anchor="start")
    sh.row(SM.bags(), 160.0)
    sh.text(S.MARGIN + 1, 200.0, "손소품 — 손목이나 치마 옆선에 접어 끼운다",
            3.5, S.C["rose2"], weight=700, anchor="start")
    sh.row(SM.props(), 226.0)
    sh.footer("드레스 밑단은 발목 위로 끊어 두었다 — 어떤 드레스를 입어도 신발이 보인다.")
    return sh


# ─────────────────────────────────────────────────────────────
# 시트 6 — 망토 3벌 + 입혀 본 예시
# ─────────────────────────────────────────────────────────────
def sheet6():
    sh = Sheet(6, "망토", "망토 3벌 · 어깨 탭 2")
    sh.row(W.capes(), 34.0)
    sh.text(S.MARGIN + 1, 168.0, "이렇게 입힙니다",
            4.2, S.C["rose2"], weight=700, anchor="start")
    sh.text(S.MARGIN + 1, 174.6,
            "공주 → 머리 → 드레스 → 망토 → 신발 → 목걸이 → 귀걸이 → 왕관 → 손소품",
            3.1, S.LABEL, anchor="start")
    g, (fw, fh) = CP.figure(CP.SAMPLES, scale=0.44, gap=5.0)
    sh.extra.append(group(g, tx=(S.PAGE_W - fw) / 2, ty=182.0))
    sh.footer("망토는 드레스를 입힌 다음 어깨 탭을 넘겨 덧입힌다.")
    return sh


BUILDERS = {1: sheet1, 2: sheet2, 3: sheet3, 4: sheet4, 5: sheet5, 6: sheet6}


# ─────────────────────────────────────────────────────────────
# 안내 페이지
# ─────────────────────────────────────────────────────────────
def index_html(sheets):
    g, (fw, fh) = CP.figure(CP.SAMPLES, scale=1.0, gap=8.0)
    preview = (f'<svg class="preview" xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {fw:.1f} {fh:.1f}" width="100%">{g}</svg>')
    cards = []
    for n, title, sub in S.SHEETS:
        cards.append(f"""
    <a class="card" href="sheets/sheet{n}.html">
      <span class="n">{n}</span>
      <span class="t">{title}</span>
      <span class="s">{sub}</span>
    </a>""")
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{S.SET_TITLE} · 종이인형 세트</title>
<style>
  *{{box-sizing:border-box}} html,body{{margin:0}}
  body{{
    font-family:"Malgun Gothic","Apple SD Gothic Neo","Noto Sans KR",sans-serif;
    background:#f6efe9; color:#4b3f3a; line-height:1.65;
  }}
  .wrap{{max-width:880px; margin:0 auto; padding:28px 20px 60px}}
  h1{{
    font-family:Georgia,serif; font-size:34px; margin:.2em 0 0;
    color:#e5879b; letter-spacing:.5px;
  }}
  h1 small{{display:block; font-size:15px; color:#8a7a72; font-family:inherit;
    font-weight:600; letter-spacing:0; margin-top:6px}}
  h2{{font-size:17px; margin:34px 0 10px; color:#82bdb2;
     border-bottom:2px solid #d5ece7; padding-bottom:6px}}
  .grid{{display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
        gap:12px; margin-top:16px}}
  .card{{
    display:block; text-decoration:none; color:inherit; background:#fff;
    border:1px solid #ecdfd8; border-radius:14px; padding:14px 16px;
    box-shadow:0 1px 4px rgba(120,90,80,.07);
  }}
  .card:hover{{border-color:#f4aebb; box-shadow:0 3px 12px rgba(180,120,130,.16)}}
  .card .n{{
    display:inline-grid; place-items:center; width:24px; height:24px;
    border-radius:50%; background:#f4aebb; color:#fff; font-weight:700;
    font-size:13px; margin-right:8px;
  }}
  .card .t{{font-weight:700; font-size:16px}}
  .card .s{{display:block; font-size:13px; color:#8a7a72; margin-top:4px}}
  ol,ul{{padding-left:22px}} li{{margin:5px 0}}
  code{{background:#efe4dd; padding:1px 5px; border-radius:4px; font-size:13px}}
  .tip{{background:#fff; border-left:5px solid #a9d7ce; border-radius:0 10px 10px 0;
       padding:12px 16px; margin:14px 0}}
  table{{border-collapse:collapse; width:100%; font-size:14px; background:#fff;
        border-radius:10px; overflow:hidden}}
  th,td{{padding:8px 10px; border-bottom:1px solid #f0e6e0; text-align:left}}
  th{{background:#faf3ee; font-size:13px; color:#8a7a72}}
  .hero{{background:#fff; border:1px solid #ecdfd8; border-radius:16px;
        padding:18px 18px 10px; margin-top:18px}}
  .hero .cap{{font-size:13px; color:#8a7a72; margin:6px 0 4px; text-align:center}}
  svg.preview{{display:block; max-width:640px; margin:0 auto}}
</style>
</head>
<body>
<div class="wrap">
  <h1>공주 옷입히기<small>인쇄해서 오리는 종이인형 세트 · A4 {len(sheets)}장</small></h1>

  <div class="hero">{preview}
    <p class="cap">머리 6 × 드레스 6 × 신발 6 × 왕관 5 × 귀걸이 6 × 목걸이 4
       = <b>25,920가지</b>로 갈아입힐 수 있다. 위 그림은 그중 네 가지.</p>
  </div>

  <h2>시트</h2>
  <div class="grid">{"".join(cards)}</div>

  <h2>인쇄</h2>
  <div class="tip">
    시트를 열고 <b>인쇄</b> → 배율 <b>100%</b> → <b>배경 그래픽 켜기</b>.
    두꺼운 종이(160g 이상)에 뽑으면 훨씬 잘 선다. 얇은 종이면 인쇄한 뒤
    두꺼운 종이에 붙여서 오린다.
    위쪽 <b>색칠판</b>을 켜면 색이 빠진 선그림으로 나와서 아이가 직접 색칠할 수 있다.
  </div>

  <h2>만드는 순서</h2>
  <ol>
    <li><b>1번 시트</b>를 뽑아 공주 4명과 받침 4개를 오린다.</li>
    <li>받침 가운데 <b>굵은 선에만 칼집</b>을 넣는다 (오리는 게 아니라 한 번 자르기).</li>
    <li>공주 발밑 <b>꽂이를 칼집에 끼우면</b> 혼자 선다.</li>
    <li>나머지 시트에서 원하는 옷을 오리고, <b>점선 옆 탭을 뒤로 접어</b> 걸친다.</li>
  </ol>

  <h2>입히는 순서</h2>
  <p>공주 → 머리 → 드레스 → 신발 → 왕관·귀걸이·목걸이 → (망토·소품)</p>

  <h2>탭이 붙는 자리</h2>
  <table>
    <tr><th>파츠</th><th>탭</th><th>어디에</th></tr>
    <tr><td>드레스 · 망토</td><td>어깨 2 + 허리 2</td><td>어깨 위로, 옆구리 감싸 뒤로</td></tr>
    <tr><td>머리</td><td>정수리 2</td><td>머리 뒤로 넘겨 접는다</td></tr>
    <tr><td>신발</td><td>발등 1 (좌·우 각각)</td><td>발목을 감싸 뒤로</td></tr>
    <tr><td>왕관 · 머리띠</td><td>없음 (아치)</td><td>정수리에 걸친다</td></tr>
    <tr><td>귀걸이</td><td>고리 1 (좌·우 각각)</td><td>머리카락 옆선에 끼운다</td></tr>
    <tr><td>목걸이</td><td>목 옆 2</td><td>목을 감싸 뒤로</td></tr>
    <tr><td>손소품</td><td>손목 1</td><td>손목을 감싸 뒤로</td></tr>
  </table>

  <h2>선 읽는 법</h2>
  <ul>
    <li><b>회색 점선</b> — 가위로 오리는 선</li>
    <li><b>파란 짧은 점선</b> — 뒤로 접는 선 (오리지 않는다)</li>
    <li><b>굵은 검은 선</b> — 칼집 (받침 가운데. 한 번만 자른다)</li>
  </ul>

  <h2>도면</h2>
  <p>치수·부착 방식·파츠 목록은 <a href="DESIGN.md">DESIGN.md</a> 에 있다.
     시트는 전부 생성물이라 <code>python3 tools/build_paperdoll.py</code> 로 다시 만든다.</p>
</div>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────
def build(nums, check=True):
    (ROOT / "sheets").mkdir(exist_ok=True)
    made = []
    for n in nums:
        sh = BUILDERS[n]()
        title = f"{S.SET_TITLE} · {n}. {sh.title}"
        out = ROOT / "sheets" / f"sheet{n}.html"
        out.write_text(HTML.format(title=title, svg=sh.svg()), encoding="utf-8")
        made.append((n, sh, out))
        print(f"  {out.relative_to(ROOT)}  ({len(sh.items)}조각)")
    (ROOT / "index.html").write_text(index_html(S.SHEETS), encoding="utf-8")
    print("  index.html")

    if check:
        import check_paperdoll as CK
        bad = CK.run([(n, sh) for n, sh, _ in made],
                     [p for _, _, p in made])
        if bad:
            raise SystemExit(f"\n검사 실패 {bad}건 — 위 내용을 고친 뒤 다시 빌드한다.")
    return made


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    nums = [int(a) for a in args] if args else sorted(BUILDERS)
    print(f"{S.SET_TITLE} 시트 생성 — {nums}")
    build(nums, check="--no-check" not in sys.argv)
    print("완료")
