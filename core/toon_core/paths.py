"""Where things live. The app passes its folders in the environment; the defaults suit running
the core by hand during development."""

import os
import sys
from pathlib import Path

APP_ID = "com.toonstudio.app"


LEGACY_APP_ID = "com.stickmanstudio.app"
LEGACY_MOVIES = "Stickman Studio"


def _adopt(old: Path, new: Path):
    """Moves a folder from before the rename to its new place, once, so nothing downloaded or made is lost."""
    if old.exists() and not new.exists():
        new.parent.mkdir(parents=True, exist_ok=True)
        old.rename(new)


def data_dir() -> Path:
    """App data: downloaded models and settings."""
    support = Path.home() / "Library" / "Application Support"
    default = support / APP_ID
    if not os.environ.get("TOON_DATA_DIR"):
        _adopt(support / LEGACY_APP_ID, default)
    path = Path(os.environ.get("TOON_DATA_DIR") or default)
    path.mkdir(parents=True, exist_ok=True)
    return path


def models_dir() -> Path:
    path = data_dir() / "models"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir() -> Path:
    path = Path(os.environ.get("TOON_LOG_DIR") or data_dir() / "logs")
    path.mkdir(parents=True, exist_ok=True)
    return path


def projects_dir() -> Path:
    """Each video is a folder here, with its plan, shots, voice and the final MP4."""
    movies = Path.home() / "Movies"
    if not os.environ.get("TOON_PROJECTS_DIR"):
        _adopt(movies / LEGACY_MOVIES, movies / "Toon Studio")
    path = Path(os.environ.get("TOON_PROJECTS_DIR") or movies / "Toon Studio")
    path.mkdir(parents=True, exist_ok=True)
    return path


def bin_dir() -> Path:
    """The bundled native servers sit next to the app's executable (Tauri sidecars)."""
    if os.environ.get("TOON_BIN_DIR"):
        return Path(os.environ["TOON_BIN_DIR"])
    return Path(sys.executable).parent


def sidecar(name: str) -> Path:
    """A bundled server. In development Tauri's copies may carry the target triple."""
    folder = bin_dir()
    for candidate in (folder / name, folder / f"{name}-aarch64-apple-darwin"):
        if candidate.exists():
            return candidate
    raise RuntimeError(f"{name} is missing from this copy of Toon Studio")


def ffmpeg() -> str:
    """ffmpeg ships inside the core (imageio-ffmpeg's static build with libx264)."""
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()
