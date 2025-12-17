# Transcribing Video to Text

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive video-to-text transcription system that extracts audio from video files, applies noise reduction, and converts speech to text using state-of-the-art AI models (Whisper or Wav2Vec2). Supports both CLI and web interfaces with multilingual transcription capabilities.

## Features

- **Multilingual Transcription**: Support for 12 languages including English, Chinese, Japanese, Korean, and more
- **Dual Interface**: Choose between command-line tools or user-friendly web application
- **Advanced Audio Processing**: Automated noise removal and audio enhancement using spectral gating
- **Multiple AI Models**: Switch between OpenAI Whisper (large-v3) and Wav2Vec2 for optimal results
- **Batch Processing**: Process multiple audio files at once with a single command
- **Audio Visualizations**: Generate waveforms and spectrograms for quality verification
- **Flexible Input**: Supports MP4 video, M4A, and WAV audio file formats

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [CLI - Video Transcription](#cli---video-transcription)
  - [CLI - Audio Transcription](#cli---audio-transcription)
  - [Batch Processing](#batch-processing)
  - [Web Application](#web-application)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Supported Languages](#supported-languages)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Dhruv16S/Transcribing-Video-to-Text.git
cd Transcribing-Video-to-Text

# Activate environment
source /root/miniconda3/bin/activate video_transcribe

# Install dependencies
pip install -r requirements.txt

# Setup directories
mkdir videos Audio

# Transcribe a video (downloads model on first run)
./generate_transcripts.sh ./videos/my_video.mp4 whisper
```

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (required for audio processing)
- 4GB+ RAM (recommended for large-v3 Whisper model)
- Internet connection (for first-time model download)

### Step 1: Environment Setup

**Option 1: Use existing conda environment**
```bash
source /root/miniconda3/bin/activate video_transcribe
```

**Option 2: Create new virtual environment**
```bash
virtualenv env
source env/scripts/activate  # Linux/Mac
# or: source env/Scripts/activate  # Windows Git Bash
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install PyTorch

Required for Wav2Vec2 model. Install the appropriate version for your system from [pytorch.org](https://pytorch.org/get-started/locally/).

```bash
# Example for CUDA 12.1
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CPU-only (no GPU)
pip3 install torch torchvision torchaudio
```

### Step 4: Install FFmpeg

**Linux:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

### Step 5: Create Project Directories

```bash
mkdir videos  # For video file inputs
mkdir Audio   # For batch M4A processing (optional)
```

## Usage

### CLI - Video Transcription

**Extract audio only (no transcription):**
```bash
./generate_transcripts.sh ./videos/lecture.mp4
```

**Full transcription with auto-detect language:**
```bash
./generate_transcripts.sh ./videos/lecture.mp4 whisper
```

**Transcription with specific language:**
```bash
# Chinese
./generate_transcripts.sh ./videos/lecture.mp4 whisper zh

# Japanese
./generate_transcripts.sh ./videos/lecture.mp4 whisper ja

# English
./generate_transcripts.sh ./videos/lecture.mp4 whisper en
```

**Using Wav2Vec2 model:**
```bash
# Note: Requires training model first via model.ipynb
./generate_transcripts.sh ./videos/lecture.mp4 wav2vec
```

**Output files:**
- Audio: `./audio/original/audio_extracted.mp3`
- Cleaned audio: `./audio/cleaned/cleaned_audio.mp3`
- Transcript: `./output/whisper_transcript.txt`
- Visualizations: `./graphs/original/` and `./graphs/cleaned/`

### CLI - Audio Transcription

**Process M4A files:**
```bash
python m4a_to_text.py recording.m4a [language_code] [output_filename]

# Examples:
python m4a_to_text.py recording.m4a zh lecture_transcript
python m4a_to_text.py recording.m4a en meeting_notes
python m4a_to_text.py recording.m4a ja interview
```

**Process WAV files:**
```bash
python wav_to_text.py recording.wav [language_code] [output_filename]

# Example:
python wav_to_text.py recording.wav zh transcript
```

**Parameters:**
- `language_code` (optional): Language hint for better accuracy (e.g., `zh`, `en`, `ja`)
- `output_filename` (optional): Custom name for transcript file

### Batch Processing

Process all M4A files in the `Audio/` directory:

```bash
# Process all files with default language (Chinese)
./batch_m4a_to_text.sh

# Process all files with specific language
./batch_m4a_to_text.sh en
./batch_m4a_to_text.sh ja
```

**Features:**
- Automatically finds all `.m4a` files in `Audio/` directory
- Generates transcripts with filenames based on original audio files
- Provides progress tracking and success/failure reporting
- Outputs to `./output/` directory

### Web Application

**Development server:**
```bash
python app.py
# Access at: http://localhost:5000/
```

**Production deployment:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Features:**
- Drag-and-drop file upload
- Real-time transcription
- Audio playback (original and cleaned)
- Download results as ZIP file
- Automatic cleanup after download

**Limitations:**
- Maximum file size: 16MB (configurable in `app.py:44`)
- MP4 files only

## Architecture

### Processing Pipeline

```
┌─────────────┐
│  Input File │
│ (MP4/M4A/WAV)│
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│  Audio Extraction               │
│  (extract_audio.py)             │
│  • Extract audio from MP4       │
│  • Convert M4A/WAV to MP4       │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Preprocessing                  │
│  (preprocess_audio.py)          │
│  • Normalize audio levels       │
│  • Generate waveform graphs     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Noise Removal                  │
│  (noise_removal.py)             │
│  • Spectral gating algorithm    │
│  • Generate spectrograms        │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Transcription                  │
│  (main.py)                      │
│  • Whisper large-v3 OR          │
│  • Wav2Vec2 model               │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Output                         │
│  • Transcript TXT file          │
│  • Audio files (MP3/WAV)        │
│  • Visualization graphs (PNG)   │
└─────────────────────────────────┘
```

### File Organization

```
Transcribing-Video-to-Text/
├── videos/              # Input MP4 files
├── Audio/               # Input M4A files for batch processing
├── audio/
│   ├── original/        # Extracted raw audio
│   └── cleaned/         # Noise-reduced audio
├── graphs/
│   ├── original/        # Original audio visualizations
│   └── cleaned/         # Cleaned audio visualizations
├── output/              # Transcript text files
├── temp/                # Temporary conversion files
└── static/              # Web app assets (CSS, audio for playback)
```

## Configuration

### Model Selection

**Whisper (Default):**
- Model: `large-v3` (~2.9GB)
- Best for: Multilingual content, technical terminology, code-switching
- Downloads to: `~/.cache/whisper/` on first use
- Used in: `main.py`, `app.py`, `m4a_to_text.py`, `wav_to_text.py`

**Wav2Vec2:**
- Requires: Pre-training via `model.ipynb` notebook
- Model file: `model.pth` in project root
- Best for: English-only content with GPU acceleration
- Used in: `main.py` (when specified)

**Change Whisper model size** (if needed for memory constraints):
```python
# In main.py, app.py, m4a_to_text.py, wav_to_text.py
model = whisper.load_model("large-v3")  # Default
# Change to:
model = whisper.load_model("base")      # Smaller, faster
model = whisper.load_model("medium")    # Balanced
```

### Language Options

Specify language for better accuracy (Whisper only):

| Code | Language   | Code | Language    |
|------|------------|------|-------------|
| `en` | English    | `fr` | French      |
| `zh` | Chinese    | `de` | German      |
| `ja` | Japanese   | `es` | Spanish     |
| `ko` | Korean     | `ru` | Russian     |
| `pt` | Portuguese | `ar` | Arabic      |
| `hi` | Hindi      | `it` | Italian     |

### Web App File Size Limit

Default: 16MB. To change, edit `app.py:44`:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB in bytes
# Example: 100MB limit
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
```

## Supported Languages

Whisper model supports multilingual transcription with automatic detection or explicit language specification:

- **Auto-detection**: Automatically identifies language (may be less accurate)
- **Explicit specification**: Better accuracy for mixed-language content (e.g., Chinese lectures with English technical terms)

**Note:** Wav2Vec2 model supports English only.

## Troubleshooting

### FFmpeg Not Found
**Error:** `Error: ffmpeg not found. Please install ffmpeg.`

**Solution:** Install FFmpeg:
- Linux: `sudo apt-get install ffmpeg`
- Mac: `brew install ffmpeg`
- Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### Whisper Model Download Failures
**Error:** Model download times out or fails

**Solution:**
1. Check internet connection
2. Manually download from [Hugging Face](https://huggingface.co/openai/whisper-large-v3)
3. Place in `~/.cache/whisper/large-v3.pt`

### Out of Memory
**Error:** Out of memory during transcription

**Solution:**
- Use smaller model: `whisper.load_model("base")` or `"medium"`
- Process shorter audio segments
- Ensure 4GB+ RAM available

### Directory Not Found
**Error:** Directory errors during batch processing

**Solution:** Create all required directories:
```bash
mkdir -p videos Audio audio/original audio/cleaned graphs/original graphs/cleaned output temp
```

For more troubleshooting, see [CLAUDE.md](CLAUDE.md#common-issues).

## Contributing

Contributions are welcome! This project is part of a series focused on audio/video processing and translation.

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Transcribing-Video-to-Text.git`
3. Create a virtual environment and install dependencies
4. Make your changes
5. Test thoroughly with different file types and languages
6. Submit a pull request

### Areas for Contribution

- Support for additional audio/video formats
- Improved noise reduction algorithms
- Real-time transcription
- Speaker diarization
- Translation features (coming in future repositories)
- Performance optimizations
- Documentation improvements

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- **OpenAI Whisper**: [github.com/openai/whisper](https://github.com/openai/whisper)
- **Wav2Vec2**: [pytorch.org/audio](https://pytorch.org/audio/stable/tutorials/speech_recognition_pipeline_tutorial.html)
- **Noise Reduction**: [noisereduce library](https://pypi.org/project/noisereduce/)

## Related Projects

This is the first in a series of repositories for audio/video processing and translation. Future projects will include transliteration and language translation capabilities.

---

**Project Maintainer:** [Dhruv16S](https://github.com/Dhruv16S)

For detailed technical documentation, see [CLAUDE.md](CLAUDE.md).
