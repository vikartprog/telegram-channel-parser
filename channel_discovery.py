import requests
from bs4 import BeautifulSoup

def discover_channels_from_tlgrm(min_subs=2000, max_channels=50):
    url = "https://tlgrm.ru/channels"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f"[!] Ошибка подключения: {e}")
        return []

    if response.status_code != 200:
        print(f"[!] Ошибка {response.status_code} при загрузке tlgrm.ru")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    found = []

    cards = soup.select("a.channel-item")  # <== Новый селектор (обновлён)

    for card in cards:
        href = card.get("href")
        if not href or not href.startswith("/channels/"):
            continue

        username = href.replace("/channels/", "").strip()

        stats = card.select_one("div.channel-item__subscribers")
        if not stats:
            continue

        subs_text = stats.text.strip()
        subs_text = subs_text.replace(" подписчиков", "").replace(" ", "")
        subs_text = subs_text.replace("K", "000").replace("M", "000000")

        try:
            subs = int(subs_text)
            if subs >= min_subs:
                found.append(username)
        except:
            continue

        if len(found) >= max_channels:
            break

    return list(set(found))
