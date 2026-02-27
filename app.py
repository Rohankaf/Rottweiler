import streamlit as st
import time
import base64
import os
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from llm_prompt import ClaudeAI, DEFAULT_MODEL_NAMES
from tor_search import SEARCH_ENGINES, fetch_search_results, get_search_results
from catching import scrape_single
from timeline import uptime_bar_html
import ui

st.set_page_config(
    page_title="ROTTWEILER — Dark Web Intelligence",
    page_icon="🐕",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_B64 = ""
logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        LOGO_B64 = base64.b64encode(f.read()).decode()

ui.render_css()

if "discovered_sites"  not in st.session_state: st.session_state.discovered_sites  = []
if "offline_sites"     not in st.session_state: st.session_state.offline_sites     = []
if "hunt_result"       not in st.session_state: st.session_state.hunt_result       = None
if "claude_ai"         not in st.session_state: st.session_state.claude_ai         = ClaudeAI()
if "selected_model"    not in st.session_state: st.session_state.selected_model    = "Claude Sonnet 4 (Anthropic)"
if "intel_brief"       not in st.session_state: st.session_state.intel_brief       = None
if "smart_online_only" not in st.session_state: st.session_state.smart_online_only = False

claude_ai = st.session_state.claude_ai

with st.sidebar:
    last_query = ""
    requested_count = 0
    active_count = 0
    offline_count = 0
    
    if st.session_state.hunt_result:
        result = st.session_state.hunt_result
        requested_count = result.get('requested', 0)
        active_count = result.get('active', 0)
        offline_count = result.get('offline', 0)
        if st.session_state.discovered_sites:
            last_query = st.session_state.discovered_sites[0].get('query', '')
    
    sidebar_result = ui.render_sidebar(
        LOGO_B64, 
        SEARCH_ENGINES, 
        last_query, 
        requested_count, 
        active_count, 
        offline_count, 
        st.session_state.selected_model,
        st.session_state.claude_ai,
        DEFAULT_MODEL_NAMES
    )
    
    if sidebar_result == "clear":
        st.session_state.discovered_sites = []
        st.session_state.offline_sites    = []
        st.session_state.hunt_result      = None
        st.session_state.intel_brief      = None
        st.rerun()
    elif sidebar_result and sidebar_result != st.session_state.selected_model:
        st.session_state.selected_model = sidebar_result
        st.session_state.claude_ai.set_model(sidebar_result)
        claude_ai = st.session_state.claude_ai

ui.render_hero(LOGO_B64)

tab1, tab2, tab3 = st.tabs(["⬡  HUNT", "◉  AI ANALYSIS", "⚙  SETTINGS"])

with tab1:
    search_query, hunt_btn, max_results = ui.render_hunt_controls(SEARCH_ENGINES, st.session_state.selected_model)

    if hunt_btn:
        if not search_query.strip():
            st.warning("Enter a search query to begin hunting.")
        else:
            from concurrent.futures import ThreadPoolExecutor, as_completed

            q_safe      = ui.clean(search_query, 80)
            total_eng   = len(SEARCH_ENGINES)
            prog        = st.progress(0)
            term        = st.empty()

            log_lines   = [f'<span style="color:#5a5e6a;">QUERY: {q_safe}</span>',
                           f'<span style="color:#5a5e6a;">TARGET: {max_results} ONLINE sites</span>',
                           f'<span style="color:#5a5e6a;">ENGINES: {total_eng} queued via Tor</span>', ""]
            term.markdown(ui.render_terminal(log_lines, "[ 1 / 3 ]  SEARCHING ENGINES"), unsafe_allow_html=True)
            prog.progress(2)

            raw_results  = []
            done_count   = 0

            with ThreadPoolExecutor(max_workers=10) as executor:
                future_map = {
                    executor.submit(fetch_search_results, eng, search_query): eng
                    for eng in SEARCH_ENGINES
                }
                for future in as_completed(future_map):
                    eng        = future_map[future]
                    done_count += 1
                    pct        = int(2 + (done_count / total_eng) * 28)
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

                    eng_name = ui.clean(eng["name"], 22)
                    log_lines.append(
                        f'<span style="color:{color};">{icon}</span>'
                        f' <span style="color:#8a9ab0;">{eng_name:<22}</span>'
                        f' <span style="color:{color};">{msg}</span>'
                        f' <span style="color:#2a2e38;">({done_count}/{total_eng})</span>'
                    )
                    term.markdown(ui.render_terminal(log_lines, "[ 1 / 3 ]  SEARCHING ENGINES"), unsafe_allow_html=True)
                    prog.progress(pct)

            log_lines.append("")
            log_lines.append(f'<span style="color:#5a5e6a;">RANKING {len(raw_results)} results with BM25...</span>')
            term.markdown(ui.render_terminal(log_lines, "[ 2 / 3 ]  RANKING & SMART SCRAPING"), unsafe_allow_html=True)
            prog.progress(30)

            # Get ranked unique results
            ranked_results = get_search_results(search_query, max_workers=10)
            
            log_lines.append(
                f'<span style="color:#00c97a;">RANKED: {len(ranked_results)} unique sites by relevance</span>'
            )
            term.markdown(ui.render_terminal(log_lines, "[ 2 / 3 ]  RANKING & SMART SCRAPING"), unsafe_allow_html=True)
            prog.progress(35)

            log_lines.append("")
            log_lines.append(
                f'<span style="color:#5a5e6a;">SMART SCRAPING: Stopping at {max_results} ONLINE sites...</span>'
            )
            term.markdown(ui.render_terminal(log_lines, "[ 2 / 3 ]  RANKING & SMART SCRAPING"), unsafe_allow_html=True)
            prog.progress(37)

            active_sites = []
            offline_sites = []
            scraped_count = 0
            checked_count = 0
            
            scrape_limit = min(len(ranked_results), max_results * 3)
            
            batch_size = 10
            
            for batch_start in range(0, scrape_limit, batch_size):
                # Check if we already have enough online sites
                if len(active_sites) >= max_results:
                    log_lines.append(
                        f'<span style="color:#00c97a;">✓ TARGET REACHED: {len(active_sites)} online sites found</span>'
                    )
                    break
                
                batch_end = min(batch_start + batch_size, scrape_limit)
                batch = ranked_results[batch_start:batch_end]
                
                # Scrape this batch
                with ThreadPoolExecutor(max_workers=5) as executor:
                    future_map = {
                        executor.submit(scrape_single, item): item
                        for item in batch
                    }
                    
                    for future in as_completed(future_map):
                        if len(active_sites) >= max_results:
                            break
                            
                        checked_count += 1
                        pct = min(77, int(37 + (checked_count / scrape_limit) * 40))
                        
                        try:
                            url_key, data = future.result()
                            item = future_map[future]
                            
                            ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                            status_val = data.get("status", "offline")
                            title = data.get("title") or item.get("title") or url_key
                            
                            site_record = {
                                "url":           url_key,
                                "title":         title,
                                "title_safe":    ui.clean(title, 100),
                                "content":       data.get("content", ""),
                                "status":        status_val,
                                "status_code":   data.get("status_code"),
                                "response_time": 0,
                                "discovered_at": ts,
                                "query":         search_query,
                                "tags":          [search_query],
                                "description":   title,
                                "bm25_score":    item.get("bm25_score", 0),
                            }
                            
                            if status_val == "online":
                                active_sites.append(site_record)
                                st_icon = "●"
                                st_color = "#e63946"
                                status_msg = f"ONLINE ({len(active_sites)}/{max_results})"
                            else:
                                offline_sites.append(site_record)
                                st_icon = "○"
                                st_color = "#5a5e6a"
                                status_msg = "offline"
                            
                            short_url = url_key[7:47] + "…" if len(url_key) > 50 else url_key[7:]
                            short_url_safe = ui.clean(short_url, 50)
                            
                            log_lines.append(
                                f'<span style="color:{st_color};">{st_icon}</span>'
                                f' <span style="color:#8a9ab0;font-size:11px;">{short_url_safe}</span>'
                                f' <span style="color:{st_color};font-size:10px;">{status_msg}</span>'
                            )
                        except Exception:
                            checked_count += 1
                        
                        term.markdown(
                            ui.render_terminal(
                                log_lines, 
                                f"[ 2 / 3 ]  SMART SCRAPING  ({len(active_sites)}/{max_results} online)"
                            ), 
                            unsafe_allow_html=True
                        )
                        prog.progress(pct)
            
            # Final scraping summary
            log_lines.append("")
            log_lines.append(
                f'<span style="color:#00c97a;">SCRAPING COMPLETE — '
                f'{len(active_sites)} online / {checked_count} checked</span>'
            )
            term.markdown(ui.render_terminal(log_lines, "[ 2 / 3 ]  SMART SCRAPING"), unsafe_allow_html=True)
            prog.progress(78)

            # PHASE 3: AI Analysis
            log_lines.append("")
            log_lines.append('<span style="color:#5a5e6a;">GENERATING AI INTEL BRIEF...</span>')
            term.markdown(ui.render_terminal(log_lines, "[ 3 / 3 ]  AI ANALYSIS"), unsafe_allow_html=True)
            prog.progress(88)

            summary = ""
            sites_for_ai = active_sites[:20] if active_sites else []
            if sites_for_ai and claude_ai:
                try:
                    summary = claude_ai.summarize_results(search_query, sites_for_ai)
                except Exception as e:
                    summary = f"[AI summary error: {e}]"

            log_lines.append(
                f'<span style="color:#00c97a;">HUNT COMPLETE — '
                f'{len(active_sites)} online sites discovered</span>'
            )
            term.markdown(ui.render_terminal(log_lines, "[ 3 / 3 ]  AI ANALYSIS"), unsafe_allow_html=True)
            prog.progress(100)
            
            # Trim to exact count requested
            active_sites = active_sites[:max_results]
            
            st.session_state.discovered_sites = active_sites
            st.session_state.offline_sites = offline_sites
            st.session_state.smart_online_only = True
            st.session_state.hunt_result = {
                "discovered":   len(active_sites) + len(offline_sites),
                "active":       len(active_sites),
                "offline":      len(offline_sites),
                "all_sites":    active_sites + offline_sites,
                "active_sites": active_sites,
                "offline_sites": offline_sites,
                "summary":      summary,
                "requested":    int(max_results),
            }
            st.session_state.intel_brief = summary

            time.sleep(0.6)
            term.empty()
            prog.empty()

    if st.session_state.hunt_result and st.session_state.discovered_sites:
        result = st.session_state.hunt_result
        sites  = st.session_state.discovered_sites
        offline_sites = st.session_state.get('offline_sites', [])
        
        brief = st.session_state.intel_brief
        if not brief:
            last_query = sites[0].get("query", "") if sites else ""
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
        
        ui.render_hunt_results(result, sites, offline_sites, uptime_bar_html)
        
        # Download button for intel brief
        if brief:
            last_query = sites[0].get("query", "hunt") if sites else "hunt"
            st.download_button(
                label="Download Intel Brief (.md)",
                data=brief,
                file_name=f"rottweiler_{last_query}.md",
                mime="text/markdown"
            )

    elif not st.session_state.hunt_result:
        ui.render_capabilities()

with tab2:
    if not st.session_state.discovered_sites:
        ui.render_analysis_tab_empty()
    else:
        sites = st.session_state.discovered_sites
        generate_brief, custom_prompt, run_analysis = ui.render_analysis_tab_content(sites)
        
        if generate_brief:
            with st.spinner("Analyzing with AI..."):
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
                ui.render_analysis_result(brief)
                st.download_button(
                    label="Download Intelligence Report (.md)",
                    data=brief,
                    file_name=f"rottweiler_{last_query}_analysis.md",
                    mime="text/markdown"
                )

        if run_analysis:
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
                    ui.render_custom_analysis_result(result_text)
                    # Download button for custom analysis
                    st.download_button(
                        label="Download Analysis Report (.md)",
                        data=result_text,
                        file_name=f"rottweiler_custom_analysis.md",
                        mime="text/markdown"
                    )
            else:
                st.warning("Enter a prompt first.")

with tab3:
    ui.render_settings_tab()