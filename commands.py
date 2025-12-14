import subprocess
import time
from datetime import datetime
import pyautogui
from search import google_search  # функція для пошуку через Google API

class CommandHandler:
    def __init__(self):
        self.state = "idle"  # idle / awaiting_search_query / awaiting_confirmation
        self.pending_query = ""

    def handle_command(self, text):
        text = text.lower()
        response = "Невідома команда"
        action = None

        # --- Списки схожих фраз ---
        greetings = ["привіт", "привід", "хай", "здрастуйте"]
        abilities = ["що ти вмієш", "можеш", "що робиш", "твоя функція"]
        open_notepad = ["відкрити блокнот", "відкрий блокнот", "notepad"]
        close_notepad = ["закрити блокнот", "вийти з блокнота", "закрити notepad"]
        save_file = ["зберегти файл", "зберегти"]
        open_browser = ["відкрити браузер", "відкрий браузер", "chrome"]
        close_browser = ["закрити браузер", "закрий браузер", "вимкни браузер", "закрити chrome"]
        show_date = ["показати дату", "яка дата", "день сьогодні"]
        stop_commands = ["зупинись", "па-па", "стоп"]
        search_cmd = ["пошук", "знайди", "шукати"]

        # --- Обробка стану пошуку ---
        if self.state == "awaiting_search_query":
            self.pending_query = text
            response = f"Хочеш відкрити перший результат пошуку за '{self.pending_query}'? (так/ні)"
            self.state = "awaiting_confirmation"
            return response, action

        if self.state == "awaiting_confirmation":
            if text in ["так", "yes", "угу"]:
                first_link = google_search(self.pending_query)
                if first_link:
                    response = f"Відкриваю {first_link}"
                    action = {"type": "open_url", "url": first_link}
                else:
                    response = "Нічого не знайдено."
            else:
                response = "Пошук скасовано."
            self.pending_query = ""
            self.state = "idle"
            return response, action

        # --- Логіка команд ---
        if any(word in text for word in greetings):
            response = "Привіт! Готовий виконувати команди."
        elif any(word in text for word in abilities):
            response = "Можу запускати програми, показувати дату та час, а також шукати інформацію."
        elif any(word in text for word in open_notepad):
            response = "Відкриваю Блокнот..."
            subprocess.Popen(["notepad.exe"])
        elif any(word in text for word in close_notepad):
            response = "Закриваю Блокнот..."
            subprocess.Popen(["taskkill", "/IM", "notepad.exe", "/F"])
        elif any(word in text for word in save_file):
            response = "Зберігаю файл..."
            pyautogui.hotkey('ctrl', 's')
            time.sleep(0.5)
            pyautogui.press('enter')
        elif any(word in text for word in open_browser):
            response = "Відкриваю браузер..."
            subprocess.Popen(["start", "chrome"], shell=True)
        elif any(word in text for word in close_browser):
            response = "Закриваю браузер..."
            subprocess.Popen(["taskkill", "/IM", "chrome.exe", "/F"])
        elif any(word in text for word in show_date):
            today = datetime.now().strftime("%d.%m.%Y")
            response = f"Сьогодні {today}."
        elif any(word in text for word in stop_commands):
            response = "Завершую роботу..."
            action = "stop"
        elif any(word in text for word in search_cmd):
            self.state = "awaiting_search_query"
            response = "Що шукати?"

        return response, action
