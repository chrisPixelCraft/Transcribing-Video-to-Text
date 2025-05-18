import os
import sys
import subprocess
import whisper
from PIL import Image
import numpy as np

def create_blank_image(output_path, width=640, height=480):
    """Create a simple blank image with a dark background."""
    # Create a dark gray image
    img = np.zeros((height, width, 3), dtype=np.uint8) + 50
    img = Image.fromarray(img)
    img.save(output_path)
    return output_path

def convert_wav_to_mp4(wav_file, output_mp4=None):
    """Convert WAV file to MP4 with a static image."""
    if not os.path.exists(wav_file):
        print(f"Error: {wav_file} does not exist.")
        return None

    # Create directories if they don't exist
    os.makedirs("temp", exist_ok=True)
    os.makedirs("videos", exist_ok=True)

    # Default output file name
    if output_mp4 is None:
        base_name = os.path.splitext(os.path.basename(wav_file))[0]
        output_mp4 = f"videos/{base_name}.mp4"

    # Create a blank image
    image_path = "temp/blank.png"
    create_blank_image(image_path)

    # Use FFmpeg to convert wav to mp4
    try:
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", image_path,
            "-i", wav_file, "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
            "-shortest", output_mp4
        ]
        subprocess.run(cmd, check=True)
        print(f"Successfully converted {wav_file} to {output_mp4}")
        return output_mp4
    except subprocess.CalledProcessError as e:
        print(f"Error converting WAV to MP4: {e}")
        return None
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg.")
        return None

def transcribe_with_whisper(audio_file, language=None, output_filename=None):
    """Directly transcribe using Whisper model with language option."""
    try:
        # Load the Whisper model
        model = whisper.load_model("base")

        # Set transcription options
        options = {}
        if language:
            options["language"] = language

        # Perform transcription
        result = model.transcribe(audio_file, **options)

        # Save the transcription to output directory
        output_directory = "./output"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Use custom output filename if provided
        if output_filename:
            # Add .txt extension if not present
            if not output_filename.endswith('.txt'):
                output_filename += '.txt'
            output_file = f"{output_directory}/{output_filename}"
        else:
            output_file = f"{output_directory}/whisper_transcript.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["text"])

        return result["text"], output_file
    except Exception as e:
        print(f"Error transcribing with Whisper: {e}")
        return None, None

def main():
    # Define supported languages and their codes
    supported_languages = {
        "en": "English",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "fr": "French",
        "de": "German",
        "es": "Spanish",
        "ru": "Russian",
        "pt": "Portuguese",
        "ar": "Arabic",
        "hi": "Hindi",
        "it": "Italian"
    }

    # Parse command line arguments
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print("Usage: python wav_to_text.py <wav_file_path> [language_code] [output_filename]")
        print("\nSupported language codes:")
        for code, name in supported_languages.items():
            print(f"  {code} - {name}")
        print("\nExamples:")
        print("  python wav_to_text.py recording.wav zh")
        print("  python wav_to_text.py recording.wav zh my_transcript")
        return

    # Get wav file path
    wav_file = sys.argv[1]

    # Initialize language and output filename
    language = None
    output_filename = None

    # Check if language is specified
    if len(sys.argv) > 2:
        lang_code = sys.argv[2]
        if lang_code in supported_languages:
            language = lang_code
            print(f"Using language: {supported_languages[lang_code]}")
        else:
            print(f"Warning: Unsupported language code '{lang_code}'. Using auto-detection.")

    # Check if output filename is specified
    if len(sys.argv) > 3:
        output_filename = sys.argv[3]
        print(f"Using custom output filename: {output_filename}")

    # Convert WAV to MP4
    mp4_file = convert_wav_to_mp4(wav_file)
    if not mp4_file:
        print("Conversion failed. Exiting.")
        return

    # Start transcription process
    print("Starting transcription with Whisper...")
    cleaned_audio_path = './audio/cleaned/cleaned_audio.mp3'

    # First use the script to extract and preprocess audio
    try:
        # Run only audio extraction and preprocessing steps
        extract_cmd = ["./generate_transcripts.sh", mp4_file]
        subprocess.run(extract_cmd, check=True, text=True, capture_output=True)
        print("Audio extraction and preprocessing complete.")

        # Now use our custom transcription with language support
        if os.path.exists(cleaned_audio_path):
            transcript, output_file = transcribe_with_whisper(cleaned_audio_path, language, output_filename)
            if transcript:
                print(f"Transcription complete! Saved to {output_file}")
                print("\nTranscript preview:")
                print("-" * 40)
                preview = transcript[:200] + "..." if len(transcript) > 200 else transcript
                print(preview)
                print("-" * 40)
        else:
            print(f"Error: Cleaned audio file not found at {cleaned_audio_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during audio processing: {e}")
        if hasattr(e, 'stderr'):
            print(e.stderr)

if __name__ == "__main__":
    main()