import os
from pathlib import Path
from util import load_json, save_json
from github_client import get_latest_release
from telegram_client import send_message

STATE_FILE = "state.json"
CONFIG_FILE = "config.json"

def load_config():
    # ví dụ cấu trúc config:
    # { "repos": ["owner1/repo1", "owner2/repo2"] }
    cfg = load_json(CONFIG_FILE, default={"repos": []})
    return cfg["repos"]

def main():
    repos = load_config()
    state = load_json(STATE_FILE, default={})

    for full_name in repos:
        owner, repo = full_name.split("/", 1)
        latest = get_latest_release(owner, repo)
        if not latest:
            print(f"[INFO] No releases for {full_name}")
            continue

        tag = latest.get("tag_name")
        html_url = latest.get("html_url")
        published_at = latest.get("published_at")

        last_tag = state.get(full_name)
        if last_tag == tag:
            print(f"[INFO] No new release for {full_name} (still {tag})")
            continue

        text = (
            f"*New release* for `{full_name}`\n"
            f"Tag: `{tag}`\n"
            f"Published at: `{published_at}`\n"
            f"Link: {html_url}"
        )

        send_message(text)
        print(f"[OK] Sent release {tag} for {full_name}")
        state[full_name] = tag

    save_json(STATE_FILE, state)

if __name__ == "__main__":
    # check env
    if "TELEGRAM_BOT_TOKEN" not in os.environ or "TELEGRAM_CHAT_ID" not in os.environ:
        raise SystemExit("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars")
    main()
