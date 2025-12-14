import tkinter as tk
from tkinter import scrolledtext
import threading
import json
import queue
import sounddevice as sd
from tts_queue import speak
import webbrowser
from recognition import q, callback, recognizer
from commands import CommandHandler

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Голосовий Асистент Рівень 3")
        self.running = False
        self.handler = CommandHandler()

        # Кнопка старт/стоп
        self.btn = tk.Button(root, text="Запустити", command=self.toggle)
        self.btn.pack(pady=5)

        # Логи
        self.log = scrolledtext.ScrolledText(root, width=60, height=20, state='disabled')
        self.log.pack(padx=10, pady=10)

    def log_message(self, message):
        self.log.config(state='normal')
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.config(state='disabled')

    def toggle(self):
        if not self.running:
            self.running = True
            self.btn.config(text="Стоп")
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.running = False
            self.btn.config(text="Запустити")

    def listen_loop(self):
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            while self.running:
                try:
                    data = q.get(timeout=0.1)
                except queue.Empty:
                    continue

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        response, action = self.handler.handle_command(text)

                        # Логування та голосовий відгук
                        self.log_message(f"Команда: {text}")
                        self.log_message(f"Відповідь: {response}")
                        # Неблокуючий виклик: ставимо текст у TTS-чергу
                        speak(response)

                        # Обробка спеціальних дій
                        if action == "stop":
                            self.running = False
                            self.btn.config(text="Запустити")
                        elif isinstance(action, dict) and action.get("type") == "open_url":
                            webbrowser.open(action["url"])

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    root.mainloop()
