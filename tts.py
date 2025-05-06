import pyttsx3
import json

# Загрузка конфига
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

engine = pyttsx3.init()

# Установка голоса Microsoft Zira
def set_voice_properties():
    voices = engine.getProperty('voices')
    for voice in voices:
        if "Zira" in voice.name or "David" in voice.name:
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)

set_voice_properties()

def speak(text):
    print(f"[Пятница]: {text}")
    engine.say(text)
    engine.runAndWait()