#!/usr/bin/env python3
"""Render Magna's two source-of-truth pages from wiki/ + raw/ + output/.

Outputs:
  output/brain/index.html   — The Brain. What Magna IS, who's behind it,
                              what it knows. Auto-evolves from wiki/.
  output/engine/index.html  — The Content Engine. Mehr's creative output —
                              series, voices, recent drafts.
  output/index.html         — Redirect to /brain/.
  output/brain.html         — Redirect to /brain/.

Design language matches Mehr's hand-built magna-brain-overview.html:
charcoal + creme + soil + gold, Forum + Raleway, soil-orange section
labels, creme-faint cards.

Called by .github/workflows/pages.yml on every push that touches wiki/,
raw/, output/, or tools/. Brain + Engine update within ~120s of any
contributor pushing.
"""

import html
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

try:
    import markdown
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "markdown"])
    import markdown

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
RAW = ROOT / "raw"
OUTPUT = ROOT / "output"
BRAIN_OUT = OUTPUT / "brain"
ENGINE_OUT = OUTPUT / "engine"
BASE_HREF = "/magna-brain"

WIKILINK_RE = re.compile(r"\[\[([^\]|]+?)(?:\|([^\]]+))?\]\]")


def parse_frontmatter(text: str):
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


def find_wiki_target(slug: str):
    candidates = [
        ("entities", slug),
        ("concepts", slug),
        ("sources", slug),
        ("synthesis", slug),
        ("voice/exemplars", slug),
        ("voice", slug),
        ("_index", slug),
    ]
    if "/" in slug:
        parts = slug.split("/", 1)
        candidates.insert(0, (parts[0], parts[1]))
        candidates.insert(0, ("", slug))
    for folder, name in candidates:
        p = WIKI / folder / f"{name}.md" if folder else WIKI / f"{name}.md"
        if p.exists():
            rel = p.relative_to(WIKI).with_suffix(".html")
            return f"{BASE_HREF}/brain/article/{rel}"
    return None


def rewrite_wikilinks(md_text: str) -> str:
    def sub(m):
        slug = m.group(1).strip()
        label = (m.group(2) or slug).strip()
        target = find_wiki_target(slug)
        if target:
            return f"[{label}]({target})"
        return f"`[[{slug}]]`"
    return WIKILINK_RE.sub(sub, md_text)


def first_paragraph(body: str) -> str:
    m = re.search(r"\*\*One[- ]line:?\*\*\s*([^\n]+)", body)
    if m:
        return m.group(1).strip()
    m = re.search(r"\*\*TL;DR:?\*\*\s*([^\n]+)", body)
    if m:
        return m.group(1).strip()
    for line in body.splitlines():
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith("```") and not s.startswith("---"):
            return s[:240]
    return ""


def collect(folder: str):
    src = WIKI / folder
    if not src.exists():
        return []
    items = []
    for p in sorted(src.glob("**/*.md")):
        raw = p.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(raw)
        title = fm.get("name") or fm.get("title") or p.stem.replace("-", " ").title()
        excerpt = first_paragraph(body)
        items.append({"path": p, "fm": fm, "body": body, "title": title,
                      "excerpt": excerpt, "slug": p.stem})
    return items


SHELL_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Forum&family=Raleway:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --charcoal: #2D2D2D;
      --charcoal-deep: #242424;
      --creme: #E8DFC8;
      --soil: #5C3518;
      --soil-light: rgba(92,53,24,0.18);
      --taupe: #483C32;
      --gold: #9B7C35;
      --creme-dim: rgba(232,223,200,0.55);
      --creme-faint: rgba(232,223,200,0.06);
      --creme-soft: rgba(232,223,200,0.10);
      --border: rgba(232,223,200,0.10);
      --border-soft: rgba(232,223,200,0.06);
    }}
    html {{ scroll-behavior: smooth; }}
    body {{ background: var(--charcoal); color: var(--creme); font-family: 'Raleway', sans-serif; font-weight: 400; min-height: 100vh; }}
    a {{ color: inherit; text-decoration: none; }}
    header.top {{
      padding: 44px 60px 32px; border-bottom: 1px solid var(--border);
      display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; flex-wrap: wrap;
    }}
    .header-left h1 {{
      font-family: 'Forum', serif; font-size: 2.6rem; letter-spacing: 0.12em; color: var(--creme);
      line-height: 1; text-transform: uppercase;
    }}
    .header-left p {{
      margin-top: 10px; font-size: 0.74rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--creme-dim);
    }}
    .header-right {{
      font-size: 0.7rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--creme-dim); text-align: right; line-height: 1.9;
    }}
    nav.tabs {{
      display: flex; padding: 0 60px; border-bottom: 1px solid var(--border-soft);
      background: var(--charcoal-deep); position: sticky; top: 0; z-index: 10;
    }}
    nav.tabs a {{
      border-bottom: 2px solid transparent; color: var(--creme-dim);
      font-size: 0.7rem; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase;
      padding: 16px 26px 14px; transition: color 0.2s, border-color 0.2s; cursor: pointer;
    }}
    nav.tabs a:hover {{ color: var(--creme); }}
    nav.tabs a.active {{ color: var(--creme); border-bottom-color: var(--soil); }}
    main {{ padding: 48px 60px 80px; max-width: 1240px; margin: 0 auto; }}
    .section-label {{
      font-size: 0.62rem; letter-spacing: 0.3em; text-transform: uppercase;
      color: var(--soil); margin-bottom: 18px; font-weight: 600;
    }}
    h2.section-title {{
      font-family: 'Forum', serif; font-size: 1.6rem; letter-spacing: 0.04em; color: var(--creme);
      margin-bottom: 8px; line-height: 1.2;
    }}
    p.section-sub {{
      font-size: 0.85rem; color: var(--creme-dim); line-height: 1.7; margin-bottom: 28px; max-width: 820px;
    }}
    .hero {{
      background: linear-gradient(180deg, rgba(92,53,24,0.10) 0%, rgba(92,53,24,0.0) 100%);
      border: 1px solid var(--border); border-radius: 6px;
      padding: 48px 48px 40px; margin-bottom: 48px;
    }}
    .hero .eyebrow {{
      font-size: 0.65rem; letter-spacing: 0.32em; text-transform: uppercase; color: var(--gold);
      margin-bottom: 18px; font-weight: 600;
    }}
    .hero h2 {{
      font-family: 'Forum', serif; font-size: 1.9rem; letter-spacing: 0.04em; color: var(--creme);
      line-height: 1.35; margin-bottom: 18px; max-width: 920px;
    }}
    .hero blockquote {{
      padding-left: 18px; border-left: 2px solid var(--soil);
      font-style: italic; font-size: 0.92rem; color: var(--creme-dim); line-height: 1.7;
      max-width: 720px; margin-top: 8px;
    }}
    .stats-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 56px; }}
    .stat-card {{
      background: var(--creme-faint); border: 1px solid var(--border); border-radius: 4px;
      padding: 24px 20px; text-align: center;
    }}
    .stat-card .num {{ font-family: 'Forum', serif; font-size: 2.4rem; color: var(--creme); line-height: 1; margin-bottom: 8px; }}
    .stat-card .label {{ font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--creme-dim); line-height: 1.5; }}
    .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 56px; }}
    .grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 56px; }}
    .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 56px; }}
    .card {{
      background: var(--creme-faint); border: 1px solid var(--border); border-radius: 4px;
      padding: 24px 26px; transition: background 0.15s, border-color 0.15s;
      display: block; color: inherit;
    }}
    .card:hover {{ background: var(--creme-soft); border-color: rgba(232,223,200,0.18); }}
    .card .kind {{
      font-size: 0.6rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--soil); font-weight: 600; margin-bottom: 10px;
    }}
    .card h3 {{ font-family: 'Forum', serif; font-size: 1.05rem; color: var(--creme); margin-bottom: 8px; line-height: 1.3; }}
    .card p {{ font-size: 0.78rem; line-height: 1.7; color: var(--creme-dim); }}
    .founder-block {{
      background: var(--creme-faint); border: 1px solid var(--border); border-radius: 6px;
      padding: 36px 40px; margin-bottom: 16px;
    }}
    .founder-block .eyebrow {{
      font-size: 0.62rem; letter-spacing: 0.28em; text-transform: uppercase; color: var(--gold);
      margin-bottom: 12px; font-weight: 600;
    }}
    .founder-block h3 {{ font-family: 'Forum', serif; font-size: 1.8rem; letter-spacing: 0.04em; color: var(--creme); margin-bottom: 4px; }}
    .founder-block .role {{ font-size: 0.72rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--creme-dim); margin-bottom: 18px; }}
    .founder-block p {{ font-size: 0.86rem; line-height: 1.85; color: var(--creme-dim); margin-bottom: 12px; }}
    .founder-block blockquote {{ padding-left: 16px; border-left: 2px solid var(--soil); font-style: italic; color: var(--creme-dim); margin-top: 16px; line-height: 1.75; font-size: 0.84rem; }}
    .article {{ max-width: 860px; margin: 0 auto; padding: 56px 28px 96px; }}
    .article .crumb {{
      font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--creme-dim); margin-bottom: 22px;
    }}
    .article .crumb a {{ color: var(--creme-dim); border-bottom: 1px solid transparent; }}
    .article .crumb a:hover {{ color: var(--creme); border-bottom-color: var(--creme-dim); }}
    .article h1 {{ font-family: 'Forum', serif; font-size: 2.4rem; line-height: 1.15; margin-bottom: 18px; color: var(--creme); }}
    .article h2 {{ font-family: 'Forum', serif; font-size: 1.4rem; margin-top: 32px; margin-bottom: 12px; color: var(--creme); }}
    .article h3 {{ font-family: 'Forum', serif; font-size: 1.05rem; margin-top: 24px; margin-bottom: 10px; color: var(--creme); }}
    .article p, .article ul, .article ol {{ margin-bottom: 16px; color: var(--creme); font-weight: 300; line-height: 1.8; font-size: 0.92rem; }}
    .article ul, .article ol {{ padding-left: 24px; }}
    .article li {{ margin-bottom: 6px; }}
    .article a {{ color: #c0927a; border-bottom: 1px solid rgba(192,146,122,0.3); }}
    .article a:hover {{ color: var(--creme); border-bottom-color: var(--creme); }}
    .article code {{ background: var(--creme-soft); padding: 2px 6px; border-radius: 2px; font-family: ui-monospace, Menlo, monospace; font-size: 0.85em; color: var(--creme); }}
    .article blockquote {{ border-left: 3px solid var(--soil); padding-left: 18px; margin: 18px 0; font-style: italic; color: var(--creme-dim); }}
    .article em {{ font-style: italic; color: #a07860; }}
    .article strong {{ font-weight: 500; color: var(--creme); }}
    .article table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 0.85em; }}
    .article th, .article td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); }}
    .article th {{ font-family: 'Forum', serif; font-weight: 400; color: var(--creme); }}
    .article td {{ color: var(--creme-dim); font-weight: 300; }}
    .article hr {{ border: none; border-top: 1px solid var(--border); margin: 28px 0; }}
    .article .meta {{ display: flex; gap: 14px; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.14em; color: var(--creme-dim); margin-bottom: 22px; flex-wrap: wrap; padding-bottom: 18px; border-bottom: 1px solid var(--border); }}
    .article .meta-item {{ padding-right: 14px; border-right: 1px solid var(--border); }}
    .article .meta-item:last-child {{ border-right: none; }}
    footer {{
      padding: 28px 60px; border-top: 1px solid var(--border-soft);
      font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase;
      color: rgba(232,223,200,0.22); text-align: center;
    }}
    @media (max-width: 840px) {{
      header.top {{ padding: 28px 24px 24px; }}
      nav.tabs {{ padding: 0 24px; }}
      main {{ padding: 32px 24px 64px; }}
      .grid-3, .grid-4 {{ grid-template-columns: 1fr 1fr; }}
      .stats-row {{ grid-template-columns: 1fr 1fr; }}
      .hero, .founder-block {{ padding: 28px 24px; }}
      .article {{ padding: 32px 20px 64px; }}
    }}
    @media (max-width: 520px) {{
      .grid-3, .grid-4, .grid-2 {{ grid-template-columns: 1fr; }}
      .stats-row {{ grid-template-columns: 1fr 1fr; }}
    }}
  </style>
</head>
<body>"""

HEADER = """
<header class="top">
  <div class="header-left">
    <h1>Magna Brain</h1>
    <p>Ecosystem Intelligence &amp; Knowledge Architecture</p>
  </div>
  <div class="header-right">
    Chicago · Global<br>
    magna.vip
  </div>
</header>
<nav class="tabs">
  <a href="{base}/brain/" class="{brain_active}">The Brain</a>
  <a href="{base}/engine/" class="{engine_active}">Content Engine</a>
</nav>
"""

FOOTER = """
<footer>The Brain · evolves with every drop · contributed_by tracked · {date}</footer>
</body>
</html>"""


def shell(title: str, body: str, *, active: str) -> str:
    head = SHELL_HEAD.format(title=html.escape(title))
    nav = HEADER.format(
        base=BASE_HREF,
        brain_active="active" if active == "brain" else "",
        engine_active="active" if active == "engine" else "",
    )
    return head + nav + body + FOOTER.format(date=datetime.utcnow().strftime("%Y-%m-%d"))


def render_article(item, section_label: str, dest_root: Path):
    md = markdown.Markdown(extensions=["extra", "sane_lists", "tables"])
    body_md = rewrite_wikilinks(item["body"])
    body_html = md.convert(body_md)

    fm = item["fm"]
    meta_items = []
    for k in ("type", "kind", "platform", "series", "voice"):
        if fm.get(k):
            meta_items.append(html.escape(fm[k]))
    if fm.get("contributed_by"):
        meta_items.append(f"by {html.escape(fm['contributed_by'])}")
    if fm.get("updated"):
        meta_items.append(html.escape(fm["updated"]))
    elif fm.get("created"):
        meta_items.append(html.escape(fm["created"]))
    meta_html = ""
    if meta_items:
        cells = "".join(f'<span class="meta-item">{m}</span>' for m in meta_items)
        meta_html = f'<div class="meta">{cells}</div>'

    crumb = (
        f'<div class="crumb">'
        f'<a href="{BASE_HREF}/brain/">brain</a> · '
        f'<a href="{BASE_HREF}/brain/#{section_label.lower().replace(" ", "-")}">'
        f'{html.escape(section_label.lower())}</a> · '
        f'<span>{html.escape(item["title"])}</span>'
        f'</div>'
    )
    body = f"""
<main class="article">
  {crumb}
  <h1>{html.escape(item["title"])}</h1>
  {meta_html}
  {body_html}
</main>"""
    page = shell(f"{item['title']} — Magna Brain", body, active="brain")
    rel = item["path"].relative_to(WIKI).with_suffix(".html")
    dest = dest_root / "article" / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")


def render_raw_article(src: Path, dest_root: Path):
    md = markdown.Markdown(extensions=["extra", "sane_lists", "tables"])
    body_html = md.convert(src.read_text(encoding="utf-8"))
    crumb = (
        f'<div class="crumb">'
        f'<a href="{BASE_HREF}/brain/">brain</a> · '
        f'<a href="{BASE_HREF}/brain/#daily-drops">daily drops</a> · '
        f'<span>{html.escape(src.stem)}</span>'
        f'</div>'
    )
    body = f"""
<main class="article">
  {crumb}
  <h1>Daily drop — {html.escape(src.stem)}</h1>
  {body_html}
</main>"""
    page = shell(f"Daily drop {src.stem} — Magna Brain", body, active="brain")
    dest = dest_root / "raw" / f"{src.stem}.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")


def card_html(item, kind: str, href: str) -> str:
    return (
        f'<a class="card" href="{href}">'
        f'<div class="kind">{html.escape(kind)}</div>'
        f'<h3>{html.escape(item["title"])}</h3>'
        f'<p>{html.escape(item["excerpt"])}</p>'
        f'</a>'
    )


def article_href(item) -> str:
    rel = item["path"].relative_to(WIKI).with_suffix(".html")
    return f"{BASE_HREF}/brain/article/{rel}"


def render_brain():
    entities = collect("entities")
    concepts = collect("concepts")
    synthesis = collect("synthesis")
    sources = collect("sources")

    brain_concepts = [c for c in concepts if not c["slug"].startswith("content-series-")]

    shailu = next((e for e in entities if e["slug"] == "shailu"), None)
    magna = next((e for e in entities if e["slug"] == "magna"), None)

    team_slugs = {"shailu", "mehr", "raju", "sireesha"}
    portfolio_slugs = {"careerx", "student-tribe", "shiminly", "muffins", "docsynk"}
    affiliation_slugs = {"dallas-venture-capital", "emerge-education"}
    program_slugs = {"magna-academy", "magna-meetup", "quantum-leap", "dubai-roundtables", "magna-capital"}
    brand_slugs = {"magna", "magna-compass", "colosseum-group", "shailosophy", "magna-audience", "tone-compass"}

    team = [e for e in entities if e["slug"] in team_slugs and e["slug"] != "shailu"]
    brands = [e for e in entities if e["slug"] in brand_slugs]
    programs = [e for e in entities if e["slug"] in program_slugs]
    portfolio = [e for e in entities if e["slug"] in portfolio_slugs]
    affiliations = [e for e in entities if e["slug"] in affiliation_slugs]

    raw_files = sorted([p for p in RAW.glob("*.md") if p.name != ".gitkeep"], reverse=True)
    raw_files = raw_files[:12]

    if magna:
        hero_title = first_paragraph(magna["body"])
    else:
        hero_title = "Magna translates institutional-grade sector knowledge into founder and executive capability."

    stats = [
        (len(entities), "Entities"),
        (len(brain_concepts), "Concepts"),
        (len(synthesis), "Synthesis angles"),
        (len(sources), "Sources"),
    ]

    founder_html = ""
    if shailu:
        body_text = shailu["body"]
        oneline = first_paragraph(body_text)
        quote_match = re.search(r'>\s*\*"([^"]+)"\*', body_text)
        quote = quote_match.group(1) if quote_match else None
        href = article_href(shailu)
        quote_html = f'<blockquote>"{html.escape(quote)}"</blockquote>' if quote else ""
        founder_html = f"""
<div class="founder-block">
  <div class="eyebrow">The Founder</div>
  <h3>{html.escape(shailu["title"])}</h3>
  <div class="role">Founder · Magna · Colosseum Group · 4 EdTech exits</div>
  <p>{html.escape(oneline)}</p>
  {quote_html}
  <div style="margin-top:20px;"><a href="{href}" style="font-size:0.7rem;letter-spacing:0.18em;text-transform:uppercase;color:var(--gold);border-bottom:1px solid var(--gold);padding-bottom:2px;">Read the full founder file →</a></div>
</div>"""

    def cards(items, kind):
        return "".join(card_html(it, kind, article_href(it)) for it in items)

    recent_html = ""
    if raw_files:
        cards_list = []
        for src in raw_files[:5]:
            text = src.read_text(encoding="utf-8")
            preview = ""
            for line in text.splitlines():
                s = line.strip()
                if s and not s.startswith("#") and not s.startswith("---") and not s.startswith("date:") and not s.startswith("source:"):
                    preview = s[:160]
                    break
            href = f"{BASE_HREF}/brain/raw/{src.stem}.html"
            cards_list.append(
                f'<a class="card" href="{href}">'
                f'<div class="kind">Daily drop</div>'
                f'<h3>{html.escape(src.stem)}</h3>'
                f'<p>{html.escape(preview)}</p>'
                f'</a>'
            )
        recent_html = "".join(cards_list)

    body = f"""
<main>

  <section class="hero">
    <div class="eyebrow">What Magna IS</div>
    <h2>{html.escape(hero_title)}</h2>
    <blockquote>"Delivering clarity where complexity meets capital allocation."</blockquote>
  </section>

  <div class="stats-row">
    {''.join(f'<div class="stat-card"><div class="num">{n}</div><div class="label">{html.escape(l)}</div></div>' for n, l in stats)}
  </div>

  <section id="founder-and-entities">
    <div class="section-label">Founder &amp; Team</div>
    <h2 class="section-title">Who runs Magna</h2>
    <p class="section-sub">The founder, the inner team, and Magna's intentional partnership with Shailosophy — Shailu's personal philosophy brand.</p>
    {founder_html}
    <div class="grid-3">{cards(team, "Team")}</div>
  </section>

  <section id="brand-and-programs">
    <div class="section-label">The brand &amp; programs</div>
    <h2 class="section-title">What Magna does</h2>
    <p class="section-sub">The brand entities Magna is built from, the programs it runs, and the parent enterprise that holds them all together.</p>
    <div class="grid-3">{cards(brands, "Brand")}</div>
    <div class="grid-3">{cards(programs, "Program")}</div>
  </section>

  <section id="capital-and-portfolio">
    <div class="section-label">Capital &amp; portfolio</div>
    <h2 class="section-title">Where Magna's capital flows</h2>
    <p class="section-sub">The five companies Magna Capital has backed, plus the external VC roles Shailu holds.</p>
    <div class="grid-3">{cards(portfolio, "Portfolio")}</div>
    <div class="grid-3">{cards(affiliations, "Affiliation")}</div>
  </section>

  <section id="concepts">
    <div class="section-label">Concepts &amp; frameworks</div>
    <h2 class="section-title">What Magna teaches and believes</h2>
    <p class="section-sub">Magna's frameworks, Shailu's recurring positions, and the concepts that thread through every workshop, lecture, and conversation. Content series live separately on the <a href="{BASE_HREF}/engine/" style="color: var(--gold); border-bottom: 1px solid var(--gold);">Content Engine</a>.</p>
    <div class="grid-3">{cards(brain_concepts, "Concept")}</div>
  </section>

  <section id="synthesis-angles">
    <div class="section-label">Synthesis angles</div>
    <h2 class="section-title">Where the brain has formed an opinion</h2>
    <p class="section-sub">Reusable points-of-view Magna can credibly hold — drawn from the underlying entities and concepts. Every post hooks into one of these.</p>
    <div class="grid-2">{cards(synthesis, "Angle")}</div>
  </section>

  <section id="sources">
    <div class="section-label">Sources</div>
    <h2 class="section-title">Where the brain learned what it knows</h2>
    <p class="section-sub">Every wiki claim is grounded in a source. These are the originals — brand documents, books, workshop transcripts, web research, ingests from Mehr's working folder.</p>
    <div class="grid-3">{cards(sources, "Source")}</div>
  </section>

  <section id="daily-drops">
    <div class="section-label">Daily drops</div>
    <h2 class="section-title">What the team has fed the brain recently</h2>
    <p class="section-sub">The raw material Mehr (and soon the rest of the team) has dropped in. Each drop is digested into the wiki above — these are the originals.</p>
    <div class="grid-3">{recent_html}</div>
  </section>

</main>"""
    return shell("The Brain — Magna", body, active="brain")


def render_engine():
    concepts = collect("concepts")
    series = [c for c in concepts if c["slug"].startswith("content-series-")]
    voice = collect("voice")
    voice_exemplars = [v for v in voice if "exemplars" in str(v["path"])]
    voice_styleguide = next((v for v in voice if v["slug"] == "styleguide"), None)
    tone_compass_path = WIKI / "entities" / "tone-compass.md"
    tone_compass_item = None
    if tone_compass_path.exists():
        raw = tone_compass_path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(raw)
        tone_compass_item = {
            "path": tone_compass_path, "fm": fm, "body": body,
            "title": fm.get("name") or "Tone Compass",
            "excerpt": first_paragraph(body),
            "slug": "tone-compass",
        }

    drafts = []
    if OUTPUT.exists():
        for p in sorted(OUTPUT.glob("*.html"), reverse=True):
            if p.name in ("index.html", "brain.html", "magna-brain-overview.html"):
                continue
            text = p.read_text(encoding="utf-8")
            t_match = re.search(r"<title>([^<]+)</title>", text)
            title = t_match.group(1).split(" — ")[0] if t_match else p.stem
            b_match = re.search(r'<strong>Mehr asked for:</strong>\s*([^<]+)', text)
            brief = b_match.group(1).strip() if b_match else ""
            m_match = re.search(r'class="meta-item">([^<]+)</span>', text)
            meta_first = m_match.group(1) if m_match else ""
            drafts.append({"title": title, "brief": brief, "meta": meta_first,
                          "href": f"{BASE_HREF}/{p.name}", "date": p.stem[:10]})
    drafts = drafts[:20]

    hero_title = ("The Content Engine — Mehr's evolving creative output for Magna. "
                  "Series, voices, and every draft she's published, all in one place that updates as the work continues.")

    stats = [
        (len(series), "Series"),
        (len(voice_exemplars), "Voice exemplars"),
        (len(drafts), "Recent drafts"),
        ("6", "Voices in the tone compass"),
    ]

    def cards_engine(items):
        return "".join(card_html(it, "Series", article_href(it)) for it in items)

    def voice_cards(items):
        return "".join(
            f'<a class="card" href="{article_href(it)}">'
            f'<div class="kind">Exemplar</div>'
            f'<h3>{html.escape(it["title"])}</h3>'
            f'<p>{html.escape(it["excerpt"])}</p>'
            f'</a>' for it in items
        )

    drafts_html = ""
    if drafts:
        items = []
        for d in drafts:
            meta_strip = f'<div class="kind">{html.escape(d["meta"])}</div>' if d["meta"] else ""
            brief = f'<p style="margin-top:8px;font-style:italic;">"{html.escape(d["brief"])}"</p>' if d["brief"] else ""
            items.append(
                f'<a class="card" href="{d["href"]}">'
                f'{meta_strip}'
                f'<h3>{html.escape(d["title"])}</h3>'
                f'<p style="font-size:0.7rem;color:var(--creme-dim);margin-bottom:6px;">{html.escape(d["date"])}</p>'
                f'{brief}'
                f'</a>'
            )
        drafts_html = "".join(items)

    tone_html = ""
    if tone_compass_item:
        styleguide_card = ""
        if voice_styleguide:
            styleguide_card = (
                f'<a class="card" href="{article_href(voice_styleguide)}">'
                f'<div class="kind">Styleguide</div>'
                f'<h3>{html.escape(voice_styleguide["title"])}</h3>'
                f'<p>{html.escape(voice_styleguide["excerpt"])}</p>'
                f'</a>'
            )
        tone_html = f"""
  <section id="tone-compass">
    <div class="section-label">The tone compass</div>
    <h2 class="section-title">Six voices, one register</h2>
    <p class="section-sub">{html.escape(tone_compass_item["excerpt"])}</p>
    <div class="grid-2">
      <a class="card" href="{article_href(tone_compass_item)}">
        <div class="kind">System</div>
        <h3>The Tone Compass</h3>
        <p>How Magna picks a voice for every series — Naval, Dalio, Godin, Sinek, Pink, Robbins.</p>
      </a>
      {styleguide_card}
    </div>
  </section>"""

    body = f"""
<main>

  <section class="hero">
    <div class="eyebrow">The Content Engine</div>
    <h2>{html.escape(hero_title)}</h2>
    <blockquote>Built and curated by Mehr. Evolves with every drop.</blockquote>
  </section>

  <div class="stats-row">
    {''.join(f'<div class="stat-card"><div class="num">{n}</div><div class="label">{html.escape(l)}</div></div>' for n, l in stats)}
  </div>

  <section id="series">
    <div class="section-label">The 9 content series</div>
    <h2 class="section-title">How Magna shows up every week</h2>
    <p class="section-sub">Nine series across Instagram and LinkedIn — each with its own voice, format, and rhythm. The engine that turns the brain into a posting cadence.</p>
    <div class="grid-3">{cards_engine(series)}</div>
  </section>

  {tone_html}

  <section id="voice-exemplars">
    <div class="section-label">Voice exemplars</div>
    <h2 class="section-title">Reference posts that anchor each voice</h2>
    <p class="section-sub">Hand-picked exemplars for Naval, Dalio, Godin, Sinek, Pink, and Robbins registers. New posts get checked against these to make sure the voice still lands.</p>
    <div class="grid-3">{voice_cards(voice_exemplars)}</div>
  </section>

  <section id="recent-drafts">
    <div class="section-label">Recent drafts</div>
    <h2 class="section-title">What's been published</h2>
    <p class="section-sub">Every draft Magna has shipped, newest first. Click any card to open the full post in Magna's brand shell.</p>
    <div class="grid-3">{drafts_html}</div>
  </section>

</main>"""
    return shell("Content Engine — Magna", body, active="engine")


REDIRECT_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url={url}">
  <title>Magna — redirecting</title>
  <link rel="canonical" href="{url}">
  <style>body{{background:#2D2D2D;color:#E8DFC8;font-family:Georgia,serif;padding:48px;text-align:center;}}a{{color:#9B7C35;}}</style>
</head>
<body>
  <p>Taking you to <a href="{url}">the new Magna brain</a>…</p>
  <script>window.location.replace("{url}");</script>
</body>
</html>"""


def write_redirects():
    (OUTPUT / "index.html").write_text(REDIRECT_TPL.format(url=f"{BASE_HREF}/brain/"), encoding="utf-8")
    (OUTPUT / "brain.html").write_text(REDIRECT_TPL.format(url=f"{BASE_HREF}/brain/"), encoding="utf-8")


def main():
    if BRAIN_OUT.exists():
        shutil.rmtree(BRAIN_OUT)
    BRAIN_OUT.mkdir(parents=True, exist_ok=True)
    if ENGINE_OUT.exists():
        shutil.rmtree(ENGINE_OUT)
    ENGINE_OUT.mkdir(parents=True, exist_ok=True)

    (BRAIN_OUT / "index.html").write_text(render_brain(), encoding="utf-8")
    (ENGINE_OUT / "index.html").write_text(render_engine(), encoding="utf-8")

    for folder, label in [("entities", "Founder & Entities"), ("concepts", "Concepts"),
                          ("synthesis", "Synthesis angles"), ("sources", "Sources"),
                          ("voice", "Voice"), ("voice/exemplars", "Voice exemplars"),
                          ("_index", "Indexes")]:
        for it in collect(folder):
            render_article(it, label, BRAIN_OUT)

    for src in RAW.glob("*.md"):
        if src.name == ".gitkeep":
            continue
        render_raw_article(src, BRAIN_OUT)

    write_redirects()

    total = sum(1 for _ in BRAIN_OUT.rglob("*.html")) + sum(1 for _ in ENGINE_OUT.rglob("*.html"))
    print(f"Rendered {total} HTML files (brain + engine + articles + raw drops + redirects).")


if __name__ == "__main__":
    main()
