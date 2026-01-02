"""
Piperin Audio Diagnostics
A simple utility to verify audio drivers and list available input/output devices.
This helps users identify the ID for Virtual Audio Cables or specific speakers.
"""

import sounddevice as sd

def list_audio_devices():
    """
    Queries and prints details of all audio devices connected to the system.
    """
    print("═" * 50)
    print(" SCANNING AUDIO INFRASTRUCTURE ".center(50, "═"))
    print("═" * 50 + "\n")
    
    try:
        devices = sd.query_devices()
        host_apis = sd.query_hostapis()
        
        for i, dev in enumerate(devices):
            # We filter for devices that actually have I/O capabilities
            if dev['max_input_channels'] > 0 or dev['max_output_channels'] > 0:
                io_capabilities = []
                if dev['max_input_channels'] > 0: io_capabilities.append("INPUT")
                if dev['max_output_channels'] > 0: io_capabilities.append("OUTPUT")
                
                print(f"DEVICE ID: {i}")
                print(f"  Name     : {dev['name']}")
                print(f"  Host API : {host_apis[dev['hostapi']]['name']}")
                print(f"  Types    : {', '.join(io_capabilities)}")
                print(f"  Channels : In={dev['max_input_channels']}, Out={dev['max_output_channels']}")
                print("-" * 50)
                
    except Exception as e:
        print(f"[ERROR] Critical failure while querying audio devices: {e}")
        print("Suggestion: Ensure 'sounddevice' and 'numpy' are correctly installed via pip.")

if __name__ == "__main__":
    # Run diagnostics
    list_audio_devices()
    
    print("\n[PRO TIP]: To use Piperin as a voice modifier for Discord, Zoom, or OBS:")
    print(" 1. Install a 'Virtual Audio Cable' (like VB-CABLE).")
    print(" 2. In Piperin GUI, select 'CABLE Input' as your Output Device.")
    print(" 3. In Discord/Zoom settings, select 'CABLE Output' as your Input Device.")
    print("\n═" * 50)
