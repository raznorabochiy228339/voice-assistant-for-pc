import asyncio
import json
import os
import time
from stt import listen
from tts import speak
from commands.mouse_keyboard import move_cursor, click_mouse, scroll_mouse
from commands.windows import sleep_mode, shutdown_pc, restart_pc, clear_recycle_bin, check_battery_status
from commands.browser import open_website, search_in_browser, refresh_page, add_to_bookmarks
from commands.steam import launch_steam, launch_game
from commands.telegram import send_message_by_name
import subprocess
import psutil
import pyautogui
import webbrowser

# Загрузка конфига
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Глобальная переменная для управления циклом
running = True

async def main():
    wake_word = config["wake_word"].lower()
    print(f"[Пятница]: Ассистент активирован. Жду слово '{wake_word}'...")
    
    while running:
        try:
            text = listen().lower()
            if wake_word in text:
                cmd = text.replace(wake_word, "").strip()
                if cmd:
                    print(f"[Команда]: {cmd}")
                    execute_command(cmd)
        except KeyboardInterrupt:
            print("\n[Пятница]: Завершение работы.")
            speak("Отключаю питание")
            break
        except Exception as e:
            print(f"[Ошибка]: {e}")
            speak("Ошибка")

def execute_command(command):
    global running
    
    # === Управление мышью и клавиатурой ===
    if "перемести курсор" in command:
        direction = command.split()[-1]
        move_cursor(direction)
    
    elif "нажми правую кнопку" in command:
        click_mouse("right")
    
    elif "нажми левую кнопку" in command:
        click_mouse("left")
    
    elif "скроллинг" in command:
        direction = command.split()[-1]
        scroll_mouse(direction)
    
    # === Управление Windows ===
    elif "спящий режим" in command:
        sleep_mode()
    
    elif "выключи компьютер" in command:
        shutdown_pc()
    
    elif "перезагрузи компьютер" in command:
        restart_pc()
    
    elif "очисти корзину" in command:
        clear_recycle_bin()
    
    # === Управление браузером ===
    elif "открой сайт" in command:
        url = command.replace("открой сайт", "").strip()
        open_website(url)
    
    elif "поиск в браузере" in command:
        query = command.replace("поиск в браузере", "").strip()
        search_in_browser(query)
    
    elif "обнови страницу" in command:
        refresh_page()
    
    elif "добавь в закладки" in command:
        add_to_bookmarks()
    
    # === Управление Steam ===
    elif "запусти steam" in command:
        launch_steam()
    
    elif "запусти игру" in command:
        game_name = command.replace("запусти игру", "").strip()
        launch_game(game_name)
    
    # === Управление Telegram ===
    elif "отправь сообщение" in command:
        parts = command.replace("отправь сообщение", "").strip().split(" ", 1)
        if len(parts) == 2:
            recipient, message = parts
            send_message_by_name(recipient, message)
        else:
            speak("Неправильный формат команды. Используйте: 'отправь сообщение [имя] [сообщение]'")
    
    # === Системные команды ===
    elif "статус батареи" in command:
        check_battery_status()
    
    elif "выход" in command:
        speak("отключаю питание")
        running = False
    
    else:
        speak("чего вы пытаетесь добиться сэр!")