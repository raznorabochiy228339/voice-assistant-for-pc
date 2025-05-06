import pyautogui
from tts import speak

def move_cursor(direction):
    """Перемещение курсора по направлениям."""
    offsets = {
        "вправо": (50, 0),
        "влево": (-50, 0),
        "вверх": (0, -50),
        "вниз": (0, 50)
    }
    x, y = pyautogui.position()
    offset = offsets.get(direction, (0, 0))
    pyautogui.moveTo(x + offset[0], y + offset[1])
    speak(f"Курсор перемещён {direction}")

def click_mouse(button="left"):
    """Нажатие кнопки мыши."""
    if button == "right":
        pyautogui.rightClick()
        speak("Правая кнопка мыши нажата")
    else:
        pyautogui.leftClick()
        speak("Левая кнопка мыши нажата")

def scroll_mouse(direction):
    """Скроллинг мышью."""
    amount = 100 if direction == "вниз" else -100
    pyautogui.scroll(amount)
    speak(f"Скроллинг {direction}")