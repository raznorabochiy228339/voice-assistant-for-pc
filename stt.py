import speech_recognition as sr
import json

# Загрузка конфига
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Слушаю...")
        audio = recognizer.listen(source, phrase_time_limit=3)
        try:
            text = recognizer.recognize_google(audio, language=config["language"])
            return text.lower()
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"[Ошибка STT]: {e}")
            return ""