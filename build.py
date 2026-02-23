#!/usr/bin/env python3
"""PRISM Hub — Static Site Generator for Cloudflare Pages.
Generates public-safe HTML from the local hub content.
Strips: Cameras, Terminal, PRISM personal docs, Tagebuch."""

import os
import re
import json
import shutil
import random
import urllib.parse
from pathlib import Path
from datetime import date

# ─── Config ──────────────────────────────────────────────────
WORKSPACE = Path(os.environ.get("WORKSPACE", Path.home() / ".openclaw" / "workspace"))
DIST = Path(__file__).parent / "dist"
AVATAR_SRC = WORKSPACE / "projects" / "prism-avatar.png"

# Only these sections go public
PUBLIC_LIBRARY = {
    "🎮 Meat Machine Cycle": [
        ("GDD v2.2 (aktuell)", "projects/mmc/docs/gdd-v2.2.md"),
        ("Sprint Plan", "projects/mmc/docs/sprint-plan.md"),
        ("Architektur", "projects/mmc/docs/architecture.md"),
        ("Roadmap", "projects/mmc/docs/roadmap.md"),
        ("Projekt-Struktur", "MMC/meat-machine-cycle/PROJECT_STRUCTURE.md"),
    ],
    "🔬 Research": [
        ("Blender AI Pipeline", "projects/research/blender-ai-pipeline.md"),
        ("Gamedev Engines & AI", "projects/research/gamedev-engines-ai.md"),
        ("Multi-Machine Agent Teams", "projects/research/multi-machine-agent-teams.md"),
        ("n8n Workflow Automation", "projects/research/n8n-workflow-automation.md"),
    ],
}

# ─── News ────────────────────────────────────────────────────
NEWS_DIR = WORKSPACE / "projects" / "prism-hub" / "news"

def get_news_files():
    if not NEWS_DIR.exists():
        return []
    return sorted(NEWS_DIR.glob("*.md"), reverse=True)

# ─── Hero images ─────────────────────────────────────────────
HERO_IMAGES = [
    "https://picsum.photos/seed/neon1/800/200",
    "https://picsum.photos/seed/cyber2/800/200",
    "https://picsum.photos/seed/dark3/800/200",
    "https://picsum.photos/seed/grid4/800/200",
]

# ─── CSS (same as local hub, but no sidebar hover tricks — use hamburger) ──
CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Orbitron:wght@400;500;600;700;800;900&display=swap');

:root {
    --bg-void: #06060b;
    --bg-base: #0a0a14;
    --bg-surface: #111122;
    --bg-elevated: #1a1a2e;
    --neon-cyan: #00f0ff;
    --neon-magenta: #ff00aa;
    --neon-violet: #8b5cf6;
    --neon-green: #39ff14;
    --neon-amber: #ffb800;
    --text-primary: #e0e0f0;
    --text-secondary: #8888aa;
    --text-muted: #555570;
    --glass-bg: rgba(17, 17, 34, 0.6);
    --glass-border: rgba(0, 240, 255, 0.08);
    --glow-cyan: 0 0 20px rgba(0, 240, 255, 0.3);
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
    --font-sans: 'Inter', system-ui, sans-serif;
    --font-display: 'Orbitron', var(--font-sans);
    --sidebar-collapsed: 64px;
    --sidebar-expanded: 260px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-void); }
::-webkit-scrollbar-thumb { background: var(--bg-elevated); border-radius: 3px; }
* { scrollbar-width: thin; scrollbar-color: var(--bg-elevated) var(--bg-void); }

body {
    font-family: var(--font-sans);
    background: var(--bg-void);
    color: var(--text-primary);
    line-height: 1.7;
    font-size: 15px;
    min-height: 100vh;
    overflow-x: hidden;
}
body::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse at 15% 50%, rgba(0, 240, 255, 0.035) 0%, transparent 50%),
        radial-gradient(ellipse at 85% 20%, rgba(139, 92, 246, 0.03) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 90%, rgba(255, 0, 170, 0.02) 0%, transparent 50%);
    z-index: 0; pointer-events: none;
}
body::after {
    content: ''; position: fixed; inset: 0;
    background: linear-gradient(rgba(0,240,255,0.015) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,0.015) 1px, transparent 1px);
    background-size: 80px 80px; pointer-events: none; z-index: 0;
}

/* Sidebar */
.sidebar {
    position: fixed; top: 0; left: 0; bottom: 0;
    width: var(--sidebar-collapsed);
    background: var(--bg-surface);
    border-right: 1px solid var(--glass-border);
    transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden; z-index: 100;
    display: flex; flex-direction: column;
}
.sidebar:hover { width: var(--sidebar-expanded); }
.sidebar-logo {
    padding: 18px 16px; border-bottom: 1px solid var(--glass-border);
    white-space: nowrap; display: flex; align-items: center; gap: 12px; min-height: 64px;
}
.sidebar-logo .logo-icon { font-size: 1.6rem; flex-shrink: 0; width: 30px; text-align: center; filter: drop-shadow(0 0 8px rgba(0, 240, 255, 0.5)); }
.sidebar-logo .logo-text { font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; color: var(--neon-cyan); letter-spacing: 0.1em; text-transform: uppercase; text-shadow: 0 0 20px rgba(0, 240, 255, 0.4); opacity: 0; transition: opacity 0.2s 0.1s; }
.sidebar:hover .logo-text { opacity: 1; }
.sidebar-avatar { padding: 12px 16px; text-align: center; opacity: 0; transition: opacity 0.3s 0.15s; }
.sidebar:hover .sidebar-avatar { opacity: 1; }
.sidebar-avatar img { width: 80px; height: 80px; border-radius: 12px; border: 1px solid var(--glass-border); box-shadow: 0 0 20px rgba(0, 240, 255, 0.15); }
.sidebar-nav { flex: 1; overflow-y: auto; padding: 4px 0; }
.nav-section {
    padding: 14px 20px 4px; font-family: var(--font-mono); font-size: 0.58em; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted);
    white-space: nowrap; opacity: 0; transition: opacity 0.2s 0.1s;
}
.sidebar:hover .nav-section { opacity: 1; }
.nav-item {
    display: flex; align-items: center; gap: 12px;
    padding: 8px 20px; color: var(--text-secondary); text-decoration: none;
    font-family: var(--font-mono); font-size: 0.8em; letter-spacing: 0.03em;
    white-space: nowrap; border-left: 3px solid transparent; transition: all 0.2s ease;
}
.nav-item:hover { color: var(--neon-cyan); background: rgba(0, 240, 255, 0.04); border-left-color: var(--neon-cyan); }
.nav-item.active { color: var(--neon-cyan); background: rgba(0, 240, 255, 0.07); border-left-color: var(--neon-cyan); }
.nav-item .icon { width: 24px; flex-shrink: 0; text-align: center; font-size: 1.1em; }
.nav-item .label { opacity: 0; transition: opacity 0.2s 0.1s; }
.sidebar:hover .nav-item .label { opacity: 1; }
.sidebar-footer {
    padding: 14px 20px; border-top: 1px solid var(--glass-border);
    font-family: var(--font-mono); font-size: 0.65em; color: var(--text-muted);
    white-space: nowrap; display: flex; align-items: center; gap: 8px;
}
.status-dot { width: 6px; height: 6px; background: var(--neon-green); border-radius: 50%; flex-shrink: 0; box-shadow: 0 0 8px rgba(57, 255, 20, 0.5); animation: pulse 2.5s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.sidebar-footer .footer-text { opacity: 0; transition: opacity 0.2s 0.1s; }
.sidebar:hover .footer-text { opacity: 1; }

/* Main */
.main {
    margin-left: var(--sidebar-collapsed); padding: 2.5rem 3rem;
    position: relative; z-index: 1; min-height: 100vh;
    transition: margin-left 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    max-width: calc(100vw - var(--sidebar-collapsed));
}
.sidebar:hover ~ .main { margin-left: var(--sidebar-expanded); max-width: calc(100vw - var(--sidebar-expanded)); }

.hero-banner { width: 100%; height: 160px; border-radius: 14px; overflow: hidden; margin-bottom: 2rem; position: relative; border: 1px solid var(--glass-border); }
.hero-banner img { width: 100%; height: 100%; object-fit: cover; filter: brightness(0.4) saturate(1.3); }
.hero-banner .hero-overlay { position: absolute; inset: 0; background: linear-gradient(135deg, rgba(0,240,255,0.15), rgba(255,0,170,0.1)); mix-blend-mode: overlay; }
.hero-banner .hero-text { position: absolute; bottom: 20px; left: 24px; }
.hero-banner .hero-text h1 { font-family: var(--font-display); font-size: 1.8rem; font-weight: 700; color: var(--neon-cyan); text-transform: uppercase; letter-spacing: 0.06em; text-shadow: 0 0 30px rgba(0, 240, 255, 0.4); }
.hero-banner .hero-text p { font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-secondary); }

.page-title { font-family: var(--font-display); font-size: 2rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--neon-cyan); text-shadow: 0 0 30px rgba(0, 240, 255, 0.25); margin-bottom: 0.3rem; }
.page-subtitle { color: var(--text-muted); font-family: var(--font-mono); font-size: 0.85rem; margin-bottom: 2.5rem; }

h2 { font-family: var(--font-mono); font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); margin: 2.5rem 0 0.8rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--glass-border); }
h3 { font-size: 1.05rem; color: var(--neon-cyan); margin: 1.5rem 0 0.5rem; }
a { color: var(--neon-cyan); text-decoration: none; transition: all 0.15s; }
a:hover { color: #66f7ff; text-shadow: 0 0 8px rgba(0, 240, 255, 0.3); }

.card {
    background: var(--glass-bg); backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border); border-radius: 12px;
    padding: 0.9rem 1.2rem; margin: 0.4rem 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.card:hover { transform: translateY(-2px); border-color: rgba(0, 240, 255, 0.2); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4); }
.card a { display: flex; justify-content: space-between; align-items: center; color: var(--text-primary); font-weight: 500; font-size: 0.95rem; }
.card a:hover { text-decoration: none; }
.card .meta { color: var(--text-muted); font-size: 0.7rem; font-family: var(--font-mono); }
.category { margin-bottom: 1rem; }

.doc-viewer {
    background: var(--glass-bg); backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border); border-radius: 14px; padding: 2.5rem;
    font-size: 15px; line-height: 1.8;
}
.doc-viewer h1 { font-family: var(--font-display); font-size: 1.6rem; color: var(--neon-cyan); margin: 0 0 1rem; border-bottom: 1px solid var(--glass-border); padding-bottom: 0.8rem; }
.doc-viewer h2 { font-size: 1.2rem; color: var(--neon-cyan); text-transform: none; letter-spacing: normal; font-family: var(--font-sans); font-weight: 600; border-bottom: 1px solid var(--glass-border); padding-bottom: 0.4rem; margin: 2rem 0 0.8rem; }
.doc-viewer h3 { font-size: 1.05rem; color: var(--neon-violet); margin: 1.5rem 0 0.5rem; }
.doc-viewer h4 { font-size: 0.95rem; color: var(--neon-amber); margin: 1.2rem 0 0.4rem; }
.doc-viewer p { margin: 0.6rem 0; }
.doc-viewer code { background: rgba(0, 240, 255, 0.08); padding: 2px 7px; border-radius: 5px; color: var(--neon-cyan); font-size: 0.88em; font-family: var(--font-mono); }
.doc-viewer pre { background: rgba(0, 0, 0, 0.5); padding: 1.25rem; border-radius: 10px; overflow-x: auto; margin: 1rem 0; border: 1px solid var(--glass-border); }
.doc-viewer pre code { background: none; padding: 0; color: var(--neon-green); display: block; }
.doc-viewer ul, .doc-viewer ol { padding-left: 1.5rem; margin: 0.5rem 0; }
.doc-viewer li { margin: 0.3rem 0; }
.doc-viewer li::marker { color: var(--neon-cyan); }
.doc-viewer blockquote { border-left: 3px solid var(--neon-violet); padding: 0.5rem 1rem; margin: 1rem 0; background: rgba(139, 92, 246, 0.05); border-radius: 0 8px 8px 0; color: var(--text-secondary); }
.doc-viewer hr { border: none; height: 1px; background: linear-gradient(90deg, transparent, var(--glass-border), transparent); margin: 2rem 0; }
.doc-viewer table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
.doc-viewer th, .doc-viewer td { padding: 0.6rem 1rem; border: 1px solid var(--glass-border); text-align: left; }
.doc-viewer th { background: rgba(0, 240, 255, 0.06); color: var(--neon-cyan); font-family: var(--font-mono); font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }
.doc-viewer img { max-width: 100%; border-radius: 8px; }
.doc-viewer strong { color: var(--text-primary); }

.breadcrumb { color: var(--text-muted); margin-bottom: 1.5rem; font-size: 0.8rem; font-family: var(--font-mono); }
.breadcrumb a { color: var(--neon-cyan); }
.breadcrumb .sep { margin: 0 0.5rem; opacity: 0.3; }

.badge { display: inline-flex; align-items: center; padding: 2px 10px; font-family: var(--font-mono); font-size: 0.7em; text-transform: uppercase; border-radius: 4px; border: 1px solid; }
.badge-cyan { color: var(--neon-cyan); border-color: rgba(0, 240, 255, 0.3); background: rgba(0, 240, 255, 0.08); }
.badge-green { color: var(--neon-green); border-color: rgba(57, 255, 20, 0.3); background: rgba(57, 255, 20, 0.08); }
.badge-red { color: #f87171; border-color: rgba(248, 113, 113, 0.3); background: rgba(248, 113, 113, 0.08); }

.footer { margin-top: 3rem; padding-top: 1.5rem; text-align: center; font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-muted); }
.footer .line { height: 1px; background: linear-gradient(90deg, transparent, var(--glass-border), transparent); margin-bottom: 1.5rem; }

/* Hamburger (mobile) */
.hamburger {
    display: none; position: fixed; top: 12px; left: 12px; z-index: 200;
    width: 44px; height: 44px; border-radius: 10px;
    background: var(--bg-surface); border: 1px solid var(--glass-border);
    cursor: pointer; align-items: center; justify-content: center;
    backdrop-filter: blur(12px); box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
.hamburger span { display: block; width: 20px; height: 2px; background: var(--neon-cyan); border-radius: 1px; transition: all 0.3s; position: relative; }
.hamburger span::before, .hamburger span::after { content: ''; position: absolute; left: 0; width: 20px; height: 2px; background: var(--neon-cyan); border-radius: 1px; transition: all 0.3s; }
.hamburger span::before { top: -6px; }
.hamburger span::after { top: 6px; }
.hamburger.open span { background: transparent; }
.hamburger.open span::before { top: 0; transform: rotate(45deg); }
.hamburger.open span::after { top: 0; transform: rotate(-45deg); }
.sidebar-backdrop { display: none; position: fixed; inset: 0; z-index: 99; background: rgba(6,6,11,0.7); }
.sidebar-backdrop.visible { display: block; }

@media (max-width: 768px) {
    .hamburger { display: flex; }
    .sidebar { width: 280px !important; transform: translateX(-100%); transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1); z-index: 150; }
    .sidebar.mobile-open { transform: translateX(0); }
    .sidebar.mobile-open .logo-text, .sidebar.mobile-open .sidebar-avatar,
    .sidebar.mobile-open .nav-section, .sidebar.mobile-open .nav-item .label,
    .sidebar.mobile-open .footer-text { opacity: 1 !important; }
    .sidebar:hover { width: 280px !important; }
    .main { margin-left: 0 !important; max-width: 100vw !important; padding: 1rem !important; padding-top: 64px !important; }
    .sidebar:hover ~ .main { margin-left: 0 !important; max-width: 100vw !important; }
    .hero-banner { height: 110px; border-radius: 10px; }
    .hero-banner .hero-text h1 { font-size: 1.2rem; }
    .hero-banner .hero-text p { font-size: 0.7rem; }
    .page-title { font-size: 1.4rem; }
    .doc-viewer { padding: 1.2rem; font-size: 14px; }
    .doc-viewer pre { overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .doc-viewer table { display: block; overflow-x: auto; }
    .card a { min-height: 44px; }
    .nav-item { min-height: 44px; padding: 10px 20px; }
    .search-bar input { font-size: 16px; }
}
"""

# ─── HTML Generation ─────────────────────────────────────────
def sidebar_html(active="home"):
    nav_main = [
        ("home", "index.html", "🏠", "Dashboard"),
        ("news", "news.html", "📰", "AI News"),
    ]
    links = '<div class="nav-section">Navigation</div>\n'
    for key, href, icon, label in nav_main:
        cls = " active" if key == active else ""
        links += f'<a href="{href}" class="nav-item{cls}"><span class="icon">{icon}</span><span class="label">{label}</span></a>\n'

    for cat, files in PUBLIC_LIBRARY.items():
        emoji = cat.split(" ")[0]
        name = cat.split(" ", 1)[1]
        links += f'<div class="nav-section">{emoji} {name}</div>\n'
        for title, path in files:
            slug = path_to_slug(path)
            links += f'<a href="doc/{slug}.html" class="nav-item"><span class="icon">📄</span><span class="label">{title}</span></a>\n'

    return f"""<aside class="sidebar">
    <div class="sidebar-logo">
        <span class="logo-icon">🔮</span>
        <span class="logo-text">PRISM</span>
    </div>
    <div class="sidebar-avatar">
        <img src="static/avatar.png" alt="PRISM" onerror="this.style.display='none'">
    </div>
    <nav class="sidebar-nav">{links}</nav>
    <div class="sidebar-footer">
        <span class="status-dot"></span>
        <span class="footer-text">PRISM Hub // Public</span>
    </div>
</aside>"""


def wrap_page(title, content, active="home"):
    return f"""<!DOCTYPE html><html lang="de"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} // PRISM Hub</title>
<style>{CSS}</style>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head><body>
{sidebar_html(active)}
<button class="hamburger" id="hamburger" aria-label="Menu" onclick="toggleMenu()"><span></span></button>
<div class="sidebar-backdrop" id="sidebar-backdrop" onclick="closeMenu()"></div>
<main class="main">{content}</main>
<script>
function toggleMenu(){{
    document.querySelector('.sidebar').classList.toggle('mobile-open');
    document.getElementById('hamburger').classList.toggle('open');
    document.getElementById('sidebar-backdrop').classList.toggle('visible');
}}
function closeMenu(){{
    document.querySelector('.sidebar').classList.remove('mobile-open');
    document.getElementById('hamburger').classList.remove('open');
    document.getElementById('sidebar-backdrop').classList.remove('visible');
}}
document.querySelectorAll('.sidebar .nav-item').forEach(a=>a.addEventListener('click',closeMenu));
</script>
</body></html>"""


def path_to_slug(path):
    return path.replace("/", "_").replace(".md", "").replace(" ", "-")


def escape_for_js(text):
    return text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${").replace("</script>", "<\\/script>")


# ─── Page Builders ───────────────────────────────────────────
def build_home():
    hero_img = random.choice(HERO_IMAGES)
    sections = ""
    for cat, files in PUBLIC_LIBRARY.items():
        cards = ""
        for title, path in files:
            full = WORKSPACE / path
            exists = full.exists()
            size = f"{full.stat().st_size / 1024:.0f} KB" if exists else "—"
            status = "" if exists else ' <span class="badge badge-red">missing</span>'
            slug = path_to_slug(path)
            cards += f'<div class="card"><a href="doc/{slug}.html"><span>{title}{status}</span><span class="meta">{size}</span></a></div>'
        sections += f'<div class="category"><h2>{cat}</h2>{cards}</div>'

    # Recent news
    news_files = get_news_files()[:3]
    if news_files:
        news_cards = ""
        for f in news_files:
            d = f.stem
            news_cards += f'<div class="card"><a href="news/{d}.html"><span>📰 {d}</span><span class="meta"></span></a></div>'
        sections += f'<div class="category"><h2>📰 Letzte AI News</h2>{news_cards}<div class="card"><a href="news.html"><span style="color:var(--neon-cyan)">→ Alle News</span><span class="meta"></span></a></div></div>'

    content = f"""
    <div class="hero-banner">
        <img src="{hero_img}" alt="">
        <div class="hero-overlay"></div>
        <div class="hero-text">
            <h1>PRISM Hub</h1>
            <p>// clay machine games // public docs</p>
        </div>
    </div>
    {sections}
    <div class="footer"><div class="line"></div>PRISM Hub // Neon Terminal Noir // Public Edition</div>"""
    return wrap_page("Dashboard", content, "home")


def build_doc(title, path):
    full = WORKSPACE / path
    if not full.exists():
        return wrap_page("404", '<h1 class="page-title">404</h1><p class="page-subtitle">// nicht gefunden</p>')
    raw = full.read_text(encoding="utf-8")
    escaped = escape_for_js(raw)
    fname = path.split("/")[-1]
    page = f"""
    <div class="breadcrumb"><a href="index.html">Dashboard</a><span class="sep">//</span>{fname}</div>
    <div class="doc-viewer" id="doc-content"></div>
    <script>
    const raw = `{escaped}`;
    document.getElementById('doc-content').innerHTML = marked.parse(raw);
    </script>"""
    return wrap_page(title, page)


def build_news_index():
    news_files = get_news_files()
    cards = ""
    for f in news_files:
        d = f.stem
        first_line = f.read_text(encoding="utf-8").split("\n")[0].strip("# ").strip()
        cards += f'<div class="card"><a href="news/{d}.html"><span style="color:var(--neon-cyan)">{d}</span> — {first_line}</a></div>\n'
    if not cards:
        cards = '<p style="color:var(--text-muted)">Noch keine News.</p>'

    page = f"""
    <h1 class="page-title">📰 AI News Archiv</h1>
    <p class="page-subtitle">// kuratierte ai news // täglich aktualisiert</p>
    {cards}"""
    return wrap_page("AI News", page, "news")


def build_news_page(news_file):
    d = news_file.stem
    raw = news_file.read_text(encoding="utf-8")
    escaped = escape_for_js(raw)
    page = f"""
    <div class="breadcrumb"><a href="index.html">Dashboard</a><span class="sep">//</span><a href="news.html">News</a><span class="sep">//</span>{d}</div>
    <div class="doc-viewer" id="news-content"></div>
    <script>
    document.getElementById('news-content').innerHTML = marked.parse(`{escaped}`);
    </script>"""
    return wrap_page(f"AI News — {d}", page, "news")


# ─── Build ───────────────────────────────────────────────────
def build():
    # Clean dist
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "doc").mkdir()
    (DIST / "news").mkdir()
    (DIST / "static").mkdir()

    # Copy avatar
    if AVATAR_SRC.exists():
        shutil.copy2(AVATAR_SRC, DIST / "static" / "avatar.png")

    # Home
    write(DIST / "index.html", build_home())
    print("  ✓ index.html")

    # Docs
    for cat, files in PUBLIC_LIBRARY.items():
        for title, path in files:
            slug = path_to_slug(path)
            html = build_doc(title, path)
            write(DIST / "doc" / f"{slug}.html", html)
            print(f"  ✓ doc/{slug}.html")

    # News index
    write(DIST / "news.html", build_news_index())
    print("  ✓ news.html")

    # Individual news pages
    for f in get_news_files():
        html = build_news_page(f)
        write(DIST / "news" / f"{f.stem}.html", html)
        print(f"  ✓ news/{f.stem}.html")

    # 404
    write(DIST / "404.html", wrap_page("404", '<h1 class="page-title">404</h1><p class="page-subtitle">// seite nicht gefunden</p>'))
    print("  ✓ 404.html")

    total = sum(1 for _ in DIST.rglob("*.html"))
    print(f"\n🔮 Build complete: {total} pages → dist/")


def write(path, content):
    path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    print("🔮 PRISM Hub — Static Build\n")
    build()
