"""
Piperin Live Dashboard - Graphical User Interface
A premium dark-themed dashboard for real-time TTS management.
Features: 
- Audio device selection
- Voice model management
- Real-time text input
- Speech history
- Dynamic macros (F1-F12 hotkeys)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
from pathlib import Path
import keyboard # For global hotkeys
from piperin_core import PiperinEngine, get_audio_devices

# Premium Aesthetic Color Palette (Dark Mode)
DARK_THEME = {
    "bg": "#121212",        # Background
    "surface": "#1E1E1E",   # Component Surface
    "primary": "#BB86FC",   # Accent Primary (Light Purple)
    "secondary": "#03DAC6", # Accent Secondary (Teal)
    "text": "#E1E1E1",      # High Emphasis Text
    "text_dim": "#A0A0A0",  # Medium Emphasis Text
    "error": "#CF6679",     # Error/Alert
    "accent": "#3700B3"     # Darker Accent
}

# Typography Settings
FONTS = {
    "main": ("Segoe UI", 11),
    "bold": ("Segoe UI Semibold", 11),
    "header": ("Segoe UI", 16, "bold"),
    "small": ("Segoe UI", 9)
}

class PiperinGUI:
    """
    Main Application Class for Piperin GUI.
    Handles UI rendering, configuration persistence, and event processing.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Piperin Live - Pro TTS Dashboard")
        self.root.geometry("950x700")
        self.root.configure(bg=DARK_THEME["bg"])
        
        # Core Engine Instance (initialized later)
        self.engine = None
        
        # Configuration Management
        self.config_path = Path(__file__).parent / "config.json"
        self.load_config()
        
        # UI Initialization
        self.setup_styles()
        self.create_widgets()
        
        # Start the background listener for global hotkeys (Macros)
        self.hotkey_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
        self.hotkey_thread.start()
        
        # Handle graceful shutdown
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """
        Configures the ttk styles to match the premium dark theme.
        """
        style = ttk.Style()
        style.theme_use('clam')
        
        # General Frame styling
        style.configure("TFrame", background=DARK_THEME["bg"])
        style.configure("Surface.TFrame", background=DARK_THEME["surface"])
        
        # Label styling
        style.configure("TLabel", background=DARK_THEME["bg"], foreground=DARK_THEME["text"], font=FONTS["main"])
        style.configure("Surface.TLabel", background=DARK_THEME["surface"], foreground=DARK_THEME["text"], font=FONTS["main"])
        style.configure("Title.TLabel", font=FONTS["header"], foreground=DARK_THEME["primary"])
        
        # Button styling
        style.configure("TButton", font=FONTS["bold"], padding=10)
        style.configure("Primary.TButton", background=DARK_THEME["primary"], foreground=DARK_THEME["bg"])
        style.map("Primary.TButton", background=[("active", DARK_THEME["accent"])])
        
        # Combobox styling
        style.configure("TCombobox", fieldbackground=DARK_THEME["surface"], background=DARK_THEME["bg"], foreground=DARK_THEME["text"])

    def create_widgets(self):
        """
        Organizes the UI into logical panels using a grid/box layout.
        """
        # --- Header Section ---
        header = ttk.Frame(self.root, padding=25)
        header.pack(fill="x")
        
        ttk.Label(header, text="PIPERIN LIVE DASHBOARD", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="Real-time Voice Synthesis", foreground=DARK_THEME["text_dim"]).pack(side="right")
        
        # --- Main Layout Container ---
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill="both", expand=True)
        
        # Split into Left (Controls) and Right (History/Macros) panels
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        # --- LEFT PANEL: CONFIGURATION & INPUT ---
        
        # Voice & Device Selection Group
        config_group = ttk.Frame(left_panel, style="Surface.TFrame", padding=20)
        config_group.pack(fill="x", pady=(0, 20))
        
        ttk.Label(config_group, text="Audio Output Device", style="Surface.TLabel").pack(anchor="w")
        self.device_var = tk.StringVar()
        devices = get_audio_devices()
        device_names = [f"[{d['id']}] {d['name']}" for d in devices]
        self.device_cb = ttk.Combobox(config_group, textvariable=self.device_var, values=device_names, state="readonly")
        self.device_cb.pack(fill="x", pady=(5, 15))
        
        ttk.Label(config_group, text="Voice Model (.onnx)", style="Surface.TLabel").pack(anchor="w")
        self.voice_var = tk.StringVar()
        # Scan 'voices' folder for onnx files
        voices_dir = Path(__file__).parent / "voices"
        if not voices_dir.exists(): voices_dir.mkdir(exist_ok=True)
        voices = list(voices_dir.rglob("*.onnx"))
        voice_names = [v.name for v in voices]
        self.voice_cb = ttk.Combobox(config_group, textvariable=self.voice_var, values=voice_names, state="readonly")
        self.voice_cb.pack(fill="x", pady=(5, 15))
        
        self.btn_init = ttk.Button(config_group, text="INITIALIZE ENGINE", style="Primary.TButton", command=self.init_engine)
        self.btn_init.pack(fill="x")
        
        # Main Speech Input Area
        input_group = ttk.Frame(left_panel, style="Surface.TFrame", padding=20)
        input_group.pack(fill="both", expand=True)
        
        ttk.Label(input_group, text="Voice Input (Press Enter to Speak)", style="Surface.TLabel").pack(anchor="w")
        self.text_input = tk.Text(input_group, height=6, font=FONTS["main"], bg="#2A2A2A", fg="white", 
                                 insertbackground="white", borderwidth=0, padx=10, pady=10)
        self.text_input.pack(fill="both", expand=True, pady=15)
        self.text_input.bind("<Return>", lambda e: self.speak_current_text(e))
        
        btn_speak = ttk.Button(input_group, text="SPEAK NOW", command=self.speak_current_text)
        btn_speak.pack(fill="x")
        
        # --- RIGHT PANEL: HISTORY & MACROS ---
        
        # Speech History List
        ttk.Label(right_panel, text="SPEECH HISTORY", font=FONTS["bold"], foreground=DARK_THEME["secondary"]).pack(anchor="w")
        self.history_list = tk.Listbox(right_panel, height=8, bg=DARK_THEME["surface"], fg=DARK_THEME["text"], 
                                      font=FONTS["main"], borderwidth=0, selectbackground=DARK_THEME["primary"], 
                                      padx=10, pady=10)
        self.history_list.pack(fill="x", pady=(5, 20))
        self.history_list.bind("<Double-Button-1>", self.speak_from_history)
        
        # Macro / Hotkey Group
        ttk.Label(right_panel, text="HOTKEY MACROS (F1 - F12)", font=FONTS["bold"], foreground=DARK_THEME["secondary"]).pack(anchor="w")
        self.macro_frame = ttk.Frame(right_panel, style="Surface.TFrame", padding=15)
        self.macro_frame.pack(fill="both", expand=True, pady=5)
        
        # Render the macro list from config
        self.render_macros()

    def render_macros(self):
        """
        Dynamically generates the macro entry fields based on the configuration.
        """
        for widget in self.macro_frame.winfo_children():
            widget.destroy()
            
        for i, (key, text) in enumerate(self.config["macros"].items()):
            m_row = tk.Frame(self.macro_frame, bg=DARK_THEME["surface"])
            m_row.pack(fill="x", pady=3)
            
            lbl = tk.Label(m_row, text=f"{key}:", width=5, anchor="w", bg=DARK_THEME["surface"], 
                           fg=DARK_THEME["primary"], font=FONTS["bold"])
            lbl.pack(side="left")
            
            entry = tk.Entry(m_row, bg="#2A2A2A", fg="white", borderwidth=0, font=FONTS["small"])
            entry.insert(0, text)
            entry.pack(side="left", fill="x", expand=True, padx=8)
            
            # Update config when focus is lost
            entry.bind("<FocusOut>", lambda e, k=key, ent=entry: self.update_macro(k, ent.get()))
            
            speak_icon = tk.Button(m_row, text="▶", bg="#2A2A2A", fg=DARK_THEME["secondary"], 
                                  borderwidth=0, font=FONTS["small"], command=lambda t=text: self.say(t))
            speak_icon.pack(side="right")

    def load_config(self):
        """
        Loads the configuration from config.json or sets defaults.
        """
        default_config = {
            "device": "",
            "voice": "",
            "history": [],
            "macros": {f"F{i}": "" for i in range(1, 13)}
        }
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = {**default_config, **json.load(f)}
            except Exception:
                self.config = default_config
        else:
            self.config = default_config

    def save_config(self):
        """
        Saves the current UI state and macros to config.json.
        """
        # Save current selections
        if self.device_var.get(): self.config["device"] = self.device_var.get()
        if self.voice_var.get(): self.config["voice"] = self.voice_var.get()
        
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def init_engine(self):
        """
        Instantiates the PiperinEngine with the selected voice and device.
        """
        try:
            d_val = self.device_var.get()
            v_val = self.voice_var.get()
            
            if not d_val or not v_val:
                messagebox.showwarning("Incomplete Setup", "Please select both a device and a voice model.")
                return
                
            # Extract device ID from string "[ID] Name"
            d_id = int(d_val.split("]")[0][1:])
            # Locate the full path for the voice model
            v_path = next((Path(__file__).parent / "voices").rglob(v_val))
            
            self.engine = PiperinEngine(str(v_path), output_device_id=d_id)
            self.btn_init.config(text="✓ MOTOR ACTIVE", state="disabled")
            messagebox.showinfo("Success", "Piperin Engine initialized successfully!")
        except Exception as e:
            messagebox.showerror("Engine Error", f"Failed to start engine: {e}")

    def speak_current_text(self, event=None):
        """
        Reads text from the main input widget and speaks it.
        """
        text = self.text_input.get("1.0", "end").strip()
        if text:
            self.say(text)
            self.text_input.delete("1.0", "end")
            return "break" # Prevent newline in text widget

    def speak_from_history(self, event):
        """
        Reads text from a double-clicked history item.
        """
        selection = self.history_list.curselection()
        if selection:
            text = self.history_list.get(selection[0])
            self.say(text)

    def say(self, text):
        """
        The core speaking method. Interfaces with the engine and updates history.
        """
        if not text.strip(): return
        
        if not self.engine:
            messagebox.showwarning("Engine Offline", "Please initialize the engine first!")
            return
            
        self.engine.speak(text)
        
        # Update history logic
        if text not in self.config["history"]:
            self.config["history"].insert(0, text)
            self.config["history"] = self.config["history"][:50] # Keep last 50
            self.update_history_ui()

    def update_history_ui(self):
        """Refreshes the history listbox."""
        self.history_list.delete(0, "end")
        for item in self.config["history"]:
            self.history_list.insert("end", item)

    def update_macro(self, key, text):
        """Updates a specific macro and saves it."""
        if self.config["macros"].get(key) != text:
            self.config["macros"][key] = text
            self.save_config()

    def hotkey_listener(self):
        """
        Background loop using the 'keyboard' library to detect global hotkey presses.
        This allows macros to work even if the window is not in focus.
        """
        while True:
            try:
                event = keyboard.read_event()
                if event.event_type == keyboard.KEY_DOWN:
                    key_name = event.name.upper()
                    if key_name in self.config["macros"]:
                        macro_text = self.config["macros"][key_name]
                        if macro_text.strip():
                            # We use self.root.after to ensure thread safety with Tkinter
                            self.root.after(0, lambda t=macro_text: self.say(t))
            except Exception:
                pass # Silently handle keyboard read errors

    def on_closing(self):
        """Cleanup before exiting."""
        self.save_config()
        self.root.destroy()

if __name__ == "__main__":
    # App Entry Point
    root = tk.Tk()
    app = PiperinGUI(root)
    
    # Initial UI Population from Config
    if app.config["device"]: app.device_var.set(app.config["device"])
    if app.config["voice"]: app.voice_var.set(app.config["voice"])
    app.update_history_ui()
    
    root.mainloop()
