# 🎙️ Piperin: Real-Time High-Quality TTS CLI & Dashboard

Piperin is a sleek, professional-grade wrapper for the **Piper TTS** engine. It allows users to convert text into high-quality audio files or live streams with extremely low latency, making it perfect for real-time applications, virtual assistants, or content creation.

---

## ✨ Key Features

- **🚀 Real-Time Synthesis**: Powered by Piper's ONNX-based engine for near-instant speech generation.
- **🖥️ Pro Dashboard**: A premium dark-themed GUI built with Python's Tkinter, featuring audio device selection and history.
- **⌨️ Global Macros**: Assign text phrases to F1-F12 hotkeys that work even when the app is minimized (perfect for streamers!).
- **🔌 Virtual Cable Support**: Designed to work seamlessly with Virtual Audio Cables (VB-CABLE) to act as a voice modifier in Discord, Zoom, and OBS.
- **📦 Clean Architecture**: Modular codebase with clear separation between Core Engine, GUI, and CLI interfaces.
- **🇧🇷 PT-BR Focused**: Comes with pre-configured high-quality Brazilian Portuguese voices.

---

## 🛠️ Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/YourUsername/Piperin.git
cd Piperin/piperin
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*Note: Requirements include `piper-tts`, `sounddevice`, `numpy`, and `keyboard`.*

---

## 🚀 Quick Start

### 1. Download Voices
First, you need to download a voice model. We provide a convenient script:
```bash
python download_voice.py
```

### 2. Launch the Dashboard (GUI)
The easiest way to use Piperin is through the graphical interface:
```bash
python piperin_gui.py
```

### 3. Command Line Interface (CLI)
For a lightweight terminal experience:
```bash
python piperin_live.py
```

---

## 🎙️ Using Piperin as a Virtual Microphone

To use Piperin in apps like **Discord** or **Zoom**:
1. Install [VB-CABLE Virtual Audio Cable](https://vb-audio.com/Cable/).
2. Run `piperin_gui.py`.
3. In the **Audio Output Device** dropdown, select `CABLE Input`.
4. In your communication app (Discord/Zoom), set your **Input Device** (Microphone) to `CABLE Output`.
5. Type in Piperin, and others will hear the AI voice as if it were your microphone!

---

## 📂 Project Structure

- `piperin_core.py`: The heart of the project. Manages threads, Piper loading, and audio buffers.
- `piperin_gui.py`: Premium dark-mode interface with macro support.
- `piperin_live.py`: Interactive CLI tool.
- `download_voice.py`: Utility to fetch models from HuggingFace.
- `audio_check.py`: Diagnostic tool for audio hardware identification.
- `config.json`: Persistent storage for user settings, history, and macros.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License**. Piper TTS models and engine may be subject to their own respective licenses (GPL/MIT).

---

## 🌟 Acknowledgments

- **Piper TTS**: The underlying high-performance neural TTS engine.
- **Rhasspy**: For providing the amazing community voices.

---
*Created with ❤️ for the Open Source Community.*
