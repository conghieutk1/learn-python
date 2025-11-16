# telegram_client.py
import os
import requests


def send_message(text: str):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    # LƯU Ý: phải có https + /bot{token}/sendMessage
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }

    resp = requests.post(url, json=payload, timeout=5)

    # Debug trước khi raise lỗi
    if resp.status_code >= 400:
        print("[ERROR] Telegram API trả về lỗi:")
        print("Status:", resp.status_code)
        print("URL   :", resp.url)
        try:
            print("Body  :", resp.json())
        except Exception:
            print("Body  (raw):", resp.text)

    resp.raise_for_status()
    return resp.json()
