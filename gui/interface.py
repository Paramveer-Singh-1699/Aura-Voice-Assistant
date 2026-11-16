import threading
import queue
import re
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

from modules.speech import SpeechEngine
from modules.ai_engine import AIEngine
from modules.commands import CommandRouter
from database.database import initialize, get_due_reminders


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AuraApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        initialize()
        self.title("AURA — Personal Voice Assistant")
        self.geometry("980x700")
        self.minsize(820, 600)
        self.speech = SpeechEngine()
        self.ai = AIEngine()
        self.router = CommandRouter(self.ai)
        self.events = queue.Queue()
        self.listening = False
        self.wake_enabled = False
        self.wake_thread = None
        self._build_ui()
        self.after(150, self._poll_events)
        self.after(1000, self._check_reminders)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._add_message("AURA", "Hello! I'm AURA. Click the microphone or enable wake-word mode and say 'Hey Aura'.")
        self._set_status("Ready")

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        ctk.CTkLabel(sidebar, text="◉  AURA", font=ctk.CTkFont(size=27, weight="bold")).pack(pady=(28, 4))
        ctk.CTkLabel(sidebar, text="PERSONAL VOICE ASSISTANT", text_color="gray").pack(pady=(0, 30))
        self.status_label = ctk.CTkLabel(sidebar, text="● Ready", text_color="#4ade80")
        self.status_label.pack(pady=8)
        ctk.CTkButton(sidebar, text="🎙  Start listening", command=self.start_listening).pack(fill="x", padx=18, pady=8)
        self.wake_button = ctk.CTkButton(sidebar, text="Enable wake word", command=self.toggle_wake)
        self.wake_button.pack(fill="x", padx=18, pady=8)
        ctk.CTkButton(sidebar, text="Clear conversation", fg_color="transparent",
                      border_width=1, command=self.clear_chat).pack(fill="x", padx=18, pady=8)
        ctk.CTkLabel(
            sidebar,
            text="Try saying:\n• Open YouTube\n• What time is it?\n• Weather in Hyderabad\n• Take a note buy milk\n• Remind me in 10 minutes to study\n• System information",
            justify="left", text_color="#a1a1aa", wraplength=180
        ).pack(side="bottom", padx=18, pady=25, anchor="w")

        main = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=22, pady=20)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        ctk.CTkLabel(header, text="Your assistant", font=ctk.CTkFont(size=25, weight="bold")).pack(anchor="w")
        self.ai_label = ctk.CTkLabel(
            header,
            text=("AI connected" if self.ai.available else "AI not configured — predefined commands available"),
            text_color=("#4ade80" if self.ai.available else "#fbbf24")
        )
        self.ai_label.pack(anchor="w", pady=(3, 0))

        self.chat = ctk.CTkScrollableFrame(main, corner_radius=14)
        self.chat.grid(row=1, column=0, sticky="nsew")
        self.chat.grid_columnconfigure(0, weight=1)

        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        bottom.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(bottom, placeholder_text="Type a message or use the microphone…", height=44)
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry.bind("<Return>", lambda _event: self.send_text())
        ctk.CTkButton(bottom, text="Send", width=90, height=44, command=self.send_text).grid(row=0, column=1)
        ctk.CTkLabel(main, text="AURA can launch only approved apps and websites. It does not run arbitrary shell commands.",
                     text_color="gray", font=ctk.CTkFont(size=11)).grid(row=3, column=0, sticky="w", pady=(9, 0))

    def _add_message(self, sender, text):
        color = "#1d4ed8" if sender == "You" else "#27272a"
        frame = ctk.CTkFrame(self.chat, fg_color=color, corner_radius=12)
        frame.grid_columnconfigure(0, weight=1)
        frame.pack(fill="x", padx=10, pady=7)
        ctk.CTkLabel(frame, text=sender, font=ctk.CTkFont(weight="bold"),
                     text_color="#bfdbfe" if sender == "You" else "#86efac").pack(anchor="w", padx=13, pady=(8, 0))
        ctk.CTkLabel(frame, text=text, justify="left", anchor="w", wraplength=650).pack(
            anchor="w", padx=13, pady=(3, 10)
        )
        self.chat.update_idletasks()
        self.chat._parent_canvas.yview_moveto(1.0)

    def _set_status(self, status):
        self.status_label.configure(text=f"● {status}")

    def _process_command(self, text):
        self.events.put(("user", text))
        answer = self.router.handle(text)
        self.events.put(("assistant", answer))
        self.speech.speak(answer)

    def start_listening(self):
        if self.listening:
            return
        self.listening = True
        self._set_status("Listening…")
        threading.Thread(target=self._listen_worker, daemon=True).start()

    def _listen_worker(self):
        try:
            text = self.speech.listen_once(timeout=6, phrase_time_limit=9)
            if text:
                self._process_command(text)
            else:
                self.events.put(("status", "No speech detected"))
        except Exception as exc:
            self.events.put(("error", str(exc)))
        finally:
            self.listening = False
            self.events.put(("status", "Ready"))

    def toggle_wake(self):
        if self.wake_enabled:
            self.wake_enabled = False
            self.wake_button.configure(text="Enable wake word")
            self._set_status("Wake word off")
            return
        self.wake_enabled = True
        self.wake_button.configure(text="Disable wake word")
        self._set_status("Wake word active")
        self.wake_thread = threading.Thread(target=self._wake_worker, daemon=True)
        self.wake_thread.start()

    @staticmethod
    def _is_wake_phrase(phrase):
        """Accept common Google-STT renderings of the V1 wake phrase."""
        words = re.findall(r"[a-z]+", (phrase or "").lower())
        # Google sometimes transcribes the name Aura as Aurora, or drops 'hey'.
        if "aura" in words or "aurora" in words:
            return True
        return False

    def _wake_worker(self):
        # V1 uses short online Google-STT clips, not a dedicated offline wake engine.
        self.events.put(("status", "Wake listening (online)…"))
        while self.wake_enabled:
            try:
                phrase = self.speech.listen_once(timeout=2, phrase_time_limit=4)
                if phrase:
                    print(f"[AURA wake check] Heard: {phrase}", flush=True)
                if self._is_wake_phrase(phrase):
                    self.events.put(("status", "Wake word detected"))
                    self.speech.speak("I'm listening.")
                    command = self.speech.listen_once(timeout=6, phrase_time_limit=10)
                    if command:
                        self._process_command(command)
                    else:
                        self.events.put(("status", "No command heard; still listening"))
            except Exception as exc:
                self.events.put(("error", str(exc)))
                self.wake_enabled = False
                self.events.put(("status", "Wake word stopped"))
        self.events.put(("status", "Ready"))

    def send_text(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        threading.Thread(target=self._process_command, args=(text,), daemon=True).start()

    def clear_chat(self):
        for child in self.chat.winfo_children():
            child.destroy()

    def _poll_events(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "user":
                    self._add_message("You", value)
                elif kind == "assistant":
                    self._add_message("AURA", value)
                elif kind == "status":
                    self._set_status(value)
                elif kind == "error":
                    self._add_message("AURA", value)
                    self._set_status("Check microphone / connection")
        except queue.Empty:
            pass
        self.after(150, self._poll_events)

    def _check_reminders(self):
        due = get_due_reminders(datetime.now().isoformat(timespec="seconds"))
        for reminder in due:
            message = f"Reminder: {reminder['content']}"
            self._add_message("AURA", message)
            self.speech.speak(message)
            messagebox.showinfo("AURA reminder", reminder["content"])
        self.after(1000, self._check_reminders)

    def _on_close(self):
        self.wake_enabled = False
        self.destroy()
