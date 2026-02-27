# ui.py
import streamlit as st
import html as html_module
import base64
import os
import re

_TAG_RE    = re.compile(r"<[^>]+>")
_MULTI_SPC = re.compile(r"\s{2,}")

def clean(text: str, max_len: int = 120) -> str:
    if not text:
        return ""
    text = _TAG_RE.sub("", str(text))
    text = html_module.unescape(text)
    text = _TAG_RE.sub("", text)
    text = _MULTI_SPC.sub(" ", text).strip()
    text = html_module.escape(text)
    return text[:max_len] if max_len else text

def render_css():
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

.stSelectbox > div > div,
.stSelectbox [data-baseweb="select"] > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    border-radius: 2px !important;
}
.stSelectbox [data-baseweb="select"] span { color: var(--text) !important; }

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

.rott-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--red-dim), transparent);
    margin: 24px 0;
    opacity: 0.4;
}

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

@keyframes blink { 0%,50%{opacity:1} 51%,100%{opacity:0} }
.blink { animation: blink 1s infinite; }
@keyframes fadein { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.fadein { animation: fadein 0.4s ease forwards; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--red-dim); border-radius: 2px; }

.stProgress > div > div > div { background: var(--red) !important; }

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

def render_sidebar(LOGO_B64, SEARCH_ENGINES, last_query, requested_count, active_count, offline_count, selected_model, claude_ai, MODEL_DISPLAY_NAMES):
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

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
        <span class="status-dot"></span>
        <span style="font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11px;color:#00c97a;">TOR ONLINE</span>
        <span style="margin-left:auto;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11px;color:#5a5e6a;">{len(SEARCH_ENGINES)} ENGINES</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#2a1a1e;margin:14px 0;"></div>', unsafe_allow_html=True)

    st.markdown('<div style="font-family:\'Space Grotesk\',system-ui,sans-serif;font-size:9px;letter-spacing:3px;color:#e63946;text-transform:uppercase;margin-bottom:6px;">AI MODEL</div>', unsafe_allow_html=True)

    model_keys = MODEL_DISPLAY_NAMES
    if selected_model not in model_keys:
        selected_model = model_keys[0]
    default_idx = model_keys.index(selected_model)

    selected_label = st.selectbox(
        "LLM Model",
        options=model_keys,
        index=default_idx,
        label_visibility="collapsed",
        key="model_selector"
    )
    
    key_ok, key_msg = claude_ai.check_api_key()
    key_color  = "#00c97a" if key_ok else "#f0a500"
    key_icon   = "✅" if key_ok else "⚠️"
    safe_key_msg = clean(key_msg, 50)
    st.markdown(
        f'<div style="font-family:\'JetBrains Mono\',ui-monospace,monospace;font-size:10px;color:{key_color};'
        f'margin:6px 0 14px;padding:6px 8px;background:#0a0a0b;'
        f'border:1px solid #1e1e24;border-radius:2px;">'
        f'{key_icon} {safe_key_msg}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div style="height:1px;background:#2a1a1e;margin:4px 0 12px;"></div>', unsafe_allow_html=True)

    if st.button("REFRESH",  use_container_width=True): 
        st.rerun()
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
    if st.button("CLEAR ALL", use_container_width=True):
        return "clear"

    st.markdown('<div class="sidebar-label">Search Engines</div>', unsafe_allow_html=True)
    for engine in SEARCH_ENGINES:
        safe_engine_name = clean(engine["name"], 40)
        st.markdown(f'<div class="sidebar-engine">• {safe_engine_name}</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="height:1px;background:#2a1a1e;margin:18px 0 12px;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'JetBrains Mono',ui-monospace,monospace;font-size:9px;color:#5a5e6a;text-align:center;line-height:1.6;">
        Built by<br>
        <a href="https://github.com/Rohankaf" target="_blank" rel="noopener noreferrer" 
           style="color:#e63946;text-decoration:none;letter-spacing:1px;"
           onmouseover="this.style.color='#ff4757'" 
           onmouseout="this.style.color='#e63946'">
           @Rohankaf
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    return selected_label

def render_hero(LOGO_B64):
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

def render_hunt_controls(SEARCH_ENGINES, selected_model):
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
    model_short = clean(selected_model.split(" ")[0].upper(), 20)
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
    
    st.markdown(
        '<p style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#5a5e6a;margin-top:8px;">'
        'Will search broadly and return up to this many ONLINE sites</p>',
        unsafe_allow_html=True
    )
    
    return search_query, hunt_btn, max_results

def render_terminal(lines, stage_label):
    lines_html = "<br>".join(lines[-18:])
    return f'<div class="terminal-box" style="max-height:320px;overflow-y:auto;">' \
           f'<span style="color:#5a5e6a;letter-spacing:2px;font-size:10px;">' \
           f'{stage_label}</span><br><br>' \
           f'{lines_html}' \
           f'<br><span class="blink">▌</span></div>'

def render_hunt_results(result, sites, offline_sites, uptime_bar_html):
    requested = result.get('requested', 0)
    total_discovered = result.get('discovered', 0)
    online_count = len(sites)
    offline_count = len(offline_sites)

    st.markdown(f"""
    <div class="stat-row fadein">
        <div class="stat-card">
            <div class="stat-label">Requested</div>
            <div class="stat-val">{requested}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Active Sources</div>
            <div class="stat-val" style="color:#00c97a;">{online_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Offline Sources</div>
            <div class="stat-val" style="color:#5a5e6a;">{offline_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Success Rate</div>
            <div class="stat-val">{int(online_count/total_discovered*100) if total_discovered > 0 else 0}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    brief = st.session_state.intel_brief
    q_safe = clean(sites[0].get("query","") if sites else "", 60)
    
    if online_count < requested:
        intel_status = (
            f'<span style="color:#f0a500;">⚠ PARTIAL INTELLIGENCE</span><br>'
            f'<span style="color:#5a5e6a;">Only {online_count} active sources found. '
            f'{offline_count} additional sources are currently offline.</span>'
        )
    else:
        intel_status = (
            f'<span style="color:#00c97a;">✓ FULL INTELLIGENCE</span><br>'
            f'<span style="color:#5a5e6a;">All {requested} requested sources are active.</span>'
        )
    
    st.markdown('<div class="sec-header">INVESTIGATION SUMMARY</div>', unsafe_allow_html=True)
    brief_html = brief.replace("\n", "<br>") if brief else "No summary available."
    st.markdown(
        f'<div class="terminal-box fadein">'
        f'{intel_status}<br><br>{brief_html}'
        f'<br><br><span style="color:#5a5e6a;">QUERY: {q_safe} &nbsp;|&nbsp; '
        f'ACTIVE: {online_count}/{requested}</span>'
        f'<span class="blink">▌</span></div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="sec-header">ACTIVE INTELLIGENCE SOURCES</div>', unsafe_allow_html=True)

    st.markdown(
        f'<p style="font-family:Orbitron,sans-serif;font-size:10px;'
        f'letter-spacing:3px;color:#00c97a;margin-bottom:12px;">'
        f'🟢 {online_count} ACTIVE SOURCES | '
        f'{"✓ TARGET ACHIEVED" if online_count >= requested else f"⚠ {requested - online_count} SHORT OF TARGET"}'
        f'</p>',
        unsafe_allow_html=True
    )

    use_timeline = st.checkbox("Timeline bars", value=False, key="hunt_timeline")

    filtered = [s for s in sites if s["status"] == "online"]
    filtered = sorted(filtered, key=lambda x: x["url"])

    st.markdown(
        f'<p style="font-family:\'Share Tech Mono\',monospace;font-size:11px;'
        f'color:#5a5e6a;margin-bottom:10px;">SHOWING {len(filtered)} ACTIVE SITES</p>',
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

            title_safe = site.get("title_safe") or clean(site.get("title", ""), 100)
            show_title = title_safe and title_safe != clean(url, 100)

            color  = "#e63946"
            symbol = "●"

            href = html_module.escape(url, quote=True)

            safe_title_html = html_module.escape(title_safe.strip()) if title_safe else ""
            title_row = (
                f'<div class="result-title">{safe_title_html}</div>'
                if show_title and safe_title_html else ""
            )
            resp_time_html = f"{resp_time}ms" if resp_time else ""

            card_html = (
                f'<div class="site-card fadein">'
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
                + f'&nbsp;|&nbsp; STATUS: <span style="color:{color};">ONLINE</span>'
                + f'</div>'
                + f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)
    
    if offline_sites:
        st.markdown('<br>', unsafe_allow_html=True)
        with st.expander(f"Show Offline Sources ({offline_count})", expanded=False):
            st.markdown(
                f'<p style="font-family:\'Share Tech Mono\',monospace;font-size:11px;'
                f'color:#5a5e6a;margin-bottom:10px;margin-top:8px;">'
                f'THESE SOURCES ARE CURRENTLY UNAVAILABLE</p>',
                unsafe_allow_html=True
            )
            
            for i, site in enumerate(offline_sites, 1):
                status_val = site.get("status", "unknown")
                url = site.get("url", "")
                discovered_at = site.get("discovered_at", "")
                
                title_safe = site.get("title_safe") or clean(site.get("title", ""), 100)
                show_title = title_safe and title_safe != clean(url, 100)
                
                color = "#3a3a3a" if status_val == "offline" else "#5a4010"
                symbol = "○" if status_val == "offline" else "◌"
                status_label = "OFFLINE" if status_val == "offline" else "UNKNOWN"
                
                safe_title_html = html_module.escape(title_safe.strip()) if title_safe else ""
                title_row = (
                    f'<div class="result-title" style="color:#5a5e6a;">{safe_title_html}</div>'
                    if show_title and safe_title_html else ""
                )
                
                card_html = (
                    f'<div class="site-card offline fadein" style="opacity:0.5;">'
                    + title_row
                    + f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">'
                    + f'<div style="min-width:0;flex:1;">'
                    + f'<span style="color:#3a3a3a;margin-right:6px;font-size:10px;">{i}.</span>'
                    + f'<span style="color:{color};margin-right:6px;">{symbol}</span>'
                    + f'<span style="color:#5a5e6a;font-size:12px;word-break:break-all;">{html_module.escape(url)}</span>'
                    + f'</div>'
                    + f'</div>'
                    + f'<div style="margin-top:6px;font-size:10px;color:#2a2e38;">'
                    + f'{html_module.escape(discovered_at)}'
                    + f'&nbsp;|&nbsp; STATUS: <span style="color:{color};">{status_label}</span>'
                    + f'</div>'
                    + f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

def render_capabilities():
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

def render_analysis_tab_empty():
    st.markdown("""
    <div class="terminal-box">
    NO DATA TO ANALYZE.<br><br>
    → Switch to HUNT tab<br>
    → Run a search query<br>
    → Return here for deep analysis<br><br>
    <span class="blink">▌</span>
    </div>
    """, unsafe_allow_html=True)

def render_analysis_tab_content(sites):
    total_s   = len(sites)
    online_s  = total_s

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card"><div class="stat-label">Active Sites</div><div class="stat-val">{total_s}</div></div>
        <div class="stat-card"><div class="stat-label">Ready for Analysis</div><div class="stat-val">{online_s}</div></div>
        <div class="stat-card"><div class="stat-label">Status</div><div class="stat-val">🟢</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-header">INTELLIGENCE BRIEF</div>', unsafe_allow_html=True)

    generate_brief = st.button(" GENERATE INTEL BRIEF", use_container_width=True)
    
    st.markdown('<div class="sec-header">CUSTOM QUERY</div>', unsafe_allow_html=True)

    custom_prompt = st.text_area(
        "Custom AI analysis prompt",
        placeholder="What patterns do you see? What threat categories are most active?",
        height=100,
        label_visibility="collapsed",
    )

    run_analysis = st.button("RUN ANALYSIS", use_container_width=True)
    
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
    
    return generate_brief, custom_prompt, run_analysis

def render_analysis_result(brief):
    safe_brief = brief.replace("\n", "<br>") if brief else "No summary available."
    st.markdown(
        f'<div class="terminal-box">{safe_brief}'
        f'<span class="blink">▌</span></div>',
        unsafe_allow_html=True
    )

def render_custom_analysis_result(result_text):
    safe_result = result_text.replace("\n", "<br>") if result_text else "No analysis available."
    st.markdown(
        f'<div class="terminal-box">{safe_result}'
        f'<span class="blink">▌</span></div>',
        unsafe_allow_html=True
    )

def render_settings_tab():
    st.markdown('<div class="sec-header">PROVIDER CONFIGURATION</div>', unsafe_allow_html=True)

    for pname, env in [
        ("Anthropic",           "ANTHROPIC_API_KEY"),
        ("OpenAI",              "OPENAI_API_KEY"),
        ("Google Gemini",       "GOOGLE_API_KEY"),
        ("Groq (Llama/Mixtral)","GROQ_API_KEY"),
        ("OpenRouter",          "OPENROUTER_API_KEY"),
    ]:
        is_set = bool(os.getenv(env))
        color  = "#00c97a" if is_set else "#f0a500"
        label  = "configured" if is_set else "API key not set"
        safe_pname = clean(pname, 40)
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:10px 14px;margin:4px 0;background:#0f0f11;
                    border:1px solid #1e1e24;border-radius:2px;">
            <span style="font-family:'JetBrains Mono',ui-monospace,monospace;font-size:12px;color:#c9cdd4;">
                &nbsp;<strong style="color:#fff;">{safe_pname}</strong>
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