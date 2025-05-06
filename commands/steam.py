import subprocess
import os
import json
import pyautogui
from tts import speak

# Загрузка конфига
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

STEAM_PATH = config["steam_path"]

def launch_steam():
    """Запуск клиента Steam."""
    if os.path.exists(STEAM_PATH):
        subprocess.Popen([STEAM_PATH])
        speak("Запускаю Steam.")
    else:
        speak("Steam не найден.")

def launch_game(game_name):
    """Запуск игры через Steam."""
    if os.path.exists(STEAM_PATH):
        subprocess.Popen([STEAM_PATH, "-applaunch", game_name])
        speak(f"Запускаю игру {game_name}.")
    else:
        speak("Steam не найден.")

def list_installed_games():
    """Возвращает список установленных игр."""
    libraryfolders_path = os.path.join(STEAM_PATH, "steamapps", "libraryfolders.vdf")
    if not os.path.exists(libraryfolders_path):
        return []

    with open(libraryfolders_path, "r", encoding="utf-8") as f:
        import vdf
        libraryfolders = vdf.load(f)

    games = {}
    for folder in libraryfolders["libraryfolders"].values():
        path = folder.get("path")
        if path and os.path.exists(os.path.join(path, "steamapps")):
            for file in os.listdir(os.path.join(path, "steamapps")):
                if file.startswith("appmanifest_"):
                    app_id = file.split("_")[1].split(".")[0]
                    with open(os.path.join(path, "steamapps", file), "r", encoding="utf-8") as manifest:
                        data = vdf.load(manifest)
                        games[data["AppState"]["name"]] = app_id
    return games

def select_main_account():
    """Выбор основного аккаунта в Steam."""
    speak("Вхожу в основной аккаунт")
    # Пример: клик по первому аккаунту
    pyautogui.click(x=250, y=240)

def enable_mic_in_steam():
    """Включение микрофона в Steam."""
    speak("Микрофон в Steam включён.")