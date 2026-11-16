"""AURA V1 AI engine using Groq's OpenAI-compatible chat API."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class AIEngine:
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "groq").strip().lower()
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip()
        self.client = None
        self.history = []
        self.startup_error = None

        if self.provider != "groq":
            self.startup_error = (
                f"Unsupported AI_PROVIDER '{self.provider}'. AURA V1 is configured for Groq."
            )
            return

        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key or api_key == "your_groq_api_key_here":
            self.startup_error = "Groq API key is missing. Add GROQ_API_KEY to your .env file."
            return

        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1",
                timeout=30.0,
                max_retries=1,
            )
        except Exception as exc:
            self.startup_error = f"Could not initialize Groq: {type(exc).__name__}: {exc}"

    @property
    def available(self):
        return self.client is not None

    def ask(self, prompt):
        if not self.available:
            return (
                "Groq AI is not configured. "
                + (self.startup_error or "Check your .env settings.")
                + " Predefined AURA commands can still work."
            )

        self.history.append({"role": "user", "content": str(prompt)})
        messages = [{
            "role": "system",
            "content": (
                "You are AURA, a concise and helpful personal desktop voice assistant "
                "running on Linux Mint. Reply naturally in the language the user uses. "
                "Do not claim you performed a computer action unless AURA has confirmed it. "
                "For computer actions, guide the user to supported AURA commands. "
                "Keep answers suitable for being spoken aloud."
            ),
        }] + self.history[-10:]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=700,
            )
            answer = (response.choices[0].message.content or "").strip()
            if not answer:
                answer = "Groq returned an empty response. Please try again."
            self.history.append({"role": "assistant", "content": answer})
            return answer
        except Exception as exc:
            self.history.pop()
            # Do not include request headers or API-key values in user-facing errors.
            return f"I couldn't reach Groq: {type(exc).__name__}: {exc}"

    def clear_history(self):
        self.history.clear()
