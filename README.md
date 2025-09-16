# MetatronAI Video Summarizer

A powerful command-line tool that transcribes videos and creates AI-powered summaries of the content. It supports YouTube videos, local video files, and even existing transcript files.

**Created by Alvin Atillo (TS-PH)**

## 🎯 Features

- **Video Input**: Process videos from YouTube URLs or local files
- **Transcript Processing**: Process existing transcript text files
- **Audio Extraction**: Extract audio from videos using FFmpeg (auto-detected)
- **AI Transcription**: Transcribe speech to text using Whisper AI
- **Intelligent Summarization**: Generate summaries using either OpenAI's API or local transformer models
- **Progress Indicators**: Real-time progress bars and status updates during processing
- **Customizable Output**: Adjust summary length and format
- **Chapter-Based Summaries**: Break down content into logical sections with headers
- **Smart FFmpeg Detection**: Automatically finds and uses available FFmpeg installation

## 📦 Project Size & Dependencies

**Important Note:** This GitHub repository is lightweight (~40 KB) and does NOT include:
- ❌ Virtual environments (`focus/`, `venv/`) - these are recreated locally
- ❌ Python cache files (`__pycache__/`) - automatically generated
- ❌ API keys (`.env` files) - you create these yourself
- ❌ Large dependency files - downloaded via `pip install`

The AI models and dependencies (PyTorch, Transformers, Whisper) are large (3-5 GB total) but are automatically downloaded when you run `pip install -r requirements.txt` in your own environment.

## 📋 Requirements

- Python 3.8+
- FFmpeg (automatically installed via imageio-ffmpeg package)

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/MetatronAI.git
cd MetatronAI
```

### 2. Set up a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r video_summarizer/requirements.txt
```

**Note:** This step downloads ~3-5 GB of AI models and dependencies. This is normal and expected for AI applications. The download happens once and models are cached locally.

### 4. Configure API keys (optional, for better summaries)

Create a `.env` file in the video_summarizer directory:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the tool

```bash
# Process a YouTube video
python video_summarizer/main.py -u https://www.youtube.com/watch?v=VIDEO_ID

# Process a local video file
python video_summarizer/main.py -f path/to/your/video.mp4

# Process an existing transcript
python video_summarizer/main.py -f path/to/your/transcript.txt
```

## 📊 Directory Structure

```
MetatronAI/                   # Total GitHub repo size: ~35 KB (cleaned up!)
├── video_summarizer/         # Main package (~30 KB)
│   ├── core/                 # Core modules (~20 KB)
│   │   ├── summarizer.py     # Text summarization module (~8 KB)
│   │   ├── transcriber.py    # Audio transcription module (~7 KB)
│   │   └── video_handler.py  # Video processing with smart FFmpeg detection (~6 KB)
│   ├── data/                 # Example data files (~2 KB)
│   │   ├── example_transcript.txt # Sample input
│   │   ├── example_summary.txt    # Sample output
│   │   └── WSS01E01-Networking-Basics.txt # Real example
│   ├── tests/                # Test framework (placeholder)
│   │   └── __init__.py
│   ├── main.py               # Enhanced main application with progress indicators (~10 KB)
│   ├── requirements.txt      # Python dependencies list (~0.3 KB)
│   └── __init__.py           # Package initialization
├── focus/                    # Virtual environment (gitignored)
├── .gitignore               # Git ignore rules (~3 KB)
├── LICENSE                  # MIT License (~1 KB)
└── README.md                # This comprehensive documentation (~12 KB)

# Files NOT in repository (created locally):
# focus/ or venv/        # Virtual environment (3-5 GB)
# __pycache__/          # Python cache files
# .env                  # Your API keys
# output/               # Generated summaries and transcripts
```

**Why is the download large but GitHub repo small?**
- GitHub repo: Source code only (~35 KB)
- Local installation: Includes AI models from PyTorch, Transformers, Whisper (~3-5 GB)
- This is standard practice - you don't upload dependencies to GitHub!

## 🛠️ Usage Options

```
python video_summarizer/main.py [-h] (-f FILE | -u URL) [-o OUTPUT] [-l LANGUAGE] [--keep-temp] [--summary-length SUMMARY_LENGTH] [--chapters] [--debug]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `-f`, `--file` | Path to a local video file or transcript text file |
| `-u`, `--url` | URL to a video (YouTube, etc.) |
| `-o`, `--output` | Output directory for files (default: current directory) |
| `-l`, `--language` | Language of the video (default: auto-detect) |
| `--keep-temp` | Keep temporary files (audio, transcript) |
| `--summary-length` | Summary length from 1-5, with 5 being the longest (default: 3) |
| `--chapters` | Enable chapter-based summaries |
| `--debug` | Enable debug mode with detailed logging |

## 📝 Examples

### Summarize a YouTube video with chapter breakdowns

```bash
python video_summarizer/main.py -u https://www.youtube.com/watch?v=dQw4w9WgXcQ --chapters
```

### Process a local video in Spanish with a detailed summary

```bash
python video_summarizer/main.py -f my_video.mp4 -l es --summary-length 5
```

### Summarize an existing transcript file

```bash
python video_summarizer/main.py -f transcript.txt --chapters
```

### Save results to a specific directory

```bash
python video_summarizer/main.py -u https://www.youtube.com/watch?v=VIDEO_ID -o results/
```

## 🚀 Enhanced User Experience

### Real-Time Progress Indicators
The tool now includes comprehensive progress tracking:
- **Import Progress**: Shows AI library loading status (PyTorch, Whisper, etc.)
- **Step-by-Step Processing**: Clear numbered steps (1/7, 2/7, etc.)
- **Visual Progress Bars**: Real-time progress during transcription and processing
- **Model Download Progress**: Shows download status for AI models (1-2GB on first run)
- **Total Processing Time**: Complete timing information

### Sample Progress Output
```
🎬 MetatronAI Video Summarizer
📦 Loading AI libraries (this may take a moment on first run)...
  [1/6] Loading basic modules...           ✅
  [2/6] Loading PyTorch (AI engine)...     ✅
  [3/6] Loading Whisper (speech recognition)... ✅

📋 STEP 1/5: VALIDATING LOCAL VIDEO
📋 STEP 2/5: EXTRACTING AUDIO
📋 STEP 3/5: TRANSCRIBING AUDIO
📋 STEP 4/5: GENERATING SUMMARY
📋 STEP 5/5: CLEANING UP

🎉 PROCESSING COMPLETE! ⏱️ Total time: 45.2 seconds
```

## ⚙️ How It Works

1. **Input Processing**: The tool accepts a YouTube URL, local video file, or transcript file
2. **Video Download**: If a URL is provided, the video is downloaded using PyTube
3. **Audio Extraction**: For video inputs, audio is extracted using FFmpeg
4. **Transcription**: Audio is transcribed to text using OpenAI's Whisper model
5. **Summarization**: The transcript is summarized using either:
   - OpenAI's GPT API (if an API key is provided)
   - Local transformer models (fallback option)
6. **Output Generation**: Both transcript and summary are saved to text files and displayed in the terminal

## 🔧 Troubleshooting

### File Size Concerns

**Q: Why is my local installation so large (3-5 GB)?**
A: This is normal! AI applications require large models:
- PyTorch: ~2 GB (deep learning framework)
- Transformers: ~1 GB (Hugging Face models)
- Whisper: ~1-2 GB (speech recognition models)
- Other dependencies: ~500 MB

**Q: Why is the GitHub repository small (~40 KB)?**
A: GitHub repositories should only contain source code, not dependencies. The `.gitignore` file excludes:
- Virtual environments (`focus/`, `venv/`)
- Downloaded models and dependencies
- Cache files (`__pycache__/`)
- Personal configuration (`.env`)

### FFmpeg Issues

The repository includes FFmpeg binaries for Windows users. If you're on macOS or Linux, you'll need to install FFmpeg:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```

### OpenAI API Issues

If you encounter errors with the OpenAI API:
1. Check that your API key is correct in the `.env` file
2. Ensure you have sufficient credits in your OpenAI account
3. The tool will fall back to local transformer models if the API is unavailable

### Transcription Quality

For better transcription quality:
- Ensure audio is clear with minimal background noise
- Consider using a larger Whisper model by modifying `model_size` in `core/transcriber.py`
- For non-English content, specify the language with the `-l` parameter

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) for transcription
- [Hugging Face Transformers](https://github.com/huggingface/transformers) for local summarization
- [PyTube](https://github.com/pytube/pytube) for YouTube video downloading
- [FFmpeg](https://ffmpeg.org/) for audio processing

---
*Created by Alvin Atillo (TS-PH)*
