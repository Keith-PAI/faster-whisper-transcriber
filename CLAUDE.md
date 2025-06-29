# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a YouTube transcription tool that downloads audio from YouTube videos and converts them to text using OpenAI's Whisper models. The project contains multiple implementations:

- **youtube_transcriber.py**: Full-featured GUI with batch processing capabilities using OpenAI Whisper
- **faster_whisper_transcriber.py**: Optimized version using faster-whisper library for better performance
- **simple_transcriber.py**: Minimal single-video transcription tool

## Key Dependencies

The project uses different Whisper implementations:
- **OpenAI Whisper**: `openai-whisper` package (used in main and simple versions)
- **Faster Whisper**: `faster-whisper` package (used in optimized version)
- **yt-dlp**: For downloading YouTube audio
- **tkinter**: For GUI (built into Python)

## Development Commands

### Environment Setup
```bash
# Create virtual environment (recommended)
python -m venv transcript_env
# Activate on Windows
transcript_env\Scripts\activate
# Activate on Linux/Mac
source transcript_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Applications
```bash
# Run main application with batch processing
python youtube_transcriber.py

# Run faster whisper version (recommended for performance)
python faster_whisper_transcriber.py

# Run simple version
python simple_transcriber.py

# Windows batch launcher
run_transcriber.bat

# Run API server
python whisper_api.py
```

### Running the API Server
```bash
# Install API dependencies
pip install -r requirements-api.txt

# Set API key (required for authentication)
export WHISPER_API_KEY=your_secret_key_here

# Run the server
python whisper_api.py
# Or use uvicorn directly
uvicorn whisper_api:app --host 0.0.0.0 --port 8000
```

The API server will start on `http://localhost:8000` and provides:
- `POST /transcribe` - Upload audio file for transcription
- `GET /models` - List available Whisper models
- `GET /` - Health check endpoint

#### API Usage Examples

**Upload audio file with curl:**
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -H "X-API-Key: your_secret_key_here" \
  -F "file=@audio.mp3" \
  -F "model=base"
```

**JavaScript fetch example:**
```javascript
const formData = new FormData();
formData.append('file', audioFile);
formData.append('model', 'base');

const response = await fetch('http://localhost:8000/transcribe', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your_secret_key_here'
  },
  body: formData
});

const result = await response.json();
console.log(result.transcript);
```

### Building Executables
The project uses PyInstaller to create standalone executables:

```bash
# Build main application
pyinstaller Simple_Transcriber.spec

# Build faster whisper version
pyinstaller YouTubeTranscriber_FasterWhisper.spec

# Build simple version
pyinstaller Simple_Transcriber_Fixed.spec
```

Built executables are stored in `build/` directory.

## Security

### API Authentication
The Whisper API server requires authentication via API key:

- **Required**: Set `WHISPER_API_KEY` environment variable before starting the server
- **Header**: Include `X-API-Key: your_secret_key_here` in all API requests
- **Protected Endpoints**: `/transcribe` and `/models` require valid API key
- **Health Check**: `/` endpoint is public and does not require authentication

**Important**: The API key is mandatory - the server will reject requests without proper authentication.

### CORS Configuration
The API includes CORS middleware configured to allow cross-origin requests. For production use:
- Replace `allow_origins=["*"]` with specific frontend origins
- Review and restrict allowed methods/headers as needed

## Architecture

### Core Components

1. **Audio Download Pipeline**:
   - Uses yt-dlp to extract audio from YouTube URLs
   - Converts to MP3 format at 192kbps quality
   - Temporary files are cleaned up after processing

2. **Speech-to-Text Processing**:
   - **OpenAI Whisper**: More accurate but slower (youtube_transcriber.py, simple_transcriber.py)
   - **Faster Whisper**: Better performance using CPU with int8 quantization (faster_whisper_transcriber.py)
   - Model selection: tiny (fastest) → base → small → medium → large (most accurate)

3. **GUI Framework**:
   - Built with tkinter for cross-platform compatibility
   - Threaded processing to prevent UI freezing
   - Progress bars and logging for user feedback

### Key Differences Between Versions

- **youtube_transcriber.py**: 
  - Batch processing capability
  - Timestamp inclusion option
  - Combined transcript generation
  - URL clipboard integration
  - Advanced error handling

- **faster_whisper_transcriber.py**:
  - Optimized for speed using faster-whisper
  - CPU-based processing with int8 quantization
  - Language detection with probability scores

- **simple_transcriber.py**:
  - Minimal implementation
  - Single video processing only
  - Basic error handling

- **whisper_api.py**:
  - FastAPI REST API server for audio transcription
  - Accepts uploaded audio files (mp3, wav, m4a, etc.)
  - API key authentication support
  - Returns JSON with transcript and language detection

## Core STT Logic Location

The speech-to-text functionality has been extracted into a reusable module:
- **`stt_utils.py`**: Extracted STT functionality for reuse in other applications
  - `transcribe_youtube_to_file()`: High-level function for simple use cases
  - `transcribe_youtube_video()`: Advanced function returning TranscriptionResult object
  - `download_youtube_audio()`, `transcribe_audio_file()`: Lower-level functions
  - `save_transcript_to_file()`, `create_safe_filename()`, `format_timestamp()`: Utility functions

GUI implementations now use the extracted module:
- `youtube_transcriber.py:307-491` (batch processing - uses OpenAI Whisper)
- `faster_whisper_transcriber.py:113-141` (refactored to use stt_utils)  
- `simple_transcriber.py:104-224` (basic implementation - uses OpenAI Whisper)

## File Structure

```
├── stt_utils.py                    # Reusable STT functionality
├── test_stt_utils.py              # Demo/test script for stt_utils
├── whisper_api.py                 # FastAPI REST API server (NEW)
├── test_upload.py                 # API testing client (NEW)
├── youtube_transcriber.py          # Main application (batch processing)
├── faster_whisper_transcriber.py   # Faster Whisper GUI (refactored to use stt_utils)  
├── simple_transcriber.py           # Simple single-video version
├── requirements.txt                # Python dependencies for GUI applications
├── requirements-api.txt            # Python dependencies for API server (NEW)
├── .env.example                   # Example environment variables (NEW)
├── run_transcriber.bat            # Windows launcher script
├── *.spec                         # PyInstaller build specifications
├── build/                         # Compiled executables
├── transcript_env/                # Virtual environment (if created)
└── Videos.xlsx                    # Sample video list
```

## Development Notes

- **STT functionality has been extracted into `stt_utils.py` for reuse in other applications**
- The `stt_utils` module provides both high-level and low-level APIs for different use cases
- Faster-whisper version is recommended for production use due to better performance
- All versions handle temporary file cleanup automatically
- Error handling includes dependency checking and graceful failure recovery
- GUI uses threading to prevent blocking during long transcription processes

## Using STT Utils in Other Projects

The extracted `stt_utils.py` module can be easily integrated into other applications:

```python
from stt_utils import transcribe_youtube_to_file

# Simple usage
transcript_file = transcribe_youtube_to_file(
    url="https://youtube.com/watch?v=...",
    output_dir=Path("./transcripts"),
    model_name="base",
    include_timestamps=True
)
```

See `test_stt_utils.py` for comprehensive usage examples including mobile app backend integration.

## Performance Considerations

- **faster-whisper** is significantly faster than OpenAI Whisper
- CPU processing with int8 quantization provides good balance of speed and accuracy
- Model size affects both speed and accuracy: tiny (fastest) to large (most accurate)
- Audio download time depends on video length and internet connection