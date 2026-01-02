# ⚡ Piperin - Quick Start Guide

## What is Piperin?

**Piperin** converts text into speech in real-time and routes the audio to your chosen output device. It is specifically designed to function as a "virtual microphone" for calls (Discord, Zoom, Teams), allowing you to communicate by typing.

---

## 🚀 Get Started Immediately

### 1. Install Dependencies
Open your terminal and run:
```bash
pip install piper-tts sounddevice numpy keyboard
```

### 2. Launch the Dashboard (Recommended)
The Dashboard provides the best experience with history and macros.
```bash
cd piperin
python piperin_gui.py
```

### 3. CLI Mode (Lightweight Terminal)
If you prefer the terminal:
```bash
python piperin_live.py
```

---

## 🎧 Setup as a Virtual Microphone (for Calls)

### Step 1: Install a Virtual Audio Cable
- **Windows**: Download [VB-CABLE](https://vb-audio.com/Cable/) (Free/Donationware).
- Install it and restart your computer.

### Step 2: Configure Piperin
- Open the Piperin GUI or CLI.
- Select **"CABLE Input (VB-Audio Virtual Cable)"** as your **Output Device**.

### Step 3: Configure your Call App
- Open **Discord, Zoom, or Teams**.
- Go to **Audio Settings**.
- Set your **Input Device (Microphone)** to **"CABLE Output (VB-Audio Virtual Cable)"**.
- Anything you type in Piperin will now be heard by others in the call!

---

## ⌨️ Dashboard Features

- **Real-time Input**: Type and press Enter to speak.
- **Macros (F1-F12)**: Type a phrase into a macro field and press the corresponding Function key on your keyboard to speak it instantly, even if the app is in the background.
- **History**: Double-click any previous sentence to repeat it.

---

## 📂 Project Overview

```text
piperin/
├── piperin_core.py       # Core Engine: Bridges Piper TTS with Audio Hardware
├── piperin_gui.py        # Dashboard: Premium UI with Macros and History
├── piperin_live.py       # CLI: Interactive Terminal interface
├── download_voice.py     # Utility: Download voice models automatically
├── audio_check.py        # Diagnostics: List all audio hardware IDs
└── voices/               # Folder where your .onnx models are stored
```

---

## 🛠️ Roadmap

- [x] Graphical Dashboard
- [x] Global Hotkeys (F1-F12)
- [x] Speech History
- [ ] Real-time Speed/Pitch control
- [ ] Multi-voice rapid switching
- [ ] Phrase categorization for macros

---
*Stay simple. Stay clean.*
