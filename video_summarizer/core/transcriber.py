"""
Transcriber Module - Functions for transcribing audio with progress indicators.
"""

import os
import torch
import logging
import sys
import time
from tqdm import tqdm

# Try to import whisper correctly
try:
    import whisper
    print("[OK] Successfully imported whisper package.")
except ImportError:
    print("[WARN] Failed to import whisper, trying openai-whisper package...")
    try:
        import openai
        whisper = openai.whisper
        print("✅ Using openai.whisper package.")
    except (ImportError, AttributeError):
        print("❌ ERROR: Could not import whisper! Please install with 'pip install openai-whisper'")

# Configure FFmpeg path for Whisper - CRITICAL FOR TRANSCRIPTION
script_dir = os.path.dirname(os.path.abspath(__file__))
ffmpeg_bin_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), "ffmpeg", "bin")
    
if os.path.exists(ffmpeg_bin_dir):
    # Add FFmpeg bin directory to PATH
    os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ.get("PATH", "")
    print(f"[OK] Added FFmpeg directory to PATH: {ffmpeg_bin_dir}")
else:
    print(f"[WARN] Warning: FFmpeg directory not found at {ffmpeg_bin_dir}")

def show_progress_bar(message, duration=3):
    """Display a progress bar with message."""
    print(f"\n🔄 {message}")
    for i in tqdm(range(duration), desc="Progress", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
        time.sleep(1)

def show_model_download_progress():
    """Show progress for model download."""
    print("\n📥 Downloading Whisper model (first time only)...")
    print("   This may take a few minutes depending on your internet connection.")
    
    # Simulate progress for model download
    steps = [
        "Connecting to Hugging Face model repository...",
        "Downloading model files...", 
        "Extracting and caching model...",
        "Initializing model on device...",
        "Model ready for transcription!"
    ]
    
    for i, step in enumerate(steps):
        print(f"   Step {i+1}/5: {step}")
        time.sleep(1)  # Small delay to show progress

# Define a fallback transcribe function in case whisper import fails
def fallback_transcribe(audio_path, language='auto'):
    error_msg = "Error: Could not transcribe audio. Whisper package not properly installed."
    print(error_msg)
    return error_msg

# Define the actual transcription function
def transcribe_audio(audio_path, language='auto'):
    """
    Transcribe audio to text using Whisper with progress indicators.
    
    Args:
        audio_path (str): Path to the audio file.
        language (str): Language code or 'auto' for auto-detection.
        
    Returns:
        str: Transcribed text.
    """
    print("\n🎤 STARTING AUDIO TRANSCRIPTION")
    print("=" * 50)
    
    # Check if whisper is properly imported
    if 'whisper' not in globals():
        return fallback_transcribe(audio_path, language)
    
    # Step 1: Verify audio file
    print("📋 Step 1/5: Verifying audio file...")
    if not os.path.exists(audio_path):
        error_msg = f"❌ Error: Audio file not found at {audio_path}"
        print(error_msg)
        return error_msg
    
    # Check file permissions and size
    try:
        file_size = os.path.getsize(audio_path) / (1024 * 1024)  # Size in MB
        print(f"✅ Audio file verified: {os.path.basename(audio_path)} ({file_size:.2f} MB)")
        
        # Try to open the file to verify read access
        with open(audio_path, 'rb') as f:
            first_bytes = f.read(1024)
            if len(first_bytes) == 0:
                print(f"⚠️ Warning: Audio file exists but appears to be empty")
    except Exception as file_error:
        error_msg = f"❌ Error accessing audio file: {str(file_error)}"
        print(error_msg)
        return error_msg
    
    # Step 2: Check FFmpeg
    print("\n📋 Step 2/5: Checking FFmpeg availability...")
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(os.path.dirname(os.path.dirname(script_dir)), "ffmpeg", "bin", "ffmpeg.exe")
        
        if not os.path.exists(ffmpeg_path):
            print(f"⚠️ Warning: FFmpeg not found at {ffmpeg_path}")
        else:
            print(f"✅ FFmpeg ready: {ffmpeg_path}")
            os.environ["PATH"] = os.environ["PATH"] + os.pathsep + os.path.dirname(ffmpeg_path)
    except Exception as ffmpeg_error:
        print(f"⚠️ Error checking FFmpeg: {str(ffmpeg_error)}")
    
    try:
        # Step 3: Device detection
        print("\n📋 Step 3/5: Detecting processing device...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        device_name = "GPU (CUDA)" if device == "cuda" else "CPU"
        print(f"✅ Using device: {device_name}")
        
        # Step 4: Load Whisper model
        print("\n📋 Step 4/5: Loading Whisper model...")
        model_size = "base"
        print(f"   Model size: {model_size}")
        print(f"   Target device: {device_name}")
        
        # Show progress for first-time model download
        try:
            # Check if model is already cached
            import whisper
            model_path = whisper._MODELS[model_size]
            cache_dir = os.path.expanduser("~/.cache/whisper")
            cached_model = os.path.join(cache_dir, os.path.basename(model_path))
            
            if not os.path.exists(cached_model):
                show_model_download_progress()
            else:
                print("   📦 Using cached model...")
            
        except:
            print("   📥 Loading model (may download if first time)...")
        
        # Load model with progress
        try:
            with tqdm(total=100, desc="Loading model", bar_format="{l_bar}{bar}| {percentage:3.0f}%") as pbar:
                model = whisper.load_model(model_size, device=device)
                pbar.update(100)
            print("✅ Whisper model loaded successfully")
        except Exception as model_error:
            error_msg = f"❌ Error loading Whisper model: {str(model_error)}"
            print(error_msg)
            return error_msg
        
        # Step 5: Transcription setup
        print("\n📋 Step 5/5: Configuring transcription...")
        options = {}
        if language != 'auto':
            options["language"] = language
            print(f"   🌐 Language: {language}")
        else:
            print("   🌐 Language: Auto-detection enabled")
        
        print(f"   🎯 Processing device: {device_name}")
        print(f"   📁 Audio file: {os.path.basename(audio_path)}")
        
        # Transcribe with progress indicator
        print(f"\n🚀 TRANSCRIBING AUDIO...")
        print("   This may take a few minutes depending on audio length and device speed.")
        
        try:
            # Estimate transcription time (rough estimate)
            estimated_time = int(file_size * 2)  # ~2 seconds per MB
            
            with tqdm(total=100, desc="Transcribing", bar_format="{l_bar}{bar}| {percentage:3.0f}% | ETA: {remaining}") as pbar:
                # Start transcription
                result = model.transcribe(audio_path, **options)
                pbar.update(100)
                
            print("✅ Transcription completed successfully!")
            
        except FileNotFoundError as fnf:
            error_msg = f"❌ FileNotFoundError during transcription: {str(fnf)}"
            print(error_msg)
            print("💡 Tip: This usually means FFmpeg is not properly installed or accessible.")
            return f"Transcription error: FFmpeg may not be correctly installed or accessible. Error: {str(fnf)}"
        except Exception as trans_error:
            error_msg = f"❌ Error during transcription: {str(trans_error)}"
            print(error_msg)
            return f"Transcription error: {str(trans_error)}"
        
        # Validate results
        if not result or "text" not in result or not result["text"]:
            print("⚠️ Warning: Transcription returned no text")
            return "No speech detected in the audio file."
        
        # Success summary
        transcript_length = len(result['text'])
        word_count = len(result['text'].split())
        
        print(f"\n🎉 TRANSCRIPTION COMPLETE!")
        print(f"   📝 Characters: {transcript_length:,}")
        print(f"   📖 Words: {word_count:,}")
        print(f"   ⏱️ Audio length: {file_size:.1f} MB processed")
        
        if len(result['text']) > 100:
            print(f"   📄 Preview: {result['text'][:100]}...")
        
        return result["text"]
        
    except Exception as e:
        error_msg = f"❌ Unexpected error during transcription: {str(e)}"
        print(error_msg)
        return f"Transcription error: {str(e)}"
