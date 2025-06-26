import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import os
from pathlib import Path
from datetime import datetime

class SimpleTranscriber:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple YouTube Transcriber")
        self.root.geometry("600x400")
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL input
        ttk.Label(main_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=70)
        url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Model selection
        ttk.Label(main_frame, text="Whisper Model:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(main_frame, textvariable=self.model_var, 
                                  values=["tiny", "base", "small", "medium"], 
                                  state="readonly", width=15)
        model_combo.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
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
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=8, column=0, sticky=tk.W, pady=(0, 10))
        
        # Log
        ttk.Label(main_frame, text="Output Log:").grid(row=9, column=0, sticky=tk.W, pady=(0, 5))
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=70)
        self.log_text.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Configure weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(10, weight=1)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def start_transcription(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        if not any(domain in url for domain in ['youtube.com', 'youtu.be']):
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
        
        self.transcribe_btn.config(state="disabled")
        self.progress.start()
        self.status_var.set("Processing...")
        self.clear_log()
        
        thread = threading.Thread(target=self.transcribe_video)
        thread.daemon = True
        thread.start()
    
    def transcribe_video(self):
        try:
            url = self.url_var.get().strip()
            model = self.model_var.get()
            output_dir = Path(self.output_dir_var.get())
            
            # Import packages
            try:
                import yt_dlp
                import whisper
            except ImportError as e:
                raise Exception(f"Missing required packages: {e}")
            
            self.log(f"Starting transcription for: {url}")
            self.log(f"Using model: {model}")
            self.log(f"Output directory: {output_dir}")
            self.log("-" * 50)
            
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            
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
                'quiet': True,
            }
            
            # Download audio
            self.log("Downloading audio from YouTube...")
            video_title = "Unknown Video"
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    video_title = info.get('title', 'Unknown Video')
                    
                self.log(f"Downloaded: {video_title}")
            except Exception as e:
                raise Exception(f"Failed to download video: {e}")
            
            # Find audio file
            audio_file = output_dir / "temp_audio.mp3"
            if not audio_file.exists():
                raise Exception("Audio file not found after download")
            
            # Load Whisper model
            self.log(f"Loading Whisper model '{model}'...")
            try:
                model_instance = whisper.load_model(model)
            except Exception as e:
                raise Exception(f"Failed to load Whisper model: {e}")
            
            # Transcribe
            self.log("Transcribing audio...")
            try:
                result = model_instance.transcribe(str(audio_file))
            except Exception as e:
                raise Exception(f"Transcription failed: {e}")
            
            # Validate result
            if not isinstance(result, dict):
                raise Exception("Invalid transcription result format")
            
            transcript_text = result.get("text", "")
            if not transcript_text:
                transcript_text = "No transcript text was generated"
            
            # Create safe filename
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_title or len(safe_title) < 3:
                safe_title = "transcript"
            
            # Limit filename length
            if len(safe_title) > 50:
                safe_title = safe_title[:47] + "..."
            
            transcript_file = output_dir / f"{safe_title}_transcript.txt"
            
            # Write transcript file
            self.log("Saving transcript...")
            try:
                with open(transcript_file, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(f"Transcript for: {video_title}\n")
                    f.write(f"YouTube URL: {url}\n")
                    f.write(f"Generated with Whisper model: {model}\n")
                    f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(str(transcript_text))
                    
            except Exception as e:
                raise Exception(f"Failed to save transcript: {e}")
            
            # Clean up
            try:
                audio_file.unlink()
            except:
                pass  # Don't fail if cleanup fails
                
            self.log(f"✓ Transcript saved to: {transcript_file}")
            self.log("✓ Transcription completed successfully!")
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo(
                "Success", 
                f"Transcript saved to:\n{transcript_file}\n\nVideo: {video_title}"
            ))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        finally:
            self.root.after(0, self.finish_transcription)
    
    def finish_transcription(self):
        self.transcribe_btn.config(state="normal")
        self.progress.stop()
        self.status_var.set("Ready")

def main():
    root = tk.Tk()
    app = SimpleTranscriber(root)
    root.mainloop()

if __name__ == "__main__":
    main()