from telethon.sync import TelegramClient

# 🔒 Замени на свои значения
api_id = 21928399
api_hash = '91a6fd34272f7e10fecd0f7b3c8cfb10'
session_name = 'newscrapper'  # или другое имя, если хочешь

with TelegramClient(session_name, api_id, api_hash) as client:
    print("✅ Сессия успешно создана.")
