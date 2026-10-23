# Transcribing Video to Text

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Turn video or audio into text with Whisper (default) or Wav2Vec2.

- Inputs: MP4, M4A, WAV, YouTube (via `yt-dlp`)
- Pipeline: extract audio → normalize → denoise → transcribe
- Interfaces: CLI scripts and a Flask web app
- Languages: 12 for Whisper; English only for Wav2Vec2

## Quick Start

```bash
git clone https://github.com/Dhruv16S/Transcribing-Video-to-Text.git
cd Transcribing-Video-to-Text
source /root/miniconda3/bin/activate video_transcribe
pip install -r requirements.txt
mkdir -p videos Audio

./generate_transcripts.sh ./videos/my_video.mp4 whisper    # first run downloads large-v3
```

## Which Command Should I Use?

| Input | Command | Output |
|---|---|---|
| M4A / WebM audio (fastest) | `python direct_m4a_to_text.py <file> [lang] [name]` | `output/<name>.txt` |
| MP4 video | `./generate_transcripts.sh <file> whisper [lang]` | `output/whisper_transcript.txt` |
| M4A via video pipeline | `python m4a_to_text.py <file> [lang] [name]` | `output/<name>.txt` |
| WAV | `python wav_to_text.py <file> [lang] [name]` | `output/<name>.txt` |
| All M4A in `Audio/` | `./batch_m4a_to_text.sh [lang]` | `output/<audio_name>.txt` |
| YouTube URL list | edit `urls` in `quick_run.sh`, then `./quick_run.sh` | `output/<title>.txt` |
| Browser upload | `python app.py` → `http://localhost:5000/` | ZIP download |

- `lang` is optional; omit it to auto-detect
	- Mixed Chinese + English speech: use `zh`
- `direct_m4a_to_text.py` skips video conversion
	- Also accepts `--model`, `--device`, `--output-dir`

## Installation

### Requirements

- Python 3.8+ (3.10+ recommended for `yt-dlp`)
- FFmpeg
- 4GB+ RAM for Whisper `large-v3`
- Internet on first run (model download, ~2.9GB)

### Steps

```bash
# 1. Environment (pick one)
source /root/miniconda3/bin/activate video_transcribe
# or
virtualenv env && source env/bin/activate

# 2. Python packages
pip install -r requirements.txt

# 3. PyTorch — pick the build for your system: https://pytorch.org/get-started/locally/
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121   # CUDA 12.1
pip3 install torch torchvision torchaudio                                                    # CPU only

# 4. FFmpeg
sudo apt-get install ffmpeg      # Linux
brew install ffmpeg              # Mac
# Windows: download from https://ffmpeg.org/download.html and add to PATH

# 5. Working directories
mkdir -p videos Audio
```

## Usage

### YouTube

The repo does not take YouTube URLs directly. Download first with `yt-dlp`, then transcribe.

```bash
# Install / update yt-dlp (old versions break often)
python -m pip install -U --pre "yt-dlp[default,curl-cffi]"
```

**Audio only (recommended):**

```bash
yt-dlp --force-ipv4 --impersonate chrome \
  -f "bestaudio[ext=m4a]/bestaudio/best" -x --audio-format m4a \
  -o "Audio/youtube_audio.%(ext)s" \
  "https://www.youtube.com/watch?v=pWmXczxLlxY"

python direct_m4a_to_text.py "Audio/youtube_audio.m4a" zh youtube_transcript
# → output/youtube_transcript.txt
```

**Full video:**

```bash
yt-dlp --force-ipv4 --impersonate chrome \
  -f "bv*+ba/best" --merge-output-format mp4 \
  -o "videos/youtube_video.%(ext)s" \
  "https://www.youtube.com/watch?v=pWmXczxLlxY"

./generate_transcripts.sh "videos/youtube_video.mp4" whisper
# → output/whisper_transcript.txt
```

**Shortest form (default filename):**

```bash
yt-dlp --force-ipv4 --impersonate chrome "https://www.youtube.com/watch?v=xiompYe8tbM"
python direct_m4a_to_text.py "影片檔名.webm" zh
```

**If download fails with `nsig extraction failed` or `Only images are available`:**

```bash
# Install Deno (JS runtime for yt-dlp's EJS challenge solver)
curl -fsSL https://deno.land/install.sh | sh
export PATH="$HOME/.deno/bin:$PATH"

python -m pip install -U --pre "yt-dlp[default,curl-cffi]"
yt-dlp --force-ipv4 --impersonate chrome \
  --remote-components ejs:github \
  -f "bestaudio[ext=m4a]/bestaudio/best" -x --audio-format m4a \
  -o "Audio/youtube_audio.%(ext)s" \
  "https://www.youtube.com/watch?v=pWmXczxLlxY"
```

- Still warnings on Python 3.8? Use a separate download env:

```bash
conda create -n ytdlp python=3.11 -y
conda activate ytdlp
python -m pip install -U --pre "yt-dlp[default,curl-cffi]"
```

- Switch back to the transcription env before running `direct_m4a_to_text.py`

### Video (MP4)

```bash
./generate_transcripts.sh ./videos/lecture.mp4                 # extract audio only
./generate_transcripts.sh ./videos/lecture.mp4 whisper         # auto-detect language
./generate_transcripts.sh ./videos/lecture.mp4 whisper zh      # Chinese (or ja, en, ...)
./generate_transcripts.sh ./videos/lecture.mp4 wav2vec         # needs model.pth from model.ipynb
```

| Output | Path |
|---|---|
| Extracted audio | `audio/original/audio_extracted.mp3` |
| Cleaned audio | `audio/cleaned/cleaned_audio.mp3` |
| Transcript | `output/whisper_transcript.txt` |
| Graphs | `graphs/original/`, `graphs/cleaned/` |

### Audio (M4A / WAV)

```bash
python direct_m4a_to_text.py recording.m4a zh lecture    # direct, no video conversion
python m4a_to_text.py        recording.m4a en meeting    # via video pipeline
python wav_to_text.py        recording.wav ja interview  # via video pipeline
```

- `m4a_to_text.py` / `wav_to_text.py` convert audio to MP4 first
	- Lets them reuse the denoise pipeline
	- Slower than `direct_m4a_to_text.py`

### Batch

```bash
./batch_m4a_to_text.sh        # all Audio/*.m4a, default zh
./batch_m4a_to_text.sh en
```

- Transcript name follows each audio filename
- Prints progress and success / failure counts

### Web App

```bash
python app.py                              # dev: http://localhost:5000/
gunicorn -w 4 -b 0.0.0.0:5000 app:app      # production
```

- Upload, transcribe, play original vs. cleaned audio
- Results download as ZIP
	- Files are cleaned up after download
- Limits
	- MP4 only
	- 16MB max (`app.py:44`)

## Architecture

```
Input (MP4 / M4A / WAV)
  │
  ├─ extract_audio.py      extract audio; M4A/WAV first converted to MP4
  ├─ preprocess_audio.py   normalize levels, waveform graphs
  ├─ noise_removal.py      spectral gating (noisereduce), spectrograms
  └─ main.py               Whisper large-v3 or Wav2Vec2
  │
Output: transcript TXT + MP3 audio + PNG graphs
```

`direct_m4a_to_text.py` skips the first three steps and calls Whisper directly.

```
Transcribing-Video-to-Text/
├── videos/      input MP4
├── Audio/       input M4A for batch
├── audio/       original/ and cleaned/ extracted audio
├── graphs/      original/ and cleaned/ visualizations
├── output/      transcripts
├── temp/        conversion scratch files
└── static/      web assets and playback audio
```

## Configuration

### Models

| | Whisper (default) | Wav2Vec2 |
|---|---|---|
| Model | `large-v3` (~2.9GB) | `model.pth` in repo root |
| Setup | auto-download to `~/.cache/whisper/` | train via `model.ipynb` |
| Languages | 12, auto-detect or explicit | English only |
| Used by | `main.py`, `app.py`, `*_to_text.py` | `main.py` |

**Smaller Whisper model** (less memory, lower accuracy):

```python
model = whisper.load_model("large-v3")   # default
model = whisper.load_model("medium")     # balanced
model = whisper.load_model("base")       # fastest
```

- `direct_m4a_to_text.py` takes `--model medium` instead of a code edit

### Languages (Whisper)

| Code | Language | Code | Language |
|---|---|---|---|
| `en` | English | `fr` | French |
| `zh` | Chinese | `de` | German |
| `ja` | Japanese | `es` | Spanish |
| `ko` | Korean | `ru` | Russian |
| `pt` | Portuguese | `ar` | Arabic |
| `hi` | Hindi | `it` | Italian |

- Auto-detect works but can be less accurate
- Explicit code helps mixed-language audio

### Web Upload Limit

```python
# app.py:44 — value in bytes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024    # 16MB default
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Error: ffmpeg not found` | Install FFmpeg (see [Installation](#installation)) |
| Whisper download fails | • Check network<br>• Download from [Hugging Face](https://huggingface.co/openai/whisper-large-v3)<br>• Put at `~/.cache/whisper/large-v3.pt` |
| Out of memory | • Use `medium` or `base`<br>• Split long audio<br>• Need 4GB+ RAM |
| Directory not found | Run the `mkdir -p` below |
| YouTube `nsig` / images only | See [YouTube](#youtube) fix |

```bash
mkdir -p videos Audio audio/original audio/cleaned graphs/original graphs/cleaned output temp
```

More details: [CLAUDE.md](CLAUDE.md#common-issues).

## Contributing

1. Fork and clone the repo
2. Create a virtual environment and install dependencies
3. Test with several file types and languages
4. Open a pull request

Open areas: more formats, better denoising, real-time transcription, speaker diarization, translation, performance, docs.

## License & Credits

- MIT License — see `LICENSE`
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Wav2Vec2 (torchaudio)](https://pytorch.org/audio/stable/tutorials/speech_recognition_pipeline_tutorial.html)
- [noisereduce](https://pypi.org/project/noisereduce/)

Maintainer: [Dhruv16S](https://github.com/Dhruv16S). First in a series on audio/video processing and translation.
