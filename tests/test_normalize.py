import wave
import tempfile
import os
import math
import struct
import sys
import pytest

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from voice_assistant.utils import normalize_audio


def _create_stereo_wave(path, duration_seconds=1):
    framerate = 44100
    nchannels = 2
    sampwidth = 2
    nframes = framerate * duration_seconds

    with wave.open(path, 'wb') as wf:
        wf.setnchannels(nchannels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(framerate)
        for i in range(nframes):
            val = int(32767 * 0.1 * math.sin(2 * math.pi * 440 * i / framerate))
            data = struct.pack('<hh', val, val)
            wf.writeframesraw(data)


def test_normalize_audio():
    # skip if ffmpeg/pydub not available in environment
    try:
        from pydub.utils import which
    except Exception:
        pytest.skip('pydub not available')

    if which('ffmpeg') is None and which('avconv') is None:
        pytest.skip('ffmpeg/avconv not available; skipping normalization test')

    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, 'src.wav')
        out = os.path.join(td, 'out.wav')
        _create_stereo_wave(src)
        normalize_audio(src, out)

        with wave.open(out, 'rb') as wf:
            assert wf.getnchannels() == 1
            assert wf.getframerate() == 16000
            assert wf.getsampwidth() == 2
