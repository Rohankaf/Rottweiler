# scraper.py
# Copyright 2026 rohahahan
# Licensed under Apache 2.0
#
# Fetches and extracts readable text from discovered .onion sites.
# Used after tor_search.py finds links, to enrich results with actual content.

import re
import random
import warnings
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

warnings.filterwarnings("ignore")


MAX_CONTENT_CHARS = 2500   # max chars 
SCRAPE_TIMEOUT    = 45     # seconds 

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:137.0) Gecko/20100101 Firefox/137.0",
]

def get_tor_session() -> requests.Session:
    """
    Requests session routed through Tor SOCKS5 with auto-retry on server errors.
    """
    session = requests.Session()
    retry = Retry(
        total=2,
        read=2,
        connect=2,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://",  adapter)
    session.mount("https://", adapter)
    session.proxies = {
        "http":  "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050",
    }
    return session


def scrape_single(url_data: Dict) -> tuple:
    """
    Scrape one URL. Accepts a dict with at least {"link": str, "title": str}.

    Returns:
        (url: str, enriched_data: dict) where enriched_data has:
            - title       : page <title> tag or original title
            - content     : cleaned body text (truncated)
            - status      : "online" | "offline" | "error"
            - status_code : int or None
    """
    url   = url_data.get("link", "")
    title = url_data.get("title", url)

    headers = {"User-Agent": random.choice(USER_AGENTS)}

    try:
        session  = get_tor_session()
        response = session.get(url, headers=headers, timeout=SCRAPE_TIMEOUT)
        code     = response.status_code

        if code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Get page title from HTML if available - strip all tags
            title_tag = soup.find("title")
            if title_tag and title_tag.get_text(strip=True):
                raw_title = title_tag.get_text(strip=True)
                # Remove any residual HTML entities or tags
                raw_title = re.sub(r"<[^>]+>", "", raw_title)
                raw_title = raw_title.replace("&lt;", "").replace("&gt;", "").replace("&amp;", "&")
                title = raw_title.strip() or title

            # Remove noise elements
            for tag in soup(["script", "style", "nav", "footer", "header",
                              "noscript", "iframe", "form", "button"]):
                tag.decompose()

            # Extract and clean body text
            text = soup.get_text(separator=" ")
            text = " ".join(text.split())  

            if len(text) > MAX_CONTENT_CHARS:
                text = text[:MAX_CONTENT_CHARS] + "...[truncated]"

            return url, {
                "title":       title,
                "content":     text,
                "status":      "online",
                "status_code": code,
            }
        else:
            return url, {
                "title":       title,
                "content":     f"[HTTP {code}]",
                "status":      "offline",
                "status_code": code,
            }

    except requests.exceptions.Timeout:
        return url, {"title": title, "content": "[Timeout]",  "status": "offline", "status_code": None}
    except requests.exceptions.ConnectionError as e:
        err = str(e)
        if "SOCKS" in err or "unreachable" in err.lower():
            return url, {"title": title, "content": "[Tor unreachable]", "status": "offline", "status_code": None}
        return url, {"title": title, "content": "[Connection error]", "status": "offline", "status_code": None}
    except Exception as e:
        return url, {"title": title, "content": f"[Error: {str(e)[:80]}]", "status": "error", "status_code": None}



def scrape_multiple(
    urls_data: List[Dict],
    max_workers: int = 5,
) -> Dict[str, Dict]:
    """
    Scrape multiple URLs concurrently.

    Args:
        urls_data   : list of dicts with {"link": str, "title": str}
        max_workers : thread pool size (keep low — Tor has limited bandwidth)

    Returns:
        dict mapping url → enriched_data dict
    """
    results: Dict[str, Dict] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(scrape_single, item): item
            for item in urls_data
        }
        for future in as_completed(future_map):
            try:
                url, data = future.result()
                results[url] = data
            except Exception:
                continue

    return results


def scrape_urls(urls: List[str], max_workers: int = 5) -> Dict[str, Dict]:
    """
    Wrapper for scrape_multiple when you only have URL strings (no titles).
    """
    urls_data = [{"link": u, "title": u} for u in urls]
    return scrape_multiple(urls_data, max_workers=max_workers)