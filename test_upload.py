#!/usr/bin/env python3
"""
Test client for the Whisper API server.
Demonstrates how to upload audio files for transcription.
"""

import requests
import sys
from pathlib import Path


def test_transcribe_audio(file_path: str, api_key: str = None, model: str = "base", 
                         base_url: str = "http://localhost:8000"):
    """
    Test the /transcribe endpoint with an audio file.
    
    Args:
        file_path: Path to the audio file to transcribe
        api_key: Optional API key for authentication
        model: Whisper model to use (tiny, base, small, medium, large)
        base_url: Base URL of the API server
    
    Returns:
        Response from the API
    """
    
    # Check if file exists
    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        return None
    
    # Prepare headers
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    # Prepare the file for upload
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'model': model}
        
        print(f"Uploading {file_path} to {base_url}/transcribe...")
        print(f"Using model: {model}")
        if api_key:
            print(f"Using API key: {api_key[:8]}...")
        
        try:
            response = requests.post(
                f"{base_url}/transcribe",
                headers=headers,
                files=files,
                data=data,
                timeout=300  # 5 minute timeout for large files
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("\n" + "="*60)
                print("TRANSCRIPTION SUCCESSFUL")
                print("="*60)
                print(f"Detected Language: {result.get('detected_language', 'N/A')}")
                print(f"Language Probability: {result.get('language_probability', 'N/A')}")
                print("\nTranscript:")
                print("-" * 40)
                print(result.get('transcript', 'No transcript returned'))
                print("-" * 40)
                return result
            else:
                print(f"Error: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Detail: {error_detail.get('detail', 'No error detail')}")
                except:
                    print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None


def test_health_check(base_url: str = "http://localhost:8000"):
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{base_url}/")
        print(f"Health check - Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Message: {result.get('message', 'N/A')}")
            print(f"Version: {result.get('version', 'N/A')}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")
        return False


def test_models_endpoint(api_key: str = None, base_url: str = "http://localhost:8000"):
    """Test the models listing endpoint."""
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    try:
        response = requests.get(f"{base_url}/models", headers=headers)
        print(f"Models endpoint - Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Available models:")
            for model in result.get('models', []):
                print(f"  - {model.get('name', 'N/A')}: {model.get('description', 'N/A')}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Models endpoint failed: {e}")
        return False


def main():
    """Main test function."""
    print("Whisper API Test Client")
    print("=" * 40)
    
    # Test health check first
    print("\n1. Testing health check...")
    if not test_health_check():
        print("Health check failed. Is the server running?")
        return
    
    # Test models endpoint
    print("\n2. Testing models endpoint...")
    test_models_endpoint()
    
    # Test transcription if audio file provided
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        api_key = sys.argv[2] if len(sys.argv) > 2 else None
        model = sys.argv[3] if len(sys.argv) > 3 else "base"
        
        print(f"\n3. Testing transcription with {audio_file}...")
        test_transcribe_audio(audio_file, api_key, model)
    else:
        print("\n3. Skipping transcription test (no audio file provided)")
        print("Usage: python test_upload.py <audio_file> [api_key] [model]")
        print("Example: python test_upload.py audio.mp3 your_api_key base")


if __name__ == "__main__":
    main()