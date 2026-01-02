"""
Piperin Live - Command Line Interface
A fast, lightweight way to interact with Piper TTS directly from your terminal.
Perfect for streamers, podcasters, or testing voice models without a GUI.
"""

import sys
import os
from pathlib import Path
from typing import List, Optional
from piperin_core import PiperinEngine, get_audio_devices


def scan_for_voice_models() -> List[Path]:
    """
    Scans multiple directories for available .onnx voice models.
    """
    search_paths = [
        Path(__file__).parent / "voices",
        Path.home() / ".local" / "share" / "piper-voices",
        Path(__file__).parent.parent / "voices"
    ]
    
    found_models = []
    for directory in search_paths:
        if directory.exists():
            # Recursively find all onnx files
            found_models.extend(list(directory.rglob("*.onnx")))
            
    return found_models


def main():
    """Main application loop for the CLI interface."""
    print("═" * 60)
    print(" PIPERIN LIVE - COMMAND LINE TTS ".center(60, "═"))
    print("═" * 60)
    
    # 1. Hardware Detection
    print("\n[STEP 1] Detecting Audio Output Devices:")
    available_devices = get_audio_devices()
    
    if not available_devices:
        print("CRITICAL ERROR: No audio output devices detected!")
        return
    
    for dev in available_devices:
        print(f"  [{dev['id']}] {dev['name']}")
    
    # 2. Logic Choice
    print("\n[PRO TIP]: To use Piperin as a 'Virtual Mic', select your Virtual Cable Input.")
    try:
        user_choice = input("\nEnter Device ID (or Press Enter for System Default): ").strip()
        selected_device = int(user_choice) if user_choice else None
    except ValueError:
        selected_device = None
    
    # 3. Model Discovery
    print("\n[STEP 2] Scanning for Voice Models...")
    voice_models = scan_for_voice_models()
    
    if not voice_models:
        print("\nERROR: No voice models found (.onnx files missing).")
        print("\nFix solutions:")
        print("  1. Run 'python download_voice.py' to download official models.")
        print(f"  2. Manually place .onnx files in: {Path(__file__).parent / 'voices'}")
        return
    
    print("\nFound Models:")
    for i, model_path in enumerate(voice_models):
        print(f"  [{i}] {model_path.name}")
    
    try:
        model_idx = int(input("\nSelect Model ID to load: ").strip())
        target_model = str(voice_models[model_idx])
    except (ValueError, IndexError):
        print("❌ Invalid selection. Aborting.")
        return
    
    # 4. Engine Initialization
    print(f"\n[STEP 3] Initializing Engine with {voice_models[model_idx].name}...")
    try:
        engine = PiperinEngine(target_model, output_device_id=selected_device)
    except Exception as error:
        print(f"❌ Initialization failed: {error}")
        return
    
    # 5. Interactive Speech Loop
    print("\n" + "═" * 60)
    print(" READY TO SPEAK ".center(60, "═"))
    print(" Type your message and press ENTER. ")
    print(" Commands: ")
    print("  'exit'/'quit' : Shut down")
    print("  'stop'        : Kill current playback")
    print("═" * 60 + "\n")
    
    try:
        while True:
            # Capture user input
            input_text = input("🎤 > ").strip()
            
            if not input_text:
                continue
            
            # Action Handlers
            cmd_lower = input_text.lower()
            if cmd_lower in ['exit', 'quit', 'sair']:
                print("Shutting down... Goodbye!")
                break
            
            if cmd_lower in ['stop', 'parar']:
                engine.stop()
                print("[SYSTEM] Playback stopped.")
                continue
            
            # Normal speech processing
            preview = input_text[:40] + ("..." if len(input_text) > 40 else "")
            print(f"  Sprinting words: {preview}")
            engine.speak(input_text, block=False)
            
    except (KeyboardInterrupt, EOFError):
        print("\n\nAbruptly shutting down Piperin...")


if __name__ == "__main__":
    main()
