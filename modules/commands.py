import re
from datetime import datetime
from modules.automation import (
    open_app, open_website, google_search, open_downloads, play_music
)
from modules.weather import get_weather
from modules.productivity import save_note, read_notes, parse_reminder, list_reminders


def system_information():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        battery_text = (
            f"{battery.percent}% {'charging' if battery.power_plugged else 'on battery'}"
            if battery else "not detected"
        )
        return (
            f"CPU usage is {cpu} percent. RAM usage is {ram.percent} percent "
            f"with {ram.available / (1024**3):.1f} GB available. Battery: {battery_text}."
        )
    except Exception as exc:
        return f"Couldn't read system information: {exc}"


class CommandRouter:
    def __init__(self, ai_engine):
        self.ai = ai_engine

    def handle(self, raw_text):
        text = raw_text.strip()
        low = text.lower()
        if not text:
            return "I didn't hear a command."

        if low in {"hello", "hi", "hey aura", "hello aura"}:
            return "Hello! I'm AURA. What would you like me to do?"
        if "time" in low and any(x in low for x in ("what", "tell", "current")):
            return "The time is " + datetime.now().strftime("%I:%M %p") + "."
        if "date" in low and any(x in low for x in ("what", "today", "tell", "current")):
            return "Today is " + datetime.now().strftime("%A, %d %B %Y") + "."

        reminder = parse_reminder(text)
        if reminder:
            return reminder
        if low.startswith(("take a note", "save a note", "remember this")):
            content = re.sub(r"^(take a note|save a note|remember this)\s*", "", text, flags=re.I)
            return save_note(content) if content else "Please say the note after 'take a note'."
        if "read my notes" in low or "show my notes" in low:
            return read_notes()
        if "my reminders" in low or "show reminders" in low or "list reminders" in low:
            return list_reminders()
        if "system information" in low or "system status" in low or "cpu and ram" in low:
            return system_information()
        if low.startswith("weather in "):
            return get_weather(text[11:].strip())
        if low in {"weather", "what is the weather"}:
            return get_weather("Hyderabad")

        if low.startswith("search for "):
            return google_search(text[11:].strip())
        if low.startswith("search "):
            return google_search(text[7:].strip())
        if low.startswith("open "):
            target = text[5:].strip()
            website_result = open_website(target)
            if website_result:
                return website_result
            if target.lower() in {"downloads", "my downloads", "downloads folder"}:
                return open_downloads()
            return open_app(target)
        if "play music" in low or low == "play song":
            return play_music()
        if low in {"stop", "stop speaking"}:
            return "Okay."

        return self.ai.ask(text)
