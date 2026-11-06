"""Bring-your-own-key cloud AI: OpenAI, Claude, Gemini and any OpenAI-compatible server.

Each provider offers the two things the pipeline needs from the cloud, `chat_json` (the story
plan) and `draw` (one shot), with the signatures cloud.py exposes to the engine, which picks the
connected one. A provider that can't do one of them (Claude has no image model) raises
`Unavailable`, so that part is made on this Mac and the user is told why.
"""

import base64
import io
import json
import subprocess
import urllib.error
import urllib.request

from PIL import Image

from . import paths
from .cloud import Refused, Unavailable

PROVIDERS = {
    "openai": {"name": "OpenAI", "base": "https://api.openai.com/v1", "story": "gpt-5-mini", "image": "gpt-image-1", "voice": "gpt-4o-mini-tts"},
    "claude": {"name": "Claude", "base": "https://api.anthropic.com/v1", "story": "claude-sonnet-5-5", "image": "", "voice": ""},
    "gemini": {
        "name": "Gemini",
        "base": "https://generativelanguage.googleapis.com/v1beta",
        "story": "gemini-2.5-flash",
        "image": "gemini-2.5-flash-image",
        "voice": "gemini-2.5-flash-preview-tts",
    },
    "compatible": {"name": "OpenAI-compatible", "base": "", "story": "", "image": "", "voice": ""},
}


def _http(provider: str, url: str, headers: dict, payload: dict, timeout: float = 300, raw: bool = False):
    name = PROVIDERS[provider]["name"]
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "ToonStudio/0.1", **headers},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            return body if raw else json.loads(body or b"{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        if e.code in (401, 403):
            raise Unavailable(f"{name} rejected the API key") from None
        if e.code == 429:
            raise Unavailable(f"{name}’s rate limit or quota is used up") from None
        if e.code == 400 and ("safety" in body.lower() or "content_policy" in body.lower()):
            raise Refused(f"{name}’s safety filter blocked this picture") from None
        raise Unavailable(f"{name} returned error {e.code} ({body[:160].strip()})") from None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise Unavailable(f"{name} couldn’t be reached ({getattr(e, 'reason', e)})") from None


def _json_in(text: str, name: str) -> dict:
    try:
        return json.loads(text[text.index("{"): text.rindex("}") + 1])
    except ValueError:
        raise Unavailable(f"{name}’s story model didn’t answer in the plan format") from None


def _png(raw: bytes, width: int, height: int) -> bytes:
    """Fits the picture the provider made (its sizes are fixed) to the shot's size, cropping the overflow."""
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    scale = max(width / image.width, height / image.height)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    left, top = (image.width - width) // 2, (image.height - height) // 2
    out = io.BytesIO()
    image.crop((left, top, left + width, top + height)).save(out, "PNG")
    return out.getvalue()


def chat_json(provider: str, cfg: dict, key: str, system: str, user: str, schema: dict, temperature: float, max_tokens: int) -> dict:
    base, model = cfg["baseUrl"].rstrip("/"), cfg["storyModel"]
    name = PROVIDERS[provider]["name"]
    if provider == "claude":
        reply = _http(provider, f"{base}/messages", {"x-api-key": key, "anthropic-version": "2023-06-01"}, {
            "model": model, "max_tokens": max_tokens, "temperature": min(temperature, 1.0), "system": system,
            "messages": [{"role": "user", "content": user}],
            "tools": [{"name": "plan", "description": "The shot-by-shot plan", "input_schema": schema}],
            "tool_choice": {"type": "tool", "name": "plan"},
        })
        for block in reply.get("content", []):
            if block.get("type") == "tool_use":
                return block["input"]
        raise Unavailable("Claude gave an empty answer")
    if provider == "gemini":
        reply = _http(provider, f"{base}/models/{model}:generateContent", {"x-goog-api-key": key}, {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens, "responseMimeType": "application/json"},
        })
        parts = ((reply.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts)
        if not text:
            raise Unavailable("Gemini gave an empty answer")
        return _json_in(text, name)
    reply = _http(provider, f"{base}/chat/completions", {"Authorization": f"Bearer {key}"}, {
        "model": model, "temperature": temperature, "max_completion_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": f"{system}\n\nAnswer only with JSON that matches this schema:\n{json.dumps(schema)}"},
            {"role": "user", "content": user},
        ],
    })
    content = ((reply.get("choices") or [{}])[0].get("message") or {}).get("content")
    if not content:
        raise Unavailable(f"{name} gave an empty answer")
    return _json_in(content, name)


def draw(provider: str, cfg: dict, key: str, prompt: str, width: int, height: int) -> bytes:
    base, model = cfg["baseUrl"].rstrip("/"), cfg["imageModel"]
    name = PROVIDERS[provider]["name"]
    if provider == "claude" or not model:
        raise Unavailable(f"{name} can’t draw pictures")
    if provider == "gemini":
        reply = _http(provider, f"{base}/models/{model}:generateContent", {"x-goog-api-key": key}, {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        })
        for part in ((reply.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []:
            data = (part.get("inlineData") or part.get("inline_data") or {}).get("data")
            if data:
                return _png(base64.b64decode(data), width, height)
        raise Unavailable("Gemini returned no image")
    portrait = height > width
    reply = _http(provider, f"{base}/images/generations", {"Authorization": f"Bearer {key}"}, {
        "model": model, "prompt": prompt, "n": 1, "size": "1024x1536" if portrait else "1536x1024",
    })
    item = (reply.get("data") or [{}])[0]
    if item.get("b64_json"):
        return _png(base64.b64decode(item["b64_json"]), width, height)
    if item.get("url"):
        try:
            with urllib.request.urlopen(item["url"], timeout=120) as response:
                return _png(response.read(), width, height)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise Unavailable(f"{name}’s picture couldn’t be downloaded ({getattr(e, 'reason', e)})") from None
    raise Unavailable(f"{name} returned no image")


def _to_wav(data: bytes, raw_pcm_rate: int | None = None) -> bytes:
    """Whatever audio a provider sends, as the 24 kHz mono 16-bit WAV the rest of the app reads."""
    source = ["-f", "s16le", "-ar", str(raw_pcm_rate), "-ac", "1"] if raw_pcm_rate else []
    try:
        return subprocess.run(
            [paths.ffmpeg(), "-loglevel", "error", *source, "-i", "-", "-ar", "24000", "-ac", "1", "-sample_fmt", "s16", "-f", "wav", "-"],
            input=data, capture_output=True, check=True,
        ).stdout
    except subprocess.CalledProcessError:
        raise Unavailable("The voice the provider sent couldn’t be read") from None


def speak(provider: str, cfg: dict, key: str, text: str, voice: str, instruction: str) -> bytes:
    """One line read aloud in `voice`, in the manner `instruction` describes; a 24 kHz mono WAV."""
    base, model = cfg["baseUrl"].rstrip("/"), cfg["voiceModel"]
    name = PROVIDERS[provider]["name"]
    if provider == "claude" or not model:
        raise Unavailable(f"{name} can’t speak")
    if provider == "gemini":
        reply = _http(provider, f"{base}/models/{model}:generateContent", {"x-goog-api-key": key}, {
            "contents": [{"parts": [{"text": f"{instruction}\n\n{text}"}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
            },
        })
        for part in ((reply.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []:
            data = (part.get("inlineData") or part.get("inline_data") or {}).get("data")
            if data:
                return _to_wav(base64.b64decode(data), raw_pcm_rate=24000)
        raise Unavailable("Gemini returned no audio")
    audio = _http(provider, f"{base}/audio/speech", {"Authorization": f"Bearer {key}"}, {
        "model": model, "voice": voice, "input": text, "instructions": instruction, "response_format": "wav",
    }, raw=True)
    if not audio:
        raise Unavailable(f"{name} returned no audio")
    return _to_wav(audio)
