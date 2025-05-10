import os
import asyncio
import json
from telethon import TelegramClient
from db import save_channel_info, save_post_info

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Загружаем конфиг
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
session_name = config["session_name"]  # newscrapper

client = TelegramClient(session_name, api_id, api_hash)


async def process_channel(username):
    try:
        entity = await client.get_entity(username)
        full_info = await client(GetFullChannelRequest(entity))

        # Сохраняем информацию о канале
        save_channel_info(
            username=username,
            title=entity.title,
            description=full_info.full_chat.about,
            subscribers=full_info.full_chat.participants_count
        )

        # Получаем последние 10 сообщений
        async for message in client.iter_messages(entity, limit=10):
            if message.text:
                save_post_info(
                    channel=username,
                    post_id=message.id,
                    text=message.text,
                    comments=message.replies.replies if message.replies else 0
                )

        print(f"[+] Обработан {username}, постов: 10")

    except Exception as e:
        print(f"[x] Ошибка с {username}: {e}")


async def main():
    await client.connect()
    if not await client.is_user_authorized():
        raise Exception("❗ Сессия не авторизована. Создайте .session локально через auth_session.py")

    channels = config["channels"]
    print(f"[-] Обработка: {channels}")

    for channel in channels:
        await process_channel(channel)

    print("[✓] Все каналы обработаны.")


if __name__ == "__main__":
    asyncio.run(main())







