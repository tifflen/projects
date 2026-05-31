#!/bin/bash
# Example: Upload a WAV file to the local transcribe endpoint
# Usage: ./upload.sh path/to/file.wav

if [ -z "$1" ]; then
  echo "Usage: $0 path/to/file.wav"
  exit 1
fi

FILE="$1"
curl -X POST -F "audio=@${FILE}" http://localhost:5000/transcribe
