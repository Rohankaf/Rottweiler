import streamlit as st
import time
import base64
import os
import re
import html as html_module
from datetime import datetime, timezone

# ── Load .env ──────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from llm_prompt import ClaudeAI
from tor_search import SEARCH_ENGINES, fetch_search_results, _score
from catching import scrape_single
from timeline import uptime_bar_html

st.set_page_config(
    page_title="ROTTWEILER — Dark Web Intelligence",
    page_icon="🐕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════
# HTML SANITIZER  — strips ALL tags and escapes special chars
# Apply this to ANY user-data string before putting it inside st.markdown HTML
# ══════════════════════════════════════════════════════════════════════════

_TAG_RE    = re.compile(r"<[^>]+>")       # matches any HTML/XML tag
_MULTI_SPC = re.compile(r"\s{2,}")        # collapse whitespace

def clean(text: str, max_len: int = 120) -> str:
    """
    Strip all HTML tags, decode entities, collapse whitespace, truncate.
    Safe to embed inside an HTML attribute or text node.
    """
    if not text:
        return ""
    text = _TAG_RE.sub("", str(text))                  # remove <tags>
    text = html_module.unescape(text)                  # &lt; → <  etc.
    text = _TAG_RE.sub("", text)                       # second pass (nested)
    text = _MULTI_SPC.sub(" ", text).strip()
    text = html_module.escape(text)                    # re-escape for HTML output
    return text[:max_len] if max_len else text

# ── Logo embed ──────────────────────────────────────────────────────────────
LOGO_B64 = ""
logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        LOGO_B64 = base64.b64encode(f.read()).decode()

# LLM_MODELS is now defined in claude_ai.MODEL_REGISTRY — imported below as needed

# ══════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --red:        #e63946;
    --red-dim:    #9b1c26;
    --red-glow:   rgba(230,57,70,0.35);
    --red-subtle: rgba(230,57,70,0.07);
    --bg:         #0a0a0b;
    --bg2:        #0f0f11;
    --bg3:        #141417;
    --border:     #1e1e24;
    --border2:    #2a1a1e;
    --text:       #c9cdd4;
    --text-dim:   #5a5e6a;
    --mono:       'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    --head:       'Space Grotesk', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    --body:       'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--body) !important;
}

[data-testid="stAppViewContainer"]::before {
    content:'';
    position:fixed; inset:0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 3px,
        rgba(230,57,70,0.008) 3px, rgba(230,57,70,0.008) 4px
    );
    pointer-events:none; z-index:9998;
}

[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border2) !important;
}
[data-testid="stSidebar"] section { padding-top: 0 !important; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-bottom: 1px solid var(--border2) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-dim) !important;
    font-family: var(--head) !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    border: none !important;
    padding: 12px 28px !important;
}
.stTabs [aria-selected="true"] {
    color: var(--red) !important;
    border-bottom: 2px solid var(--red) !important;
    background: var(--red-subtle) !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea textarea,
.stNumberInput input {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 13px !important;
    border-radius: 2px !important;
    caret-color: var(--red) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--red-dim) !important;
    box-shadow: 0 0 0 1px var(--red-dim), 0 0 14px var(--red-glow) !important;
    outline: none !important;
}

/* Buttons */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--red-dim) !important;
    color: var(--red) !important;
    font-family: var(--head) !important;
    font-size: 11px !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    transition: all 0.2s !important;
    padding: 10px 18px !important;
}
.stButton > button:hover {
    background: var(--red-subtle) !important;
    border-color: var(--red) !important;
    box-shadow: 0 0 20px var(--red-glow) !important;
}
.hunt-btn .stButton > button {
    background: var(--red) !important;
    color: #fff !important;
    font-weight: 700 !important;
    letter-spacing: 4px !important;
    font-size: 13px !important;
    border: none !important;
    padding: 12px 0 !important;
}
.hunt-btn .stButton > button:hover {
    background: #c1121f !important;
    box-shadow: 0 0 28px var(--red-glow) !important;
}

/* Selectbox */
.stSelectbox > div > div,
.stSelectbox [data-baseweb="select"] > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    border-radius: 2px !important;
}
.stSelectbox [data-baseweb="select"] span { color: var(--text) !important; }

/* Metrics */
[data-testid="stMetric"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border2) !important;
    border-left: 3px solid var(--red-dim) !important;
    padding: 14px !important;
    border-radius: 2px !important;
}
[data-testid="stMetricValue"] {
    color: var(--red) !important;
    font-family: var(--head) !important;
    font-size: 28px !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-dim) !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-family: var(--head) !important;
}

/* Divider */
.rott-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--red-dim), transparent);
    margin: 24px 0;
    opacity: 0.4;
}

/* Capability cards */
.cap-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 8px;
}
.cap-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 20px;
    transition: border-color 0.2s, background 0.2s;
}
.cap-card:hover {
    border-color: var(--red-dim);
    background: var(--red-subtle);
}
.cap-icon  { font-size: 20px; margin-bottom: 10px; color: var(--red); }
.cap-title { font-family: var(--body); font-size: 15px; font-weight: 600; color: #e0e4ec; margin-bottom: 6px; }
.cap-desc  { font-family: var(--body); font-size: 13px; color: var(--text-dim); line-height: 1.5; font-weight: 300; }

/* Status dot */
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #00c97a;
    display: inline-block;
    animation: blink-dot 2s ease-in-out infinite;
}
@keyframes blink-dot {
    0%,100% { opacity:1; box-shadow: 0 0 6px #00c97a; }
    50%      { opacity:0.3; box-shadow: none; }
}

/* Terminal */
.terminal-box {
    background: #050507;
    border: 1px solid var(--border2);
    padding: 20px 24px;
    font-family: var(--mono);
    font-size: 12px;
    color: var(--red);
    line-height: 1.9;
    max-height: 480px;
    overflow-y: auto;
    border-radius: 2px;
}

/* Result cards */
.site-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--red);
    padding: 13px 18px;
    margin: 5px 0;
    font-family: var(--mono);
    font-size: 12px;
    border-radius: 0 2px 2px 0;
    word-break: break-word;
}
.site-card.offline { border-left-color: #333; opacity: 0.55; }
.site-card.unknown { border-left-color: #4a3a10; opacity: 0.65; }

/* Stat cards */
.stat-row {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 12px;
    margin: 18px 0;
}
.stat-card {
    background: var(--bg2);
    border: 1px solid var(--border2);
    border-top: 2px solid var(--red);
    padding: 18px 20px;
    border-radius: 2px;
    text-align: center;
}
.stat-label {
    font-family: var(--head);
    font-size: 10px;
    letter-spacing: 3px;
    color: var(--red);
    margin-bottom: 8px;
    text-transform: uppercase;
}
.stat-val {
    font-family: var(--head);
    font-size: 32px;
    font-weight: 700;
    color: #fff;
    line-height: 1;
}

/* Section header */
.sec-header {
    font-family: var(--head);
    font-size: 10px;
    letter-spacing: 4px;
    color: var(--text-dim);
    text-transform: uppercase;
    margin: 28px 0 14px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.sec-header::after { content:''; flex:1; height:1px; background:var(--border2); }

/* Sidebar */
.sidebar-label {
    font-family: var(--head);
    font-size: 9px;
    letter-spacing: 3px;
    color: var(--red);
    text-transform: uppercase;
    margin: 18px 0 8px;
}
.sidebar-engine {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--text-dim);
    padding: 3px 0;
    border-bottom: 1px solid var(--border);
}

/* Animations */
@keyframes blink { 0%,50%{opacity:1} 51%,100%{opacity:0} }
.blink { animation: blink 1s infinite; }
@keyframes fadein { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.fadein { animation: fadein 0.4s ease forwards; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--red-dim); border-radius: 2px; }

/* Progress bar */
.stProgress > div > div > div { background: var(--red) !important; }

/* Hero */
.rott-hero { text-align: center; padding: 32px 0 16px; }
.rott-logo-wrap { display: flex; justify-content: center; margin-bottom: 14px; }
.rott-logo-img {
    width: 160px; height: 160px; object-fit: contain;
    filter: drop-shadow(0 0 30px rgba(230,57,70,0.7));
    animation: logo-pulse 3s ease-in-out infinite;
}
@keyframes logo-pulse {
    0%,100% { filter: drop-shadow(0 0 24px rgba(230,57,70,0.55)); }
    50%      { filter: drop-shadow(0 0 48px rgba(230,57,70,1.0)); }
}
.rott-title {
    font-family: var(--head);
    font-size: 58px; font-weight: 900; letter-spacing: 16px;
    color: #fff; text-shadow: 0 0 50px rgba(230,57,70,0.4);
    margin: 0 0 6px; line-height: 1;
}
.rott-sub  { font-family: var(--head); font-size: 11px; letter-spacing: 7px; color: var(--text-dim); margin-bottom: 14px; }
.rott-desc { font-family: var(--body); font-size: 15px; color: var(--text-dim); max-width: 580px; margin: 0 auto; line-height: 1.65; font-weight: 300; }

/* Result title row */
.result-title {
    font-size: 11px;
    color: #8a9ab0;
    margin-bottom: 4px;
    font-family: var(--body);
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 80%;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────
if "discovered_sites"  not in st.session_state: st.session_state.discovered_sites  = []
if "hunt_result"       not in st.session_state: st.session_state.hunt_result       = None
if "claude_ai"         not in st.session_state: st.session_state.claude_ai         = ClaudeAI()
if "selected_model"    not in st.session_state: st.session_state.selected_model    = "Claude Sonnet"
if "intel_brief"       not in st.session_state: st.session_state.intel_brief       = None
if "smart_online_only" not in st.session_state: st.session_state.smart_online_only = False

claude_ai = st.session_state.claude_ai

# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    if LOGO_B64:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:16px 0 20px;">
            <img src="data:image/png;base64,{LOGO_B64}"
                 style="width:40px;height:40px;object-fit:contain;
                 filter:drop-shadow(0 0 8px rgba(230,57,70,0.8));">
            <span style="font-family:'Space Grotesk',system-ui,sans-serif;font-size:15px;
                  font-weight:700;letter-spacing:3px;color:#fff;">ROTTWEILER</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="padding:16px 0 20px;font-family:\'Space Grotesk\',system-ui,sans-serif;font-size:18px;font-weight:700;letter-spacing:3px;color:#fff;">🐕 ROTTWEILER</div>', unsafe_allow_html=True)

    active_count = sum(1 for s in st.session_state.discovered_sites if s.get("status") == "online")

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
        <span class="status-dot"></span>
        <span style="font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11px;color:#00c97a;">ONLINE</span>
        <span style="margin-left:auto;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11px;color:#5a5e6a;">{len(SEARCH_ENGINES)} ENGINES</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#2a1a1e;margin:14px 0;"></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    c1.metric("Sites Found", len(st.session_state.discovered_sites))
    c2.metric("Active", active_count)

    st.markdown('<div style="height:1px;background:#2a1a1e;margin:14px 0;"></div>', unsafe_allow_html=True)

    # Find a model
    st.markdown('<div style="font-family:\'Space Grotesk\',system-ui,sans-serif;font-size:9px;letter-spacing:3px;color:#e63946;text-transform:uppercase;margin-bottom:6px;">FIND A MODEL</div>', unsafe_allow_html=True)

    from llm_prompt import MODEL_DISPLAY_NAMES
    model_keys = MODEL_DISPLAY_NAMES
    if st.session_state.selected_model not in model_keys:
        st.session_state.selected_model = model_keys[0]
    default_idx = model_keys.index(st.session_state.selected_model)

    selected_label = st.selectbox(
        "LLM Model",
        options=model_keys,
        index=default_idx,
        label_visibility="collapsed",
        key="model_selector"
    )
    # If model changed, update session state AND the live claude_ai instance
    if selected_label != st.session_state.selected_model:
        st.session_state.selected_model = selected_label
        st.session_state.claude_ai.set_model(selected_label)
        claude_ai = st.session_state.claude_ai

    # Show live API key status for the selected provider
    key_ok, key_msg = st.session_state.claude_ai.check_api_key()
    key_color  = "#00c97a" if key_ok else "#f0a500"
    key_icon   = "✅" if key_ok else "⚠️"
    st.markdown(
        f'<div style="font-family:\'JetBrains Mono\',ui-monospace,monospace;font-size:10px;color:{key_color};'
        f'margin:6px 0 14px;padding:6px 8px;background:#0a0a0b;'
        f'border:1px solid #1e1e24;border-radius:2px;">'
        f'{key_icon} {html_module.escape(key_msg)}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div style="height:1px;background:#2a1a1e;margin:4px 0 12px;"></div>', unsafe_allow_html=True)

    if st.button("REFRESH",  use_container_width=True): st.rerun()
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
    if st.button("CLEAR ALL", use_container_width=True):
        st.session_state.discovered_sites = []
        st.session_state.hunt_result      = None
        st.session_state.intel_brief      = None
        st.rerun()

    st.markdown('<div class="sidebar-label">Search Engines</div>', unsafe_allow_html=True)
    for engine in SEARCH_ENGINES:
        st.markdown(f'<div class="sidebar-engine">• {clean(engine["name"], 40)}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════
logo_img_html = (
    f'<img src="data:image/png;base64,{LOGO_B64}" class="rott-logo-img" alt="Rottweiler">'
    if LOGO_B64 else
    '<div style="font-size:120px;line-height:1;">🐕</div>'
)

st.markdown(f"""
<div class="rott-hero">
    <div class="rott-logo-wrap">{logo_img_html}</div>
    <div class="rott-title">ROTTWEILER</div>
    <div class="rott-sub">DARK WEB INTELLIGENCE ENGINE</div>
    <div class="rott-desc">
        Multi-engine Tor search with AI-powered analysis. Hunt across hidden
        services, extract onion links, and generate actionable intelligence.
    </div>
</div>
<div class="rott-divider"></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["⬡  HUNT", "◉  AI ANALYSIS", "⚙  SETTINGS"])

# ─────────────────────────────────────────────────────────────────────────
# TAB 1 — HUNT
# ─────────────────────────────────────────────────────────────────────────
with tab1:

    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input(
            "Search query",
            placeholder="What You Want To Hunt Down",
            key="search_query",
            label_visibility="collapsed",
        )
    with col2:
        st.markdown('<div class="hunt-btn">', unsafe_allow_html=True)
        hunt_btn = st.button("HUNT", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    engine_names_html = " &nbsp;·&nbsp; ".join(
        f'<span style="color:#e63946;font-family:\'JetBrains Mono\',ui-monospace,monospace;font-size:11px;">{clean(e["name"],20)}</span>'
        for e in SEARCH_ENGINES[:3]
    )
    model_short = clean(st.session_state.selected_model.split(" ")[0].upper(), 20)
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;padding:5px 2px 18px;">
        <div style="font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11px;color:#5a5e6a;">
            ENGINES: {engine_names_html}
            <span style="color:#2a2e38;"> +{len(SEARCH_ENGINES)-3} more</span>
        </div>
        <div style="font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11px;color:#5a5e6a;">
            MODEL: <span style="color:#e63946;">{model_short}</span>
            &nbsp;|&nbsp; AI: <span style="color:#e63946;">ON</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    max_results = st.number_input("Max Results", min_value=10, max_value=200, value=50, step=10)

    # ── Run hunt ──────────────────────────────────────────────────────
    if hunt_btn:
        if not search_query.strip():
            st.warning("Enter a search query to begin hunting.")
        else:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            from tor_search import fetch_search_results, SEARCH_ENGINES, _score, _normalise
            from catching import scrape_multiple
            import urllib.parse, re

            q_safe      = clean(search_query, 80)
            total_eng   = len(SEARCH_ENGINES)
            prog        = st.progress(0)
            term        = st.empty()   # live terminal display

            # ── helper to re-render the terminal ──────────────────────
            def render_term(lines, stage_label):
                lines_html = "<br>".join(lines[-18:])   # show last 18 log lines
                term.markdown(
                    f'<div class="terminal-box" style="max-height:320px;overflow-y:auto;">'
                    f'<span style="color:#5a5e6a;letter-spacing:2px;font-size:10px;">'
                    f'{stage_label}</span><br><br>'
                    f'{lines_html}'
                    f'<br><span class="blink">▌</span></div>',
                    unsafe_allow_html=True
                )

            # ════════════════════════════════════════════════════════
            # STAGE 1 — Search engines (live per-engine updates)
            # ════════════════════════════════════════════════════════
            log_lines   = [f'<span style="color:#5a5e6a;">QUERY: {q_safe}</span>',
                           f'<span style="color:#5a5e6a;">ENGINES: {total_eng} queued via Tor</span>', ""]
            render_term(log_lines, "[ 1 / 3 ]  SEARCHING ENGINES")
            prog.progress(2)

            raw_results  = []
            seen_links   = set()
            done_count   = 0

            with ThreadPoolExecutor(max_workers=10) as executor:
                future_map = {
                    executor.submit(fetch_search_results, eng, search_query): eng
                    for eng in SEARCH_ENGINES
                }
                for future in as_completed(future_map):
                    eng        = future_map[future]
                    done_count += 1
                    pct        = int(2 + (done_count / total_eng) * 38)   # 2 → 40%
                    try:
                        results = future.result()
                        count   = len(results)
                        raw_results.extend(results)
                        if count > 0:
                            color = "#e63946"
                            icon  = "●"
                            msg   = f"{count} links"
                        else:
                            color = "#5a5e6a"
                            icon  = "○"
                            msg   = "no results"
                    except Exception as e:
                        color = "#f0a500"
                        icon  = "✕"
                        msg   = f"error: {str(e)[:40]}"

                    eng_name = clean(eng["name"], 22)
                    log_lines.append(
                        f'<span style="color:{color};">{icon}</span>'
                        f' <span style="color:#8a9ab0;">{eng_name:<22}</span>'
                        f' <span style="color:{color};">{msg}</span>'
                        f' <span style="color:#2a2e38;">({done_count}/{total_eng})</span>'
                    )
                    render_term(log_lines, "[ 1 / 3 ]  SEARCHING ENGINES")
                    prog.progress(pct)

            # Deduplicate + sort
            unique = []
            seen_set = set()
            for item in raw_results:
                lnk = item["link"]
                if lnk not in seen_set:
                    seen_set.add(lnk)
                    unique.append(item)
            unique.sort(key=lambda x: _score(x, search_query), reverse=True)
            unique = unique[:int(max_results)]

            log_lines.append("")
            log_lines.append(
                f'<span style="color:#00c97a;">SEARCH COMPLETE — '
                f'{len(raw_results)} raw → {len(unique)} unique links</span>'
            )
            render_term(log_lines, "[ 1 / 3 ]  SEARCHING ENGINES")
            prog.progress(40)

            # ════════════════════════════════════════════════════════
            # STAGE 2 — Scrape pages (batch, show running count)
            # ════════════════════════════════════════════════════════
            log_lines.append("")
            log_lines.append(
                f'<span style="color:#5a5e6a;">SCRAPING {len(unique)} PAGES VIA TOR...</span>'
            )
            render_term(log_lines, "[ 2 / 3 ]  SCRAPING PAGES")
            prog.progress(42)

            from catching import scrape_single
            scraped      = {}
            scrape_done  = 0
            scrape_total = len(unique)

            with ThreadPoolExecutor(max_workers=5) as executor:
                future_map2 = {
                    executor.submit(scrape_single, item): item
                    for item in unique
                }
                for future in as_completed(future_map2):
                    scrape_done += 1
                    pct2 = int(42 + (scrape_done / max(scrape_total, 1)) * 35)  # 42 → 77%
                    try:
                        url_key, data = future.result()
                        scraped[url_key] = data
                        st_icon  = "●" if data.get("status") == "online" else "○"
                        st_color = "#e63946" if data.get("status") == "online" else "#5a5e6a"
                        short_url = url_key[7:47] + "…" if len(url_key) > 50 else url_key[7:]
                        log_lines.append(
                            f'<span style="color:{st_color};">{st_icon}</span>'
                            f' <span style="color:#8a9ab0;font-size:11px;">{short_url}</span>'
                        )
                    except Exception:
                        pass
                    render_term(log_lines, f"[ 2 / 3 ]  SCRAPING PAGES  ({scrape_done}/{scrape_total})")
                    prog.progress(pct2)

            log_lines.append("")
            online_count = sum(1 for d in scraped.values() if d.get("status") == "online")
            log_lines.append(
                f'<span style="color:#00c97a;">SCRAPE COMPLETE — '
                f'{online_count} online / {scrape_total} total</span>'
            )
            render_term(log_lines, "[ 2 / 3 ]  SCRAPING PAGES")
            prog.progress(78)

            # ════════════════════════════════════════════════════════
            # STAGE 3 — Build records + AI summary
            # ════════════════════════════════════════════════════════
            log_lines.append("")
            log_lines.append('<span style="color:#5a5e6a;">BUILDING SITE RECORDS...</span>')
            render_term(log_lines, "[ 3 / 3 ]  AI ANALYSIS")
            prog.progress(80)

            ts         = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            all_sites  = []
            active_sites = []

            for item in unique:
                url  = item["link"]
                data = scraped.get(url, {})
                status_val = data.get("status", "offline")
                title      = data.get("title") or item.get("title") or url
                content    = data.get("content", "")

                site_record = {
                    "url":           url,
                    "title":         title,
                    "title_safe":    clean(title, 100),
                    "content":       content,
                    "status":        status_val,
                    "status_code":   data.get("status_code"),
                    "response_time": 0,
                    "discovered_at": ts,
                    "query":         search_query,
                    "tags":          [search_query],
                    "description":   title,
                }
                all_sites.append(site_record)
                if status_val == "online":
                    active_sites.append(site_record)

            log_lines.append('<span style="color:#5a5e6a;">GENERATING AI INTEL BRIEF...</span>')
            render_term(log_lines, "[ 3 / 3 ]  AI ANALYSIS")
            prog.progress(88)

            summary = ""
            sites_for_ai = active_sites[:20] if active_sites else all_sites[:20]
            if sites_for_ai and claude_ai:
                try:
                    summary = claude_ai.summarize_results(search_query, sites_for_ai)
                except Exception as e:
                    summary = f"[AI summary error: {e}]"

            log_lines.append(
                f'<span style="color:#00c97a;">HUNT COMPLETE — '
                f'{len(active_sites)} active / {len(all_sites)} discovered</span>'
            )
            render_term(log_lines, "[ 3 / 3 ]  AI ANALYSIS")
            prog.progress(100)

            st.session_state.discovered_sites = all_sites
            # Smart display filter: if user asked for ≤30 results, show online only by default
            # (they want quality over quantity); above 30 show everything
            st.session_state.smart_online_only = (int(max_results) <= 30)
            st.session_state.hunt_result      = {
                "discovered":   len(all_sites),
                "active":       len(active_sites),
                "all_sites":    all_sites,
                "active_sites": active_sites,
                "summary":      summary,
            }
            st.session_state.intel_brief = summary

            time.sleep(0.6)
            term.empty()
            prog.empty()

    # ── Inline results ──────────────────────────────────────────────────
    if st.session_state.hunt_result and st.session_state.discovered_sites:
        result = st.session_state.hunt_result
        sites  = st.session_state.discovered_sites

        total   = len(sites)
        online  = sum(1 for s in sites if s["status"] == "online")
        offline = sum(1 for s in sites if s["status"] == "offline")
        unknown = sum(1 for s in sites if s["status"] == "unknown")

        # Stat cards
        st.markdown(f"""
        <div class="stat-row fadein">
            <div class="stat-card">
                <div class="stat-label">Search Results</div>
                <div class="stat-val">{result['discovered']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Active Online</div>
                <div class="stat-val">{online}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Offline / Unknown</div>
                <div class="stat-val">{offline + unknown}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # AI summary (cached so it doesn't regenerate on every rerun)
        brief = st.session_state.intel_brief
        if not brief:
            last_query = sites[0].get("query", search_query) if sites else search_query
            site_data  = [
                {
                    "url": s["url"], "status": s["status"],
                    "uptime_pct": 100 if s["status"] == "online" else 0,
                    "tags": [s.get("query","")],
                    "title": s.get("title_safe", s.get("title","")),
                    "content": s.get("content","")[:300],
                }
                for s in sites[:30]
            ]
            with st.spinner("Generating intelligence brief..."):
                brief = claude_ai.summarize_results(last_query, site_data)
            st.session_state.intel_brief = brief

        q_safe = clean(search_query or (sites[0].get("query","") if sites else ""), 60)
        st.markdown('<div class="sec-header">INVESTIGATION SUMMARY</div>', unsafe_allow_html=True)
        # Brief is AI text — safe to render as-is but wrap in terminal box
        brief_html = brief.replace("\n", "<br>") if brief else "No summary available."
        st.markdown(
            f'<div class="terminal-box fadein">{brief_html}'
            f'<br><br><span style="color:#5a5e6a;">QUERY: {q_safe} &nbsp;|&nbsp; '
            f'TOTAL: {total} &nbsp;|&nbsp; ACTIVE: {online}</span>'
            f'<span class="blink">▌</span></div>',
            unsafe_allow_html=True
        )

        # Filter + list
        st.markdown('<div class="sec-header">SOURCE LINKS</div>', unsafe_allow_html=True)

        # Smart default: ≤30 max_results requested → default to Online Only (quality focus)
        #                >30 max_results requested → default to All (breadth focus)
        filter_options   = ["All", "Online Only", "Offline Only"]
        smart_default    = "Online Only" if st.session_state.smart_online_only else "All"
        smart_default_i  = filter_options.index(smart_default)

        fcol1, fcol2 = st.columns([1, 3])
        with fcol1:
            filter_status = st.selectbox(
                "Filter", filter_options,
                index=smart_default_i,
                key="hunt_filter",
                help="Auto-set to 'Online Only' when Max Results ≤ 30"
            )
        with fcol2:
            use_timeline = st.checkbox("Timeline bars", value=False, key="hunt_timeline")

        # Show hint about smart filter
        if st.session_state.smart_online_only and filter_status == "Online Only":
            st.caption("💡 Showing online-only (auto) — you requested ≤30 results. Change filter above to see all.")

        filtered = sites
        if filter_status == "Online Only":
            filtered = [s for s in sites if s["status"] == "online"]
        elif filter_status == "Offline Only":
            filtered = [s for s in sites if s["status"] == "offline"]

        filtered = sorted(filtered, key=lambda x: (0 if x["status"] == "online" else 1, x["url"]))

        st.markdown(
            f'<p style="font-family:\'Share Tech Mono\',monospace;font-size:11px;'
            f'color:#5a5e6a;margin-bottom:10px;">SHOWING {len(filtered)} OF {total} RESULTS</p>',
            unsafe_allow_html=True
        )

        for i, site in enumerate(filtered, 1):
            if use_timeline:
                st.markdown(uptime_bar_html(site), unsafe_allow_html=True)
            else:
                status_val    = site.get("status", "unknown")
                url           = site.get("url", "")
                resp_time     = site.get("response_time", 0)
                discovered_at = site.get("discovered_at", "")

                # ── KEY FIX: use pre-sanitized title_safe ──────────────
                title_safe = site.get("title_safe") or clean(site.get("title", ""), 100)
                # If still empty or same as URL, hide it
                show_title = title_safe and title_safe != clean(url, 100)

                color  = {"online": "#e63946", "offline": "#444", "unknown": "#5a4010"}.get(status_val, "#444")
                symbol = {"online": "●", "offline": "○", "unknown": "◌"}.get(status_val, "?")
                card_cls = "offline" if status_val != "online" else ""

                # Safely escape URL for href (keep raw, don't clean it)
                href = html_module.escape(url, quote=True)

                # Double-escape title to prevent any HTML leaking through
                safe_title_html = html_module.escape(title_safe.strip()) if title_safe else ""
                title_row = (
                    f'<div class="result-title">{safe_title_html}</div>'
                    if show_title and safe_title_html else ""
                )
                resp_time_html = f"{resp_time}ms" if resp_time else ""

                # Build card as a single concatenated string — multi-line f-strings with
                # closing </div> tags confuse Streamlit's markdown parser, causing it to
                # render stray </div> tokens as visible text nodes outside the card.
                card_html = (
                    f'<div class="site-card {card_cls} fadein">'
                    + title_row
                    + f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">'
                    + f'<div style="min-width:0;flex:1;">'
                    + f'<span style="color:#5a5e6a;margin-right:6px;font-size:10px;">{i}.</span>'
                    + f'<span style="color:{color};margin-right:6px;">{symbol}</span>'
                    + f'<a href="{href}" target="_blank" rel="noopener noreferrer"'
                    + f' style="color:#c9cdd4;text-decoration:none;word-break:break-all;font-size:12px;"'
                    + f' onmouseover="this.style.color=\'#e63946\'"'
                    + f' onmouseout="this.style.color=\'#c9cdd4\'">{html_module.escape(url)}</a>'
                    + f'</div>'
                    + f'<div style="flex-shrink:0;font-size:10px;color:#5a5e6a;white-space:nowrap;">{resp_time_html}</div>'
                    + f'</div>'
                    + f'<div style="margin-top:6px;font-size:10px;color:#2a2e38;">'
                    + f'{html_module.escape(discovered_at)}'
                    + f'&nbsp;|&nbsp; STATUS: <span style="color:{color};">{status_val.upper()}</span>'
                    + f'</div>'
                    + f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

    elif not st.session_state.hunt_result:
        st.markdown('<div class="rott-divider"></div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="text-align:center;font-family:Orbitron,sans-serif;font-size:10px;'
            'letter-spacing:5px;color:#5a5e6a;margin-bottom:16px;">CAPABILITIES</p>',
            unsafe_allow_html=True
        )
        st.markdown("""
        <div class="cap-grid">
            <div class="cap-card">
                <div class="cap-icon">⊕</div>
                <div class="cap-title">Multi-Engine Search</div>
                <div class="cap-desc">Query across 18+ Tor engines concurrently with ThreadPoolExecutor</div>
            </div>
            <div class="cap-card">
                <div class="cap-icon">◈</div>
                <div class="cap-title">Onion Extraction</div>
                <div class="cap-desc">Auto-discover and validate .onion URLs with strict filtering</div>
            </div>
            <div class="cap-card">
                <div class="cap-icon">◉</div>
                <div class="cap-title">AI Analysis</div>
                <div class="cap-desc">LLM-powered summaries and threat context — multiple providers</div>
            </div>
            <div class="cap-card">
                <div class="cap-icon">◎</div>
                <div class="cap-title">Page Scraping</div>
                <div class="cap-desc">Fetches and reads actual page content for richer AI analysis</div>
            </div>
            <div class="cap-card">
                <div class="cap-icon">⊘</div>
                <div class="cap-title">Secure Routing</div>
                <div class="cap-desc">All traffic through Tor SOCKS5 proxy — zero attribution</div>
            </div>
            <div class="cap-card">
                <div class="cap-icon">≡</div>
                <div class="cap-title">Result Archival</div>
                <div class="cap-desc">Session storage with export, filter, and AI re-analysis</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────
# TAB 2 — AI ANALYSIS
# ─────────────────────────────────────────────────────────────────────────
with tab2:
    if not st.session_state.discovered_sites:
        st.markdown("""
        <div class="terminal-box">
        NO DATA TO ANALYZE.<br><br>
        → Switch to HUNT tab<br>
        → Run a search query<br>
        → Return here for deep analysis<br><br>
        <span class="blink">▌</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        sites     = st.session_state.discovered_sites
        total_s   = len(sites)
        online_s  = sum(1 for s in sites if s["status"] == "online")
        offline_s = sum(1 for s in sites if s["status"] == "offline")
        unknown_s = sum(1 for s in sites if s["status"] == "unknown")

        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-card"><div class="stat-label">Total Results</div><div class="stat-val">{total_s}</div></div>
            <div class="stat-card"><div class="stat-label">Active (Online)</div><div class="stat-val">{online_s}</div></div>
            <div class="stat-card"><div class="stat-label">Offline / Unknown</div><div class="stat-val">{offline_s + unknown_s}</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sec-header">INTELLIGENCE BRIEF</div>', unsafe_allow_html=True)

        if st.button("⊕  GENERATE INTEL BRIEF", use_container_width=True):
            with st.spinner("Analyzing with Claude..."):
                last_query = sites[0].get("query", "dark web") if sites else "dark web"
                site_data  = [
                    {
                        "url": s["url"], "status": s["status"],
                        "uptime_pct": 100 if s["status"] == "online" else 0,
                        "tags": [s.get("query","")],
                        "title": s.get("title_safe", ""),
                        "content": s.get("content","")[:300],
                    }
                    for s in sites[:30]
                ]
                brief = claude_ai.summarize_results(last_query, site_data)
                st.session_state.intel_brief = brief
                st.markdown(
                    f'<div class="terminal-box">{brief.replace(chr(10),"<br>")}'
                    f'<span class="blink">▌</span></div>',
                    unsafe_allow_html=True
                )

        st.markdown('<div class="sec-header">CUSTOM QUERY</div>', unsafe_allow_html=True)

        custom_prompt = st.text_area(
            "Custom AI analysis prompt",
            placeholder="What patterns do you see? What threat categories are most active?",
            height=100,
            label_visibility="collapsed",
        )

        if st.button("◉  RUN ANALYSIS", use_container_width=True):
            if custom_prompt.strip():
                with st.spinner("Analyzing..."):
                    site_data = [
                        {
                            "url": s["url"], "status": s["status"],
                            "uptime_pct": 100 if s["status"] == "online" else 0,
                            "tags": [s.get("query","")], "check_count": 1,
                            "title": s.get("title_safe",""),
                            "content": s.get("content","")[:400],
                        }
                        for s in sites[:50]
                    ]
                    result_text = claude_ai.analyze_sites(custom_prompt, site_data)
                    st.markdown(
                        f'<div class="terminal-box">{result_text.replace(chr(10),"<br>")}'
                        f'<span class="blink">▌</span></div>',
                        unsafe_allow_html=True
                    )
            else:
                st.warning("Enter a prompt first.")

        st.markdown('<div class="sec-header">RESPONSE METRICS</div>', unsafe_allow_html=True)
        online_timed = [s for s in sites if s["status"] == "online" and s.get("response_time", 0) > 0]
        if online_timed:
            avg_r = sum(s["response_time"] for s in online_timed) / len(online_timed)
            min_r = min(s["response_time"] for s in online_timed)
            max_r = max(s["response_time"] for s in online_timed)
            st.markdown(f"""
            <div class="terminal-box" style="max-height:160px;">
            RESPONSE TIME ANALYSIS<br>──────────────────────────────<br>
            AVERAGE : {avg_r:>7.0f} ms<br>
            FASTEST : {min_r:>7.0f} ms<br>
            SLOWEST : {max_r:>7.0f} ms<br>
            SAMPLES : {len(online_timed):>7}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="terminal-box" style="max-height:120px;">NO TIMING DATA AVAILABLE</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────
# TAB 3 — SETTINGS
# ─────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec-header">PROVIDER CONFIGURATION</div>', unsafe_allow_html=True)

    for pname, env in [
        ("Anthropic (Claude)",  "ANTHROPIC_API_KEY"),
        ("OpenAI (GPT-4)",      "OPENAI_API_KEY"),
        ("Groq (Llama/Mixtral)","GROQ_API_KEY"),
        ("OpenRouter",          "OPENROUTER_API_KEY"),
    ]:
        is_set = bool(os.getenv(env))
        color  = "#00c97a" if is_set else "#f0a500"
        icon   = "✅" if is_set else "⚠️"
        label  = "configured" if is_set else "API key not set"
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:10px 14px;margin:4px 0;background:#0f0f11;
                    border:1px solid #1e1e24;border-radius:2px;">
            <span style="font-family:'JetBrains Mono',ui-monospace,monospace;font-size:12px;color:#c9cdd4;">
                {icon} &nbsp;<strong style="color:#fff;">{html_module.escape(pname)}</strong>
            </span>
            <span style="font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11px;color:{color};">{label}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sec-header">TOR CONFIGURATION</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="terminal-box" style="max-height:130px;">
    PROXY   : socks5h://127.0.0.1:9050<br>
    TIMEOUT : 40s per engine<br>
    THREADS : up to 10 concurrent search + 5 scrape<br>
    ENGINES : 18 search engines indexed
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-header">ABOUT</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Inter',system-ui,sans-serif;font-size:14px;color:#5a5e6a;line-height:1.8;">
    ROTTWEILER — Dark Web Intelligence Engine<br>
    Built with Streamlit · Tor · Anthropic Claude<br>
    All traffic routed through Tor for anonymity.
    </div>
    """, unsafe_allow_html=True)