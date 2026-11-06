"""The narrator: Kokoro (82M parameters, ONNX on the CPU) reads each shot's line.

The narrator's voice reads the narration, identical across the whole video (the skill's narrator
lock, for free); in a story with character voices each character's lines are read in their own
voice. Each shot's audio length sets how long the shot stays on screen.
"""

import subprocess
import threading
import wave

import numpy as np

from . import models, paths, styles

SAMPLE_RATE = 24000

_kokoro = None
_lock = threading.Lock()


def _engine():
    global _kokoro
    with _lock:
        if _kokoro is None:
            from kokoro_onnx import Kokoro

            _kokoro = Kokoro(str(models.path("kokoro")), str(models.path("kokoro-voices")))
        return _kokoro


def _repitch(samples: np.ndarray, rate: int, factor: float) -> np.ndarray:
    """The voice played `factor` times faster (higher, shorter), resampled back to `rate` by ffmpeg's
    resampler: plain interpolation would dull the voice."""
    raw = subprocess.run(
        [paths.ffmpeg(), "-loglevel", "error", "-f", "f32le", "-ar", str(rate), "-ac", "1", "-i", "-",
         "-af", f"asetrate={rate * factor:.2f},aresample={rate}", "-f", "f32le", "-ac", "1", "-"],
        input=samples.astype(np.float32).tobytes(), capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def _speak_cloud(text: str, voice: str, speed: float, out_path, mood: dict) -> float:
    """A cloud voice: it's told the emotion (and the pace, if it isn't normal) in words."""
    from . import cloud

    instruction = mood["say"] + (" Speak a little slowly." if speed < 0.95 else " Speak a little briskly." if speed > 1.05 else "")
    wav = cloud.speak(text, voice.partition(":")[2], instruction)
    with open(out_path, "wb") as f:
        f.write(wav)
    return len(read_wav(out_path)) / SAMPLE_RATE


def speak(text: str, voice: str, speed: float, out_path, emotion: str = "neutral") -> float:
    """Writes the narration to a 24 kHz mono WAV and returns its length in seconds."""
    if not styles.voice_ok(voice):
        raise ValueError(f"Unknown voice: {voice}")
    mood = styles.EMOTIONS.get(emotion, styles.EMOTIONS["neutral"])
    if styles.is_cloud_voice(voice):
        return _speak_cloud(text, voice, speed, out_path, mood)
    pitch = 2 ** (mood["pitch"] / 12)
    samples, rate = _engine().create(text, voice=voice, speed=speed * mood["speed"] / pitch, lang=styles.speech_lang(voice))
    samples = np.asarray(samples, dtype=np.float32)
    if abs(pitch - 1) > 1e-3 and len(samples) > 1:
        samples = _repitch(samples, rate, pitch)
    samples = np.clip(samples * mood["gain"], -1.0, 1.0)
    pcm = (samples * 32767).astype(np.int16)
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
    return len(pcm) / rate


def read_wav(path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        if w.getframerate() != SAMPLE_RATE or w.getnchannels() != 1:
            raise ValueError(f"Unexpected audio format in {path}")
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)


SAMPLE_VERSION = 1


def sample(voice: str, emotion: str = "neutral") -> str:
    """A short sample of a voice (in an emotion), for the preview button: made once, then cached."""
    if voice not in styles.VOICES:
        raise ValueError(f"Unknown voice: {voice}")
    if emotion not in styles.EMOTIONS:
        raise ValueError(f"Unknown emotion: {emotion}")
    folder = paths.data_dir() / "voice-samples"
    folder.mkdir(exist_ok=True)
    path = folder / f"{voice}-{emotion}-v{SAMPLE_VERSION}.wav"
    if not path.exists():
        partial = path.with_suffix(".part")
        speak(styles.SAMPLE_TEXT[styles.voice_language(voice) if styles.voice_language(voice) != "*" else "en"], voice, 1.0, partial, emotion)
        partial.replace(path)
    return str(path)
