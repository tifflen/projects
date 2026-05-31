import wave
import json
from vosk import Model, KaldiRecognizer
import os


def transcribe_vosk(path, model_path=None):
    """Transcribe WAV (16kHz mono PCM) using VOSK offline model.

    model_path: directory containing VOSK model. If None, uses environment
    variable `VOSK_MODEL_PATH` or `/tmp/vosk-model/*`.
    """
    if model_path is None:
        model_path = os.environ.get('VOSK_MODEL_PATH', '/tmp/vosk-model/vosk-model-small-en-us-0.15')

    if not os.path.isdir(model_path):
        raise FileNotFoundError(f"VOSK model not found at {model_path}")

    wf = wave.open(path, 'rb')
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError('Audio file must be WAV 16kHz mono 16-bit PCM')

    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())

    texts = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            if res.get('text'):
                texts.append(res['text'])

    final = json.loads(rec.FinalResult())
    if final.get('text'):
        texts.append(final['text'])

    return ' '.join(texts)
