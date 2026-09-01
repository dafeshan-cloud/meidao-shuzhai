#!/usr/bin/env python3
"""《梅导书斋》v2 — 多板块在线书库
板块: 经书(多本,原文+白话+评析) / 哲学 / 广告文案 / 故事(每日更新+评析)
数据: data/经书/*.json, data/{哲学,广告文案,故事}/daily.json
"""
import json, os, html, re, glob

BASE = '/Users/rocky-mei/Books/梅导书斋'
DATA = os.path.join(BASE, 'data')

# ---------- 读取经书 ----------
def load_jingshu():
    books = []
    for f in sorted(glob.glob(os.path.join(DATA, '经书', '*.json'))):
        name = os.path.basename(f)[:-5]
        try:
            chapters = json.load(open(f, encoding='utf-8'))
        except Exception as e:
            print(f"!! {name} 读取失败: {e}")
            continue
        books.append({"name": name, "chapters": chapters})
        print(f"经书: {name} — {len(chapters)} 章/分")
    return books

# ---------- 读取每日板块 ----------
def load_daily(section):
    f = os.path.join(DATA, section, 'daily.json')
    if not os.path.exists(f):
        return []
    return json.load(open(f, encoding='utf-8'))

# ---------- 构建经书章节 HTML ----------
def build_books_html(books):
    sections = []
    toc = {}
    for book in books:
        secs = []
        for i, ch in enumerate(book["chapters"]):
            title = ch.get("章") or ch.get("分") or f"第{i+1}节"
            # 经书标题:道德经用"第X章",金刚经用"X分"
            label = f"第{cn_num(int(ch['章']))}章" if book['name'] == '道德经' and '章' in ch else title
            orig = html.escape(ch.get("原文", ""))
            trans = html.escape(ch.get("译文", ch.get("白话", "")))
            jie = html.escape(ch.get("评析", ""))
            secs.append(f'''<section class="chapter" data-book="{book['name']}" data-idx="{i}">
<h2 class="ch-title">{label}</h2>
<div class="ch-body">{orig}</div>
<details class="trans"><summary>白话译文</summary><p>{trans}</p></details>
<details class="jiexi"><summary>评析</summary><p>{jie}</p></details>
</section>''')
        sections.append(f'''<!-- {book['name']} -->
{"".join(secs)}''')
        toc[book['name']] = len(book["chapters"])
    return "\n".join(sections), toc

# ---------- 构建每日板块 HTML ----------
def build_daily_html(section, items, meta):
    if not items:
        return f'<div class="daily-empty">暂无内容,敬请期待</div>'
    cards = []
    for it in items:
        title = html.escape(it.get("标题", "未命名"))
        body = html.escape(it.get("正文", ""))
        jie = html.escape(it.get("评析", ""))
        date = html.escape(it.get("日期", ""))
        cards.append(f'''<article class="daily-card">
  <div class="daily-head"><span class="daily-date">{date}</span><h3>{title}</h3></div>
  <div class="daily-body">{body}</div>
  <details class="jiexi"><summary>评析</summary><p>{jie}</p></details>
</article>''')
    return "\n".join(cards)

def cn_num(n):
    c = ['零','一','二','三','四','五','六','七','八','九','十']
    if n <= 10: return c[n]
    if n < 20: return '十' + c[n % 10]
    if n % 10 == 0: return c[n // 10] + '十'
    return c[n // 10] + '十' + c[n % 10]

# ---------- 主流程 ----------
books = load_jingshu()
books_html, book_toc = build_books_html(books)

sections_meta = {
    "哲学": {"icon": "哲", "desc": "每日一篇哲学短文", "sub": "每日更新"},
    "广告文案": {"icon": "案", "desc": "每日一篇广告拆解", "sub": "泰式广告为主"},
    "故事": {"icon": "故", "desc": "每日一篇故事", "sub": "寓言·人间·微小说"},
}
daily_html = {}
for sec, meta in sections_meta.items():
    items = load_daily(sec)
    daily_html[sec] = build_daily_html(sec, items, meta)
    print(f"{sec}: {len(items)} 篇")

# 经书目录(用于JS)
book_titles_json = json.dumps({
    b["name"]: [ (c.get("章") or c.get("分") or f"节{i+1}") for i, c in enumerate(b["chapters"]) ]
    for b in books
}, ensure_ascii=False)

html_doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>梅导书斋 — 经书 · 哲学 · 广告 · 故事</title>
<style>
:root {{
  --paper:#f6f1e5; --paper-deep:#ece3cd; --ink:#2c261c; --ink-soft:#7a715d;
  --accent:#8a6d3b; --accent-deep:#6b5430; --line:#d9cfb6; --gold:#a8894a;
  --card:#fbf8f0; --bar-bg:rgba(246,241,229,.94);
  --fs-body:17px; --fs-title:28px; --fs-p:17px;
}}
body[data-size="small"] {{ --fs-body:15px; --fs-title:25px; --fs-p:15px; }}
body[data-size="large"] {{ --fs-body:19px; --fs-title:31px; --fs-p:19px; }}
body[data-size="xlarge"] {{ --fs-body:21px; --fs-title:34px; --fs-p:21px; }}
body[data-theme="parchment"] {{
  --paper:#f3ead6; --paper-deep:#e9dcc0; --ink:#3a3020; --ink-soft:#8a7a5a;
  --accent:#9a7b4f; --accent-deep:#7c6138; --line:#ddcfae; --gold:#b59363;
  --card:#f8f2e2; --bar-bg:rgba(243,234,214,.94);
}}
body[data-theme="plain"] {{
  --paper:#ffffff; --paper-deep:#f4f4ee; --ink:#262626; --ink-soft:#8b8b85;
  --accent:#8a6d3b; --accent-deep:#6b5430; --line:#e2e2d8; --gold:#a8894a;
  --card:#ffffff; --bar-bg:rgba(255,255,255,.94);
}}
body[data-theme="night"] {{
  --paper:#1c1a16; --paper-deep:#262219; --ink:#d8cfba; --ink-soft:#a09682;
  --accent:#c9a86a; --accent-deep:#d8bc82; --line:#3a342a; --gold:#d4b678;
  --card:#232019; --bar-bg:rgba(28,26,22,.94);
}}
body[data-theme="forest"] {{
  --paper:#202b25; --paper-deep:#27352d; --ink:#cfd9cd; --ink-soft:#8fa394;
  --accent:#7fa88c; --accent-deep:#9cbfa6; --line:#36473c; --gold:#a8c49a;
  --card:#243129; --bar-bg:rgba(32,43,37,.94);
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ background:var(--paper); color:var(--ink); font-size:var(--fs-body);
  font-family:"Songti SC","Noto Serif SC","Source Han Serif SC","STSong",Georgia,serif;
  line-height:2.05; letter-spacing:.02em; transition:background .3s,color .3s; }}

#topbar {{ position:fixed; top:0; left:0; right:0; height:52px; z-index:100;
  display:flex; align-items:center; gap:14px; padding:0 18px;
  background:var(--bar-bg); backdrop-filter:blur(8px); border-bottom:1px solid var(--line); }}
#topbar .back {{ background:none; border:none; color:var(--accent-deep); font-size:15px;
  cursor:pointer; font-family:inherit; letter-spacing:.1em; padding:6px 10px; }}
#topbar .back:hover {{ color:var(--accent); }}
#topbar .sep {{ color:var(--line); }}
#topbar .bookname {{ font-size:15px; letter-spacing:.25em; }}
#topbar .spacer {{ flex:1; }}
#topbar .btn {{ background:none; border:1px solid var(--line); color:var(--ink-soft);
  font-size:13px; padding:5px 12px; border-radius:4px; cursor:pointer; font-family:inherit; letter-spacing:.1em; }}
#topbar .btn:hover {{ border-color:var(--accent); color:var(--accent); }}
#progress {{ position:fixed; top:52px; left:0; height:2px; width:0; background:var(--accent); z-index:101; }}

/* ===== 书架首页 ===== */
#shelf {{ max-width:920px; margin:0 auto; padding:110px 24px 80px; }}
.shelf-head {{ text-align:center; margin-bottom:52px; }}
.shelf-head .seal {{ display:inline-block; width:52px; height:52px; border:2px solid var(--accent);
  color:var(--accent); font-size:15px; line-height:52px; letter-spacing:.15em; border-radius:8px;
  transform:rotate(-4deg); margin-bottom:22px; font-weight:700; }}
.shelf-head h1 {{ font-size:clamp(28px,5vw,42px); letter-spacing:.3em; font-weight:700; margin-bottom:14px; }}
.shelf-head .rule {{ width:64px; height:1px; background:var(--accent); margin:0 auto 18px; }}
.shelf-head p {{ color:var(--ink-soft); font-size:14px; letter-spacing:.2em; }}
.section-title {{ font-size:17px; letter-spacing:.35em; color:var(--accent-deep); margin:44px 0 18px;
  display:flex; align-items:center; gap:12px; }}
.section-title::after {{ content:""; flex:1; height:1px; background:var(--line); }}
.book-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:20px; }}
.book-card {{ background:var(--card); border:1px solid var(--line); border-radius:10px;
  padding:26px 24px; cursor:pointer; transition:all .25s; position:relative; overflow:hidden; }}
.book-card:hover {{ transform:translateY(-4px); box-shadow:0 10px 30px rgba(107,84,48,.12); border-color:var(--accent); }}
.book-card .book-spine {{ position:absolute; left:0; top:0; bottom:0; width:5px; background:var(--accent); }}
.book-card .book-kicker {{ font-size:11px; color:var(--accent); letter-spacing:.3em; margin-bottom:12px; }}
.book-card h3 {{ font-size:21px; letter-spacing:.15em; margin-bottom:8px; }}
.book-card .book-sub {{ color:var(--ink-soft); font-size:12px; letter-spacing:.08em; margin-bottom:18px; }}
.book-card .book-meta {{ display:flex; justify-content:space-between; align-items:center;
  font-size:12px; color:var(--ink-soft); border-top:1px dashed var(--line); padding-top:14px; }}
.book-card .progress-bar {{ flex:1; height:3px; background:var(--line); border-radius:2px; overflow:hidden; margin:0 12px; }}
.book-card .progress-fill {{ height:100%; width:0; background:var(--accent); transition:width .4s; }}
.shelf-foot {{ text-align:center; margin-top:64px; color:var(--ink-soft); font-size:12px; letter-spacing:.25em; }}

/* ===== 每日板块卡片 ===== */
.daily-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:20px; }}
.daily-card {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:24px; }}
.daily-head {{ margin-bottom:12px; }}
.daily-date {{ font-size:11px; color:var(--accent); letter-spacing:.2em; }}
.daily-card h3 {{ font-size:17px; letter-spacing:.08em; margin-top:6px; }}
.daily-body {{ font-size:14px; color:var(--ink-soft); line-height:1.9;
  display:-webkit-box; -webkit-line-clamp:4; -webkit-box-orient:vertical; overflow:hidden; margin-bottom:10px; }}
.daily-card .jiexi {{ border-top:1px dashed var(--line); padding-top:10px; }}
.daily-card .jiexi summary {{ cursor:pointer; color:var(--accent); font-size:12px; letter-spacing:.15em; }}
.daily-card .jiexi p {{ font-size:13px; color:var(--ink-soft); margin-top:8px; line-height:1.85; }}
.daily-empty {{ color:var(--ink-soft); font-size:14px; letter-spacing:.15em; padding:20px 0; }}

/* ===== 阅读页 ===== */
#reader {{ display:none; max-width:700px; margin:0 auto; padding:96px 26px 120px; }}
.ch-title {{ font-size:var(--fs-title); letter-spacing:.25em; text-align:center; margin-bottom:40px; }}
.chapter .ch-body {{ white-space:pre-wrap; text-indent:0; margin-bottom:18px; font-size:var(--fs-p); }}
.chapter .trans {{ margin-top:24px; border-top:1px dashed var(--line); padding-top:16px; }}
.chapter .trans summary, .chapter .jiexi summary {{ cursor:pointer; color:var(--accent);
  font-size:13px; letter-spacing:.2em; user-select:none; padding:6px 0; }}
.chapter .trans p {{ text-indent:2em; color:var(--ink-soft); font-size:calc(var(--fs-p) - 2px); line-height:1.95; }}
.chapter .jiexi {{ border-top:1px dashed var(--line); padding-top:16px; margin-top:14px; }}
.chapter .jiexi p {{ text-indent:2em; color:var(--accent-deep); font-size:calc(var(--fs-p) - 1px); line-height:1.95; }}
.ch-end {{ text-align:center; color:var(--ink-soft); margin:70px 0 10px; font-size:13px; letter-spacing:.4em; }}

#chnav {{ position:fixed; bottom:0; left:0; right:0; display:none; justify-content:space-between;
  align-items:center; padding:12px 18px calc(12px + env(safe-area-inset-bottom));
  background:var(--bar-bg); backdrop-filter:blur(8px); border-top:1px solid var(--line); }}
#chnav button {{ background:none; border:1px solid var(--line); color:var(--ink);
  font-size:13px; padding:8px 16px; border-radius:5px; cursor:pointer; font-family:inherit; letter-spacing:.15em; }}
#chnav button:hover:not(:disabled) {{ border-color:var(--accent); color:var(--accent); }}
#chnav button:disabled {{ opacity:.35; cursor:default; }}
#chnav .ch-info {{ font-size:12px; color:var(--ink-soft); letter-spacing:.1em; }}

#drawer {{ position:fixed; top:0; left:0; bottom:0; width:300px; max-width:85vw; z-index:200;
  background:var(--paper-deep); border-right:1px solid var(--line); overflow-y:auto;
  transform:translateX(-100%); transition:transform .3s ease; padding:70px 0 40px; }}
#drawer.open {{ transform:translateX(0); }}
#drawer h3 {{ text-align:center; letter-spacing:.4em; font-size:16px; margin-bottom:8px; color:var(--accent-deep); }}
#drawer .drawer-book {{ text-align:center; font-size:12px; color:var(--ink-soft); letter-spacing:.2em; margin-bottom:22px; }}
#drawer ol {{ list-style:none; }}
#drawer li {{ border-bottom:1px dashed var(--line); }}
#drawer .toc-item {{ width:100%; background:none; border:none; font-family:inherit; cursor:pointer;
  display:flex; align-items:baseline; gap:14px; padding:13px 20px; color:var(--ink); font-size:14px; }}
#drawer .toc-item:hover {{ background:rgba(138,109,59,.08); color:var(--accent); }}
#drawer .toc-item .toc-num {{ color:var(--accent); font-size:12px; min-width:40px; letter-spacing:.1em; }}
#drawer .toc-item.current {{ color:var(--accent); background:rgba(138,109,59,.1); }}
#mask {{ position:fixed; inset:0; background:rgba(44,38,28,.35); z-index:150; display:none; }}
#mask.show {{ display:block; }}

#resume {{ position:fixed; top:70px; left:50%; transform:translateX(-50%); z-index:300;
  background:var(--card); border:1px solid var(--accent); border-radius:8px; padding:14px 22px;
  display:none; align-items:center; gap:16px; box-shadow:0 8px 30px rgba(0,0,0,.15); }}
#resume .txt {{ font-size:14px; letter-spacing:.05em; }}
#resume button {{ background:var(--accent); color:#fff; border:none; padding:7px 16px; border-radius:5px;
  cursor:pointer; font-family:inherit; font-size:13px; letter-spacing:.1em; }}
#resume button.plain {{ background:none; color:var(--ink-soft); border:1px solid var(--line); }}

.settings-mask {{ position:fixed; inset:0; background:rgba(44,38,28,.4); z-index:250; display:none;
  align-items:center; justify-content:center; }}
.settings-mask.show {{ display:flex; }}
.settings-panel {{ background:var(--card); border:1px solid var(--line); border-radius:12px;
  width:320px; max-width:88vw; padding:24px 26px; box-shadow:0 16px 50px rgba(0,0,0,.2); }}
.settings-head {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }}
.settings-head span {{ font-size:16px; letter-spacing:.25em; }}
.settings-close {{ background:none; border:none; font-size:22px; color:var(--ink-soft); cursor:pointer; line-height:1; }}
.settings-close:hover {{ color:var(--accent); }}
.settings-group {{ margin-bottom:20px; }}
.settings-label {{ font-size:12px; color:var(--ink-soft); letter-spacing:.2em; margin-bottom:10px; }}
.size-row {{ display:flex; gap:8px; }}
.size-btn {{ flex:1; background:none; border:1px solid var(--line); color:var(--ink); font-size:14px;
  padding:9px 0; border-radius:6px; cursor:pointer; font-family:inherit; }}
.size-btn.active {{ background:var(--accent); border-color:var(--accent); color:#fff; }}
.theme-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }}
.theme-btn {{ display:flex; align-items:center; gap:8px; background:none; border:1px solid var(--line);
  color:var(--ink); font-size:13px; padding:8px 10px; border-radius:6px; cursor:pointer; font-family:inherit; }}
.theme-btn.active {{ border-color:var(--accent); color:var(--accent); background:rgba(138,109,59,.08); }}
.theme-btn .swatch {{ width:16px; height:16px; border-radius:50%; border:1px solid rgba(0,0,0,.15); flex-shrink:0; }}
.theme-btn[data-theme="night"] .swatch, .theme-btn[data-theme="forest"] .swatch {{ border-color:rgba(255,255,255,.25); }}
</style>
</head>
<body>
<div id="topbar">
  <button class="back" id="btnBack" onclick="goShelf()">‹ 书架</button>
  <span class="sep" id="barSep" style="display:none">|</span>
  <span class="bookname" id="barBook"></span>
  <span class="spacer"></span>
  <button class="btn" id="btnToc" style="display:none" onclick="openDrawer()">目录</button>
  <button class="btn" id="btnTop" style="display:none" onclick="scrollTo({{top:0,behavior:'smooth'}})">顶部</button>
  <button class="btn" id="btnSettings" onclick="openSettings()">Aa</button>
</div>
<div id="progress"></div>

<div id="shelf">
  <div class="shelf-head">
    <div class="seal">书斋</div>
    <h1>梅 导 书 斋</h1>
    <div class="rule"></div>
    <p>经书 · 哲学 · 广告 · 故事 — 每日更新</p>
  </div>

  <div class="section-title">经 书</div>
  <div class="book-grid" id="bookGrid"></div>

  <div class="section-title">哲 学</div>
  <div class="daily-grid" id="daily-哲学">{daily_html["哲学"]}</div>

  <div class="section-title">广 告 文 案</div>
  <div class="daily-grid" id="daily-广告文案">{daily_html["广告文案"]}</div>

  <div class="section-title">故 事</div>
  <div class="daily-grid" id="daily-故事">{daily_html["故事"]}</div>

  <div class="shelf-foot">梅导书斋 · 私人图书馆</div>
</div>

<div id="reader"></div>
<div id="chnav">
  <button id="btnPrev">‹ 上一章</button>
  <span class="ch-info" id="chInfo"></span>
  <button id="btnNext">下一章 ›</button>
</div>
<div id="drawer">
  <h3 id="drawerTitle">目录</h3>
  <div class="drawer-book" id="drawerBook"></div>
  <ol id="drawerList"></ol>
</div>
<div id="mask" onclick="closeDrawer()"></div>
<div id="resume">
  <span class="txt" id="resumeTxt"></span>
  <button id="resumeYes" onclick="resumeReading(true)">继续阅读</button>
  <button class="plain" id="resumeNo" onclick="resumeReading(false)">从头开始</button>
</div>
<div id="settings" class="settings-mask" onclick="if(event.target===this)closeSettings()">
  <div class="settings-panel">
    <div class="settings-head"><span>阅读设置</span><button class="settings-close" onclick="closeSettings()">×</button></div>
    <div class="settings-group">
      <div class="settings-label">字号</div>
      <div class="size-row" id="sizeRow">
        <button class="size-btn" data-size="small">小</button>
        <button class="size-btn active" data-size="mid">中</button>
        <button class="size-btn" data-size="large">大</button>
        <button class="size-btn" data-size="xlarge">特大</button>
      </div>
    </div>
    <div class="settings-group">
      <div class="settings-label">主题</div>
      <div class="theme-grid" id="themeGrid">
        <button class="theme-btn active" data-theme="paper"><span class="swatch" style="background:#f6f1e5"></span>宣纸</button>
        <button class="theme-btn" data-theme="parchment"><span class="swatch" style="background:#f3ead6"></span>羊皮</button>
        <button class="theme-btn" data-theme="plain"><span class="swatch" style="background:#ffffff"></span>素白</button>
        <button class="theme-btn" data-theme="night"><span class="swatch" style="background:#1c1a16"></span>夜读</button>
        <button class="theme-btn" data-theme="forest"><span class="swatch" style="background:#202b25"></span>墨绿</button>
      </div>
    </div>
  </div>
</div>

<script>
const BOOKS = {book_titles_json};
const KEY = 'meidao-book-progress-v1';
let PROG = {{}}; try {{ PROG = JSON.parse(localStorage.getItem(KEY)) || {{}}; }} catch(e) {{}}
let currentBook = null, currentIdx = 0;

function refreshShelf() {{
  const grid = document.getElementById('bookGrid');
  grid.innerHTML = '';
  Object.entries(BOOKS).forEach(([book, titles], bi) => {{
    const p = PROG[book];
    const pct = p && p.idx > 0 ? Math.min(100, Math.round(p.idx / (titles.length - 1) * 100)) : 0;
    const card = document.createElement('div');
    card.className = 'book-card';
    card.onclick = () => openBook(book);
    card.innerHTML = `<div class="book-spine"></div>
      <div class="book-kicker">经 书</div>
      <h3>${{book}}</h3>
      <div class="book-sub">${{titles.length}} 篇 · 原文+白话+评析</div>
      <div class="book-meta">
        <span>${{p && p.idx >= titles.length - 1 ? '已读完' : (pct ? '读到 ' + (p.idx + 1) + '/' + titles.length : '未开始')}}</span>
        <span class="progress-bar"><span class="progress-fill" style="width:${{pct}}%"></span></span>
        <span>${{pct}}%</span>
      </div>`;
    grid.appendChild(card);
  }});
}}

function openBook(book) {{
  currentBook = book;
  const p = PROG[book];
  document.getElementById('shelf').style.display = 'none';
  document.getElementById('reader').style.display = 'block';
  document.getElementById('chnav').style.display = 'flex';
  document.getElementById('btnToc').style.display = 'inline-block';
  document.getElementById('btnTop').style.display = 'inline-block';
  document.getElementById('barBook').textContent = book;
  document.getElementById('barSep').style.display = 'inline';
  if (p && p.idx > 0 && p.idx < BOOKS[book].length) {{
    document.getElementById('resumeTxt').textContent = '上次读到 ' + book + ' 第 ' + (p.idx + 1) + ' 篇';
    document.getElementById('resume').style.display = 'flex';
  }}
  showChapter(book, p ? p.idx : 0);
}}

function showChapter(book, idx) {{
  currentIdx = idx;
  const sections = document.querySelectorAll('#reader .chapter[data-book="' + book + '"]');
  const sec = sections[idx];
  if (!sec) return;
  sections.forEach(s => s.style.display = 'none');
  sec.style.display = 'block';
  document.getElementById('chInfo').textContent = '第 ' + (idx + 1) + ' / ' + sections.length + ' 篇';
  document.getElementById('btnPrev').disabled = idx === 0;
  document.getElementById('btnNext').disabled = idx === sections.length - 1;
  document.querySelectorAll('#drawerList .toc-item').forEach(b => b.classList.toggle('current', +b.dataset.idx === idx));
  PROG[book] = {{ idx: idx, at: Date.now() }};
  saveProgress(); refreshShelf();
  scrollTo({{top: 0}});
}}

let scrollTimer = null;
addEventListener('scroll', () => {{
  const h = document.documentElement;
  const pct = h.scrollTop / (h.scrollHeight - h.clientHeight || 1);
  document.getElementById('progress').style.width = (pct * 100) + '%';
  if (!currentBook || document.getElementById('reader').style.display === 'none') return;
  clearTimeout(scrollTimer);
  scrollTimer = setTimeout(() => {{
    PROG[currentBook] = PROG[currentBook] || {{ idx: currentIdx }};
    PROG[currentBook].scrollY = h.scrollTop;
    saveProgress();
  }}, 400);
}});

function saveProgress() {{ localStorage.setItem(KEY, JSON.stringify(PROG)); }}
function resumeReading(yes) {{
  document.getElementById('resume').style.display = 'none';
  if (yes && PROG[currentBook] && PROG[currentBook].scrollY) scrollTo({{top: PROG[currentBook].scrollY}});
}}
function goShelf() {{
  document.getElementById('reader').style.display = 'none';
  document.getElementById('chnav').style.display = 'none';
  document.getElementById('shelf').style.display = 'block';
  document.getElementById('btnToc').style.display = 'none';
  document.getElementById('btnTop').style.display = 'none';
  document.getElementById('barBook').textContent = '';
  document.getElementById('barSep').style.display = 'none';
  document.getElementById('resume').style.display = 'none';
  currentBook = null;
  refreshShelf();
  scrollTo({{top: 0}});
}}
function openDrawer() {{
  const titles = BOOKS[currentBook] || [];
  const list = document.getElementById('drawerList');
  list.innerHTML = '';
  titles.forEach((t, i) => {{
    const li = document.createElement('li');
    const btn = document.createElement('button');
    btn.className = 'toc-item';
    btn.dataset.idx = i;
    btn.innerHTML = '<span class="toc-num">' + t + '</span>';
    btn.onclick = () => {{ showChapter(currentBook, i); closeDrawer(); }};
    li.appendChild(btn); list.appendChild(li);
  }});
  document.getElementById('drawerBook').textContent = currentBook;
  document.getElementById('drawer').classList.add('open');
  document.getElementById('mask').classList.add('show');
}}
function closeDrawer() {{
  document.getElementById('drawer').classList.remove('open');
  document.getElementById('mask').classList.remove('show');
}}
document.getElementById('btnPrev').onclick = () => {{ if (currentIdx > 0) showChapter(currentBook, currentIdx - 1); }};
document.getElementById('btnNext').onclick = () => {{ if (currentIdx < BOOKS[currentBook].length - 1) showChapter(currentBook, currentIdx + 1); }};

const SET_KEY = 'meidao-book-settings-v1';
const SIZES = ['small','mid','large','xlarge'];
let SET = {{}}; try {{ SET = JSON.parse(localStorage.getItem(SET_KEY)) || {{}}; }} catch(e) {{}}
function applySettings() {{
  const size = SIZES.includes(SET.size) ? SET.size : 'mid';
  const theme = SET.theme || 'paper';
  document.body.dataset.size = size;
  document.body.dataset.theme = theme;
  document.querySelectorAll('#sizeRow .size-btn').forEach(b => b.classList.toggle('active', b.dataset.size === size));
  document.querySelectorAll('#themeGrid .theme-btn').forEach(b => b.classList.toggle('active', b.dataset.theme === theme));
  localStorage.setItem(SET_KEY, JSON.stringify(SET));
}}
function openSettings() {{ document.getElementById('settings').classList.add('show'); }}
function closeSettings() {{ document.getElementById('settings').classList.remove('show'); }}
document.querySelectorAll('#sizeRow .size-btn').forEach(b => b.onclick = () => {{ SET.size = b.dataset.size; applySettings(); }});
document.querySelectorAll('#themeGrid .theme-btn').forEach(b => b.onclick = () => {{ SET.theme = b.dataset.theme; applySettings(); }});
applySettings();
refreshShelf();
</script>
</body>
</html>'''

# 注入经书正文
reader_html = books_html
html_doc = html_doc.replace('<div id="reader"></div>', '<div id="reader">' + reader_html + '</div>')

out = os.path.join(BASE, 'index.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html_doc)
print(f"\nOK → {out} ({len(html_doc)//1024} KB, {len(books)} 本经书)")
