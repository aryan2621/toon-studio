"""The soundtrack: a music bed, transition whooshes, and the final mix under the narration.

The music is composed here rather than shipped as files: a few chords played by a soft pad, a
plucked arpeggio and a low bass, with a little echo. It's quiet background texture, there so the
pauses between lines never fall into dead silence, and it ducks whenever the narrator speaks.
Everything is generated with numpy at 48 kHz stereo; ffmpeg only encodes the result.
"""

import subprocess

import numpy as np

from . import paths

RATE = 48000

MOODS = {
    "curious": {"bpm": 84, "chords": [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]},
    "calm": {"bpm": 68, "chords": [[48, 52, 55, 59], [45, 48, 52, 55], [53, 57, 60, 64], [55, 59, 62, 65]]},
    "uplifting": {"bpm": 100, "chords": [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]]},
    "lofi": {
        "bpm": 76, "chords": [[48, 52, 55, 59], [45, 48, 52, 55], [50, 53, 57, 60], [43, 47, 50, 53]],
        "pad": 0.03, "arp": "keys", "arp_gain": 0.07, "arp_pattern": [0, 2, 1, 3, 2, 1, 3, 2], "drums": "lofi", "swing": 0.2, "vinyl": 0.012,
    },
    "cinematic": {
        "bpm": 60, "chords": [[45, 48, 52], [41, 45, 48], [48, 52, 55], [43, 47, 50]],
        "pad": 0.085, "bass": 0.14, "arp": "none", "drums": "boom", "drone": 0.05,
    },
    "suspense": {
        "bpm": 72, "chords": [[45, 48, 51], [44, 47, 50], [45, 48, 51], [43, 46, 49]],
        "pad": 0.035, "bass": 0.1, "arp": "bell", "arp_gain": 0.03, "arp_step": 2.0, "arp_pattern": [2, 0], "drums": "heartbeat", "drone": 0.06,
    },
    "upbeat": {
        "bpm": 118, "chords": [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]],
        "pad": 0.035, "bass_style": "pulse", "arp_gain": 0.05, "drums": "four",
    },
    "playful": {
        "bpm": 108, "chords": [[53, 57, 60], [48, 52, 55], [50, 53, 57], [58, 62, 65]],
        "pad": 0.025, "bass_style": "staccato", "arp": "bell", "arp_gain": 0.06, "arp_pattern": [0, 2, 1, 2, 0, 2, 1, 2], "drums": "soft",
    },
    "chiptune": {
        "bpm": 124, "chords": [[57, 60, 64], [55, 59, 62], [53, 57, 60], [52, 56, 59]],
        "pad": 0.0, "bass_style": "pulse", "arp": "square", "arp_gain": 0.05, "arp_step": 0.25, "arp_pattern": [0, 1, 2, 1], "drums": "four",
    },
    "dreamy": {
        "bpm": 62, "chords": [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]],
        "pad": 0.06, "arp": "bell", "arp_gain": 0.05, "arp_step": 1.0, "arp_pattern": [3, 2, 1, 2],
    },
    "sad": {
        "bpm": 58, "chords": [[57, 60, 64], [50, 53, 57], [53, 57, 60], [52, 56, 59]],
        "pad": 0.03, "bass": 0.09, "arp": "keys", "arp_gain": 0.07, "arp_step": 1.0, "arp_pattern": [0, 1, 2, 1],
    },
}
_DEFAULTS = {"pad": 0.05, "bass": 0.12, "bass_style": "sustain", "arp": "pluck", "arp_gain": 0.045, "arp_step": 0.5,
             "drums": None, "swing": 0.0, "vinyl": 0.0, "drone": 0.0}
DRUMS = {
    "lofi": {"kick": [0, 5], "snare": [2, 6], "hat": [0, 1, 2, 3, 4, 5, 6, 7]},
    "four": {"kick": [0, 2, 4, 6], "snare": [2, 6], "hat": [1, 3, 5, 7]},
    "soft": {"hat": [1, 3, 5, 7], "kick": [0]},
    "heartbeat": {"kick": [0, 1]},
    "boom": {"kick": [0]},
}


def _hz(note: float) -> float:
    return 440.0 * 2 ** ((note - 69) / 12)


def _envelope(n: int, attack: float, release: float) -> np.ndarray:
    env = np.ones(n, dtype=np.float32)
    a, r = min(n, int(attack * RATE)), min(n, int(release * RATE))
    if a:
        env[:a] = np.linspace(0, 1, a, dtype=np.float32)
    if r:
        env[n - r:] *= np.linspace(1, 0, r, dtype=np.float32)
    return env


def _pad(freq: float, n: int, detune: float) -> np.ndarray:
    """A soft, warm tone: a few odd and even harmonics falling away quickly (a filtered saw)."""
    t = np.arange(n, dtype=np.float32) / RATE
    f = freq * (1 + detune)
    wave = sum(np.sin(2 * np.pi * f * k * t) / (k ** 1.6) for k in range(1, 6))
    return (wave * _envelope(n, 0.8, 1.0)).astype(np.float32)


def _pluck(freq: float, n: int) -> np.ndarray:
    t = np.arange(n, dtype=np.float32) / RATE
    wave = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)
    return (wave * np.exp(-t / 0.28) * _envelope(n, 0.004, 0.05)).astype(np.float32)


def _echo(stereo: np.ndarray) -> np.ndarray:
    """A small room: a few delayed, quieter copies bouncing between the channels."""
    out = stereo.copy()
    for delay, gain in ((0.19, 0.32), (0.31, 0.22), (0.47, 0.14), (0.71, 0.08)):
        d = int(delay * RATE)
        out[d:, 0] += gain * stereo[:-d, 1]
        out[d:, 1] += gain * stereo[:-d, 0]
    return out


def _keys(freq: float, n: int) -> np.ndarray:
    """A soft electric-piano note: a fundamental and one overtone, plucked and fading."""
    t = np.arange(n, dtype=np.float32) / RATE
    wave = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t) * np.exp(-t / 0.15)
    return (wave * np.exp(-t / 0.45) * _envelope(n, 0.006, 0.08)).astype(np.float32)


def _bell(freq: float, n: int) -> np.ndarray:
    """A glassy bell: inharmonic partials ringing out."""
    t = np.arange(n, dtype=np.float32) / RATE
    wave = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t / 0.2) + 0.25 * np.sin(2 * np.pi * freq * 5.4 * t) * np.exp(-t / 0.08)
    return (wave * np.exp(-t / 0.7) * _envelope(n, 0.003, 0.1)).astype(np.float32)


def _square(freq: float, n: int) -> np.ndarray:
    """A short chiptune blip: a quarter-width pulse wave."""
    t = np.arange(n, dtype=np.float32) / RATE
    wave = np.where((t * freq) % 1.0 < 0.25, 1.0, -1.0).astype(np.float32)
    return (wave * np.exp(-t / 0.12) * _envelope(n, 0.002, 0.02)).astype(np.float32)


def _kick(volume: float = 1.0) -> np.ndarray:
    n = int(0.3 * RATE)
    t = np.arange(n, dtype=np.float32) / RATE
    return (np.sin(2 * np.pi * (45 + 90 * np.exp(-t / 0.04)) * t) * np.exp(-t / 0.13) * volume).astype(np.float32)


def _snare(volume: float = 1.0) -> np.ndarray:
    n = int(0.2 * RATE)
    t = np.arange(n, dtype=np.float32) / RATE
    noise = np.random.default_rng(7).standard_normal(n).astype(np.float32)
    return ((noise * 0.8 + np.sin(2 * np.pi * 190 * t)) * np.exp(-t / 0.07) * volume).astype(np.float32)


def _hat(volume: float = 1.0) -> np.ndarray:
    n = int(0.06 * RATE)
    noise = np.random.default_rng(11).standard_normal(n + 1).astype(np.float32)
    return (np.diff(noise) * np.exp(-np.arange(n, dtype=np.float32) / RATE / 0.018) * volume).astype(np.float32)


def _place(out: np.ndarray, sound: np.ndarray, at: int, gain: float, pan: float = 0.5):
    n = min(len(sound), len(out) - at)
    if n > 0:
        out[at:at + n, 0] += sound[:n] * gain * (1 - pan) * 2
        out[at:at + n, 1] += sound[:n] * gain * pan * 2


def music(mood: str, seconds: float) -> np.ndarray:
    """A music bed `seconds` long (stereo float32), fading in and out."""
    spec = {**_DEFAULTS, **MOODS[mood]}
    beat = 60 / spec["bpm"]
    bar = 4 * beat
    total = int(seconds * RATE) + 1
    out = np.zeros((total, 2), dtype=np.float32)
    bar_n = int(bar * RATE)
    eighth_n = int(beat / 2 * RATE)
    note = {"pluck": _pluck, "keys": _keys, "bell": _bell, "square": _square}.get(spec["arp"])
    drums = DRUMS.get(spec["drums"], {})
    kick, snare, hat = _kick(), _snare(), _hat()
    if spec["drone"]:
        out += spec["drone"] * _pad(_hz(MOODS[mood]["chords"][0][0] - 36), total, 0)[:, None]
    for b in range(int(seconds / bar) + 2):
        chord = spec["chords"][b % len(spec["chords"])]
        start = int(b * bar * RATE)
        if start >= total:
            break
        length = min(bar_n + int(0.9 * RATE), total - start)
        if spec["pad"]:
            for n_ in chord:
                out[start:start + length, 0] += spec["pad"] * _pad(_hz(n_), length, -0.0018)
                out[start:start + length, 1] += spec["pad"] * _pad(_hz(n_), length, 0.0018)
        if spec["bass_style"] == "sustain":
            bass = spec["bass"] * _pad(_hz(chord[0] - 24), min(bar_n, total - start), 0)
            out[start:start + len(bass)] += bass[:, None]
        else:
            step = 1 if spec["bass_style"] == "pulse" else 2
            for i in range(0, 8, step):
                s0 = start + i * eighth_n
                if s0 < total:
                    _place(out, _pluck(_hz(chord[0] - 24), int(0.3 * RATE)), s0, spec["bass"] * 1.4, 0.5)
        if note and b >= 1:
            pattern = spec.get("arp_pattern") or ([0, 1, 2, 1, 2, 1, 0, 1] if len(chord) == 3 else [0, 1, 2, 3, 2, 3, 1, 2])
            step_n = int(spec["arp_step"] * beat * RATE)
            for i in range(int(4 / spec["arp_step"])):
                s0 = start + i * step_n + (int(spec["swing"] * step_n) if i % 2 else 0)
                n_ = min(int((0.2 if spec["arp"] == "square" else 0.6) * RATE) if spec["arp"] != "bell" else int(1.2 * RATE), total - s0)
                if n_ <= 0:
                    break
                pan = 0.35 + 0.3 * (i % 2)
                p = spec["arp_gain"] * note(_hz(chord[pattern[i % len(pattern)] % len(chord)] + 12), n_)
                out[s0:s0 + n_, 0] += p * (1 - pan)
                out[s0:s0 + n_, 1] += p * pan
        for name, sound, gain in (("kick", kick, 0.16), ("snare", snare, 0.06), ("hat", hat, 0.03)):
            for i in drums.get(name, []):
                s0 = start + i * eighth_n + (int(spec["swing"] * eighth_n) if i % 2 else 0)
                soft = 0.6 if (spec["drums"] == "heartbeat" and i == 1) else 1.0
                if s0 < total:
                    _place(out, sound, s0, gain * soft, 0.5 + (0.12 if name == "hat" else 0))
    out = _echo(out)
    if spec["vinyl"]:
        rng = np.random.default_rng(3)
        crackle = rng.standard_normal(total).astype(np.float32) * 0.35 + (rng.random(total) < 0.0002) * rng.standard_normal(total).astype(np.float32) * 6
        out += spec["vinyl"] * crackle[:, None]
    out *= _envelope(total, 1.5, 2.5)[:, None]
    return out / max(1e-6, np.abs(out).max()) * 0.5


def load_file(path, seconds: float) -> np.ndarray:
    """The user's own music file, decoded by ffmpeg and looped to `seconds`, fading out."""
    raw = subprocess.run(
        [paths.ffmpeg(), "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(RATE), "-"],
        capture_output=True, check=True,
    ).stdout
    track = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
    total = int(seconds * RATE) + 1
    if len(track) == 0:
        return np.zeros((total, 2), dtype=np.float32)
    track = np.tile(track, (total // len(track) + 1, 1))[:total].copy()
    track *= _envelope(total, 0.3, 2.5)[:, None]
    return track / max(1e-6, np.abs(track).max()) * 0.5


def whoosh(seconds: float = 0.42, seed: int = 0) -> np.ndarray:
    """A soft airy sweep for a transition: noise through a filter that opens and closes,
    panning across. Its loudest point is at the middle."""
    n = int(seconds * RATE)
    noise = np.random.default_rng(seed).standard_normal(n).astype(np.float32)
    shape = np.sin(np.linspace(0, np.pi, n)) ** 2
    out = np.empty(n, dtype=np.float32)
    y = 0.0
    for i in range(n):
        a = 0.02 + 0.5 * shape[i]
        y += a * (noise[i] - y)
        out[i] = y
    out *= shape
    out /= max(1e-6, np.abs(out).max())
    pan = np.linspace(0.2, 0.8, n, dtype=np.float32)
    return np.stack([out * (1 - pan), out * pan], axis=1) * 0.22


def _stereo(mono: np.ndarray, gain: float) -> np.ndarray:
    mono = mono / max(1e-6, np.abs(mono).max())
    return np.stack([mono, mono], axis=1).astype(np.float32) * gain


def _impact(seed: int = 0) -> np.ndarray:
    """A soft low thump with a short noise tick, for a flash."""
    n = int(0.5 * RATE)
    t = np.arange(n, dtype=np.float32) / RATE
    thump = np.sin(2 * np.pi * (48 + 70 * np.exp(-t / 0.05)) * t) * np.exp(-t / 0.16)
    tick = np.random.default_rng(seed).standard_normal(n).astype(np.float32) * np.exp(-t / 0.012) * 0.35
    return _stereo(thump + tick, 0.3)


def _pop(seed: int = 0) -> np.ndarray:
    """A short rising blip, for an iris."""
    n = int(0.14 * RATE)
    t = np.arange(n, dtype=np.float32) / RATE
    blip = np.sin(2 * np.pi * (380 + 2600 * t) * t) * np.exp(-t / 0.05) * _envelope(n, 0.002, 0.03)
    return _stereo(blip, 0.2)


def _zap(seed: int = 0) -> np.ndarray:
    """Gated bursts of crushed noise, for a glitch."""
    n = int(0.3 * RATE)
    rng = np.random.default_rng(seed)
    gate = np.repeat(rng.random(n // 1200 + 1) > 0.35, 1200)[:n].astype(np.float32)
    noise = np.sign(rng.standard_normal(n)).astype(np.float32) * gate
    return _stereo(noise * np.exp(-np.arange(n, dtype=np.float32) / RATE / 0.18), 0.12)


def transition_sound(kind: str, seed: int = 0) -> np.ndarray:
    """The sound that goes with a transition (see render.TRANSITIONS)."""
    if kind == "flash":
        return _impact(seed)
    if kind == "iris":
        return _pop(seed)
    if kind == "glitch":
        return _zap(seed)
    if kind in ("crossfade", "dip"):
        return whoosh(0.7, seed) * 0.6
    if kind == "whip":
        return whoosh(0.3, seed)
    return whoosh(seed=seed)


def mix(voice: np.ndarray, voice_rate: int, bed: np.ndarray | None, effects: list[tuple[float, np.ndarray]]) -> np.ndarray:
    """Voice (mono int16 at `voice_rate`) over the music bed, which dips while the voice speaks,
    plus effects placed at their times. Returns stereo int16 at 48 kHz."""
    v = voice.astype(np.float32) / 32768
    positions = np.arange(int(len(v) * RATE / voice_rate)) * (voice_rate / RATE)
    v = np.interp(positions, np.arange(len(v)), v).astype(np.float32)
    total = len(v)
    out = np.repeat(v[:, None], 2, axis=1)
    if bed is not None:
        bed = bed[:total] if len(bed) >= total else np.pad(bed, ((0, total - len(bed)), (0, 0)))
        level = np.abs(v)
        hop = RATE // 100
        frames = level[: len(level) // hop * hop].reshape(-1, hop).max(axis=1)
        smooth = np.zeros_like(frames)
        state = 0.0
        for i, x in enumerate(frames):
            state = max(x, state * 0.93)
            smooth[i] = state
        speaking = np.clip(np.repeat(smooth, hop) / 0.08, 0, 1)
        speaking = np.pad(speaking, (0, total - len(speaking)), mode="edge")
        gain = 0.30 - 0.18 * speaking
        out += bed * gain[:, None]
    for at, clip in effects:
        i = max(0, int(at * RATE) - len(clip) // 2)
        j = min(total, i + len(clip))
        out[i:j] += clip[: j - i]
    peak = np.abs(out).max()
    if peak > 0.98:
        out *= 0.98 / peak
    return (out * 32767).astype(np.int16)


SAMPLE_SECONDS = 15
SAMPLE_VERSION = 2


def sample(mood: str):
    """A short sample of a mood's music, for the preview button (made once, then cached)."""
    import wave

    from . import paths

    if mood not in MOODS:
        raise ValueError("Unknown music")
    folder = paths.data_dir() / "music-samples"
    folder.mkdir(exist_ok=True)
    path = folder / f"{mood}-v{SAMPLE_VERSION}.wav"
    if not path.exists():
        pcm = (music(mood, SAMPLE_SECONDS) * 0.9 * 32767).astype(np.int16)
        partial = path.with_suffix(".part")
        with wave.open(str(partial), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(pcm.tobytes())
        partial.replace(path)
    return str(path)
