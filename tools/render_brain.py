#!/usr/bin/env python3
"""Render wiki/ as browsable HTML under output/brain/ using Magna brand shell.

Called by .github/workflows/pages.yml during the build step so Mehr can
view the full brain at:
    https://mehrpatni9-lgtm.github.io/magna-brain/brain/

Each wiki file becomes an HTML page. Wikilinks are rewritten to anchor
links to the rendered pages. Frontmatter is parsed and shown as a meta
strip above the body. Output index at output/brain/index.html groups every
file by its wiki folder.
"""

import os
import re
import html
import shutil
from pathlib import Path
from typing import Optional

try:
    import markdown
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "markdown"])
    import markdown

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
RAW = ROOT / "raw"
OUT = ROOT / "output" / "brain"

SECTIONS = [
    ("entities", "Entities", "Who and what — the brand, founder, programs, audience."),
    ("concepts", "Concepts", "Content series, the five Compass pillars, recurring themes."),
    ("synthesis", "Synthesis angles", "Cross-cutting angles — pre-built POVs write-post reaches for first."),
    ("sources", "Sources", "Raw source documents the brain was seeded from."),
    ("voice/exemplars", "Voice exemplars", "Hand-picked posts across the six tone voices."),
    ("voice", "Voice styleguide", "The master tone document."),
    ("_index", "Indexes", "Master index and topic summaries."),
]

BASE_HREF = "/magna-brain"

BRAND_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — MAGNA brain</title>
  <link href="https://fonts.googleapis.com/css2?family=Forum&family=Raleway:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap" rel="stylesheet">
  <style>
    :root {{
      --charcoal: #2D2D2D;
      --creme: #E8DFC8;
      --creme-60: rgba(232,223,200,0.6);
      --creme-08: rgba(232,223,200,0.06);
      --creme-20: rgba(232,223,200,0.12);
      --soil: #5C3518;
      --taupe: #483C32;
      --taupe-border: rgba(72,60,50,0.8);
      --font-display: 'Forum', Georgia, serif;
      --font-body: 'Raleway', system-ui, -apple-system, sans-serif;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{ background: var(--charcoal); color: var(--creme); font-family: var(--font-body); font-size: 15px; line-height: 1.7; min-height: 100vh; }}
    .nav {{ padding: 20px 28px; border-bottom: 1px solid var(--taupe-border); display: flex; align-items: center; gap: 18px; background: #242424; position: sticky; top: 0; z-index: 10; flex-wrap: wrap; }}
    .nav-mark {{ font-family: var(--font-display); font-size: 15px; letter-spacing: 0.22em; color: var(--creme); text-decoration: none; }}
    .nav-tag {{ font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--creme-60); padding-left: 16px; border-left: 1px solid var(--taupe-border); }}
    .nav-links {{ margin-left: auto; display: flex; gap: 22px; }}
    .nav-links a {{ font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--creme-60); text-decoration: none; }}
    .nav-links a:hover {{ color: var(--creme); }}
    .nav-links a.active {{ color: var(--creme); border-bottom: 2px solid var(--soil); padding-bottom: 4px; }}
    main {{ max-width: 820px; margin: 0 auto; padding: 56px 28px 96px; }}
    .crumb {{ font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--creme-60); margin-bottom: 22px; }}
    .crumb a {{ color: var(--creme-60); text-decoration: none; }}
    .crumb a:hover {{ color: var(--creme); }}
    h1 {{ font-family: var(--font-display); font-size: clamp(30px, 5vw, 48px); font-weight: 400; line-height: 1.12; margin-bottom: 18px; color: var(--creme); }}
    h2 {{ font-family: var(--font-display); font-size: 22px; font-weight: 400; margin-top: 36px; margin-bottom: 14px; color: var(--creme); }}
    h3 {{ font-family: var(--font-display); font-size: 17px; font-weight: 400; margin-top: 28px; margin-bottom: 10px; color: var(--creme); }}
    p, ul, ol {{ margin-bottom: 16px; color: var(--creme); font-weight: 300; }}
    ul, ol {{ padding-left: 24px; }}
    li {{ margin-bottom: 6px; }}
    a {{ color: #c0927a; text-decoration: none; border-bottom: 1px solid rgba(192,146,122,0.3); }}
    a:hover {{ color: var(--creme); border-bottom-color: var(--creme); }}
    code {{ background: var(--creme-20); padding: 2px 6px; border-radius: 2px; font-family: ui-monospace, Menlo, monospace; font-size: 13px; color: var(--creme); }}
    blockquote {{ border-left: 3px solid var(--soil); padding-left: 18px; margin: 18px 0; font-style: italic; color: var(--creme-60); }}
    em {{ font-style: italic; color: #a07860; }}
    strong {{ font-weight: 500; color: var(--creme); }}
    table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13px; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--taupe-border); }}
    th {{ font-family: var(--font-display); font-weight: 400; color: var(--creme); }}
    td {{ color: var(--creme-60); font-weight: 300; }}
    hr {{ border: none; border-top: 1px solid var(--taupe-border); margin: 28px 0; }}
    .meta {{ display: flex; gap: 14px; font-size: 10px; text-transform: uppercase; letter-spacing: 0.14em; color: var(--creme-60); margin-bottom: 22px; flex-wrap: wrap; padding-bottom: 18px; border-bottom: 1px solid var(--taupe-border); }}
    .meta-item {{ padding-right: 14px; border-right: 1px solid var(--taupe-border); }}
    .meta-item:last-child {{ border-right: none; }}
    .section-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 2px; margin-bottom: 32px; }}
    .section-card {{ background: var(--creme-08); border: 1px solid var(--taupe-border); padding: 22px; text-decoration: none; color: inherit; border-bottom: 1px solid var(--taupe-border); transition: background 0.2s; }}
    .section-card:hover {{ background: var(--creme-20); }}
    .section-card h4 {{ font-family: var(--font-display); font-size: 16px; font-weight: 400; color: var(--creme); margin-bottom: 8px; }}
    .section-card p {{ font-size: 12px; color: var(--creme-60); margin: 0; font-weight: 300; line-height: 1.55; }}
    .section-header {{ display: flex; align-items: baseline; gap: 14px; margin: 44px 0 18px; }}
    .section-header h2 {{ margin: 0; }}
    .section-header-sub {{ font-size: 11px; color: var(--creme-60); font-style: italic; }}
  </style>
</head>
<body>
  <nav class="nav">
    <a class="nav-mark" href="{base}/">MAGNA</a>
    <span class="nav-tag">the brain · {section_tag}</span>
    <div class="nav-links">
      <a href="{base}/">drafts</a>
      <a href="{base}/brain/" class="active">brain</a>
    </div>
  </nav>
  <main>
    {crumb}
    {body}
  </main>
</body>
</html>
"""


def parse_frontmatter(text: str):
    """Return (frontmatter_dict, body_text). Simple parser — no YAML lib."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_block = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    fm = {}
    for line in fm_block.splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, body


def find_wiki_target(slug: str) -> Optional[str]:
    """Given a [[slug]], find the relative path of the rendered HTML."""
    # Try each section folder
    candidates = [
        ("entities", slug),
        ("concepts", slug),
        ("sources", slug),
        ("synthesis", slug),
        ("voice/exemplars", slug),
        ("voice", slug),
        ("_index", slug),
    ]
    # Also handle [[voice/styleguide]], [[voice/exemplars/foo]], etc.
    if "/" in slug:
        parts = slug.split("/", 1)
        candidates.insert(0, (parts[0], parts[1]))
        candidates.insert(0, ("", slug))

    for folder, name in candidates:
        p = WIKI / folder / f"{name}.md" if folder else WIKI / f"{name}.md"
        if p.exists():
            rel = p.relative_to(WIKI).with_suffix(".html")
            return f"{BASE_HREF}/brain/{rel}"
    return None


WIKILINK_RE = re.compile(r"\[\[([^\]|]+?)(?:\|([^\]]+))?\]\]")


def rewrite_wikilinks(md_text: str) -> str:
    def sub(m):
        slug = m.group(1).strip()
        label = (m.group(2) or slug).strip()
        target = find_wiki_target(slug)
        if target:
            return f"[{label}]({target})"
        return f"`[[{slug}]]`"
    return WIKILINK_RE.sub(sub, md_text)


def render_meta_strip(fm: dict) -> str:
    items = []
    if fm.get("type"):
        items.append(fm["type"])
    if fm.get("kind"):
        items.append(fm["kind"])
    if fm.get("platform"):
        items.append(fm["platform"])
    if fm.get("series"):
        items.append(fm["series"])
    if fm.get("voice"):
        items.append(fm["voice"])
    if fm.get("updated"):
        items.append(fm["updated"])
    elif fm.get("created"):
        items.append(fm["created"])
    if not items:
        return ""
    cells = "".join(f'<span class="meta-item">{html.escape(x)}</span>' for x in items)
    return f'<div class="meta">{cells}</div>'


def render_file(src: Path, dest: Path, section_label: str):
    raw = src.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(raw)
    body = rewrite_wikilinks(body)

    # Page title from frontmatter or first H1
    title = fm.get("name") or fm.get("title") or src.stem.replace("-", " ").title()

    # Convert markdown
    md = markdown.Markdown(extensions=["extra", "sane_lists", "tables"])
    html_body = md.convert(body)

    crumb = (
        f'<div class="crumb">'
        f'<a href="{BASE_HREF}/">drafts</a> · '
        f'<a href="{BASE_HREF}/brain/">brain</a> · '
        f'<a href="{BASE_HREF}/brain/#{section_label.lower().replace(" ", "-")}">{section_label.lower()}</a>'
        f'</div>'
    )

    page = BRAND_SHELL.format(
        title=html.escape(title),
        base=BASE_HREF,
        section_tag=html.escape(section_label.lower()),
        crumb=crumb,
        body=f"<h1>{html.escape(title)}</h1>{render_meta_strip(fm)}{html_body}",
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")


def one_line(fm: dict, body: str) -> str:
    """Pull the first bolded one-liner or first sentence for the index card."""
    m = re.search(r"\*\*One[- ]line:?\*\*\s*([^\n]+)", body)
    if m:
        return m.group(1).strip()
    m = re.search(r"\*\*TL;DR:?\*\*\s*([^\n]+)", body)
    if m:
        return m.group(1).strip()
    # Fallback: first non-heading, non-blank line
    for line in body.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("```"):
            return line[:160]
    return ""


def render_index(raw_files=None):
    raw_files = raw_files or []
    sections_html = []

    # Hero
    sections_html.append(
        '<h1>The brain</h1>'
        '<p style="color: var(--creme-60); margin-bottom: 36px; font-size: 14px;">'
        'Every entity, concept, source, and exemplar the brain is currently built from. '
        'When Mehr asks for a post, the write-post skill pulls from this material first. '
        'Click into any card to read the underlying note.'
        '</p>'
    )

    for folder, label, sub in SECTIONS:
        src_dir = WIKI / folder
        if not src_dir.exists():
            continue

        if folder == "_index":
            files = sorted(src_dir.glob("*.md"))
        elif folder == "voice":
            # Only the top-level styleguide, not exemplars (handled separately)
            files = sorted([p for p in src_dir.glob("*.md") if p.is_file()])
        else:
            files = sorted(src_dir.glob("**/*.md"))

        if not files:
            continue

        anchor = label.lower().replace(" ", "-")
        sections_html.append(
            f'<div class="section-header" id="{anchor}">'
            f'<h2>{html.escape(label)}</h2>'
            f'<span class="section-header-sub">{html.escape(sub)}</span>'
            f'</div>'
        )
        cards = []
        for f in files:
            raw = f.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(raw)
            title = fm.get("name") or fm.get("title") or f.stem.replace("-", " ").title()
            excerpt = one_line(fm, body)
            rel = f.relative_to(WIKI).with_suffix(".html")
            href = f"{BASE_HREF}/brain/{rel}"
            cards.append(
                f'<a class="section-card" href="{href}">'
                f'<h4>{html.escape(title)}</h4>'
                f'<p>{html.escape(excerpt)}</p>'
                f'</a>'
            )
        sections_html.append(f'<div class="section-grid">{"".join(cards)}</div>')

    # Daily drops section — Mehr's raw logs, most recent first
    if raw_files:
        sections_html.append(
            '<div class="section-header" id="daily-drops">'
            '<h2>Daily drops</h2>'
            '<span class="section-header-sub">Everything Mehr has fed the brain, newest first</span>'
            '</div>'
        )
        cards = []
        for src in raw_files[:20]:  # cap at 20 most recent
            raw_text = src.read_text(encoding="utf-8")
            # First meaningful line as a preview
            preview = ""
            for line in raw_text.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    preview = line[:140]
                    break
            if not preview:
                preview = "No content yet"
            href = f"{BASE_HREF}/brain/raw/{src.stem}.html"
            cards.append(
                f'<a class="section-card" href="{href}">'
                f'<h4>{html.escape(src.stem)}</h4>'
                f'<p>{html.escape(preview)}</p>'
                f'</a>'
            )
        sections_html.append(f'<div class="section-grid">{"".join(cards)}</div>')

    body_html = "".join(sections_html)

    crumb = f'<div class="crumb"><a href="{BASE_HREF}/">drafts</a> · <span>brain</span></div>'
    page = BRAND_SHELL.format(
        title="The brain",
        base=BASE_HREF,
        section_tag="overview",
        crumb=crumb,
        body=body_html,
    )
    (OUT / "index.html").write_text(page, encoding="utf-8")


def render_raw_logs():
    """Render raw/YYYY-MM-DD.md files as a 'daily drops' section of the brain."""
    if not RAW.exists():
        return []
    raw_files = sorted(
        [p for p in RAW.glob("*.md") if p.name != ".gitkeep"],
        reverse=True,
    )
    rendered = []
    for src in raw_files:
        dest = OUT / "raw" / f"{src.stem}.html"
        raw = src.read_text(encoding="utf-8")
        md = markdown.Markdown(extensions=["extra", "sane_lists", "tables"])
        html_body = md.convert(raw)
        crumb = (
            f'<div class="crumb">'
            f'<a href="{BASE_HREF}/">drafts</a> · '
            f'<a href="{BASE_HREF}/brain/">brain</a> · '
            f'<a href="{BASE_HREF}/brain/#daily-drops">daily drops</a>'
            f'</div>'
        )
        title = f"Daily drop — {src.stem}"
        page = BRAND_SHELL.format(
            title=html.escape(title),
            base=BASE_HREF,
            section_tag="daily drops",
            crumb=crumb,
            body=f"<h1>{html.escape(title)}</h1>{html_body}",
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")
        rendered.append(src)
    return rendered


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    # Render every wiki/*.md and wiki/**/*.md
    for src in WIKI.rglob("*.md"):
        rel = src.relative_to(WIKI)
        dest = OUT / rel.with_suffix(".html")
        top = rel.parts[0]
        section_label = {
            "entities": "Entities",
            "concepts": "Concepts",
            "synthesis": "Synthesis angles",
            "sources": "Sources",
            "voice": "Voice" if len(rel.parts) == 2 else "Voice exemplars",
            "_index": "Indexes",
        }.get(top, "Brain")
        render_file(src, dest, section_label)

    # Render raw/ daily drops so Mehr can see her own inputs
    raw_files = render_raw_logs()

    # Render the browse-all index
    render_index(raw_files=raw_files)

    print(f"Rendered {sum(1 for _ in OUT.rglob('*.html'))} HTML files to {OUT}")


if __name__ == "__main__":
    main()
