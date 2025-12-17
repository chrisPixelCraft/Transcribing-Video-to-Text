#!/bin/bash

# Batch process all M4A files in the Audio/ directory
# Usage: ./batch_m4a_to_text.sh [language_code]
# Default language is Chinese (zh)

# Set language code (default to Chinese)
LANG_CODE="${1:-zh}"

# Check if Audio directory exists
if [ ! -d "Audio" ]; then
    echo "Error: Audio/ directory not found in current directory"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Count total m4a files
total_files=$(find Audio -type f -name "*.m4a" | wc -l)

if [ "$total_files" -eq 0 ]; then
    echo "No .m4a files found in Audio/ directory"
    exit 0
fi

echo "=========================================="
echo "Batch M4A to Text Transcription"
echo "=========================================="
echo "Found $total_files .m4a file(s) to process"
echo "Language: $LANG_CODE"
echo "=========================================="
echo ""

# Counter for progress tracking
current=0
success=0
failed=0

# Build array of all m4a files to avoid stdin consumption by subprocess
mapfile -t m4a_files < <(find Audio -type f -name "*.m4a")

# Process each m4a file using array iteration (not stdin reading)
# This prevents subprocess calls from consuming stdin and stopping the loop
for m4a_file in "${m4a_files[@]}"; do
    current=$((current + 1))

    # Extract filename without path and extension
    filename=$(basename "$m4a_file")
    filename_no_ext="${filename%.m4a}"

    echo "[$current/$total_files] Processing: $filename"
    echo "  Input:  $m4a_file"
    echo "  Output: output/${filename_no_ext}_transcript.txt"
    echo "----------------------------------------"

    # Run m4a_to_text.py with language code and output filename
    if python m4a_to_text.py "$m4a_file" "$LANG_CODE" "${filename_no_ext}_transcript"; then
        echo "✓ Success: $filename"
        success=$((success + 1))
    else
        echo "✗ Failed: $filename"
        failed=$((failed + 1))
    fi

    echo ""
done

echo "=========================================="
echo "Batch Processing Complete"
echo "=========================================="
echo "Total: $total_files files"
echo "Success: $success files"
echo "Failed: $failed files"
echo ""
echo "Transcripts saved to: ./output/"
echo "=========================================="
