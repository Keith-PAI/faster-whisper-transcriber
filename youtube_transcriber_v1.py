import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import os
import subprocess
import sys
from pathlib import Path

class YouTubeTranscriber:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Transcript Generator")
        self.root.geometry("800x600")
        
        # Check if required packages are installed
        self.check_dependencies()
        
        self.setup_ui()
        
    def check_dependencies(self):
        """Check if required packages are installed"""
        try:
            import yt_dlp
            import whisper
        except ImportError as e:
            messagebox.showerror(
                "Missing Dependencies", 
                f"Required packages not found: {e}\n\n"
                "Please install with:\n"
                "pip install yt-dlp openai-whisper"
            )
            sys.exit(1)
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL input
        ttk.Label(main_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=70)
        url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Model selection
        ttk.Label(main_frame, text="Whisper Model (larger = more accurate but slower):").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(main_frame, textvariable=self.model_var, 
                                  values=["tiny", "base", "small", "medium", "large"], 
                                  state="readonly", width=20)
        model_combo.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Output directory selection
        ttk.Label(main_frame, text="Output Directory:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.transcribe_btn = ttk.Button(button_frame, text="Generate Transcript", command=self.start_transcription)
        self.transcribe_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=8, column=0, sticky=tk.W, pady=(0, 10))
        
        # Log output
        ttk.Label(main_frame, text="Output Log:").grid(row=9, column=0, sticky=tk.W, pady=(0, 5))
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.log_text.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(10, weight=1)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def start_transcription(self):
        """Start transcription in a separate thread"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if not url.startswith(("https://www.youtube.com/", "https://youtu.be/", "www.youtube.com/", "youtu.be/")):
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
        
        # Disable button and start progress
        self.transcribe_btn.config(state="disabled")
        self.progress.start()
        self.status_var.set("Processing...")
        self.clear_log()
        
        # Start transcription in separate thread
        thread = threading.Thread(target=self.transcribe_video)
        thread.daemon = True
        thread.start()
    
    def transcribe_video(self):
        """Main transcription logic"""
        try:
            url = self.url_var.get().strip()
            model = self.model_var.get()
            output_dir = Path(self.output_dir_var.get())
            
            # Import here to avoid startup delays
            import yt_dlp
            import whisper
            
            self.log(f"Starting transcription for: {url}")
            self.log(f"Using model: {model}")
            self.log(f"Output directory: {output_dir}")
            self.log("-" * 50)
            
            # Configure yt-dlp
            audio_path = output_dir / "temp_audio.%(ext)s"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(audio_path),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,  # Suppress yt-dlp output
            }
            
            # Download audio
            self.log("Downloading audio from YouTube...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'Unknown')
                
            self.log(f"Downloaded: {video_title}")
            
            # Find the downloaded audio file
            audio_file = output_dir / "temp_audio.mp3"
            if not audio_file.exists():
                raise FileNotFoundError("Audio file not found after download")
            
            # Load Whisper model
            self.log(f"Loading Whisper model '{model}'...")
            model_instance = whisper.load_model(model)
            
            # Transcribe
            self.log("Transcribing audio... (this may take a while)")
            result = model_instance.transcribe(str(audio_file))
            
            # Save transcript
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            transcript_file = output_dir / f"{safe_title}_transcript.txt"
            
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(f"Transcript for: {video_title}\n")
                f.write(f"YouTube URL: {url}\n")
                f.write(f"Generated with Whisper model: {model}\n")
                f.write("-" * 80 + "\n\n")
                f.write(result["text"])
            
            # Clean up temporary audio file
            audio_file.unlink()
            
            self.log(f"Transcript saved to: {transcript_file}")
            self.log("✓ Transcription completed successfully!")
            
            # Show completion message
            self.root.after(0, lambda: messagebox.showinfo(
                "Success", 
                f"Transcript saved to:\n{transcript_file}\n\n"
                f"Video: {video_title}"
            ))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        finally:
            # Re-enable button and stop progress
            self.root.after(0, self.finish_transcription)
    
    def finish_transcription(self):
        """Clean up after transcription"""
        self.transcribe_btn.config(state="normal")
        self.progress.stop()
        self.status_var.set("Ready")

def main():
    root = tk.Tk()
    app = YouTubeTranscriber(root)
    root.mainloop()

if __name__ == "__main__":
    main()