#!/bin/bash
if [ "$#" -gt 3 ] || [ "$#" -eq 0 ]
then
    echo "Usage: $0 <path_to_audio_file> <transcription_method>(optional) <language_code>(optional)"
    echo "<transcription_method>: whisper or wav2vec"
    echo "<language_code>: en, zh, ja, ko, etc. (for whisper only)"
    exit 1
fi

if [ "$#" -eq 1 ]
then
    input_file="$1"
    python extract_audio.py "$input_file"
    python preprocess_audio.py
    echo "Preprocessing complete"
    python noise_removal.py
    echo "Noise removal complete"
else
    if [ "$2" != "whisper" ] && [ "$2" != "wav2vec" ]
    then
        printf "\nInvalid transcription method. Please choose 'whisper' or 'wav2vec'.\n"
        printf "Usage: $0 <path_to_audio_file> <transcription_method>(optional) <language_code>(optional)\n\n"
        exit 1
    else
        transcript_method="$2"
    fi

    input_file="$1"
    python extract_audio.py "$input_file"
    python preprocess_audio.py
    echo "Preprocessing complete"
    python noise_removal.py
    echo "Noise removal complete"

    # If language code is provided and method is whisper, use it
    if [ "$#" -eq 3 ] && [ "$2" == "whisper" ]
    then
        language_code="$3"
        python main.py "$transcript_method" "$language_code"
    else
        python main.py "$transcript_method"
    fi
    echo "Transcript generation complete"
fi