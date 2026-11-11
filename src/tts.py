"""Text-to-speech (works offline). Runs in a background thread so the video never freezes."""
import queue
import sys
import threading

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import win32com.client
    import pythoncom
except ImportError:
    win32com = None
    pythoncom = None


class Speaker:
    def __init__(self):
        self.q = queue.Queue()
        self.enabled = (win32com is not None) or (pyttsx3 is not None)
        if self.enabled:
            threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        # On Windows, COM must be initialized inside each secondary thread
        if pythoncom is not None:
            try:
                pythoncom.CoInitialize()
            except Exception:
                pass

        # Native Windows SAPI voice instance (fastest and most reliable on Windows)
        sapi_voice = None
        if win32com is not None and sys.platform == "win32":
            try:
                sapi_voice = win32com.client.Dispatch("SAPI.SpVoice")
                sapi_voice.Rate = 1  # Comfortable speaking rate (-10 to 10)
            except Exception:
                sapi_voice = None

        while True:
            text = self.q.get()
            if text is None:
                break
            text = str(text).strip()
            if not text:
                continue

            spoken = False

            # Strategy 1: Native Windows SAPI (avoids pyttsx3 event-loop freeze bug)
            if sapi_voice is not None:
                try:
                    sapi_voice.Speak(text)
                    spoken = True
                except Exception:
                    # If SAPI failed, retry creating fresh SAPI dispatch
                    try:
                        sapi_voice = win32com.client.Dispatch("SAPI.SpVoice")
                        sapi_voice.Rate = 1
                        sapi_voice.Speak(text)
                        spoken = True
                    except Exception:
                        sapi_voice = None

            # Strategy 2: pyttsx3 with fresh engine per utterance
            if not spoken and pyttsx3 is not None:
                try:
                    engine = pyttsx3.init()
                    engine.setProperty("rate", 160)
                    engine.say(text)
                    engine.runAndWait()
                    try:
                        engine.stop()
                    except Exception:
                        pass
                    del engine
                    spoken = True
                except Exception as e:
                    print(f"[TTS Warning] Speech error: {e}")

    def say(self, text):
        if self.enabled and text:
            self.q.put(text)

    def close(self):
        if self.enabled:
            self.q.put(None)
