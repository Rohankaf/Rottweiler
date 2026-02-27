import time
import requests
import threading
from datetime import datetime
from typing import List

TOR_PROXY = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}

REQUEST_TIMEOUT = 60  # seconds


class SiteMonitor:
    """
    Site monitor WITHOUT database dependency.
    Just checks sites and returns status.
    """
    def __init__(self):
        self.interval = 900  # 15 min default
        self._log: List[str] = []
        self._lock = threading.Lock()
        self._running = True

    def set_interval(self, seconds: int):
        self.interval = seconds

    def _log_entry(self, msg: str):
        ts = datetime.utcnow().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        with self._lock:
            self._log.append(line)
            if len(self._log) > 200:
                self._log = self._log[-200:]

    def get_log(self) -> List[str]:
        with self._lock:
            return list(self._log)

    def check_site(self, url: str) -> dict:
        """
        Check a single site. Returns status dict.
        NO DATABASE - just returns the result.
        """
        if not url.startswith("http"):
            check_url = f"http://{url}"
        else:
            check_url = url

        start = time.time()
        try:
            resp = requests.get(
                check_url,
                proxies=TOR_PROXY,
                timeout=REQUEST_TIMEOUT,
                headers={"User-Agent": "Mozilla/5.0"},
                allow_redirects=True,
            )
            elapsed = int((time.time() - start) * 1000)
            
            if resp.status_code < 500:
                self._log_entry(f"✓ ONLINE  {url[:50]}  ({elapsed}ms)")
                return {"status": "online", "response_time": elapsed}
            else:
                self._log_entry(f"✗ HTTP{resp.status_code}  {url[:50]}")
                return {"status": "offline", "response_time": 0}
                
        except requests.exceptions.ConnectTimeout:
            self._log_entry(f"✗ TIMEOUT  {url[:50]}")
            return {"status": "offline", "response_time": 0}
            
        except requests.exceptions.ConnectionError as e:
            err_str = str(e)[:60]
            # Tor might not be running
            if "SOCKS" in err_str or "10061" in err_str or "refused" in err_str.lower():
                self._log_entry(f"⚠ TOR NOT AVAILABLE — {url[:40]}")
                return {"status": "unknown", "error": "Tor not available", "response_time": 0}
            self._log_entry(f"✗ CONNFAIL  {url[:50]}")
            return {"status": "offline", "response_time": 0}
            
        except Exception as e:
            self._log_entry(f"✗ ERROR  {url[:40]}  {str(e)[:40]}")
            return {"status": "offline", "response_time": 0}

    def check_multiple(self, urls: List[str]) -> List[dict]:
        """
        Check multiple sites and return results.
        """
        results = []
        for url in urls:
            result = self.check_site(url)
            result['url'] = url
            results.append(result)
        return results