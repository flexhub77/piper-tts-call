"""
Piperin Core - Real-time TTS Engine
Converts text into high-quality audio and plays it through the selected output device.
This module handles the core Piper TTS integration and audio stream management.
"""

import wave
import io
import threading
import queue
from pathlib import Path
from typing import Optional, List, Dict, Any

# Sounddevice and Numpy are used for audio playback and manipulation
try:
    import sounddevice as sd
    import numpy as np
except ImportError:
    print("CRITICAL: sounddevice or numpy not found. Please install requirements.")
    sd = None
    np = None

# Attempt to import Piper components
# Piper is the underlying TTS engine based on ONNX
try:
    from piper.voice import PiperVoice
except ImportError:
    PiperVoice = None


class PiperinEngine:
    """
    PiperinEngine: The central controller for Text-to-Speech operations.
    
    This class manages:
    1. Loading the ONNX voice model.
    2. Queueing speech requests to prevent overlapping.
    3. Processing synthesis in a background thread for non-blocking UI.
    4. Playing audio chunks directly to an output device.
    """
    
    def __init__(self, voice_model_path: str, output_device_id: Optional[int] = None):
        """
        Initializes the Piperin Engine.
        
        Args:
            voice_model_path (str): Absolute or relative path to the .onnx voice model.
            output_device_id (int, optional): The ID of the audio device to use. Defaults to system default.
        
        Raises:
            ImportError: If the piper-tts library is not installed.
            FileNotFoundError: If the voice model path is invalid.
        """
        # Ensure Piper is installed before proceeding
        if PiperVoice is None:
            raise ImportError("Piper TTS library not found. Installation required: pip install piper-tts")
        
        # Check if the model file exists
        model_path = Path(voice_model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Voice model not found at: {voice_model_path}")

        # Load the voice model into memory
        # This might take a second depending on the model size (low, medium, high)
        self.voice = PiperVoice.load(str(model_path))
        self.output_device = output_device_id
        
        # State tracking
        self.is_speaking = False
        
        # Thread-safe queue for incoming text sentences
        # This allows the user to send multiple texts without waiting for each to finish
        self.speech_queue = queue.Queue()
        
        # Background worker thread initialization
        # We use a daemon thread so it shuts down automatically when the main program exits
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()
        
        # Log successful initialization
        print(f"[SUCCESS] Piperin Engine started!")
        print(f"  > Voice Model: {model_path.name}")
        print(f"  > Output Device ID: {output_device_id if output_device_id is not None else 'Default'}")
    
    def speak(self, text: str, block: bool = False):
        """
        Adds text to the speech queue to be synthesized and played.
        
        Args:
            text (str): The text content to be spoken.
            block (bool): If True, the function will wait until the speech is finished.
        """
        # Trim whitespace and ignore empty strings
        clean_text = text.strip()
        if not clean_text:
            return
        
        # Add to queue
        self.speech_queue.put(clean_text)
        
        # If blocking is requested, we wait for the queue to be fully processed
        if block:
            self.speech_queue.join()
    
    def _speech_worker(self):
        """
        Internal worker method that runs in a background thread.
        Continuously monitors the queue and processes text as it arrives.
        """
        while True:
            # This blocks until an item is available in the queue
            text = self.speech_queue.get()
            
            try:
                self.is_speaking = True
                self._synthesize_and_play(text)
            except Exception as e:
                print(f"[ERROR] Failed to synthesize or play text: {e}")
            finally:
                # Ensure state is reset even on error
                self.is_speaking = False
                # Notify the queue that the task is complete
                self.speech_queue.task_done()
    
    def _synthesize_and_play(self, text: str):
        """
        Performs the actual synthesis and audio playback.
        Iterates through sentences as Piper generates them.
        """
        # Piper's synthesize method returns a generator of audio chunks
        # This is efficient for memory and allows for faster first-byte-to-audio
        for audio_chunk in self.voice.synthesize(text):
            # audio_chunk.audio_float_array is already in float32 [-1.0, 1.0] format
            # This matches sounddevice's internal processing perfectly
            audio_array = audio_chunk.audio_float_array
            sample_rate = audio_chunk.sample_rate
            
            # Start playing the specific chunk
            # We use sd.play followed by sd.wait for synchronous sentence playback
            # but since this runs in a worker thread, the GUI remains responsive
            sd.play(audio_array, sample_rate, device=self.output_device)
            sd.wait() 
    
    def stop(self):
        """
        Immediately stops any ongoing audio playback.
        Note: This does not clear the queue, only stops the current sound device buffer.
        """
        if sd:
            sd.stop()
    
    def is_busy(self) -> bool:
        """
        Checks if the engine is currently speaking or has items pending in the queue.
        
        Returns:
            bool: True if busy, False if idle.
        """
        return self.is_speaking or not self.speech_queue.empty()


def get_audio_devices() -> List[Dict[str, Any]]:
    """
    Scans the system for available audio output devices.
    
    Returns:
        List[Dict]: A list of dictionaries containing device metadata (id, name, channels, sample_rate).
    """
    if sd is None:
        return []
        
    devices = []
    try:
        all_devices = sd.query_devices()
        
        for i, dev in enumerate(all_devices):
            # We only care about devices that can output audio (max_output_channels > 0)
            if dev['max_output_channels'] > 0:
                devices.append({
                    'id': i,
                    'name': dev['name'],
                    'channels': dev['max_output_channels'],
                    'sample_rate': dev['default_samplerate']
                })
    except Exception as e:
        print(f"[ERROR] Failed to query audio devices: {e}")
    
    return devices


if __name__ == "__main__":
    # Internal module test
    print("=== Piperin Core Test Mode ===")
    
    # List available devices
    print("\nAvailable Output Devices:")
    available_devices = get_audio_devices()
    for dev in available_devices:
        print(f"  [{dev['id']}] {dev['name']}")
    
    if not available_devices:
        print("  No output devices found!")
    
    print("\nUsage Example:")
    print("  engine = PiperinEngine('path/to/voice.onnx')")
    print("  engine.speak('Hello World!')")
