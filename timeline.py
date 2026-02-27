
from datetime import datetime, timedelta
from typing import Dict, List


COLOUR = {
    "online":  "#00ffaa",
    "offline": "#ff3355",
    "unknown": "#1a2a3a",
}

TOOLTIP_LABEL = {
    "online":  "ONLINE",
    "offline": "OFFLINE",
    "unknown": "NO DATA",
}


def _slot_label(slot_index: int, total_slots: int, days: int) -> str:
    """Human-readable label for a slot (e.g. 'Jun 12 18:00')."""
    now   = datetime.utcnow()
    start = now - timedelta(days=days)
    slot_duration = timedelta(days=days) / total_slots
    slot_time = start + slot_duration * slot_index
    return slot_time.strftime("%b %d %H:%M UTC")


def _generate_slots_from_site(site: Dict, slots: int = 30) -> List[str]:
    """
    Generate timeline slot data from a site dict (no DB needed).
    Since we only have current status (no history), we fill the bar
    based on what we know: current status fills the last slot,
    the rest are 'unknown' (no historical data available).
    """
    status = site.get("status", "unknown")
    slot_data = ["unknown"] * (slots - 1) + [status]
    return slot_data


def uptime_bar_html(site: Dict, slots: int = 30, days: int = 7) -> str:
    """
    Returns an HTML string with:
      • The .onion URL
      • A slot colour bar showing status history (or current status)
      • Meta: uptime %, discovered at, response time

    Args:
        site: dict with keys: url, status, response_time, discovered_at, query
    """
    if not site:
        return ""

    url          = site.get("url", "")
    status       = site.get("status", "unknown")
    resp_time    = site.get("response_time", 0)
    discovered_at = site.get("discovered_at", "—")
    query        = site.get("query", "")
    uptime_pct   = 100 if status == "online" else 0

    slot_data = _generate_slots_from_site(site, slots)

    badge_colour = COLOUR.get(status, COLOUR["unknown"])
    badge_text   = status.upper()
    pulse_anim   = "animation:pulse 2s infinite;" if status == "online" else ""

    bar_cells = ""
    for i, s in enumerate(slot_data):
        colour  = COLOUR[s]
        tooltip = f"{_slot_label(i, slots, days)} — {TOOLTIP_LABEL[s]}"
        opacity = 0.9 if s != "unknown" else 0.25
        bar_cells += (
            f'<div title="{tooltip}" style="'
            f'flex:1;height:22px;background:{colour};'
            f'border-radius:2px;margin:0 1px;cursor:default;'
            f'opacity:{opacity};transition:opacity .15s;" '
            f'onmouseover="this.style.opacity=1" '
            f'onmouseout="this.style.opacity={opacity}">'
            f'</div>'
        )

    tag_html = ""
    if query:
        tag_html = (
            f'<span style="background:rgba(0,255,170,.07);border:1px solid rgba(0,255,170,.18);'
            f'color:#00ffaa;font-size:10px;padding:1px 7px;margin:0 2px;letter-spacing:1px;'
            f'text-transform:uppercase;">{query}</span>'
        )

    import html as _html
    safe_url          = _html.escape(url)
    safe_discovered   = _html.escape(discovered_at)
    resp_time_html    = f'<span style="font-size:11px;color:#1a4a3a;">{resp_time}ms</span>' if resp_time else ""

    return (
        '<style>@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}</style>'
        + f'<div style="background:#07080f;border:1px solid #0d3347;border-left:3px solid {badge_colour};padding:14px 18px 10px;margin:6px 0;font-family:\'Share Tech Mono\',monospace;">'
        + f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">'
        + f'<div style="display:flex;align-items:center;gap:10px;">'
        + f'<span style="width:9px;height:9px;border-radius:50%;background:{badge_colour};display:inline-block;flex-shrink:0;{pulse_anim}"></span>'
        + f'<span style="color:#e0eaf5;font-size:13px;word-break:break-all;">{safe_url}</span>'
        + f'</div>'
        + f'<div style="display:flex;align-items:center;gap:14px;flex-shrink:0;">'
        + f'<span style="font-size:11px;color:{badge_colour};letter-spacing:1px;">{badge_text}</span>'
        + f'<span style="font-size:11px;color:#2a6a5a;">↑ {uptime_pct:.0f}% uptime</span>'
        + resp_time_html
        + f'</div>'
        + f'</div>'
        + f'<div style="margin:6px 0 10px;">{tag_html}</div>'
        + f'<div style="margin-bottom:3px;"><span style="font-size:9px;color:#1e3a4a;letter-spacing:2px;">7-DAY UPTIME HISTORY</span></div>'
        + f'<div style="display:flex;align-items:stretch;width:100%;gap:0;">{bar_cells}</div>'
        + f'<div style="display:flex;width:100%;margin-top:3px;">'
        + f'<span style="font-size:9px;color:#1e3a4a;font-family:Share Tech Mono,monospace;">← 7 days ago</span>'
        + f'<span style="flex:1;"></span>'
        + f'<span style="font-size:9px;color:#1e3a4a;font-family:Share Tech Mono,monospace;">now →</span>'
        + f'</div>'
        + f'<div style="display:flex;gap:20px;margin-top:8px;flex-wrap:wrap;">'
        + f'<span style="font-size:10px;color:#1e3a4a;">DISCOVERED: <span style="color:#2a5a4a;">{safe_discovered}</span></span>'
        + f'</div>'
        + f'</div>'
    )