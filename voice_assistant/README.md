# Voice-Activated Virtual Assistant

Minimal starter project integrating:
- Python (Flask)
- Google Cloud Speech-to-Text
- Dialogflow webhook
- SQLite for simple transcript storage

## Structure

- `app.py` - Flask app with `/transcribe` and `/webhook` endpoints
- `speech.py` - Google Cloud Speech-to-Text helper
- `db.py` - Simple SQLite helpers
- `examples/upload.sh` - Example curl script to upload audio

## Quick start

1. Create a Google Cloud service account with the Speech-to-Text API enabled and download the JSON key.
2. Set the credentials environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

3. Install dependencies (preferably inside a virtualenv):

```bash
pip install -r requirements.txt
```

4. Run the Flask app:

```bash
python app.py
```

5. Upload a WAV file (LINEAR16 PCM, 16kHz recommended):

```bash
./examples/upload.sh path/to/file.wav
```

## Offline transcription fallback

This project supports offline transcription using VOSK when `GOOGLE_APPLICATION_CREDENTIALS` is not set. The app will try Google Cloud Speech-to-Text first, then automatically fall back to VOSK if no credentials are available.

To use the offline fallback:

1. Install the dependencies:

```bash
pip install -r requirements.txt
```

2. Download a VOSK model, for example:

```bash
mkdir -p /tmp/vosk-model
cd /tmp
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d /tmp/vosk-model
```

3. Set `VOSK_MODEL_PATH` if you want a custom model location:

```bash
export VOSK_MODEL_PATH="/tmp/vosk-model/vosk-model-small-en-us-0.15"
```

4. Start the app and upload audio as above.

## Dialogflow

- Create a Dialogflow CX/ES agent (this project shows a simple webhook implementation compatible with Dialogflow ES fulfillment JSON).
- Configure the agent's fulfillment webhook to point to `http://<host>:5000/webhook`.

The webhook responds with a simple echo; extend `app.py` to handle intents and session logic.

## Notes

- `assistant.db` is created next to the Python files and is ignored by Git.
- This is a minimal starter: add auth, HTTPS, and robust audio handling for production.
