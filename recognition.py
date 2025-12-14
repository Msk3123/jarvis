import sounddevice as sd
import vosk
import queue

q = queue.Queue()
model = vosk.Model("model")  # Шлях до української моделі
recognizer = vosk.KaldiRecognizer(model, 16000)

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))
