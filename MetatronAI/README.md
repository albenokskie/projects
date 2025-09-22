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

**What gets installed:**
- **🎙️ OpenAI Whisper** (~1.6GB) - Audio transcription AI model
- **🧠 PyTorch** (~2GB) - Deep learning framework
- **📝 Transformers** (~1GB) - BART summarization model
- **🔗 OpenAI API Client** - For enhanced summarization (optional)
- **📹 PyTube** - YouTube video downloading
- **⚙️ Supporting libraries** - Progress bars, environment management

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

## 🚀 Quick Start Guide

### First Time Setup (Windows)

1. **Activate your virtual environment:**
```bash
.\meta\Scripts\activate
```

2. **Test the installation:**
```bash
python video_summarizer/main.py --help
```
*Note: First run may take 2-3 minutes as AI models download (~1.6GB)*

3. **Run your first test:**
```bash
# Test with a short YouTube video (recommended for first run)
python video_summarizer/main.py -u "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --summary-length 2
```

### Command Line Options

```bash
python video_summarizer/main.py [OPTIONS]

Required (choose one):
  -f, --file PATH        Local video file or transcript (.mp4, .avi, .txt, etc.)
  -u, --url URL          Video URL (YouTube, Vimeo, etc.)

Optional:
  -o, --output DIR       Output directory (default: current directory)
  -l, --language LANG    Language code (default: auto-detect)
  --summary-length 1-5   Summary detail level (1=brief, 5=detailed, default=3)
  --chapters             Include chapter-based summaries (requires OpenAI)
  --keep-temp            Keep temporary files (audio, transcript)
  --debug                Enable detailed logging
  --help                 Show this help message
```

### Summary Length Levels

The `--summary-length` parameter controls how detailed your AI-generated summary will be:

| Level | Description | Approximate Length | Best For | Example Use |
|-------|-------------|-------------------|----------|-------------|
| **1** | Very Brief | ~50-100 words | Quick overviews, bullet points | `--summary-length 1` |
| **2** | Brief | ~100-200 words | Short videos, key points only | `--summary-length 2` |
| **3** | Moderate | ~200-400 words | **Default**, balanced detail | `--summary-length 3` |
| **4** | Detailed | ~400-600 words | Educational content, thorough analysis | `--summary-length 4` |
| **5** | Very Detailed | ~600+ words | Long lectures, comprehensive summaries | `--summary-length 5` |

**Examples:**
```bash
# Quick summary for a short video
python video_summarizer/main.py -f "video.mp4" --summary-length 1

# Standard summary (default)
python video_summarizer/main.py -f "video.mp4"  # Uses level 3

# Detailed summary for educational content
python video_summarizer/main.py -f "lecture.mp4" --summary-length 5
```

**Recommendation:** Start with level 2-3 for testing, use level 4-5 for important educational content.

## 🔧 Command Line Options Explained

### Input Options (Required - Choose One)

#### `-f, --file PATH`
**Purpose:** Process a local video file or existing transcript
**Supported formats:** `.mp4`, `.avi`, `.mov`, `.mkv`, `.wmv`, `.txt`, `.srt`

```bash
# Video files
python video_summarizer/main.py -f "C:\Videos\lecture.mp4"

# Transcript files (skips transcription, goes straight to summary)
python video_summarizer/main.py -f "transcript.txt"
```

#### `-u, --url URL`
**Purpose:** Download and process videos from online platforms
**Supported platforms:** YouTube, Vimeo, and other pytube-compatible sites

```bash
# YouTube video
python video_summarizer/main.py -u "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Vimeo video
python video_summarizer/main.py -u "https://vimeo.com/123456789"
```

### Output Options

#### `-o, --output DIR`
**Purpose:** Specify where to save output files
**Default:** Current directory

```bash
# Save to specific folder
python video_summarizer/main.py -f "video.mp4" -o "C:\Summaries"

# Save to relative path
python video_summarizer/main.py -f "video.mp4" -o "results"
```

### Language Options

#### `-l, --language LANG`
**Purpose:** Specify video language for better transcription accuracy
**Default:** `auto` (automatic detection)
**Supported:** Any language code (en, es, fr, de, ja, etc.)

```bash
# Spanish video
python video_summarizer/main.py -f "video.mp4" -l es

# Japanese video
python video_summarizer/main.py -f "video.mp4" -l ja

# Auto-detect (default)
python video_summarizer/main.py -f "video.mp4" -l auto
```

### Summary Enhancement Options

#### `--chapters`
**Purpose:** Generate chapter-based summaries with section breakdowns
**Requirement:** OpenAI API key in `.env` file
**Benefits:** Structured summaries with clear topic divisions

```bash
# With chapters (enhanced structure)
python video_summarizer/main.py -f "lecture.mp4" --chapters

# Without chapters (standard summary)
python video_summarizer/main.py -f "lecture.mp4"
```

**Example output difference:**
- **Without chapters:** Single flowing summary
- **With chapters:** Organized sections like "Introduction", "Main Concepts", "Conclusion"

### File Management Options

#### `--keep-temp`
**Purpose:** Preserve temporary files created during processing
**Keeps:** Audio files (`.wav`), intermediate transcripts, processing logs

```bash
# Keep all temporary files for review
python video_summarizer/main.py -f "video.mp4" --keep-temp

# Clean up temporary files (default)
python video_summarizer/main.py -f "video.mp4"
```

**Useful when:**
- Debugging processing issues
- Wanting to reuse extracted audio
- Analyzing intermediate steps

### Debugging Options

#### `--debug`
**Purpose:** Enable detailed logging for troubleshooting
**Shows:** Step-by-step processing, error details, timing information

```bash
# Enable debug logging
python video_summarizer/main.py -f "video.mp4" --debug
```

**Use when:**
- First-time setup issues
- Processing fails unexpectedly
- Performance analysis needed

#### `--help`
**Purpose:** Display all available options and usage examples

```bash
python video_summarizer/main.py --help
```

## 📝 Usage Examples

### Example 1: Basic YouTube Video Processing
```bash
# Simple YouTube video with standard summary
python video_summarizer/main.py -u "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Example 2: Local Video with Custom Settings
```bash
# Process local video with detailed summary and chapters
python video_summarizer/main.py -f "C:\Videos\my_video.mp4" --summary-length 4 --chapters
```

### Example 3: Educational Content with Chapters
```bash
# Perfect for educational videos - includes chapter breakdown
python video_summarizer/main.py -u "https://www.youtube.com/watch?v=EDUCATION_VIDEO" --chapters --summary-length 5
```

### Example 4: Quick Processing with Custom Output
```bash
# Fast processing with brief summary to specific folder
python video_summarizer/main.py -f "video.mp4" --summary-length 1 -o "C:\Summaries"
```

### Example 5: Process Existing Transcript
```bash
# If you already have a transcript file
python video_summarizer/main.py -f "transcript.txt" --summary-length 3
```

## 🎯 Expected Output

After processing, you'll get:
- **`[filename]_summary.txt`** - Main AI-generated summary
- **`[filename].txt`** - Full transcript (if from video)
- **Temporary files** (if `--keep-temp` used):
  - Audio file (`.wav`)
  - Processing logs

### Sample Output Structure:
```
📁 Output Directory/
├── 📄 my_video_summary.txt    # ⭐ Main summary with chapters
├── 📄 my_video.txt            # 📝 Full transcript  
└── 🎵 my_video.wav            # 🎧 Extracted audio (if --keep-temp)
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

### First Run Issues

**Q: The help command takes forever to load**
A: This is normal on first run! The app is downloading AI models (~1.6GB):
- Whisper model for transcription
- BART model for summarization
- This only happens once - subsequent runs are fast

**Q: Command hangs after "Loading summarizer..."**
A: The BART model is downloading. Wait 3-5 minutes depending on internet speed.

**Q: Import errors or "Module not found"**
A: Make sure your virtual environment is activated:
```bash
# Windows
.\meta\Scripts\activate

# Then install dependencies
pip install -r video_summarizer/requirements.txt
```

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

### Runtime Issues

**Q: "FFmpeg not found" warnings**
A: The app uses system FFmpeg. Warnings are normal if local FFmpeg folder doesn't exist.

**Q: OpenAI summarization fails**
A: App automatically falls back to local BART model. Check:
- API key in `.env` file
- Internet connection
- API endpoint configuration

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
