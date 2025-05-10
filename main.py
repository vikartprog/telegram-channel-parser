import os
import json
import asyncio
import random
from datetime import datetime

from telethon.sync import TelegramClient
from telethon.errors import (
    FloodWaitError, UsernameNotOccupiedError, PeerIdInvalidError
)
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetDiscussionMessageRequest

from db import init_db, save_channel, save_posts

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
STATE_PATH = os.path.join(BASE_DIR, "data", "state.json")

with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

api_id = config['api_id']
api_hash = config['api_hash']
session_name = os.path.join(BASE_DIR, config['session_name'])


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, 'r') as f:
            return json.load(f)
    return {"processed": []}


def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)


async def process_channel(client, username, state):
    if username in state["processed"]:
        return

    try:
        try:
            entity = await client.get_entity(username)
        except (UsernameNotOccupiedError, PeerIdInvalidError):
            print(f"[!] Канал {username} не найден.")
            return

        full = await client(GetFullChannelRequest(channel=entity))
        subscribers = full.full_chat.participants_count

        if subscribers < 2000:
            print(f"[–] Пропущен {username}: {subscribers} подписчиков")
            return

        channel_info = {
            "username": username,
            "title": entity.title,
            "description": full.full_chat.about,
            "subscriber_count": subscribers,
            "last_updated": datetime.now().isoformat()
        }
        save_channel(channel_info)

        posts = []
        async for message in client.iter_messages(entity, limit=10):
            if message.id and message.text:
                try:
                    discussion = await client(GetDiscussionMessageRequest(
                        peer=entity,
                        msg_id=message.id
                    ))
                    comments = len(discussion.replies.replies) if discussion.replies else 0
                except:
                    comments = 0

                posts.append({
                    "id": str(message.id),
                    "channel_username": username,
                    "text": message.text,
                    "date": message.date.isoformat(),
                    "comments": comments
                })

        save_posts(posts)
        print(f"[+] Обработан {username}, постов: {len(posts)}")
        state["processed"].append(username)
        save_state(state)

        await asyncio.sleep(random.uniform(8, 15))

    except FloodWaitError as e:
        print(f"[!] FloodWait: {e.seconds}s")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        print(f"[X] Ошибка с {username}: {e}")


async def main():
    init_db()
    state = load_state()

    all_channels = [
        "coinmarketcap",
        "okxwallet",
        "durov",
        "binance_russian"
    ]

    to_process = [ch for ch in all_channels if ch not in state["processed"]][:1]
    if not to_process:
        print("[✓] Все каналы обработаны.")
        return

    print(f"[→] Обработка: {to_process}")
    async with TelegramClient(session_name, api_id, api_hash) as client:
        for username in to_process:
            await process_channel(client, username, state)


if __name__ == "__main__":
    asyncio.run(main())






