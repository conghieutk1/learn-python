from datetime import datetime
import requests

API_BASE = "https://api.github.com"

def list_releases(owner, repo, per_page=20, max_pages=3):
    url = f"{API_BASE}/repos/{owner}/{repo}/releases"
    releases = []
    for page in range(1, max_pages + 1):
        resp = requests.get(url, params={"per_page": per_page, "page": page}, timeout=5)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        releases.extend(batch)
    return releases

def get_latest_release(owner, repo):
    releases = list_releases(owner, repo, per_page=5, max_pages=5)
    if not releases:
        return None
    # sort theo published_at
    releases.sort(key=lambda r: r.get("published_at") or "")
    return releases[-1]
