import os
from typing import Optional

# Try Google Cloud STT first if credentials exist, otherwise fall back to VOSK
def transcribe_file(path: str, language_code: str = 'en-US') -> str:
    """Transcribe a WAV file using Google Speech-to-Text if available, else VOSK.

    Expects LINEAR16 PCM WAV (16kHz mono) for best results.
    """
    # Prefer Google if credentials are set
    cred = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if cred:
        try:
            from google.cloud import speech

            client = speech.SpeechClient()
            with open(path, 'rb') as f:
                content = f.read()

            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
            )

            response = client.recognize(config=config, audio=audio)
            transcripts = [result.alternatives[0].transcript for result in response.results]
            if transcripts:
                return ' '.join(transcripts)
        except Exception:
            # fall through to VOSK fallback
            pass

    # VOSK fallback
    try:
        from offline_stt import transcribe_vosk

        return transcribe_vosk(path)
    except Exception as e:
        raise RuntimeError(f"No STT available: {e}")
