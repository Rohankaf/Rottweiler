# tor_search.py
# Copyright 2026 rohahahan
# Licensed under Apache 2.0

import requests
import random
import re
import urllib.parse
import warnings
from typing import List, Dict, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# TOR SESSION  — with retry logic (from search.py)
# ══════════════════════════════════════════════════════════════════════════════

def get_tor_session() -> requests.Session:
    """
    Creates a requests Session routed through Tor SOCKS5 proxy,
    with automatic retries on server errors.
    """
    session = requests.Session()
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.proxies = {
        "http":  "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050",
    }
    return session


# ══════════════════════════════════════════════════════════════════════════════
# USER AGENT ROTATION
# ══════════════════════════════════════════════════════════════════════════════

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Mozilla/5.0 (X11; Linux i686; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.3179.54",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.3179.54",
]

def get_headers() -> Dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "close",
    }


# ══════════════════════════════════════════════════════════════════════════════
# SEARCH ENGINE LIST  — kept identical to your original set
# ══════════════════════════════════════════════════════════════════════════════

SEARCH_ENGINES = [
    {"name": "Ahmia",            "url": "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q={query}"},
    {"name": "OnionLand",        "url": "http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/search?q={query}"},
    {"name": "Torgle",           "url": "http://iy3544gmoeclh5de6gez2256v6pjh4omhpqdh2wpeeppjtvqmjhkfwad.onion/torgle/?query={query}"},
    {"name": "Amnesia",          "url": "http://amnesia7u5odx5xbwtpnqk3edybgud5bmiagu75bnqx2crntw5kry7ad.onion/search?query={query}"},
    {"name": "Torland",          "url": "http://torlbmqwtudkorme6prgfpmsnile7ug2zm4u3ejpcncxuhpu4k2j4kyd.onion/index.php?a=search&q={query}"},
    {"name": "Find Tor",         "url": "http://findtorroveq5wdnipkaojfpqulxnkhblymc7aramjzajcvpptd4rjqd.onion/search?q={query}"},
    {"name": "Excavator",        "url": "http://2fd6cemt4gmccflhm6imvdfvli3nf7zn6rfrwpsy7uhxrgbypvwf5fad.onion/search?query={query}"},
    {"name": "Onionway",         "url": "http://oniwayzz74cv2puhsgx4dpjwieww4wdphsydqvf5q7eyz4myjvyw26ad.onion/search.php?s={query}"},
    {"name": "Tor66",            "url": "http://tor66sewebgixwhcqfnp5inzp5x5uohhdy3kvtnyfxc2e5mxiuh34iid.onion/search?q={query}"},
    {"name": "OSS",              "url": "http://3fzh7yuupdfyjhwt3ugzqqof6ulbcl27ecev33knxe3u7goi3vfn2qqd.onion/oss/index.php?search={query}"},
    {"name": "Torgol",           "url": "http://torgolnpeouim56dykfob6jh5r2ps2j73enc42s2um4ufob3ny4fcdyd.onion/?q={query}"},
    {"name": "The Deep Searches","url": "http://searchgf7gdtauh7bhnbyed4ivxqmuoat3nm6zfrg3ymkq6mtnpye3ad.onion/search?q={query}"},
    {"name": "Torch",            "url": "http://rz6wxogwwbqdadlncnp2q26kbgcbbaqnitzueohj73fzmlx3mt467wqd.onion/search?q={query}"},
    {"name": "Dark Search",      "url": "http://darkzqtmbdeauwq5mzcmgeeuhet42fhfjj4p5wbak3ofx2yqgecoeqyd.onion/search?q={query}"},
]

# Flat list of URL templates (backward compatible)
DEFAULT_SEARCH_ENGINES = [e["url"] for e in SEARCH_ENGINES]


# ══════════════════════════════════════════════════════════════════════════════
# BLACKLIST  — auto-built from engine domains + known junk
# ══════════════════════════════════════════════════════════════════════════════

_ENGINE_DOMAINS: Set[str] = set()
for _e in SEARCH_ENGINES:
    _m = re.search(r"https?://([a-z2-7]{16,56}\.onion)", _e["url"])
    if _m:
        _ENGINE_DOMAINS.add(_m.group(1).lower())

# Extra domains known to be aggregators/redirectors rather than real sites
BLACKLISTED_DOMAINS: Set[str] = _ENGINE_DOMAINS | {
    "zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion",
    "zqktlwi4fecvo6ri.onion",
}

# URL fragments that indicate a navigation / search-engine-internal link
_JUNK_PATH_PATTERNS = re.compile(
    r"/(search|login|register|signup|about|contact|help|faq|tos|privacy|"
    r"sitemap|robots|feed|rss|cdn|static|assets|img|js|css|fonts)/",
    re.IGNORECASE,
)


# ══════════════════════════════════════════════════════════════════════════════
# URL VALIDATION & NORMALISATION
# ══════════════════════════════════════════════════════════════════════════════

def _extract_domain(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.lower().split(":")[0]
    except Exception:
        return ""


def _is_valid_result(href: str, title: str = "") -> bool:
    """
    Accept a link only if ALL of the following are true:
      1. href contains .onion
      2. Domain is NOT blacklisted (search engines, known junk)
      3. The path does NOT look like a search/nav page
      4. Title (if given) is longer than 3 chars — filters out icon-only links
      5. Onion address is v2 (16 chars) or v3 (56 chars)
      6. 'search' keyword NOT in the raw href path  ← from search.py
    """
    if ".onion" not in href:
        return False

    domain = _extract_domain(href)
    if not domain:
        return False
    if domain in BLACKLISTED_DOMAINS:
        return False

    host = domain.replace(".onion", "")
    if not (len(host) == 56 or len(host) == 16):
        return False

    # Reject if the href itself contains search-engine path fragments
    if "search" in href.lower():
        return False

    parsed_path = urllib.parse.urlparse(href).path
    if _JUNK_PATH_PATTERNS.search(parsed_path):
        return False

    # Title must be meaningful (> 3 chars) — from search.py
    if title and len(title.strip()) <= 3:
        return False

    return True


def _normalise(url: str) -> str:
    """Lowercase host, strip query/fragment, remove trailing slash."""
    try:
        p = urllib.parse.urlparse(url)
        path = p.path.rstrip("/") or "/"
        return urllib.parse.urlunparse(("http", p.netloc.lower(), path, "", "", ""))
    except Exception:
        return url


# ══════════════════════════════════════════════════════════════════════════════
# SINGLE ENGINE SEARCH  — returns list of {title, link} dicts  (like search.py)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_search_results(engine: Dict, query: str) -> List[Dict[str, str]]:
    """
    Query one search engine via Tor.
    Returns a list of {"title": ..., "link": ...} dicts.
    Uses the proven approach from search.py:
      - find all <a> tags
      - regex-extract .onion hrefs
      - apply _is_valid_result filter (title length, 'search' exclusion, blacklist)
    """
    name     = engine["name"]
    endpoint = engine["url"].format(query=urllib.parse.quote_plus(query))
    headers  = get_headers()
    session  = get_tor_session()

    try:
        response = session.get(endpoint, headers=headers, timeout=40)
        if response.status_code != 200:
            print(f"[{name}] Non-200: {response.status_code}")
            return []

        soup  = BeautifulSoup(response.text, "html.parser")
        links = []
        seen_links: Set[str] = set()

        for a in soup.find_all("a", href=True):
            try:
                href  = a["href"]
                title = a.get_text(strip=True)

                # Extract the .onion URL from the href
                match = re.findall(r"https?://[a-z2-7A-Z0-9\.\-]+\.onion[^\s\"'<>]*", href)
                if not match:
                    continue
                raw_link = match[0]

                if not _is_valid_result(raw_link, title):
                    continue

                clean = _normalise(raw_link)
                if clean in seen_links:
                    continue
                seen_links.add(clean)

                links.append({"title": title or clean, "link": clean})

            except Exception:
                continue

        print(f"[{name}] found {len(links)} clean results")
        return links

    except requests.exceptions.ConnectionError as e:
        err = str(e)
        if "SOCKS" in err or "unreachable" in err.lower() or "refused" in err.lower():
            print(f"[{name}] Tor unreachable — skipping")
        else:
            print(f"[{name}] connection error: {err[:100]}")
        return []
    except Exception as e:
        print(f"[{name}] error: {str(e)[:100]}")
        return []


# ══════════════════════════════════════════════════════════════════════════════
# RELEVANCE SCORING
# ══════════════════════════════════════════════════════════════════════════════

def _score(item: Dict[str, str], query: str) -> int:
    score     = 0
    url_lower = item["link"].lower()
    ttl_lower = item.get("title", "").lower()
    words     = query.lower().split()

    for word in words:
        if word in url_lower: score += 8
        if word in ttl_lower: score += 12   # title match is a stronger signal

    host = _extract_domain(item["link"]).replace(".onion", "")
    if len(host) == 56: score += 3   # prefer v3 onions

    path = urllib.parse.urlparse(item["link"]).path
    if path and path != "/": score += 2

    return score


# ══════════════════════════════════════════════════════════════════════════════
# MULTI-ENGINE RUNNER  — returns list of {title, link} dicts
# ══════════════════════════════════════════════════════════════════════════════

def get_search_results(query: str, max_workers: int = 10) -> List[Dict[str, str]]:
    """
    Query all engines concurrently.
    Returns deduplicated, relevance-sorted list of {"title", "link"} dicts.
    Used by pipeline.py and app.py.
    """
    raw: List[Dict[str, str]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_search_results, engine, query): engine
            for engine in SEARCH_ENGINES
        }
        for future in as_completed(futures):
            engine = futures[future]
            try:
                raw.extend(future.result())
            except Exception as e:
                print(f"[{engine['name']}] thread error: {e}")

    # Deduplicate by link
    seen: Set[str] = set()
    unique: List[Dict[str, str]] = []
    for item in raw:
        lnk = item["link"]
        if lnk not in seen:
            seen.add(lnk)
            unique.append(item)

    # Sort by relevance
    unique.sort(key=lambda x: _score(x, query), reverse=True)

    print(f"\n[ROTTWEILER] Raw: {len(raw)} → Unique: {len(unique)}")
    return unique


# ══════════════════════════════════════════════════════════════════════════════
# BACKWARD-COMPATIBLE WRAPPER  — run_search_agents() returns plain URL list
# Called by old pipeline.py code that expects List[str]
# ══════════════════════════════════════════════════════════════════════════════

def run_search_agents(query: str, max_results: int = 50) -> List[str]:
    """
    Backward-compatible wrapper. Returns a plain list of URL strings.
    """
    results = get_search_results(query, max_workers=10)
    return [r["link"] for r in results][:max_results]