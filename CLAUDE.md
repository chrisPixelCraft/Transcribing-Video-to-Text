# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a video-to-text transcription system that extracts audio from video files, applies noise reduction, and converts speech to text using AI models (Whisper or Wav2Vec2). It supports both CLI and web interfaces with multilingual transcription capabilities.

## Environment Setup

### Activate Environment

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

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Install PyTorch
Required for Wav2Vec2 model. Install the appropriate version for your system from [pytorch.org](https://pytorch.org/get-started/locally/). Example for CUDA 12.1:
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### System Dependencies
- **FFmpeg** is required for audio processing and format conversions. Install via:
  - Linux: `sudo apt-get install ffmpeg`
  - Mac: `brew install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Setup Project Directories
```bash
mkdir videos  # Required for video file inputs
mkdir Audio   # Required for batch M4A processing
```

## Common Commands

### CLI Transcription

**Audio extraction only (no transcription):**
```bash
./generate_transcripts.sh ./videos/input_video.mp4
```

**Full transcription with Whisper (auto-detect language):**
```bash
./generate_transcripts.sh ./videos/input_video.mp4 whisper
```

**Full transcription with Whisper (specific language):**
```bash
./generate_transcripts.sh ./videos/input_video.mp4 whisper zh
```

**Full transcription with Wav2Vec2:**
```bash
./generate_transcripts.sh ./videos/input_video.mp4 wav2vec
```

**Note:** Before using Wav2Vec2, you must run `model.ipynb` to train/prepare the model.

### Audio-Only Transcription

**Process M4A files:**
```bash
python m4a_to_text.py recording.m4a [language_code] [output_filename]
# Example: python m4a_to_text.py recording.m4a zh my_transcript
```

**Process WAV files:**
```bash
python wav_to_text.py recording.wav [language_code] [output_filename]
# Example: python wav_to_text.py recording.wav ja my_transcript
```

**Batch process all M4A files in Audio/ directory:**
```bash
./batch_m4a_to_text.sh [language_code]
# Example with default Chinese: ./batch_m4a_to_text.sh
# Example with English: ./batch_m4a_to_text.sh en
```
This script automatically processes all .m4a files in the Audio/ folder, generates transcripts with filenames based on the original audio files, and provides progress tracking.

### Web Application

**Start the Flask development server:**
```bash
python app.py
```
Access at: `http://localhost:5000/`

**Production deployment:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Architecture

### Processing Pipeline (Sequential)

The transcription process follows this sequential pipeline:

1. **extract_audio.py** - Extracts audio stream from MP4 video using MoviePy
   - Output: `./audio/original/audio_extracted.mp3`

2. **preprocess_audio.py** - Normalizes audio and generates visualizations
   - Uses librosa for audio analysis
   - Output: Normalized audio + graphs in `./graphs/original/`

3. **noise_removal.py** - Removes background noise using spectral gating
   - Uses noisereduce library
   - Output: `./audio/cleaned/cleaned_audio.mp3` + visualizations

4. **main.py** - Transcribes audio to text
   - Dispatches to either Wav2Vec2 or Whisper model
   - Output: `./output/{method}_transcript.txt`

### Dual Interface Pattern

**CLI Interface:**
- Entry point: `generate_transcripts.sh`
- Orchestrates entire pipeline via shell script
- Supports batch processing and automation
- Audio-specific converters: `m4a_to_text.py`, `wav_to_text.py`

**Web Interface:**
- Entry point: `app.py`
- Flask server with HTML frontend
- Routes: `/` (upload), `/generate` (process), `/download` (zip results)
- User-friendly for single-file processing

### Model Selection Architecture

**Wav2Vec2:**
- PyTorch-based model with GPU acceleration
- Requires pre-training via `model.ipynb`
- Model file: `model.pth`
- Loader: `utils.py` (contains `load_wav2vec2_asr_model()` and `transcribe_audio()`)

**Whisper (OpenAI):**
- Default model: "large-v3" (~2.9GB, downloads on first use)
- Supports multilingual auto-detection
- Can specify language explicitly for better accuracy
- No pre-training required
- Optimized for technical terminology and code-switching (mixed language content)

### Integration Points (Key File Locations)

**Whisper Model Loading:**
- `main.py:37` - CLI transcription with language option
- `app.py:60` - Web app transcription (no language option)
- `m4a_to_text.py:62` - M4A audio transcription
- `wav_to_text.py:62` - WAV audio transcription

**Wav2Vec2 Model:**
- `utils.py` - Complete implementation with `load_wav2vec2_asr_model()` and `transcribe_audio()`
- `main.py:18-32` - CLI integration
- Model file: `model.pth` (must be trained via `model.ipynb`)

**Audio Visualization:**
- `plots.py:6` - `plot_audio()` - Generates waveform plots
- `plots.py:15` - `plot_spectrogram()` - Generates mel-spectrogram visualizations
- Used by: `preprocess_audio.py`, `noise_removal.py`

**FFmpeg Conversion:**
- `m4a_to_text.py:37-43` - M4A to MP4 conversion command
- `wav_to_text.py:37-43` - WAV to MP4 conversion command
- Creates `temp/blank.png` (800x600 black image) combined with audio

### File Organization Patterns

**Inputs:**
- `./videos/` - Video files (MP4)
- Direct file paths for audio files (M4A, WAV)

**Processing Artifacts:**
- `./audio/original/` - Extracted raw audio
- `./audio/cleaned/` - Noise-reduced audio
- `./graphs/` - Audio visualizations (spectrograms, waveforms)
- `./temp/` - Temporary files (e.g., blank images for audio-to-video conversion)

**Outputs:**
- `./output/` - Transcript files (TXT)
- Web app: `./static/audio/` (moved during processing)

## Multilingual Support

### Supported Languages (Whisper Only)
- `en` - English
- `zh` - Chinese
- `ja` - Japanese
- `ko` - Korean
- `fr` - French
- `de` - German
- `es` - Spanish
- `ru` - Russian
- `pt` - Portuguese
- `ar` - Arabic
- `hi` - Hindi
- `it` - Italian

### Language Usage
- Specify language code as parameter: `whisper zh`
- Auto-detection if no language specified
- Language parameter only applies to Whisper, not Wav2Vec2

## Key Technical Notes

### Audio Format Conversion

M4A/WAV files are converted to MP4 using FFmpeg before processing:

**Conversion Process:**
1. Create blank 800x600 black PNG image (`temp/blank.png`)
2. Combine static image with audio using FFmpeg:
   ```bash
   ffmpeg -y -loop 1 -i temp/blank.png \
          -i audio.m4a \
          -c:v libx264 -tune stillimage \
          -c:a aac -b:a 192k \
          -pix_fmt yuv420p \
          -shortest output.mp4
   ```
3. Process resulting MP4 through standard video pipeline
4. Extract audio (identical to original M4A/WAV)

**Why this approach?**
- Enables code reuse of video-centric pipeline
- Ensures identical audio processing for all input formats
- Avoids duplicating extraction/preprocessing/noise-removal logic

### Model Loading
- Whisper model is loaded on-demand: `whisper.load_model("large-v3")`
- Whisper models download to: `~/.cache/whisper/` (Linux/Mac) or `%USERPROFILE%\.cache\whisper\` (Windows)
- large-v3 model size: ~2.9GB (downloads on first use, subsequent runs use cached model)
- Wav2Vec2 requires pre-trained model file at `model.pth`
- Models use GPU if available (via PyTorch CUDA detection)

### Web App Behavior
- Automatically cleans up uploaded videos after processing
- Moves audio files to `./static/` for web access
- Download endpoint packages all outputs into ZIP file
- Cleanup removes `./videos/`, `./output/`, `./static/audio/` after download

### Noise Reduction
- Uses spectral gating algorithm from `noisereduce` library
- Operates on both original and cleaned audio for comparison
- Visualizations help verify quality of noise reduction

## Common Issues

### FFmpeg Not Found
**Error:** `Error: ffmpeg not found. Please install ffmpeg.`

**Solution:** Install FFmpeg for your system:
- Linux: `sudo apt-get install ffmpeg`
- Mac: `brew install ffmpeg`
- Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### Whisper Model Download Failures
**Error:** Model download times out or fails

**Solution:**
- Check internet connection
- Manually download from [Hugging Face](https://huggingface.co/openai/whisper-large-v3)
- Place in `~/.cache/whisper/large-v3.pt`

### Wav2Vec2 Model Missing
**Error:** `model.pth` not found

**Solution:** Run `model.ipynb` notebook to train/prepare the Wav2Vec2 model before use

### Audio Directory Errors
**Error:** Directory not found during batch processing

**Solution:** Create required directories:
```bash
mkdir -p videos Audio audio/original audio/cleaned graphs/original graphs/cleaned output temp
```

### Memory Issues with Whisper
**Error:** Out of memory during transcription

**Solution:**
- Use smaller model: `whisper.load_model("base")` or `"medium"`
- Process shorter audio segments
- Ensure sufficient RAM (4GB+ recommended for large-v3)

## Important Constraints

1. **FFmpeg Dependency**: Critical for audio extraction and format conversions. System must have FFmpeg installed.

2. **Wav2Vec2 Setup**: Model must be trained/prepared using `model.ipynb` before use. Missing `model.pth` will cause failures.

3. **Directory Structure**: Pipeline expects specific directory structure. Missing directories are created automatically.

4. **File Size Limits**: Web app limits uploads to 16MB (configurable in `app.py:44`).
   - Change limit: `app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024`
   - Value is in bytes (current: 16 * 1024 * 1024 = 16MB)

5. **Audio File Conversion**: M4A and WAV processors convert files to MP4 internally before using the main pipeline.
