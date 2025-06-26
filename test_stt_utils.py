#!/usr/bin/env python3
"""
Test script demonstrating the usage of stt_utils module

This script shows how to use the extracted STT functionality
for other applications like mobile app backends.
"""

from pathlib import Path
from stt_utils import (
    transcribe_youtube_to_file, 
    transcribe_youtube_video,
    save_transcript_to_file,
    create_safe_filename,
    format_timestamp
)

def demo_high_level_api():
    """Demonstrate the high-level API for simple use cases"""
    print("=== High-Level API Demo ===")
    
    # Example usage - this would work with a real YouTube URL
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example URL
    output_dir = Path("./test_output")
    
    print(f"Would transcribe: {url}")
    print(f"Output directory: {output_dir}")
    print(f"This is how you'd use it:")
    print("""
    transcript_file = transcribe_youtube_to_file(
        url=url,
        output_dir=output_dir,
        model_name="base",
        include_timestamps=True,
        progress_callback=lambda msg: print(f"Progress: {msg}")
    )
    print(f"Transcript saved to: {transcript_file}")
    """)

def demo_advanced_api():
    """Demonstrate the advanced API for more control"""
    print("\n=== Advanced API Demo ===")
    
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example URL
    output_dir = Path("./test_output")
    
    print(f"For more control over the process:")
    print("""
    # Step 1: Transcribe and get result object
    result = transcribe_youtube_video(
        url=url,
        output_dir=output_dir,
        model_name="base",
        include_timestamps=False,
        cleanup_audio=True,
        progress_callback=lambda msg: print(msg)
    )
    
    # Step 2: Access the transcription data
    print(f"Video title: {result.video_title}")
    print(f"Detected language: {result.detected_language}")
    print(f"Language probability: {result.language_probability}")
    
    # Step 3: Process segments manually
    full_text = ""
    for segment in result.segments:
        full_text += segment.text.strip() + " "
    
    # Step 4: Save with custom formatting
    custom_file = output_dir / "custom_transcript.txt"
    save_transcript_to_file(result, custom_file, include_timestamps=True)
    """)

def demo_utility_functions():
    """Demonstrate utility functions"""
    print("\n=== Utility Functions Demo ===")
    
    # Test filename creation
    messy_title = "This is a messy title with special chars!@#$%^&*()"
    safe_title = create_safe_filename(messy_title)
    print(f"Original title: {messy_title}")
    print(f"Safe filename: {safe_title}")
    
    # Test timestamp formatting
    seconds_list = [30, 125, 3665]
    for seconds in seconds_list:
        formatted = format_timestamp(seconds)
        print(f"{seconds} seconds = {formatted}")

def mobile_app_backend_example():
    """Example of how this could be used in a mobile app backend"""
    print("\n=== Mobile App Backend Example ===")
    
    print("""
    # Flask/FastAPI endpoint example:
    
    from flask import Flask, request, jsonify
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
            
            # Read the transcript content
            with open(transcript_file, 'r') as f:
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
    """)

if __name__ == "__main__":
    print("STT Utils Test & Demo Script")
    print("=" * 40)
    
    demo_high_level_api()
    demo_advanced_api()
    demo_utility_functions()
    mobile_app_backend_example()
    
    print("\n" + "=" * 40)
    print("Demo complete!")
    print("\nTo actually test with a real YouTube video:")
    print("1. Ensure you have faster-whisper and yt-dlp installed")
    print("2. Replace the example URLs with real YouTube URLs")
    print("3. Run the transcription functions")