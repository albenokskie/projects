"""
Test script to verify dependencies are installed correctly.
"""

def test_dependencies():
    """Test if all required dependencies are installed."""
    try:
        import torch
        print("✓ PyTorch installed")
    except ImportError:
        print("✗ PyTorch not found")
    
    try:
        import transformers
        print("✓ Transformers installed")
    except ImportError:
        print("✗ Transformers not found")
    
    try:
        import whisper
        print("✓ Whisper installed")
    except ImportError:
        print("✗ Whisper not found")
    
    try:
        import pytube
        print("✓ PyTube installed")
    except ImportError:
        print("✗ PyTube not found")
    
    try:
        from moviepy.editor import VideoFileClip
        print("✓ MoviePy installed")
    except ImportError:
        print("✗ MoviePy not found")

if __name__ == "__main__":
    print("Testing dependencies...")
    test_dependencies()
