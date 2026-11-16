import threading
import speech_recognition as sr
import pyttsx3


class SpeechEngine:
    """Online Google speech recognition + local Windows text-to-speech."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.microphone = None
        self.tts = pyttsx3.init()
        self.tts.setProperty("rate", 178)
        self._tts_lock = threading.Lock()
        self._mic_lock = threading.Lock()

    def listen_once(self, timeout=5, phrase_time_limit=8):
        try:
            # Prevent the wake-word loop and push-to-talk from opening the mic together.
            with self._mic_lock:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(
                        source, timeout=timeout, phrase_time_limit=phrase_time_limit
                    )
            return self.recognizer.recognize_google(audio, language="en-IN")
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as exc:
            raise RuntimeError(f"Speech recognition service unavailable: {exc}") from exc
        except OSError as exc:
            raise RuntimeError(
                "Microphone could not be opened. Check Windows microphone permissions "
                "and the default recording device."
            ) from exc

    def speak(self, text):
        if not text:
            return
        # pyttsx3 is synchronous; lock prevents overlapping speech from threads.
        with self._tts_lock:
            self.tts.say(str(text))
            self.tts.runAndWait()
