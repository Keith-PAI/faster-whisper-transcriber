# Faster Whisper YouTube Transcriber

A high-performance YouTube transcription tool that downloads audio from YouTube videos and converts them to text using OpenAI's Whisper models. Features both a user-friendly GUI application and a reusable Python module for integration into other projects.

## ✨ Features

- **Multiple Transcription Engines**: Choose between OpenAI Whisper and faster-whisper for optimal speed/accuracy balance
- **Batch Processing**: Transcribe multiple YouTube videos at once
- **GUI Applications**: Three different interfaces for various use cases
- **Reusable Module**: Extract and reuse STT functionality in other applications
- **Timestamp Support**: Optional timestamp inclusion in transcripts
- **Language Detection**: Automatic language detection with confidence scores
- **Progress Tracking**: Real-time progress updates and logging
- **Error Handling**: Robust error handling with graceful recovery
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Keith-PAI/faster-whisper-transcriber.git
   cd faster-whisper-transcriber
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv transcript_env
   
   # Windows
   transcript_env\Scripts\activate
   
   # macOS/Linux
   source transcript_env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Additional Dependencies

For the **faster-whisper** version (recommended for better performance):
```bash
pip install faster-whisper
```

For **FFmpeg** (required for audio processing):
- **Windows**: Download from [FFmpeg.org](https://ffmpeg.org/download.html)
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt install ffmpeg`

## 🖥️ GUI Applications

### 1. Faster Whisper Transcriber (Recommended)
```bash
python faster_whisper_transcriber.py
```
- Optimized performance using faster-whisper
- Single video transcription
- Optional timestamp inclusion
- CPU-optimized with int8 quantization

### 2. Full-Featured Batch Transcriber
```bash
python youtube_transcriber.py
```
- Batch processing of multiple videos
- Combined transcript generation
- Advanced error handling and recovery
- URL clipboard integration

### 3. Simple Transcriber
```bash
python simple_transcriber.py
```
- Minimal interface for basic use cases
- Single video processing
- Lightweight and straightforward

### Windows Quick Launch
```bash
run_transcriber.bat
```

## 📚 Using the STT Utils Module

The `stt_utils.py` module provides reusable transcription functionality for integration into other applications.

### Simple Usage

```python
from pathlib import Path
from stt_utils import transcribe_youtube_to_file

# Basic transcription
transcript_file = transcribe_youtube_to_file(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    output_dir=Path("./transcripts"),
    model_name="base",
    include_timestamps=True,
    progress_callback=lambda msg: print(f"Progress: {msg}")
)

print(f"Transcript saved to: {transcript_file}")
```

### Advanced Usage

```python
from stt_utils import transcribe_youtube_video, save_transcript_to_file
from pathlib import Path

# Get detailed transcription results
result = transcribe_youtube_video(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    output_dir=Path("./transcripts"),
    model_name="base",
    include_timestamps=False,
    cleanup_audio=True,
    progress_callback=lambda msg: print(msg)
)

# Access transcription metadata
print(f"Video title: {result.video_title}")
print(f"Detected language: {result.detected_language}")
print(f"Language confidence: {result.language_probability:.2f}")

# Process segments manually
full_text = ""
for segment in result.segments:
    full_text += segment.text.strip() + " "
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s]: {segment.text}")

# Save with custom formatting
custom_file = Path("./transcripts/custom_transcript.txt")
save_transcript_to_file(result, custom_file, include_timestamps=True)
```

### Flask/FastAPI Integration Example

```python
from flask import Flask, request, jsonify
from pathlib import Path
from stt_utils import transcribe_youtube_to_file

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe_endpoint():
    data = request.json
    url = data.get('youtube_url')
    model = data.get('model', 'base')
    timestamps = data.get('include_timestamps', False)
    
    try:
        transcript_file = transcribe_youtube_to_file(
            url=url,
            output_dir=Path('./transcripts'),
            model_name=model,
            include_timestamps=timestamps
        )
        
        # Read transcript content
        with open(transcript_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'transcript': content,
            'file_path': str(transcript_file)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)
```

## ⚙️ Model Settings & Performance Tips

### Recommended Models

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| `tiny` | Fastest | Basic | Real-time, quick tests |
| `base` | Fast | Good | **Recommended for most users** |
| `small` | Medium | Better | Higher accuracy needed |
| `medium` | Slow | High | Professional transcription |
| `large` | Slowest | Highest | Maximum accuracy required |

### Performance Optimization

1. **Use faster-whisper**: 2-3x faster than OpenAI Whisper
2. **CPU with int8**: Best balance of speed and accuracy for most hardware
3. **Model selection**: Start with `base` model for best speed/accuracy ratio
4. **Batch processing**: Use the batch GUI for multiple videos
5. **SSD storage**: Store temporary files on SSD for faster I/O

### Hardware Requirements

- **RAM**: 4GB minimum, 8GB+ recommended for larger models
- **Storage**: 1-5GB per model (downloaded automatically)
- **CPU**: Multi-core recommended for faster processing
- **GPU**: Optional, faster-whisper can use CUDA if available

## 📁 Project Structure

```
├── stt_utils.py                    # Reusable STT functionality
├── test_stt_utils.py              # Demo/test script for stt_utils
├── faster_whisper_transcriber.py  # Faster Whisper GUI (recommended)
├── youtube_transcriber.py          # Full-featured batch GUI
├── simple_transcriber.py           # Minimal single-video GUI
├── requirements.txt                # Python dependencies
├── run_transcriber.bat            # Windows launcher script
├── CLAUDE.md                      # Development guidance
├── *.spec                         # PyInstaller build specifications
└── build/                         # Compiled executables
```

## 🔧 Building Executables

Create standalone executables using PyInstaller:

```bash
# Build faster whisper version (recommended)
pyinstaller YouTubeTranscriber_FasterWhisper.spec

# Build full-featured version
pyinstaller Simple_Transcriber.spec

# Build simple version
pyinstaller Simple_Transcriber_Fixed.spec
```

Executables will be created in the `build/` directory.

## 🐛 Troubleshooting

### Common Issues

1. **"Missing required packages"**
   ```bash
   pip install faster-whisper yt-dlp
   ```

2. **"FFmpeg not found"**
   - Install FFmpeg and ensure it's in your system PATH

3. **"Audio file not found after download"**
   - Check internet connection and YouTube URL validity
   - Ensure sufficient disk space

4. **Slow transcription**
   - Use faster-whisper instead of OpenAI Whisper
   - Try a smaller model (e.g., `tiny` or `base`)
   - Check available system RAM

### Getting Help

- Check the `test_stt_utils.py` file for usage examples
- Review error messages in the GUI log output
- Ensure all dependencies are properly installed

## 📄 License

This project is open source. Please check the repository for license details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 🔗 Repository

**GitHub**: [https://github.com/Keith-PAI/faster-whisper-transcriber](https://github.com/Keith-PAI/faster-whisper-transcriber)

---

**Made with ❤️ for efficient YouTube transcription**