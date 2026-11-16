# AURA --- Personal Desktop Voice Assistant

AURA is a Python desktop voice-assistant prototype that combines
predefined commands, desktop automation, productivity utilities, speech
interaction, and AI-powered conversation through the Groq API.

> **Project status:** AURA V1 / Groq Edition is an experimental personal
> project. The current source package includes a Groq-backed AI engine
> and a basic phrase-based wake listener. Review the platform notes
> below before treating this repository as a fully Linux-native release.

## Features

-   Desktop GUI built with CustomTkinter
-   Push-to-talk microphone input
-   Text-to-speech responses through `pyttsx3`
-   Speech-to-text through the SpeechRecognition library's Google
    recognizer
-   Basic "Hey Aura" phrase detection using short speech-recognition
    clips
-   Groq-powered conversational responses through an OpenAI-compatible
    API client
-   Predefined commands for time, date, web search, websites, notes,
    reminders, weather, and system information
-   SQLite persistence for notes and reminders
-   Weather lookup using Open-Meteo
-   Allowlisted application and website actions

## Important platform and feature limitations

Please read this section before installing or contributing.

1.  **Wake-word detection is online, not offline.** AURA periodically
    records short clips and checks the Google speech-to-text result for
    words such as `aura` or `aurora`. It is not a dedicated offline
    keyword-spotting engine and is not voice authentication.
2.  **Speech recognition requires internet access.** The current
    recognizer uses Google's online recognition service and is
    configured for `en-IN`.
3.  **Groq AI requires internet access.** Model availability, free-tier
    quotas, and rate limits are controlled by Groq and can change.
4.  **The current automation module contains Windows-specific calls and
    application names** (for example, `os.startfile`, `notepad.exe`, and
    `explorer.exe`). These parts need Linux-specific adaptation before
    all desktop automation features can be considered Linux Mint
    compatible. Some functions may fail on Linux as currently written.
5.  **Reminders are checked while the AURA GUI is running.** They are
    stored in SQLite, but AURA does not currently install a background
    service that triggers reminders after the application is closed.
6.  **No language model is trained by this project.** AURA sends prompts
    to a pretrained model hosted by Groq. The project performs
    inference/API integration, not model training or fine-tuning.
7.  **No speaker verification is implemented.** The wake listener does
    not verify that the speaker is the owner.

## Technology stack

  Component            Technology
  -------------------- ---------------------------------------
  Main language        Python
  Desktop GUI          CustomTkinter
  Speech-to-text       SpeechRecognition + Google recognizer
  Microphone access    PyAudio
  Text-to-speech       pyttsx3
  Conversational AI    Groq API using the OpenAI Python SDK
  Local storage        SQLite
  Weather              Open-Meteo
  System information   psutil
  Configuration        python-dotenv

## Project structure

``` text
AURA-Voice-Assistant/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── gui/
│   ├── __init__.py
│   └── interface.py
├── modules/
│   ├── __init__.py
│   ├── ai_engine.py
│   ├── automation.py
│   ├── commands.py
│   ├── productivity.py
│   ├── speech.py
│   └── weather.py
└── database/
    ├── __init__.py
    └── database.py
```

## Requirements

-   Python 3.10 or newer (use a version compatible with the installed
    dependencies)
-   Working microphone and speakers
-   Internet connection for Google speech recognition, Groq AI, weather,
    and web search
-   PortAudio/PyAudio development dependencies for Linux microphone
    support
-   `espeak-ng` or another supported speech backend may be needed by
    `pyttsx3` on Linux

## Installation

### 1. Clone the repository

``` bash
git clone https://github.com/YOUR-USERNAME/AURA-Voice-Assistant.git
cd AURA-Voice-Assistant
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Install Linux dependencies (Linux Mint / Ubuntu)

``` bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-tk \
  build-essential portaudio19-dev python3-dev espeak-ng xdg-utils
```

### 3. Create and activate a virtual environment

``` bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 4. Install Python dependencies

``` bash
pip install -r requirements.txt
```

If PyAudio installation fails, first confirm that `portaudio19-dev` and
`python3-dev` are installed, then try:

``` bash
pip install --no-cache-dir PyAudio
```

### 5. Configure the Groq API key

Create a key in the [Groq Console](https://console.groq.com/keys). Then
create your local environment file:

``` bash
cp .env.example .env
xed .env
```

Set the values:

``` env
AI_PROVIDER=groq
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
DEFAULT_CITY=Hyderabad
```

Save the file and restrict its permissions:

``` bash
chmod 600 .env
```

**Never commit `.env`, paste your API key into source code, or share it
in screenshots.** The `.env` file is excluded by `.gitignore`.

### 6. Run AURA

``` bash
python main.py
```

## Example commands

The command router currently recognises examples such as:

-   `Hello Aura`
-   `What time is it?`
-   `What's today's date?`
-   `Open YouTube`
-   `Search Python decorators`
-   `Weather in Hyderabad`
-   `Take a note buy groceries`
-   `Read my notes`
-   `Remind me in 10 minutes to take a break`
-   `Show reminders`
-   `System information`
-   `Play music`

General questions that do not match a predefined command are sent to the
configured Groq model.

> Actual application launching and media playback depend on the
> platform-specific implementation in `modules/automation.py`. See the
> platform limitation above.

## Groq configuration

AURA uses the OpenAI Python SDK with Groq's OpenAI-compatible endpoint:

-   Base URL: `https://api.groq.com/openai/v1`
-   Default model: `openai/gpt-oss-20b`
-   Temperature: `0.5`
-   Maximum output tokens: `700`
-   Request timeout: `30 seconds`
-   Retry setting: `1`

These are inference/request settings. AURA does not train or fine-tune
the Groq-hosted model. Groq may change model availability and account
quotas.

## Architecture overview

``` text
User (voice or text)
        |
        v
CustomTkinter GUI
        |
        +---- Voice input ---> SpeechRecognition / Google STT
        |                               |
        +-------------------------------+
                                        v
                                  Command Router
                                  /            \
                         Known command       General prompt
                              |                    |
                              v                    v
                    Local application logic    Groq AI Engine
                    /       |       \                |
                SQLite   Weather  Automation         |
                    \       |       /                |
                     \      |      /                 |
                      +-----+------------------------+
                                        |
                                        v
                              GUI response + pyttsx3
```

## Safety and privacy notes

-   The app's command routing is based on predefined patterns.
-   The current application automation code should be reviewed and
    adapted for the target operating system before use.
-   Do not add arbitrary shell execution to voice commands without
    strict validation and user confirmation.
-   Keep API credentials in `.env`; do not commit secrets.
-   Speech-to-text audio is sent to Google's online recognition service.
    Groq receives text prompts for AI responses. Do not use this
    configuration for confidential conversations.

## Troubleshooting

### Microphone is not detected

-   Open Linux Mint **Sound Settings → Input** and select the correct
    microphone.
-   Check available capture devices:

``` bash
arecord -l
```

-   Check PyAudio:

``` bash
python -c "import pyaudio; p=pyaudio.PyAudio(); print(p.get_device_count()); p.terminate()"
```

### Groq AI is not configured

-   Confirm that `.env` exists in the project root.
-   Confirm `GROQ_API_KEY` is set correctly.
-   Confirm that the key has not been revoked and that the selected
    model is available to your Groq account.
-   Do not include the key when sharing error logs.

### Wake phrase does not activate AURA

-   Start AURA from a terminal: `python main.py`.
-   Enable wake-word mode and say "Hey Aura" clearly after a short
    pause.
-   Check terminal output for `[AURA wake check] Heard: ...`.
-   The wake listener relies on internet-based speech recognition and
    may mis-transcribe the phrase.

## Roadmap

-   Replace online phrase matching with a dedicated offline wake-word
    engine.
-   Add offline multilingual speech recognition for English, Hindi, and
    Punjabi.
-   Add optional local LLM support through Ollama.
-   Add speaker verification as a convenience feature (not as sole
    security authentication).
-   Replace Windows-specific desktop automation with Linux-native
    application launching and file opening.
-   Add a background reminder service and login startup support.
-   Improve automated tests and error handling.

## Contributing

Issues and pull requests are welcome. Before contributing, please:

1.  Create a feature branch.
2.  Keep API keys and personal databases out of commits.
3.  Test changes on the target operating system.
4.  Document platform-specific limitations.

## License

Choose and add a license before accepting external contributions or
presenting the repository as open source. If you want a permissive
license, the MIT License is a common option; add a `LICENSE` file with
the appropriate copyright holder and year.

## Author

**Rishab Jain & Paramveer Singh**\

Built as a personal desktop voice-assistant project.
