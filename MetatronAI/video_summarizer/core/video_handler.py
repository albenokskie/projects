"""
Video Handl    # Option 1: Check for local FFmpeg in project directory
    local_ffmpeg = os.path.join(os.path.dirname(__file__), '..', '..', 'ffmpeg', 'bin', 'ffmpeg.exe')
    if os.path.exists(local_ffmpeg):
        print(f"[OK] Using local FFmpeg: {local_ffmpeg}")
        return local_ffmpeg
    
    # Option 2: Try system PATH (if user installed FFmpeg globally)
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        print(f"[OK] Using system FFmpeg: {system_ffmpeg}")
        return system_ffmpeg
    
    # Option 3: Try imageio-ffmpeg (bundled with imageio)
    try:
        import imageio_ffmpeg
        imageio_ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.exists(imageio_ffmpeg_path):
            print(f"[OK] Using imageio FFmpeg: {imageio_ffmpeg_path}")
            return imageio_ffmpeg_pathns for handling video files with progress indicators.
"""

import os
import subprocess
import tempfile
from urllib.parse import urlparse
from pytube import YouTube
from tqdm import tqdm
import time
import shutil

# Smart FFmpeg detection - try multiple sources
def find_ffmpeg():
    """Find FFmpeg executable from multiple possible sources."""
    # Option 1: Try local ffmpeg directory first
    local_ffmpeg = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ffmpeg", "bin", "ffmpeg.exe")
    if os.path.exists(local_ffmpeg):
        print(f"✅ Using local FFmpeg: {local_ffmpeg}")
        return local_ffmpeg
    
    # Option 2: Try system PATH (if user installed FFmpeg globally)
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        print(f"[OK] Using system FFmpeg: {system_ffmpeg}")
        return system_ffmpeg
    
    # Option 3: Try imageio-ffmpeg (bundled with imageio)
    try:
        import imageio_ffmpeg
        imageio_ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.exists(imageio_ffmpeg_path):
            print(f"✅ Using imageio FFmpeg: {imageio_ffmpeg_path}")
            return imageio_ffmpeg_path
    except (ImportError, AttributeError):
        pass
    
    # Option 4: Try to download via imageio
    try:
        import imageio
        print("📥 Downloading FFmpeg via imageio (this may take a moment)...")
        imageio.plugins.ffmpeg.download()
        import imageio_ffmpeg
        imageio_ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.exists(imageio_ffmpeg_path):
            print(f"[OK] Downloaded and using imageio FFmpeg: {imageio_ffmpeg_path}")
            return imageio_ffmpeg_path
    except Exception as e:
        print(f"[WARN] Could not download FFmpeg via imageio: {e}")
    
    return None

# Find FFmpeg executable
FFMPEG_PATH = find_ffmpeg()

if FFMPEG_PATH:
    # Add FFmpeg bin directory to PATH - important for other libraries that use FFmpeg
    ffmpeg_bin_dir = os.path.dirname(FFMPEG_PATH)
    if ffmpeg_bin_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ.get("PATH", "")
        print(f"[OK] Added FFmpeg directory to PATH: {ffmpeg_bin_dir}")
else:
    print("[WARN] FFmpeg not found. Some features may not work properly.")
    print("[INFO] Install FFmpeg using: pip install imageio-ffmpeg")

def is_youtube_url(url):
    """Check if the URL is a valid YouTube URL."""
    parsed_url = urlparse(url)
    return ('youtube.com' in parsed_url.netloc or 
            'youtu.be' in parsed_url.netloc)

def download_video(url, output_dir='.'):
    """
    Download a video from a URL with progress indicators.
    
    Args:
        url (str): URL to the video.
        output_dir (str): Directory to save the video.
        
    Returns:
        str: Path to the downloaded video file.
    """
    print("\n📹 STARTING VIDEO DOWNLOAD")
    print("=" * 50)
    
    os.makedirs(output_dir, exist_ok=True)
    
    if is_youtube_url(url):
        print(f"[VIDEO] YouTube video detected")
        print(f"📂 Output directory: {output_dir}")
        
        try:
            # Get video info with progress
            print("\n📋 Step 1/3: Getting video information...")
            with tqdm(total=100, desc="Fetching info", bar_format="{l_bar}{bar}| {percentage:3.0f}%") as pbar:
                yt = YouTube(url)
                pbar.update(50)
                video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                pbar.update(50)
            
            print(f"✅ Video found: {yt.title}")
            print(f"   📺 Duration: {yt.length//60}:{yt.length%60:02d}")
            print(f"   [INFO] Resolution: {video.resolution}")
            print(f"   [INFO] Size: ~{video.filesize/(1024*1024):.1f} MB")
            
            # Create filename
            print("\n📋 Step 2/3: Preparing download...")
            filename = ''.join(c if c.isalnum() or c in ' ._-' else '_' for c in yt.title)
            filename = filename.rstrip() + '.mp4'
            print(f"   📄 Filename: {filename}")
            
            # Download with progress
            print("\n📋 Step 3/3: Downloading video...")
            print("   This may take several minutes depending on video size and internet speed.")
            
            # Note: pytube doesn't have built-in progress callback, so we simulate
            with tqdm(total=100, desc="Downloading", bar_format="{l_bar}{bar}| {percentage:3.0f}%") as pbar:
                video_path = video.download(output_path=output_dir, filename=filename)
                pbar.update(100)
            
            print(f"✅ Download complete: {os.path.basename(video_path)}")
            return video_path
            
        except Exception as e:
            print(f"[ERROR] Download failed: {str(e)}")
            raise
    else:
        # Handle other video URLs
        raise ValueError("Currently only YouTube URLs are supported.")

def extract_audio(video_path, output_dir='.'):
    """
    Extract audio from a video file using FFmpeg with progress indicators.
    
    Args:
        video_path (str): Path to the video file.
        output_dir (str): Directory to save the audio.
        
    Returns:
        str: Path to the extracted audio file.
    """
    print("\n🔊 STARTING AUDIO EXTRACTION")
    print("=" * 50)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Validate input
    print("📋 Step 1/4: Validating video file...")
    base_filename = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(output_dir, f"{base_filename}.wav")
    
    if not os.path.exists(video_path):
        error_msg = f"[ERROR] Video file not found at {video_path}"
        print(error_msg)
        raise FileNotFoundError(error_msg)
    
    video_size = os.path.getsize(video_path) / (1024 * 1024)  # Size in MB
    print(f"✅ Video file validated: {os.path.basename(video_path)} ({video_size:.2f} MB)")
    
    # Step 2: Check FFmpeg
    print("\n[STEP] Step 2/4: Checking FFmpeg availability...")
    if FFMPEG_PATH is None or not os.path.exists(FFMPEG_PATH):
        ffmpeg_cmd = "ffmpeg"
        if FFMPEG_PATH is None:
            print("[WARN] FFmpeg not found automatically. Trying system FFmpeg...")
        else:
            print(f"[WARN] FFmpeg not found at {FFMPEG_PATH}. Trying system FFmpeg...")
    else:
        ffmpeg_cmd = FFMPEG_PATH
        print(f"[OK] FFmpeg ready: {FFMPEG_PATH}")
    
    # Step 3: Prepare extraction
    print("\n📋 Step 3/4: Preparing audio extraction...")
    print(f"   [INFO] Input: {os.path.basename(video_path)}")
    print(f"   🎵 Output: {os.path.basename(audio_path)}")
    print(f"   🔧 Format: WAV (16-bit, 44.1kHz, Stereo)")
    
    cmd = [
        ffmpeg_cmd,
        '-i', video_path,
        '-vn',  # No video
        '-acodec', 'pcm_s16le',  # Audio codec
        '-ar', '44100',  # Sample rate
        '-ac', '2',  # Stereo
        '-y',  # Overwrite output file
        audio_path
    ]
    
    # Step 4: Extract audio
    print("\n📋 Step 4/4: Extracting audio...")
    print("   This may take a few minutes depending on video length.")
    
    try:
        # Show command (truncated for readability)
        cmd_display = ' '.join(cmd[:3]) + ' ... ' + ' '.join(cmd[-3:])
        print(f"   🔧 Command: {cmd_display}")
        
        # Run with progress simulation
        with tqdm(total=100, desc="Extracting", bar_format="{l_bar}{bar}| {percentage:3.0f}%") as pbar:
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pbar.update(100)
        
        # Validate output
        if os.path.exists(audio_path):
            audio_size = os.path.getsize(audio_path) / (1024 * 1024)  # Size in MB
            print(f"✅ Audio extraction complete!")
            print(f"   [INFO] Output file: {os.path.basename(audio_path)}")
            print(f"   [INFO] Size: {audio_size:.2f} MB")
            print(f"   💾 Saved to: {audio_path}")
            return audio_path
        else:
            error_msg = "[ERROR] FFmpeg completed but no output file was created"
            print(error_msg)
            raise RuntimeError(error_msg)
            
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8') if e.stderr else "No error output available"
        error_msg = f"[ERROR] FFmpeg error: {error_output}"
        print(error_msg)
        print("💡 Tip: Check if the video file is corrupted or in an unsupported format.")
        raise RuntimeError(error_msg)
    except FileNotFoundError as e:
        error_msg = f"[ERROR] FFmpeg executable not found: {str(e)}"
        print(error_msg)
        print("💡 Tip: Ensure FFmpeg is installed and accessible.")
        raise FileNotFoundError(error_msg)
