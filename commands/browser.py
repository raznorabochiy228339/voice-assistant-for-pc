from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pyautogui
import webbrowser
import os

def open_website(url):
    """Открытие указанного сайта."""
    webbrowser.open(url)

def open_youtube():
    open_website("https://www.youtube.com")

def open_vk():
    open_website("https://vk.com")

def search_in_browser(query):
    """Поиск в Google."""
    driver = open_browser()
    driver.get("https://www.google.com")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    pyautogui.sleep(2)

def open_browser():
    """Открытие браузера и возврат драйвера."""
    service = Service("drivers/chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def refresh_page():
    """Обновление страницы (F5)."""
    pyautogui.hotkey('f5')

def add_to_bookmarks():
    """Добавление в закладки (Ctrl+D)."""
    pyautogui.hotkey('ctrl', 'd')

def clear_browser_history():
    """Очистка истории браузера (Ctrl+Shift+Delete)."""
    pyautogui.hotkey('ctrl', 'shift', 'delete')

def open_downloads():
    """Открытие окна загрузок (Ctrl+J)."""
    pyautogui.hotkey('ctrl', 'j')

def search_images(query):
    """Поиск изображений в Google."""
    open_website(f"https://images.google.com/search?q={query}")