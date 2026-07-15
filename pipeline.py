
from tor_search import get_search_results
from catching import scrape_multiple
from datetime import datetime


def run_discovery(query: str, monitor, llm, max_results: int = 50) -> dict:
    print(f"\n[PIPELINE] Searching for: {query}")
    search_results = get_search_results(query, max_workers=10)
    search_results = search_results[:max_results]
    print(f"[PIPELINE] Search returned {len(search_results)} unique links")

    if not search_results:
        return {
            "discovered":  0,
            "active":      0,
            "all_sites":   [],
            "active_sites":[],
            "summary":     "No results found. Try a different query or check Tor connection.",
        }

    print(f"[PIPELINE] Scraping {len(search_results)} sites via Tor...")
    scraped = scrape_multiple(search_results, max_workers=5)

    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    all_sites: list  = []
    active_sites: list = []

    for item in search_results:
        url  = item["link"]
        data = scraped.get(url, {})

        status    = data.get("status", "offline")
        http_code = data.get("status_code")
        title     = data.get("title") or item.get("title") or url
        content   = data.get("content", "")

        
        site_record = {
            "url":           url,
            "title":         title,
            "content":       content,      
            "status":        status,
            "status_code":   http_code,
            "response_time": 0,
            "discovered_at": ts,
            "query":         query,
            "tags":          [query],
            "description":   title,
        }

        all_sites.append(site_record)
        if status == "online":
            active_sites.append(site_record)

    print(f"[PIPELINE] Online: {len(active_sites)} / Total: {len(all_sites)}")

    # summary
    summary = ""
    sites_for_ai = active_sites[:20] if active_sites else all_sites[:20]
    if sites_for_ai and llm:
        try:
            summary = llm.summarize_results(query, sites_for_ai)
        except Exception as e:
            summary = f"[AI summary error: {e}]"

    return {
        "discovered":   len(all_sites),
        "active":       len(active_sites),
        "all_sites":    all_sites,
        "active_sites": active_sites,
        "summary":      summary,
    }
