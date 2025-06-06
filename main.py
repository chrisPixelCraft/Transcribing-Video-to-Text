# For generating scripts through CLI. Find the transcript in the output folder.

from utils import load_wav2vec2_asr_model, transcribe_audio
import os
import sys
import whisper

output_directory = "./output"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

def create_transcript(transcript_method, language=None):
    cleaned_audio_path = './audio/cleaned/cleaned_audio.mp3'
    original_audio_path = './audio/original/audio_extracted.mp3'
    transcript = f'Speech to Text through {transcript_method}\n'
    output_file = f'{output_directory}/{transcript_method}_transcript.txt'

    if transcript_method == 'wav2vec':
        model_path = 'model.pth'
        model = load_wav2vec2_asr_model(model_path)

        audio_path = cleaned_audio_path
        temp = str(transcribe_audio(model, audio_path))
        temp = temp.replace("|", " ").title()
        transcript += f"Audio that has been cleaned: {temp}\n"

        audio_path = original_audio_path
        temp = str(transcribe_audio(model, audio_path))
        temp = temp.replace("|", " ").title()
        transcript += f"Audio that has not been cleaned: {temp}\n"

        return transcript, output_file

    try:
        model = whisper.load_model("base")
        # Set language if provided
        options = {}
        if language:
            options["language"] = language
            print(f"Using language: {language}")

        result = model.transcribe(cleaned_audio_path, **options)
    except:
        return "Error: Could not transcribe"
    return result["text"], output_file

# Get transcription method and language from command line arguments
transcript_method = sys.argv[1]
language = sys.argv[2] if len(sys.argv) > 2 else None

transcript, output_file = create_transcript(transcript_method, language)
with open(output_file, 'w+') as file:
    file.write(transcript)