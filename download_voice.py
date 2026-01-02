"""
Piperin Voice Downloader
Utility script to download official Piper TTS voice models from HuggingFace.
This script focuses on high-quality Portuguese (BR) voices but can be extended.
"""

import urllib.request
import json
from pathlib import Path
from typing import List, Tuple

# Official repository for Piper voices
VOICES_REPOSITORY_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main"

# Predefined high-quality Brazilian Portuguese voices
# Format: { "key": { "url_path": "path", "description": "text" } }
PT_BR_CATALOG = {
    "faber-medium": {
        "path": "pt/pt_BR/faber/medium/pt_BR-faber-medium",
        "description": "Male Voice - Natural, Medium Quality"
    },
    "edresson-low": {
         "path": "pt/pt_BR/edresson/low/pt_BR-edresson-low",
         "description": "Male Voice - Lite, Fast Performance"
    }
}


def download_with_progress(url: str, destination: Path, label: str = ""):
    """
    Downloads a file from a URL with a visual progress bar in the console.
    
    Args:
        url (str): Source URL.
        destination (Path): local file path output.
        label (str): Text to display during download.
    """
    print(f"Downloading: {label or url}")
    
    def report_hook(block_num, block_size, total_size):
        """Standard hook for urllib to calculate progress."""
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(downloaded * 100 / total_size, 100)
            bar_len = 40
            filled = int(bar_len * percent / 100)
            status_bar = '█' * filled + '░' * (bar_len - filled)
            print(f"\r   [{status_bar}] {percent:.1f}%", end='', flush=True)
    
    try:
        urllib.request.urlretrieve(url, destination, report_hook)
        print()  # Finalize the progress line
    except Exception as e:
        print(f"\n[ERROR] Failed to download from {url}: {e}")


def main():
    """Main execution flow for the downloader CLI."""
    print("═" * 60)
    print(" PIPERIN VOICE DOWNLOAD UTILITY ".center(60, "═"))
    print("═" * 60)
    
    # Root directory for voices
    voices_base_dir = Path(__file__).parent / "voices"
    voices_base_dir.mkdir(exist_ok=True)
    
    print(f"\nStorage Directory: {voices_base_dir}\n")
    
    # List catalog items
    print("Available Brazilian Portuguese Voices:")
    catalog_items = list(PT_BR_CATALOG.items())
    for i, (key, info) in enumerate(catalog_items, 1):
        print(f"  [{i}] {key}: {info['description']}")
    
    # User interaction
    try:
        raw_choice = input("\nSelect voice number to download (or press Enter for ALL): ").strip()
        
        if raw_choice:
            choice_idx = int(raw_choice) - 1
            if 0 <= choice_idx < len(catalog_items):
                selected_queue = [catalog_items[choice_idx]]
            else:
                print("❌ Choice out of range.")
                return
        else:
            selected_queue = catalog_items
    
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
        return
    
    # Process the download queue
    for key, info in selected_queue:
        print(f"\nProcessing Voice: {key}")
        
        # Each voice gets its own subfolder to keep files organized
        voice_folder = voices_base_dir / key
        voice_folder.mkdir(exist_ok=True)
        
        # Every Piper voice needs the .onnx model and the corresponding .json config
        model_url = f"{VOICES_REPOSITORY_URL}/{info['path']}.onnx"
        config_url = f"{VOICES_REPOSITORY_URL}/{info['path']}.onnx.json"
        
        local_model = voice_folder / f"{key}.onnx"
        local_config = voice_folder / f"{key}.onnx.json"
        
        # Perform downloads if files are missing
        if not local_model.exists():
            download_with_progress(model_url, local_model, f"Model File ({key})")
        else:
            print(f"✓ Model file already exists: {local_model.name}")
            
        if not local_config.exists():
            download_with_progress(config_url, local_config, f"Config JSON ({key})")
        else:
            print(f"✓ Config file already exists: {local_config.name}")
    
    print("\n" + "═" * 60)
    print(" TASKS COMPLETED ".center(60, "═"))
    print(f"Vozes salvas em: {voices_base_dir}")
    print("\nNext step: Run 'python piperin_gui.py' to start using your voices.")
    print("═" * 60)


if __name__ == "__main__":
    main()
