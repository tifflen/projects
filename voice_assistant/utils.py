import os


def normalize_audio(input_path: str, output_path: str, target_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> str:
    """Normalize/convert audio to WAV PCM 16kHz mono 16-bit.

    Uses pydub (ffmpeg) under the hood. Imports pydub locally so callers
    can choose to handle environments without pydub available.
    """
    from pydub import AudioSegment

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(target_rate).set_channels(channels).set_sample_width(sample_width)
    # Ensure output directory exists
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    audio.export(output_path, format="wav")
    return output_path
