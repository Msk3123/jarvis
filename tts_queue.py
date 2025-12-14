import pyttsx3
import threading
import queue
import traceback
import time

# Для fallback SAPI (опціонально, якщо встановлено pywin32)
try:
    import pythoncom
    from win32com.client import Dispatch
    HAS_SAPI = True
except Exception:
    HAS_SAPI = False

tts_queue = queue.Queue()

def _create_engine():
    try:
        return pyttsx3.init('sapi5')
    except Exception:
        try:
            return pyttsx3.init()
        except Exception:
            return None

def _create_sapi_voice():
    if not HAS_SAPI:
        return None
    try:
        pythoncom.CoInitialize()
        return Dispatch("SAPI.SpVoice")
    except Exception:
        return None

def tts_worker():
    engine = _create_engine()
    sapi_voice = None
    if engine:
        try:
            engine.setProperty('rate', 150)
            # діагностика: список голосів
            try:
                voices = engine.getProperty('voices')
                print(f"[TTS] pyttsx3 voices: {[v.name for v in voices]}")
            except Exception:
                pass
        except Exception:
            pass
    else:
        print("[TTS] pyttsx3 init failed, will try SAPI fallback if available")
        sapi_voice = _create_sapi_voice()
        if sapi_voice:
            print("[TTS] SAPI fallback available")
        else:
            print("[TTS] No TTS engine available")

    while True:
        text = tts_queue.get()
        try:
            if text is None:  # сигнал для завершення
                break
            print(f"[TTS] Speaking: {text!r}")

            # Основний шлях: pyttsx3
            if engine is not None:
                try:
                    # захист: зупинити попередні вузли перед новим викликом
                    try:
                        engine.stop()
                    except Exception:
                        pass
                    engine.say(text)
                    engine.runAndWait()
                    # після програвання інколи корисно зупинити
                    try:
                        engine.stop()
                    except Exception:
                        pass
                    continue
                except Exception as e:
                    print("[TTS] pyttsx3 error, will attempt reinit:", e)
                    traceback.print_exc()
                    # спроба реініціалізації
                    try:
                        engine = _create_engine()
                        if engine:
                            engine.setProperty('rate', 150)
                            engine.say(text)
                            engine.runAndWait()
                            try:
                                engine.stop()
                            except Exception:
                                pass
                            continue
                    except Exception:
                        print("[TTS] pyttsx3 reinit failed")
                        engine = None

            # Fallback на SAPI (win32com)
            if sapi_voice is None:
                sapi_voice = _create_sapi_voice()
            if sapi_voice is not None:
                try:
                    # Ініціалізація COM в потоці (на випадок)
                    try:
                        pythoncom.CoInitialize()
                    except Exception:
                        pass
                    sapi_voice.Speak(text)
                    continue
                except Exception as e:
                    print("[TTS] SAPI speak error:", e)
                    traceback.print_exc()
                    sapi_voice = None

            # Якщо нічого з вищезгаданого не працює — лог
            print("[TTS] Skipping speak, no available engine")
        finally:
            try:
                tts_queue.task_done()
            except Exception:
                pass
        time.sleep(0.01)

# Запуск потоку TTS
threading.Thread(target=tts_worker, daemon=True).start()

def speak(text):
    tts_queue.put(text)
