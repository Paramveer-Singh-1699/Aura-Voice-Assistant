import os
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import quote_plus


APP_ALLOWLIST = {
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "paint": ["mspaint.exe"],
    "vscode": ["code"],
    "visual studio code": ["code"],
    "file explorer": ["explorer.exe"],
}


def open_app(name):
    key = name.lower().strip()
    command = APP_ALLOWLIST.get(key)
    if not command:
        return f"I don't have {name} in my approved application list."
    try:
        subprocess.Popen(command, shell=False)
        return f"Opening {name}."
    except FileNotFoundError:
        return f"{name} isn't installed or isn't available in Windows PATH."


def open_website(site):
    sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "linkedin": "https://www.linkedin.com",
        "stackoverflow": "https://stackoverflow.com",
    }
    url = sites.get(site.lower().strip())
    if not url:
        return None
    webbrowser.open(url)
    return f"Opening {site}."


def google_search(query):
    webbrowser.open("https://www.google.com/search?q=" + quote_plus(query))
    return f"Searching Google for {query}."


def open_downloads():
    path = Path.home() / "Downloads"
    if path.exists():
        os.startfile(str(path))
        return "Opening Downloads."
    return "I couldn't find the Downloads folder."


def play_music():
    music_dir = Path.home() / "Music"
    if not music_dir.exists():
        return "I couldn't find your Music folder."
    extensions = {".mp3", ".wav", ".m4a", ".wma", ".flac"}
    tracks = [p for p in music_dir.rglob("*") if p.is_file() and p.suffix.lower() in extensions]
    if not tracks:
        return "No supported audio files were found in your Music folder."
    os.startfile(str(tracks[0]))
    return f"Playing {tracks[0].name}. Add your songs to the Music folder to use this feature."
