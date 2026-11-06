"""The optional cloud engine: the user's own OpenAI, Claude, Gemini or OpenAI-compatible account.

It's off until a provider is connected, and then each video chooses where it's made (this Mac or
the provider). The API key lives in the macOS Keychain, the provider and model choices in
cloud.json. Whenever the cloud can't do the work (quota used up, key rejected, no internet, a
provider with no image model), the caller falls back to this Mac and tells the user why.
The calls themselves are in providers.py.
"""

import json
import time

import keyring

from . import paths

KEYCHAIN_SERVICE = "com.toonstudio.app.cloud"
SETTINGS_FILE = "cloud.json"


class Unavailable(Exception):
    """The cloud can't do this now; `str(e)` says why, in words for the user."""


class Refused(Unavailable):
    """The provider's safety filter blocked this one request (often a false alarm on a harmless
    scene). Only this request needs another way; the next ones can still go to the cloud."""




def settings() -> dict:
    from . import providers

    try:
        saved = json.loads((paths.data_dir() / SETTINGS_FILE).read_text())
    except (OSError, ValueError):
        saved = {}
    provider = str(saved.get("provider", ""))
    provider = provider if provider in providers.PROVIDERS else ""
    d = providers.PROVIDERS.get(provider, {})
    return {
        "provider": provider,
        "baseUrl": saved.get("baseUrl") or d.get("base", ""),
        "storyModel": saved.get("storyModel") or d.get("story", ""),
        "imageModel": saved.get("imageModel") or d.get("image", ""),
        "voiceModel": saved.get("voiceModel") or d.get("voice", ""),
    }


def _token(provider: str) -> str | None:
    try:
        return keyring.get_password(KEYCHAIN_SERVICE, provider) if provider else None
    except keyring.errors.KeyringError:
        return None


def connected() -> bool:
    return bool(_token(settings()["provider"]))


def connect(provider: str, token: str, base_url: str = "", story_model: str = "", image_model: str = "", voice_model: str = "") -> dict:
    """Saves a key for a provider (the key in the Keychain) after proving it works with a tiny request."""
    from . import providers

    token = token.strip()
    if provider not in providers.PROVIDERS:
        raise ValueError(f"Unknown provider {provider}")
    if not token:
        raise ValueError("Enter your API key")
    values = {"provider": provider, "baseUrl": base_url.strip(), "storyModel": story_model.strip(), "imageModel": image_model.strip(), "voiceModel": voice_model.strip()}
    (paths.data_dir() / SETTINGS_FILE).write_text(json.dumps(values, indent=2))
    cfg = settings()
    if not cfg["baseUrl"] or not cfg["storyModel"]:
        disconnect()
        raise ValueError("Enter the server’s address and a story model")
    try:
        providers.chat_json(provider, cfg, token, "Answer with JSON.", 'Reply {"ok": true}',
                            {"type": "object", "properties": {"ok": {"type": "boolean"}}}, 0.0, 64)
    except Unavailable as e:
        disconnect()
        raise ValueError(str(e)) from None
    keyring.set_password(KEYCHAIN_SERVICE, provider, token)
    note_success()
    return status()


def disconnect():
    provider = settings()["provider"]
    if provider:
        try:
            keyring.delete_password(KEYCHAIN_SERVICE, provider)
        except keyring.errors.KeyringError:
            pass
    (paths.data_dir() / SETTINGS_FILE).write_text(json.dumps({"provider": ""}))
    note_success()


_last_problem: dict | None = None


def note_problem(what: str, reason: str):
    global _last_problem
    _last_problem = {"what": what, "reason": reason, "at": time.time()}


def note_success():
    global _last_problem
    _last_problem = None


def status() -> dict:
    from . import providers

    s = settings()
    return {**s, "providerName": providers.PROVIDERS.get(s["provider"], {}).get("name", ""), "connected": connected(), "problem": _last_problem}




def _key(provider: str) -> str:
    token = _token(provider)
    if not token:
        raise Unavailable("No cloud AI is connected")
    return token


def draw(prompt: str, width: int, height: int, seed: int) -> bytes:
    """Draws one image with the connected provider; returns PNG bytes. (`seed` is unused: they don't take one.)"""
    from . import providers

    s = settings()
    return providers.draw(s["provider"], s, _key(s["provider"]), prompt, width, height)


def chat_json(system: str, user: str, schema: dict, temperature: float, max_tokens: int) -> dict:
    """Asks the connected provider for an answer in `schema`."""
    from . import providers

    s = settings()
    return providers.chat_json(s["provider"], s, _key(s["provider"]), system, user, schema, temperature, max_tokens)


def voices() -> list[dict]:
    """The connected provider's voices, as the UI lists them (empty when none, or when it can't speak)."""
    from . import providers, styles

    s = settings()
    if not s["provider"] or not s["voiceModel"] or not connected():
        return []
    label = providers.PROVIDERS[s["provider"]]["name"]
    return [{"id": f"{s['provider']}:{vid}", "name": f"{label} · {name}", "language": "*", "gender": gender}
            for vid, name, gender in styles.CLOUD_VOICES.get(s["provider"], [])]


def speak(text: str, voice: str, instruction: str) -> bytes:
    """One line read aloud by the connected provider in its voice id (without the provider prefix); a 24 kHz mono WAV."""
    from . import providers

    s = settings()
    return providers.speak(s["provider"], s, _key(s["provider"]), text, voice, instruction)
