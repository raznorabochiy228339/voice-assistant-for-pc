import os
import subprocess
import psutil
import shutil
from tts import speak

def sleep_mode():
    """Переход в спящий режим."""
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    speak("Перехожу в спящий режим")

def shutdown_pc():
    """Выключение ПК."""
    os.system("shutdown /s /t 1")
    speak("Выключаю ПК")

def restart_pc():
    """Перезагрузка ПК."""
    os.system("shutdown /r /t 1")
    speak("Перезагружаю ПК")

def clear_recycle_bin():
    """Очистка временных файлов."""
    try:
        os.system("del /Q /F %TEMP%\\*")
        os.system("del /Q /F %SystemRoot%\\Temp\\*")
        speak("Корзина очищена")
    except Exception as e:
        speak("Ошибка при очистке корзины")

def check_battery_status():
    """Проверка уровня заряда батареи."""
    battery = psutil.sensors_battery()
    percent = battery.percent
    speak(f"Энергия {percent}%")