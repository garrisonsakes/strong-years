"""Shared typesetting for the Strong Years paid products.

Pipeline: Markdown source (hand-written or generated from Python data) -> HTML (python-markdown)
-> PDF (WeasyPrint). Brand rules: jade / cream / ink / persimmon palette, Fraunces headings,
Atkinson Hyperlegible body (Braille Institute face for low-vision readers), body 15pt, nothing
below 12pt, NO gray text anywhere, no slash decorations, no mono kickers.
"""
import os, re, subprocess, markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

HERE = os.path.dirname(os.path.abspath(__file__))
PRODUCTS = os.path.dirname(HERE)
FONTS = os.path.join(HERE, "fonts")

INK = "#16120E"
PAPER = "#FBF6EC"   # cream
JADE = "#1F5A46"
PERSIMMON = "#B3311C"
RICE = "#FFFFFF"
BRASS = "#E7B85A"   # highlight bars only, never text

BASE_CSS = f"""
@font-face {{ font-family: 'Atkinson'; src: url('file://{FONTS}/Atkinson-Regular.ttf'); font-weight: 400; font-style: normal; }}
@font-face {{ font-family: 'Atkinson'; src: url('file://{FONTS}/Atkinson-Bold.ttf'); font-weight: 700; font-style: normal; }}
@font-face {{ font-family: 'Atkinson'; src: url('file://{FONTS}/Atkinson-Italic.ttf'); font-weight: 400; font-style: italic; }}
@font-face {{ font-family: 'Atkinson'; src: url('file://{FONTS}/Atkinson-BoldItalic.ttf'); font-weight: 700; font-style: italic; }}
@font-face {{ font-family: 'Fraunces'; src: url('file://{FONTS}/Fraunces-SemiBold.ttf'); font-weight: 600; }}
@font-face {{ font-family: 'Fraunces'; src: url('file://{FONTS}/Fraunces-Bold.ttf'); font-weight: 700; }}

@page {{
  size: Letter;
  margin: 0.7in 0.75in 0.85in 0.75in;
  background: {PAPER};
  @bottom-left {{ content: string(prodname); font-family: 'Atkinson'; font-size: 12pt; color: {INK}; }}
  @bottom-right {{ content: "Page " counter(page) " of " counter(pages); font-family: 'Atkinson'; font-size: 12pt; color: {INK}; }}
}}
@page cover {{ margin: 0; background: {JADE}; @bottom-left {{ content: none; }} @bottom-right {{ content: none; }} }}
@page wide {{ size: Letter landscape; margin: 0.55in 0.6in 0.7in 0.6in; }}

html {{ color: {INK}; }}
body {{ font-family: 'Atkinson'; font-size: 15pt; line-height: 1.5; color: {INK}; }}
.prodname {{ string-set: prodname content(); height: 0; overflow: hidden; margin: 0; font-size: 1pt; color: {PAPER}; }}

h1, h2, h3, h4 {{ font-family: 'Fraunces'; font-weight: 600; color: {INK}; line-height: 1.2; }}
h1 {{ font-size: 30pt; color: {JADE}; margin: 0 0 14pt 0; page-break-before: always; }}
h1.nobreak {{ page-break-before: avoid; }}
h2 {{ font-size: 21pt; margin: 22pt 0 8pt 0; color: {JADE}; page-break-after: avoid; }}
h3 {{ font-size: 17pt; margin: 16pt 0 6pt 0; page-break-after: avoid; }}
h4 {{ font-size: 15pt; margin: 12pt 0 4pt 0; page-break-after: avoid; font-family: 'Atkinson'; font-weight: 700; }}
p {{ margin: 0 0 9pt 0; orphans: 3; widows: 3; }}
strong {{ font-weight: 700; }}
a {{ color: {INK}; text-decoration: underline; }}
ul, ol {{ margin: 0 0 10pt 0; padding-left: 22pt; }}
li {{ margin-bottom: 4pt; }}
hr {{ border: none; border-top: 2pt solid {JADE}; margin: 16pt 0; }}

table {{ width: 100%; border-collapse: collapse; margin: 6pt 0 14pt 0; font-size: 14pt; page-break-inside: auto; }}
thead {{ display: table-header-group; }}
tr {{ page-break-inside: avoid; }}
th {{ background: {JADE}; color: {RICE}; font-weight: 700; text-align: left; padding: 6pt 7pt; border: 1.2pt solid {JADE}; vertical-align: bottom; }}
td {{ padding: 6pt 7pt; border: 1.2pt solid {INK}; vertical-align: top; background: {RICE}; }}
table.small {{ font-size: 13pt; }}
table.small th, table.small td {{ padding: 4pt 5pt; }}
table.write td {{ height: 30pt; }}

.box {{ border-radius: 8pt; padding: 10pt 14pt; margin: 10pt 0 12pt 0; page-break-inside: avoid; background: {RICE}; border: 1.5pt solid {INK}; }}
.box p:last-child, .box ul:last-child, .box ol:last-child {{ margin-bottom: 0; }}
.stop {{ border: 2.5pt solid {PERSIMMON}; border-left-width: 10pt; }}
.stop .label, .easier .label, .harder .label, .note .label, .safety .label {{ font-weight: 700; }}
.easier {{ border: 2pt solid {JADE}; border-left-width: 10pt; }}
.harder {{ border: 2pt solid {INK}; border-left-width: 10pt; }}
.note {{ border: 1.5pt solid {INK}; border-left: 10pt solid {BRASS}; }}
.chang, .sun {{ background: {RICE}; border: 1.5pt solid {JADE}; border-radius: 8pt; padding: 10pt 14pt; margin: 10pt 0 12pt 0; page-break-inside: avoid; }}
.sun {{ border-color: {PERSIMMON}; }}
.who {{ font-family: 'Fraunces'; font-weight: 700; font-size: 15pt; margin-bottom: 3pt; }}
.chang .who {{ color: {JADE}; }}
.sun .who {{ color: {PERSIMMON}; }}
.big {{ font-family: 'Fraunces'; font-size: 22pt; color: {PERSIMMON}; font-weight: 700; }}
.dose {{ font-size: 16pt; font-weight: 700; color: {PERSIMMON}; margin: 2pt 0 8pt 0; }}
.hl {{ background: {BRASS}; padding: 0 3pt; }}
.pb {{ page-break-before: always; }}
.keep {{ page-break-inside: avoid; }}
.center {{ text-align: center; }}
.fine {{ font-size: 13pt; }}
.src {{ font-size: 12pt; word-wrap: break-word; overflow-wrap: anywhere; }}
.exercise {{ border-top: 2pt solid {JADE}; padding-top: 6pt; margin-top: 14pt; }}
.dose {{ page-break-after: avoid; }}
.eh {{ width: 100%; border-collapse: separate; border-spacing: 0; margin: 8pt 0 8pt 0; page-break-inside: avoid; font-size: 15pt; }}
.eh td {{ width: 50%; background: {RICE}; padding: 8pt 11pt; vertical-align: top; border-radius: 8pt; }}
.eh td.e {{ border: 2pt solid {JADE}; border-left-width: 9pt; }}
.eh td.gap {{ width: 8pt; padding: 0; border: none; background: transparent; }}
.eh td.h {{ border: 2pt solid {INK}; border-left-width: 9pt; }}
.eh p {{ margin: 0; }}
.exercise h3 {{ margin-top: 2pt; }}
a.pref {{ text-decoration: none; font-weight: 700; }}
a.pref::after {{ content: " (full instructions on page " target-counter(attr(href), page) ")"; }}
.compact {{ page-break-inside: avoid; border-top: 2pt solid {JADE}; padding-top: 6pt; margin-top: 12pt; }}
.compact h3 {{ margin-top: 2pt; }}
.twocol {{ columns: 2; column-gap: 22pt; }}
.check {{ font-size: 18pt; }}
.blank {{ display: inline-block; border-bottom: 1.5pt solid {INK}; width: 2.2in; height: 1em; }}
.blank.s {{ width: 0.8in; }}

/* cover */
.cover {{ page: cover; height: 11in; width: 8.5in; background: {JADE}; color: {PAPER}; position: relative; }}
.cover .inner {{ padding: 1.1in 0.9in 0 0.9in; }}
.cover .kicker {{ font-family: 'Atkinson'; font-size: 17pt; font-weight: 700; color: {PAPER}; margin-bottom: 14pt; }}
.cover .title {{ font-family: 'Fraunces'; font-weight: 700; font-size: 50pt; line-height: 1.05; color: {PAPER}; margin: 0 0 18pt 0; }}
.cover .sub {{ font-size: 19pt; line-height: 1.4; color: {PAPER}; margin-bottom: 26pt; }}
.cover .bar {{ height: 10pt; width: 2.2in; background: {PERSIMMON}; margin: 0 0 26pt 0; }}
.cover .who2 {{ font-size: 16pt; color: {PAPER}; }}
.cover .disc {{ position: absolute; bottom: 0.8in; left: 0.9in; right: 0.9in; font-size: 13pt; color: {PAPER}; border-top: 1.5pt solid {PAPER}; padding-top: 10pt; }}
.cover.wide {{ page: widecover; width: 11in; height: 8.5in; }}
@page widecover {{ size: Letter landscape; margin: 0; background: {JADE}; @bottom-left {{ content: none; }} @bottom-right {{ content: none; }} }}

.wide {{ page: wide; }}
"""

MD_EXT = ["tables", "md_in_html", "attr_list", "sane_lists", "footnotes"]


def md_to_html(md_text):
    return markdown.markdown(md_text, extensions=MD_EXT, output_format="html5")


def cover_html(kicker, title, sub, who, disclosure, wide=False):
    cls = "cover wide" if wide else "cover"
    return f"""<section class="{cls}"><div class="inner">
<div class="kicker">{kicker}</div>
<div class="title">{title}</div>
<div class="bar"></div>
<div class="sub">{sub}</div>
<div class="who2">{who}</div>
</div>
<div class="disc">{disclosure}</div></section>"""


DISCLOSURE = ("Chang Yin and Sun Yoon are AI characters created by a team of people. Their life story is fiction. "
              "The exercises and recipes are built on published research for older adults (sources in the back). "
              "This is education, not medical advice. Check with your doctor before starting new exercise.")


def render(md_text, out_pdf, prodname, cover=None, extra_css="", out_md=None, md_header=None):
    """Write the Markdown source (if out_md) and render the PDF."""
    if out_md:
        with open(out_md, "w") as f:
            if md_header:
                f.write(md_header.rstrip() + "\n\n")
            f.write(md_text)
    body = md_to_html(md_text)
    # first h1 after cover should not force a blank page
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{prodname}</title></head>
<body>{cover or ''}<div class="prodname">{prodname}</div>{body}</body></html>"""
    fc = FontConfiguration()
    HTML(string=html, base_url=HERE).write_pdf(
        out_pdf, stylesheets=[CSS(string=BASE_CSS + extra_css, font_config=fc)], font_config=fc)
    return out_pdf


def page_count(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", out)
    return int(m.group(1)) if m else -1


def snap(pdf, pages, outdir, res=60):
    os.makedirs(outdir, exist_ok=True)
    outs = []
    for p in pages:
        base = os.path.join(outdir, f"{os.path.basename(pdf)[:-4]}_p{p}")
        subprocess.run(["pdftoppm", "-png", "-r", str(res), "-f", str(p), "-l", str(p), "-singlefile", pdf, base])
        outs.append(base + ".png")
    return outs


def box(kind, label, text):
    """Inline HTML callout usable inside Markdown (md_in_html)."""
    return f'<div class="box {kind}" markdown="1">\n<span class="label">{label}</span> {text}\n</div>\n'


def say(who, text):
    cls = "chang" if who.lower().startswith("chang") else "sun"
    name = "Chang Yin" if cls == "chang" else "Sun Yoon"
    return f'<div class="{cls}" markdown="1">\n<div class="who">{name}</div>\n\n{text}\n</div>\n'
