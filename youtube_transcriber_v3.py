import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import os
import subprocess
import sys
from pathlib import Path
import re
from datetime import datetime

class YouTubeTranscriber:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Transcript Generator - Batch Edition")
        self.root.geometry("900x700")
        
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
        # Main frame with notebook (tabs)
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Single video tab
        self.single_frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.single_frame, text="Single Video")
        
        # Batch processing tab
        self.batch_frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.batch_frame, text="Batch Processing")
        
        self.setup_single_tab()
        self.setup_batch_tab()
        self.setup_common_controls(main_frame)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
    def setup_single_tab(self):
        # URL input
        ttk.Label(self.single_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(self.single_frame, textvariable=self.url_var, width=70)
        url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Paste button
        ttk.Button(self.single_frame, text="Paste from Clipboard", command=self.paste_from_clipboard).grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        self.single_frame.columnconfigure(0, weight=1)
        
    def setup_batch_tab(self):
        # Instructions
        instructions = ttk.Label(self.batch_frame, 
                                text="Enter multiple YouTube URLs (one per line or comma-separated):")
        instructions.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # URL text area
        self.batch_urls_text = scrolledtext.ScrolledText(self.batch_frame, height=8, width=70)
        self.batch_urls_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Batch controls frame
        batch_controls = ttk.Frame(self.batch_frame)
        batch_controls.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(batch_controls, text="Load URLs from File", command=self.load_urls_from_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(batch_controls, text="Clear URLs", command=self.clear_batch_urls).pack(side=tk.LEFT, padx=(0, 10))
        
        # Batch processing options
        options_frame = ttk.LabelFrame(self.batch_frame, text="Batch Options", padding="5")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.skip_errors_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Skip failed videos and continue", 
                       variable=self.skip_errors_var).grid(row=0, column=0, sticky=tk.W)
        
        self.add_timestamps_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Include timestamps in transcript", 
                       variable=self.add_timestamps_var).grid(row=1, column=0, sticky=tk.W)
        
        self.combine_transcripts_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Create combined transcript file", 
                       variable=self.combine_transcripts_var).grid(row=2, column=0, sticky=tk.W)
        
        self.batch_frame.columnconfigure(0, weight=1)
        
    def setup_common_controls(self, main_frame):
        # Common controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Model selection
        ttk.Label(controls_frame, text="Whisper Model:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(controls_frame, textvariable=self.model_var, 
                                  values=["tiny", "base", "small", "medium", "large"], 
                                  state="readonly", width=15)
        model_combo.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Model info
        model_info = ttk.Label(controls_frame, text="tiny=fastest, large=most accurate", 
                              font=("TkDefaultFont", 8))
        model_info.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Output directory selection
        ttk.Label(controls_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        dir_frame = ttk.Frame(controls_frame)
        dir_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Language selection
        ttk.Label(controls_frame, text="Language (optional):").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.language_var = tk.StringVar(value="auto")
        language_combo = ttk.Combobox(controls_frame, textvariable=self.language_var, 
                                     values=["auto", "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"], 
                                     state="readonly", width=15)
        language_combo.grid(row=5, column=0, sticky=tk.W, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        self.transcribe_btn = ttk.Button(button_frame, text="Generate Transcript(s)", command=self.start_transcription)
        self.transcribe_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(controls_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(controls_frame, textvariable=self.status_var).grid(row=8, column=0, sticky=tk.W, pady=(0, 10))
        
        # Log output
        ttk.Label(controls_frame, text="Output Log:").grid(row=9, column=0, sticky=tk.W, pady=(0, 5))
        self.log_text = scrolledtext.ScrolledText(controls_frame, height=12, width=80)
        self.log_text.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.rowconfigure(10, weight=1)
        
    def paste_from_clipboard(self):
        """Paste URL from clipboard"""
        try:
            clipboard_content = self.root.clipboard_get()
            if clipboard_content:
                self.url_var.set(clipboard_content.strip())
        except tk.TclError:
            messagebox.showwarning("Clipboard", "No text found in clipboard")
            
    def load_urls_from_file(self):
        """Load URLs from a text file"""
        file_path = filedialog.askopenfilename(
            title="Select URL file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.batch_urls_text.delete(1.0, tk.END)
                self.batch_urls_text.insert(1.0, content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
                
    def clear_batch_urls(self):
        """Clear the batch URLs text area"""
        self.batch_urls_text.delete(1.0, tk.END)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
            
    def open_output_folder(self):
        """Open the output folder in file explorer"""
        output_path = Path(self.output_dir_var.get())
        if output_path.exists():
            if sys.platform == "win32":
                os.startfile(output_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", output_path])
            else:
                subprocess.run(["xdg-open", output_path])
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        
    def extract_urls(self, text):
        """Extract YouTube URLs from text"""
        # Common YouTube URL patterns
        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://youtu\.be/[\w-]+',
            r'youtube\.com/watch\?v=[\w-]+',
            r'youtu\.be/[\w-]+'
        ]
        
        urls = []
        
        # Split by common separators
        lines = re.split(r'[,\n\r\t]+', text)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line matches any pattern
            for pattern in patterns:
                if re.search(pattern, line):
                    # Ensure it starts with https://
                    if not line.startswith('http'):
                        if line.startswith('www.youtube.com') or line.startswith('youtube.com'):
                            line = 'https://' + line
                        elif line.startswith('youtu.be'):
                            line = 'https://' + line
                    urls.append(line)
                    break
                    
        return urls
    
    def start_transcription(self):
        """Start transcription in a separate thread"""
        # Get current tab
        current_tab = self.root.nametowidget(self.root.focus_get()).winfo_parent()
        
        # Determine if single or batch mode
        if "single" in str(current_tab) or self.url_var.get().strip():
            # Single mode
            url = self.url_var.get().strip()
            if not url:
                messagebox.showerror("Error", "Please enter a YouTube URL")
                return
            urls = [url]
        else:
            # Batch mode
            batch_text = self.batch_urls_text.get(1.0, tk.END).strip()
            if not batch_text:
                messagebox.showerror("Error", "Please enter YouTube URLs for batch processing")
                return
            urls = self.extract_urls(batch_text)
            
        if not urls:
            messagebox.showerror("Error", "No valid YouTube URLs found")
            return
        
        # Validate URLs
        valid_urls = []
        for url in urls:
            if any(domain in url for domain in ['youtube.com', 'youtu.be']):
                valid_urls.append(url)
            else:
                self.log(f"Skipping invalid URL: {url}")
                
        if not valid_urls:
            messagebox.showerror("Error", "No valid YouTube URLs found")
            return
        
        # Disable button and start progress
        self.transcribe_btn.config(state="disabled")
        self.progress.start()
        self.status_var.set(f"Processing {len(valid_urls)} video(s)...")
        self.clear_log()
        
        # Start transcription in separate thread
        thread = threading.Thread(target=self.transcribe_videos, args=(valid_urls,))
        thread.daemon = True
        thread.start()
    
    def transcribe_videos(self, urls):
        """Main transcription logic for multiple videos"""
        try:
            model = self.model_var.get()
            language = self.language_var.get() if self.language_var.get() != "auto" else None
            output_dir = Path(self.output_dir_var.get())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Import here to avoid startup delays
            import yt_dlp
            import whisper
            
            self.log(f"Starting batch transcription for {len(urls)} video(s)")
            self.log(f"Using model: {model}")
            if language:
                self.log(f"Language: {language}")
            self.log(f"Output directory: {output_dir}")
            self.log("-" * 50)
            
            # Load Whisper model once
            self.log(f"Loading Whisper model '{model}'...")
            model_instance = whisper.load_model(model)
            
            successful_transcripts = []
            failed_videos = []
            combined_content = []
            
            for i, url in enumerate(urls, 1):
                try:
                    self.log(f"\n[{i}/{len(urls)}] Processing: {url}")
                    
                    # Configure yt-dlp
                    audio_path = output_dir / f"temp_audio_{i}.%(ext)s"
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
                    self.log("Downloading audio...")
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        video_title = info.get('title', f'Unknown_Video_{i}')
                        duration = info.get('duration', 0)
                        
                    self.log(f"Downloaded: {video_title}")
                    if duration:
                        self.log(f"Duration: {duration//60}:{duration%60:02d}")
                    
                    # Find the downloaded audio file
                    audio_file = output_dir / f"temp_audio_{i}.mp3"
                    if not audio_file.exists():
                        raise FileNotFoundError("Audio file not found after download")
                    
                    # Transcribe
                    self.log("Transcribing...")
                    transcribe_options = {"language": language} if language else {}
                    result = model_instance.transcribe(str(audio_file), **transcribe_options)
                    
                    # Save individual transcript
                    safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    if not safe_title:
                        safe_title = f"transcript_{i}"
                    
                    transcript_file = output_dir / f"{safe_title}_transcript.txt"
                    
                    with open(transcript_file, 'w', encoding='utf-8') as f:
                        f.write(f"Transcript for: {video_title}\n")
                        f.write(f"YouTube URL: {url}\n")
                        f.write(f"Generated with Whisper model: {model}\n")
                        if language:
                            f.write(f"Language: {language}\n")
                        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("-" * 80 + "\n\n")
                        
                        transcript_text = result.get("text", "No transcript generated")
                        
                        # Add timestamps if requested
                        if self.add_timestamps_var.get() and "segments" in result:
                            f.write("TRANSCRIPT WITH TIMESTAMPS:\n\n")
                            for segment in result["segments"]:
                                start_time = self.format_timestamp(segment.get("start", 0))
                                end_time = self.format_timestamp(segment.get("end", 0))
                                text = segment.get("text", "").strip()
                                f.write(f"[{start_time} - {end_time}] {text}\n")
                        else:
                            f.write(transcript_text)
                    
                    # Add to combined content if requested
                    if self.combine_transcripts_var.get():
                        combined_content.append({
                            'title': video_title,
                            'url': url,
                            'text': transcript_text
                        })
                    
                    # Clean up temporary audio file
                    audio_file.unlink()
                    
                    successful_transcripts.append(transcript_file)
                    self.log(f"✓ Saved: {transcript_file.name}")
                    
                except Exception as e:
                    error_msg = f"✗ Failed to process {url}: {str(e)}"
                    self.log(error_msg)
                    failed_videos.append((url, str(e)))
                    
                    # Clean up temp file if it exists
                    temp_file = output_dir / f"temp_audio_{i}.mp3"
                    if temp_file.exists():
                        temp_file.unlink()
                    
                    if not self.skip_errors_var.get():
                        self.log("Stopping batch processing due to error")
                        break
            
            # Create combined transcript if requested
            if self.combine_transcripts_var.get() and combined_content:
                combined_file = output_dir / f"combined_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(combined_file, 'w', encoding='utf-8') as f:
                    f.write("COMBINED TRANSCRIPT FILE\n")
                    f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total videos: {len(combined_content)}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for i, content in enumerate(combined_content, 1):
                        f.write(f"VIDEO {i}: {content['title']}\n")
                        f.write(f"URL: {content['url']}\n")
                        f.write("-" * 40 + "\n")
                        f.write(content['text'])
                        f.write("\n\n" + "=" * 80 + "\n\n")
                
                self.log(f"✓ Combined transcript saved: {combined_file.name}")
            
            # Summary
            self.log("\n" + "=" * 50)
            self.log("BATCH PROCESSING COMPLETE")
            self.log(f"✓ Successful: {len(successful_transcripts)}")
            self.log(f"✗ Failed: {len(failed_videos)}")
            
            if failed_videos:
                self.log("\nFailed videos:")
                for url, error in failed_videos:
                    self.log(f"  - {url}: {error}")
            
            # Show completion message
            success_msg = f"Batch processing complete!\n\n"
            success_msg += f"Successful: {len(successful_transcripts)}\n"
            success_msg += f"Failed: {len(failed_videos)}\n\n"
            success_msg += f"Files saved to: {output_dir}"
            
            self.root.after(0, lambda: messagebox.showinfo("Batch Complete", success_msg))
            
        except Exception as e:
            error_msg = f"Batch processing error: {str(e)}"
            self.log(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        finally:
            # Re-enable button and stop progress
            self.root.after(0, self.finish_transcription)
    
    def format_timestamp(self, seconds):
        """Format seconds to MM:SS or HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
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