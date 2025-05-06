import os
import sys
import json
import time
import threading
import subprocess
import shutil
import psutil
import zipfile
import logging
import webbrowser
import pyautogui
import platform
import speech_recognition as sr
from pathlib import Path
from playsound import playsound
from datetime import datetime

# === Настройки логирования ===
logging.basicConfig(
    filename="voice_assis.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Глобальные переменные ===
running = True
SOUNDS_DIR = "sounds"
# === Переменные для записи ===
is_recording = False
recorded_text = []

# === Конфигурация ===
config = {
    "wake_word": "пятница",
    "language": "ru-RU",
    "steam_path": r"C:\Program Files (x86)\Steam\steam.exe",
    "volume_step": 5,
    "brightness_step": 10,
    #инструкция по получению в файле readme.md
    "telegram_api_hash": "", #вставте сюда ваш API HASH
    "telegram_api_id": 12345678 #вставте сюда ваш API ID
}

# === Функция воспроизведения аудио ===
import pyttsx3

# Инициализация синтезатора речи
engine = pyttsx3.init()

# Настройка голоса (Microsoft)
def set_voice_properties():
    voices = engine.getProperty('voices')
    for voice in voices:
        if "Irina" in voice.name:
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 150)  # Скорость речи
    engine.setProperty('volume', 1.0)  # Громкость (от 0.0 до 1.0)

set_voice_properties()

def speak(text):
    """Произносит текст через голосовой движок."""
    print(f"[Пятница]: {text}")
    engine.say(text)
    engine.runAndWait()

# === Функция распознавания речи ===
def listen():
    """Распознаёт речь через микрофон."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Слушаю...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language=config["language"])
            print(f"Вы сказали: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Не понял вас.")
            return ""
        except sr.RequestError:
            print("Ошибка сервиса распознавания.")
            return ""

# === Функции управления системой ===
def execute_command(command):
    global running

    if "приветствие" in command:
        speak("Здравствуйте, сэр!")

    elif "создать резервную копию" in command:
        speak("образ создан")
        backup_name = f"backup_{time.strftime('%Y%m%d_%H%M%S')}.zip"
        with zipfile.ZipFile(backup_name, 'w') as zipf:
            for folder in ['sounds', '.']:
                for root, _, files in os.walk(folder):
                    for file in files:
                        if file.endswith((".py", ".json", ".wav")):
                            zipf.write(os.path.join(root, file))
        print(f"Резервная копия создана: {backup_name}")

    elif "очисти кэш" in command:
        speak("включилось аварийное резервное питание")
        temp_dirs = [
            os.getenv("TEMP"),
            os.path.join(os.getenv("LOCALAPPDATA"), "Temp")
        ]
        for temp_dir in temp_dirs:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                    except Exception:
                        pass
        print("Кэш очищен.")

    elif "мониторинг активности" in command:
        speak("вывожу список активных приложений")
        def monitor_activity():
            while True:
                processes = list(psutil.process_iter(['name']))
                active_apps = [p.info['name'] for p in processes]
                logging.info(f"Активные приложения: {', '.join(active_apps)}")
                time.sleep(30)
        threading.Thread(target=monitor_activity, daemon=True).start()

    elif "статус батареи" in command:
        battery = psutil.sensors_battery()
        percent = battery.percent
        speak(f"Энергия {percent}%")

    elif "выключи монитор" in command:
        speak("отключаю питание")
        import ctypes
        ctypes.windll.user32.SendMessageW(65535, 274, 61808, 2)

    elif "диспетчер задач" in command:
        speak("реактор принял модифицированное ядро")
        subprocess.Popen("taskmgr.exe", shell=True)

    elif "покажи логи" in command:
        speak("открываю логи")
        os.startfile("jarvis.log")

    elif "выход" in command:
        speak("отключаю питание")
        running = False

    # === Управление мышью и клавиатурой ===
    elif "перемести курсор" in command:
        direction = command.split("перемести курсор")[-1].strip()
        move_cursor(direction)

    elif "нажми правую кнопку" in command:
        click_mouse("right")

    elif "нажми левую кнопку" in command:
        click_mouse("left")

    elif "скроллинг" in command:
        direction = command.split("скроллинг")[-1].strip()
        scroll_mouse(direction)

    elif "курсор в начало строки" in command:
        move_cursor_to_position("начало строки")

    elif "курсор в конец строки" in command:
        move_cursor_to_position("конец строки")

    elif "навигация по шрифтам влево" in command:
        navigate_fonts("влево")

    elif "навигация по шрифтам вправо" in command:
        navigate_fonts("вправо")

    elif "напечатай" in command:
        text = command.replace("напечатай", "").strip()
        type_text(text)

    elif "смени язык ввода" in command:
        change_input_language()

    elif "удали последнее слово" in command:
        delete_last_word()

    elif "удали весь текст" in command:
        delete_all_text()

    elif "скопируй текст" in command:
        copy_text()

    elif "вставь текст" in command:
        paste_text()

    elif "выдели текст" in command:
        select_text()

    elif "отмени действие" in command:
        undo_action()

    elif "открой youtube" in command:
        open_youtube()

    elif "открой vk" in command:
        open_vk()

    elif "поиск в браузере" in command:
        query = command.replace("поиск в браузере", "").strip()
        search_in_browser(query)

    elif "обнови страницу" in command:
        refresh_page()

    elif "добавь в закладки" in command:
        add_to_bookmarks()

    elif "очисти историю браузера" in command:
        clear_browser_history()

    elif "открой загрузки" in command:
        open_downloads()

    elif "поиск изображений" in command:
        image_query = command.replace("поиск изображений", "").strip()
        search_images(image_query)

    elif "закрой окно" in command:
        close_window()

    elif "сверни окно" in command:
        minimize_window()

    elif "развёрни окно" in command:
        maximize_window()

    elif "переключи окно" in command:
        switch_window()

    elif "установи громкость" in command:
        try:
            level = int(''.join(filter(str.isdigit, command)))
            set_volume(level)
        except:
            speak("укажите уровень громкости в процентах")

    elif "без звука" in command:
        mute_audio()

    elif "установи яркость" in command:
        try:
            brightness_level = int(''.join(filter(str.isdigit, command)))
            adjust_brightness(brightness_level)
        except:
            speak("укажите уровень яркости от 0 до 100")

    elif "спящий режим" in command:
        sleep_mode()

    elif "выключи компьютер" in command:
        shutdown_pc()

    elif "перезагрузи компьютер" in command:
        restart_pc()

    elif "очисти корзину" in command:
        clear_recycle_bin()

    elif "сохрани документ как" in command:
        save_document_as()

    elif "отправь сообщение" in command:
        parts = command.replace("отправь сообщение", "").strip().split(" ", 1)
        if len(parts) == 2:
            contact, msg = parts
            send_message_by_name(contact, msg)
        else:
            speak("неправильный формат команды")

    elif "запусти steam" in command:
        launch_steam()

    elif "запусти игру" in command:
        game_name = command.replace("запусти игру", "").strip()
        launch_game(game_name)

    elif "список игр" in command:
        games = list_installed_games()
        if games:
            speak("установленные игры:")
            for game in games:
                print(f"- {game}")
        else:
            speak("игр не найдено")

    # === Не распознанная команда ===
    else:
        speak("чего вы пытаетесь добиться сэр!")

# === Функции управления мышью и клавиатурой ===
def move_cursor(direction):
    """Перемещает курсор мыши."""
    offsets = {"вправо": (50, 0), "влево": (-50, 0), "вверх": (0, -50), "вниз": (0, 50)}
    x, y = pyautogui.position()
    offset = offsets.get(direction, (0, 0))
    pyautogui.moveTo(x + offset[0], y + offset[1])
    speak(f"курсор перемещён {direction}")

def click_mouse(button="left"):
    """Нажимает левую или правую кнопку мыши."""
    if button == "right":
        pyautogui.rightClick()
        speak("правая кнопка мыши нажата")
    else:
        pyautogui.leftClick()
        speak("левая кнопка мыши нажата")

def scroll_mouse(direction):
    """Скроллинг."""
    amount = 100 if direction == "вниз" else -100
    pyautogui.scroll(amount)
    speak(f"скроллинг {direction}")

# === Перемещение курсора ===
def move_cursor_to_position(position):
    """Перемещает курсор в начало/конец строки/документа."""
    if position == "начало строки":
        pyautogui.hotkey('ctrl', 'home')
    elif position == "конец строки":
        pyautogui.hotkey('ctrl', 'end')
    speak(f"курсор перемещён {position}")

# === Навигация по шрифтам ===
def navigate_fonts(direction):
    """Переключение между шрифтами или вкладками."""
    if direction == "влево":
        pyautogui.hotkey('ctrl', 'shift', 'tab')
    elif direction == "вправо":
        pyautogui.hotkey('ctrl', 'tab')
    speak(f"навигация по шрифтам {direction}")

# === Текстовые команды ===
def type_text(text):
    """Автозаполнение текста."""
    pyautogui.write(text, interval=0.1)
    speak(f"напечатано: {text}")

def change_input_language():
    """Смена языка ввода."""
    pyautogui.hotkey('alt', 'shift')
    speak("язык ввода изменён")

def delete_last_word():
    """Удаление последнего слова."""
    pyautogui.hotkey('ctrl', 'backspace')
    speak("последнее слово удалено")

def delete_all_text():
    """Удаление всего текста."""
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('delete')
    speak("весь текст удалён")

def copy_text():
    """Копирование выделенного текста."""
    pyautogui.hotkey('ctrl', 'c')
    speak("текст скопирован")

def paste_text():
    """Вставка текста из буфера."""
    pyautogui.hotkey('ctrl', 'v')
    speak("текст вставлен")

def select_text():
    """Выделение всего текста."""
    pyautogui.hotkey('ctrl', 'a')
    speak("текст выделен")

def undo_action():
    """Отмена последнего действия."""
    pyautogui.hotkey('ctrl', 'z')
    speak("действие отменено")

# === Управление браузером ===
def open_website(url):
    """Открытие сайта."""
    webbrowser.open(url)
    speak(f"открываю {url}")

def open_youtube():
    open_website("https://youtube.com")

def open_vk():
    open_website("https://vk.com")

def search_in_browser(query):
    open_website(f"https://www.google.com/search?q={query}")

def refresh_page():
    pyautogui.hotkey('f5')
    speak("страница обновлена")

def add_to_bookmarks():
    pyautogui.hotkey('ctrl', 'd')
    speak("добавлено в закладки")

def clear_browser_history():
    pyautogui.hotkey('ctrl', 'shift', 'delete')
    speak("история браузера очищена")

def open_downloads():
    pyautogui.hotkey('ctrl', 'j')
    speak("открытие загрузок")

def search_images(query):
    open_website(f"https://images.google.com/search?q={query}")

# === Управление окнами ===
def close_window():
    pyautogui.hotkey('alt', 'f4')
    speak("окно закрыто")

def minimize_window():
    pyautogui.hotkey('win', 'down')
    speak("окно свёрнуто")

def maximize_window():
    pyautogui.hotkey('win', 'up')
    speak("окно развернуто")

def switch_window():
    pyautogui.hotkey('alt', 'tab')
    speak("переключаюсь между окнами")

# === Управление громкостью и яркостью ===
def set_volume(level):
    """Устанавливает громкость."""
    for _ in range(level // config["volume_step"]):
        pyautogui.press('volumeup')
    speak(f"громкость установлена на {level}%")

def mute_audio():
    """Отключение звука."""
    pyautogui.press('volumemute')
    speak("звук отключён")

def adjust_brightness(level):
    """Изменение яркости экрана."""
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(level)
        speak("яркость изменена")
    except ImportError:
        speak("не удалось изменить яркость")

# === Управление Windows ===
def sleep_mode():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    speak("перехожу в спящий режим")

def shutdown_pc():
    os.system("shutdown /s /t 1")
    speak("выключаю ПК")

def restart_pc():
    os.system("shutdown /r /t 1")
    speak("перезагружаю ПК")

def clear_recycle_bin():
    try:
        os.system("del /Q /F %TEMP%\\*")
        os.system("del /Q /F %SystemRoot%\\Temp\\*")
        speak("корзина очищена")
    except Exception as e:
        speak("ошибка при очистке корзины")

def save_document_as():
    pyautogui.hotkey('ctrl', 'shift', 's')
    speak("сохраняю документ как...")

# === Управление Steam ===
def launch_steam():
    try:
        subprocess.Popen([config["steam_path"]])
        speak("запускаю Steam")
    except Exception as e:
        speak("не удалось запустить Steam")

def launch_game(game_name):
    try:
        subprocess.Popen([config["steam_path"], "-applaunch", game_name])
        speak(f"запускаю игру {game_name}")
    except Exception as e:
        speak("не удалось запустить игру")

def list_installed_games():
    libraryfolders_path = os.path.join(config["steam_path"], "steamapps", "libraryfolders.vdf")
    if not os.path.exists(libraryfolders_path):
        return {} 
    with open(libraryfolders_path, "r") as f:
        import vdf
        libraryfolders = vdf.load(f)
    games = {}
    for folder in libraryfolders["libraryfolders"].values():
        path = folder.get("path")
        if path and os.path.exists(os.path.join(path, "steamapps")):
            for file in os.listdir(os.path.join(path, "steamapps")):
                if file.startswith("appmanifest_"):
                    app_id = file.split("_")[1].split(".")[0]
                    with open(os.path.join(path, "steamapps", file), "r") as manifest:
                        data = vdf.load(manifest)
                        games[data["AppState"]["name"]] = app_id
    return games

# === Управление Telegram ===
def send_message_by_name_async(name, message):
    try:
        import asyncio
        from telethon import TelegramClient
        client = TelegramClient(
            "voice_assis",
            api_id=config.telegram_api_id,
            api_hash=config.telegram_api_hash,
            system_version="4.16.30-vxCUSTOM",  # Версия системы
            device_model="CustomDevice",       # Модель устройства
            app_version="1.0.0"                # Версия приложения
        )
        async def send():
            await client.connect()
            contacts = {dialog.name.lower(): dialog.entity.id async for dialog in client.iter_dialogs()}
            if name.lower() in contacts:
                await client.send_message(contacts[name.lower()], message)
        asyncio.run(send())
    except Exception as e:
        speak("ошибка при отправке сообщения")

def send_message_by_name(name, message):
    threading.Thread(target=send_message_by_name_async, args=(name, message), daemon=True).start()

# === Системные функции ===
def system_diagnostics():
    total, used, free = shutil.disk_usage("/")
    cpu_info = platform.processor()
    python_version = platform.python_version()
    print(f"Диск: {total//(2**30)} ГБ | CPU: {cpu_info} | Python: {python_version}")
    speak("проверка завершена")

def run_speedtest():
    webbrowser.open('https://www.speedtest.net/')
    speak("запуск проверки сети")

def check_battery_status():
    battery = psutil.sensors_battery()
    percent = battery.percent
    speak(f"Энергия {percent}%")

def clear_temp_cache():
    temp_dirs = [os.getenv("TEMP"), os.path.join(os.getenv("LOCALAPPDATA"), "Temp")]
    for temp_dir in temp_dirs:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                try:
                    os.remove(os.path.join(root, file))
                except Exception:
                    pass
    speak("кэш очищен")

def run_defragmentation():
    speak("начинаю автоматическую сборку")
    subprocess.Popen("defrag C: /u /v", shell=True)

def open_task_manager():
    speak("реактор принял модифицированное ядро")
    subprocess.Popen("taskmgr.exe", shell=True)

# === Функции для работы с GitHub ===
import git

# === Основной цикл ===
def background_listener():
    while running:
        try:
            text = listen()
            if text and config["wake_word"] in text:
                cmd = text.replace(config["wake_word"], "").strip()
                if cmd:
                    execute_command(cmd)
        except Exception as e:
            speak("ошибка")
            print(f"[Ошибка]: {e}")

# === Запуск ассистента ===
def main():
    print(f"[Пятница]: Ассистент активирован. Жду слово '{config['wake_word']}'...")
    speak("здравствуйте, сэр!")
    listener_thread = threading.Thread(target=background_listener, daemon=True)
    listener_thread.start()
    while running:
        time.sleep(1)

if __name__ == "__main__":
    main()