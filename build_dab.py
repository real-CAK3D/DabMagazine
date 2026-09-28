#!/usr/bin/env python3
"""DAB MAGAZINE — the Garden's monthly humor magazine: every comic strip drawn that month (Ganja writes 1-2 a day; The Sunday
Smoke keeps them) bound into one issue behind a drawn cover starring Clydius, the Garden's goofy mascot.

Usage: build_dab.py [YYYY-MM] [--final]   (default: this month so far; --final also rings The Corner Chronicle's bell)
The cover is drawn once per issue with the Codex image model (gpt-image-2, the agents' ChatGPT login).
"""
import base64, datetime as dt, glob, importlib.util, io, json, os, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, ROOT)
import pubkit as pk   # noqa: E402
import flipbook as fb   # noqa: E402
from pubkit import e   # noqa: E402

fb.CSS_FILE = "dab.css"
REPO = "https://github.com/real-CAK3D/DabMagazine"
SMOKE = os.path.join(pk.GARDEN, "sunday-smoke")


def month_strips(m):
    out = []
    for f in sorted(glob.glob(os.path.join(SMOKE, "strips", m + "-*.json"))):
        day = os.path.basename(f)[:10]
        for s in (pk.load(f).get("funnies") or {}).get("strips") or []:
            img = str(s.get("image") or "")
            src = os.path.join(SMOKE, "site", img.replace("../", "")) if img else ""
            if src and os.path.exists(src):
                os.makedirs(os.path.join(SITE, "img", "strips"), exist_ok=True)
                dest = os.path.join(SITE, "img", "strips", os.path.basename(src))
                if not os.path.exists(dest):
                    shutil.copy2(src, dest)
                out.append((day, dict(s, image="../img/strips/" + os.path.basename(src))))
    return out


def draw_cover(m, titles):
    out = os.path.join(SITE, "img", "covers", m + ".jpg")
    if os.path.exists(out):
        return True
    os.makedirs(os.path.dirname(out), exist_ok=True)
    spec = importlib.util.spec_from_file_location("cx", os.path.join(pk.HERMES, "hermes-agent", "plugins", "image_gen", "openai-codex", "__init__.py"))
    sys.path.insert(0, os.path.join(pk.HERMES, "hermes-agent"))
    cx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cx)
    token = cx._read_codex_access_token()
    if not token:
        return False
    month = dt.date.fromisoformat(m + "-01").strftime("%B %Y").upper()
    prompt = ("A satirical humor-magazine cover in the style of classic 1960s-70s American humor magazines, painted illustration, busy and funny. "
              "The masthead at the top reads exactly 'DAB' in huge bold slanted red-and-white letters, with a small banner 'THE GARDEN'S HUMOR MAGAZINE' and '%s'. "
              "The cover star is CLYDIUS, a stocky muscular short-haired American pit bull terrier with a copper-brown coat, red nose and white chest, grinning goofily "
              "with his tongue out, wearing a tiny newspaper hat, sitting on a pile of tangled network cables and Raspberry Pi boards while a server rack smokes gently behind him. "
              "Small cover blurbs in hand lettering: 'THE CRON JOB THAT ATE MAINE', 'WHAT, ME REBOOT?', and '%s STRIPS INSIDE'. "
              "Clean and family-friendly, no real brands, no real people, no copyrighted characters." % (month, len(titles)))
    try:
        b64 = cx._collect_image_b64(token, prompt=prompt, size="1024x1536", quality="medium")
    except Exception:
        return False
    if not b64:
        return False
    from PIL import Image
    im = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
    im.thumbnail((1100, 1600))
    im.save(out, "JPEG", quality=85, optimize=True, progressive=True)
    return True


def build(m, final=False):
    pk.sync_portraits(SITE)
    strips = month_strips(m)
    d = dt.date.fromisoformat(m + "-01")
    no = (d.year - 2026) * 12 + d.month - 8
    has_cover = draw_cover(m, strips) if strips else False
    seal = '<a class="seal" href="/" aria-label="Back to The Corner Chronicle">%s</a>' % fb.SEAL
    cover = ('<div class="dab-cover">%s<div class="dab-ear">No. %d · %s · ONE PINCH</div></div>'
             % (('<img src="../img/covers/%s.jpg" alt="Dab Magazine cover, %s">' % (m, d.strftime("%B %Y"))) if has_cover else
                '<div class="dab-flag">DAB</div><div class="dab-sub">THE GARDEN\'S HUMOR MAGAZINE</div><div class="dab-blurb">WHAT, ME REBOOT?</div>',
                no, e(d.strftime("%B %Y").upper())))
    pages = [fb.page("Dab Magazine", cover, " hardcover dab-cov")]
    toc = "".join('<li><a data-goto="%d"><b>%s</b> <span>%s</span></a></li>' % (3 + i // 2, e(s.get("title")), e(pk.nice(day, "%a %b %-d"))) for i, (day, s) in enumerate(strips))
    pages.append(fb.page("Contents", '<div class="dab-toc"><h2>In This Issue</h2><p class="small">%d strips from %s — tap one to turn to it.</p><ol>%s</ol>'
                         '<p class="dab-note">DAB is written by the Garden\'s agents and drawn fresh every day. No cron jobs were harmed.</p></div>'
                         % (len(strips), e(d.strftime("%B")), toc or "<li>No strips yet this month.</li>")))
    for i in range(0, len(strips), 2):
        pair = strips[i:i + 2]
        pages.append(fb.page("Strips %d–%d" % (i + 1, i + len(pair)), "".join(
            '<div class="dab-strip"><div class="dab-day">%s</div>%s</div>' % (e(pk.nice(day, "%A, %B %-d")), fb.strips_block({"strips": [s]}).replace('<div class="fn-head">The Funnies</div>', ""))
            for day, s in pair), " comic-page"))
    pages.append(fb.page("Back Page", ('<div class="gum"><span>DAB · THE GARDEN\'S HUMOR MAGAZINE</span></div><div class="pb-body">%s<h2 class="pb-title">DAB</h2>'
                                       '<p class="dab-ad">✱ AMAZING OFFER! ✱<br>Send no money! Get NOTHING! Every Dab is free forever.</p>%s'
                                       '<p class="pb-code">%s · No. %d</p><p><a href="../archive.html">Back issues ›</a></p></div>')
                         % (seal, fb.back_codes(REPO, "DabMagazine"), e(d.strftime("%B %Y")), no), " hardcover back"))
    html = fb.book(pages, date=m + "-01", no=no, lists={}, paper="DAB", motto="The Garden's humor magazine", gum="DAB · WHAT, ME REBOOT?",
                   price="PRICE: ONE PINCH — CHEAP!", delivered="DRAWN DAILY, BOUND MONTHLY", flap="Dab Magazine · the Garden's humor magazine",
                   body_class="pub-dab", est="THE GARDEN'S HUMOR MAGAZINE")
    os.makedirs(os.path.join(SITE, "issues"), exist_ok=True)
    open(os.path.join(SITE, "issues", m + ".html"), "w").write(html)
    eds = pk.issues(SITE, pattern=r"\d{4}-\d{2}")
    open(os.path.join(SITE, "index.html"), "w").write(open(os.path.join(SITE, "issues", eds[0] + ".html")).read().replace('href="../', 'href="').replace('src="../', 'src="'))
    # the back-issue rack is a cover gallery: every painted cover, tap one to read that issue
    tiles = []
    for i, x in enumerate(eds):
        img = os.path.exists(os.path.join(SITE, "img", "covers", x + ".jpg"))
        tiles.append('<li class="dab-cv"><a href="issues/%s.html">%s<span><b>No. %d</b> · %s</span></a></li>'
                     % (x, ('<img src="img/covers/%s.jpg" alt="Dab Magazine cover, %s" loading="lazy">' % (x, pk.nice(x + "-01", "%B %Y"))) if img
                        else '<i class="dab-cv-blank">DAB</i>', len(eds) - i, pk.nice(x + "-01", "%B %Y")))
    pk.archive_page(SITE, os.path.join(ROOT, fb.CSS_FILE), "pub-dab dab-gallery", "Dab Magazine", "the cover gallery", "".join(tiles), "🤪")
    pk.latest(SITE, "Dab Magazine", m + "-01", "%s issue — %d strips" % (d.strftime("%B"), len(strips)), "issues/%s.html" % m, [x + "-01" for x in eds if x < m or final][:10],
              cover=("img/covers/%s.jpg" % m) if has_cover else "")
    if final:
        pk.notify("🤪 Dab Magazine No. %d is out" % no, "%d strips from %s, bound in one issue." % (len(strips), d.strftime("%B")), "/dab/")
    print("dab built:", m, len(strips), "strips", "cover" if has_cover else "no cover")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    build(args[0] if args else dt.date.today().strftime("%Y-%m"), "--final" in sys.argv)
