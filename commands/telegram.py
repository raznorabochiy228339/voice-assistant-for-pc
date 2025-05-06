from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import json

# Загрузка конфига
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TELEGRAM_API_ID = config["telegram_api_id"]
TELEGRAM_API_HASH = config["telegram_api_hash"]
TELEGRAM_PHONE = config["telegram_phone"]

client = TelegramClient(
    "jarvis", 
    TELEGRAM_API_ID, 
    TELEGRAM_API_HASH,
    system_version="4.16.30-vxCUSTOM",  # Версия системы
    device_model="CustomDevice",       # Модель устройства
    app_version="1.0.0"                # Версия приложения
    )

async def send_message_by_name_async(name, message):
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(TELEGRAM_PHONE)
        code = input("Введите код из Telegram: ")
        try:
            await client.sign_in(TELEGRAM_PHONE, code)
        except SessionPasswordNeededError:
            password = input("Введите пароль от двухфакторной аутентификации: ")
            await client.sign_in(password=password)

    contacts = {}
    async for dialog in client.iter_dialogs():
        if dialog.is_user:
            contacts[dialog.name.lower()] = dialog.entity.id
    return contacts

def send_message_by_name(name, message):
    import asyncio
    asyncio.run(send_message_by_name_async(name, message))