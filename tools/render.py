#!/usr/bin/env python3
"""시트 HTML 을 실제 인쇄 엔진(Chromium)으로 그려 보는 개발용 도구.

브라우저에서 Ctrl+P 로 뽑는 것과 같은 결과를 PDF·PNG 로 받는다.
그림을 고칠 때 눈으로 확인하고, 인쇄가 A4 한 장에 들어가는지도 여기서 본다.

    python3 tools/render.py sheets/sheet1.html            # PNG 미리보기
    python3 tools/render.py sheets/sheet1.html --pdf out.pdf
    python3 tools/render.py sheets/sheet1.html --line     # 색칠판으로
"""
import os
import pathlib
import sys

CHROME = os.environ.get("PAPERTOY_CHROME") or next(
    (p for p in ("/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                 "/usr/bin/chromium", "/usr/bin/google-chrome") if os.path.exists(p)),
    None)


def browser(pw):
    kw = dict(args=["--no-sandbox", "--font-render-hinting=none"])
    if CHROME:
        kw["executable_path"] = CHROME
    return pw.chromium.launch(**kw)


def shot(html, png=None, pdf=None, line=False, scale=2.2):
    from playwright.sync_api import sync_playwright
    url = pathlib.Path(html).resolve().as_uri()
    with sync_playwright() as pw:
        b = browser(pw)
        pg = b.new_page(viewport={"width": 900, "height": 1300},
                        device_scale_factor=scale)
        pg.goto(url)
        if line:
            pg.evaluate("document.body.classList.add('line')")
        pg.wait_for_timeout(250)
        if pdf:
            pg.emulate_media(media="print")
            pg.pdf(path=pdf, format="A4", print_background=True,
                   margin={k: "0mm" for k in ("top", "bottom", "left", "right")})
        if png or not pdf:
            el = pg.query_selector(".page") or pg.query_selector("svg") or pg.query_selector("body")
            el.screenshot(path=png or "preview.png")
        b.close()


def pages(html):
    """인쇄했을 때 몇 장이 되는지 — A4 한 장을 넘기면 시트 설계가 틀린 것이다."""
    import re
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as t:
        shot(html, pdf=t.name)
        raw = pathlib.Path(t.name).read_bytes()
    os.unlink(t.name)
    return len(re.findall(rb"/Type\s*/Page[^s]", raw))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    src = a[0]
    ln = "--line" in a
    if "--pdf" in a:
        out = a[a.index("--pdf") + 1]
        shot(src, pdf=out, line=ln)
    elif "--pages" in a:
        print(f"{src}: {pages(src)}장")
    else:
        out = pathlib.Path(src).with_suffix(".line.png" if ln else ".png").name
        out = str(pathlib.Path("/tmp") / out)
        shot(src, png=out, line=ln)
        print(out)
