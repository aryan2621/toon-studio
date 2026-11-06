"""Visual styles, formats and voices.

The catalog is the looks that are popular in short-form faceless video (stickman explainers, whiteboard and
chalkboard doodles, claymation, talking fruit, talking organs, mascots); the stickman looks follow the Stickman Video Director skill. The look and the character are
locked here, in code, and wrapped around every shot's scene description, so a small story model
only has to describe what happens; it can't drift the drawing style from shot to shot.
"""

import re

STYLES: dict[str, dict] = {
    "classic-light": {
        "name": "Classic · Light",
        "note": "Black stick figure on a pure white canvas, one bold accent colour.",
        "intro": "A minimalist stick figure illustration.",
        "hero": "a stick figure with a hollow circular head with no face, a single straight line for a body and thin straight black line limbs",
        "people": "Every person is a simple black stick figure with a hollow round head and thin uniform line limbs, no realistic hair or clothing, no realistic hands; figures are drawn large and close.",
        "look": (
            "Bold clean black vector linework of uniform medium weight on a perfectly flat pure white background, "
            "no shading, no gradients, no texture, lots of white negative space. "
            "Only the key object of the idea is vivid red; everything else is black line art."
        ),
    },
    "classic-dark": {
        "name": "Classic · Dark",
        "note": "White stick figure on a pitch-black canvas, glowing accent colour.",
        "intro": "A minimalist stick figure illustration.",
        "hero": "a stick figure with a hollow circular head with no face, a single straight line for a body and thin straight white line limbs",
        "people": "Every person is a simple white stick figure with a hollow round head and thin uniform line limbs, no realistic hair or clothing, no realistic hands; figures are drawn large and close.",
        "look": (
            "Bold clean white vector linework of uniform medium weight on a perfectly flat pitch black background, "
            "no shading, no gradients, no texture, lots of black negative space. "
            "Only the key object of the idea glows electric cyan; everything else is white line art."
        ),
    },
}

_CHARACTER = {"kind": "illustrated", "auto": False}
STYLES.update({
    "whiteboard": {
        "name": "Whiteboard",
        "note": "Black marker doodles on a white board, like a hand-drawn lesson.",
        "kind": "illustrated",
        "intro": "A hand-drawn whiteboard marker doodle.",
        "people": "Simple marker-drawn doodle characters with round heads and expressive faces.",
        "look": (
            "Black and one accent colour dry-erase marker line art on a clean white whiteboard, "
            "sketchy hand-drawn strokes, small arrows and icons, lots of white space, no shading."
        ),
    },
    "chalkboard": {
        "name": "Chalkboard",
        "note": "White and pastel chalk drawings on a dark green classroom board.",
        "kind": "illustrated",
        "intro": "A chalk drawing on a classroom blackboard.",
        "people": "Simple chalk-drawn doodle characters with round heads and expressive faces.",
        "look": (
            "White and pastel chalk line art on a dark green slate chalkboard with soft chalk dust smudges, "
            "hand-drawn sketchy strokes, simple icons and arrows, no photographic detail."
        ),
    },
    "claymation": {
        "name": "Claymation",
        "note": "Plasticine stop-motion characters with fingerprints, in a tiny handmade set.",
        "kind": "illustrated",
        "intro": "A frame from a stop-motion claymation film.",
        "people": "Chunky plasticine clay characters with big simple eyes and visible fingerprint texture.",
        "look": (
            "Handmade plasticine clay figures and miniature set, visible fingerprints and soft imperfections, "
            "warm soft studio light, shallow depth of field, bright playful colours."
        ),
    },
    "fruit-drama": {
        "name": "Fruit drama",
        "note": "Glossy talking fruit and objects with faces, acting out a soap opera.",
        **_CHARACTER,
        "figures": (
            "Every character is a fruit, vegetable or everyday object with a face and arms, never a human. A character's look is its kind, "
            "colour and one accessory.",
            'e.g. "a glossy red strawberry with big eyes and a tiny gold crown"',
        ),
        "intro": "A glossy 3D animated frame of talking fruit.",
        "people": "Every character is a glossy fruit or object with big expressive cartoon eyes, a mouth and small arms, never a human.",
        "look": (
            "Shiny 3D rendered characters on a cosy kitchen counter, dramatic soap-opera lighting, "
            "shallow depth of field, vivid saturated colours, expressive emotions."
        ),
    },
    "organs": {
        "name": "Talking organs",
        "note": "Cute body organs with personalities, inside a stylised body.",
        **_CHARACTER,
        "figures": (
            "Every character is a body organ (heart, brain, liver, lungs, stomach...) with a face and small arms, never a human. "
            "A character's look is which organ it is and one expressive trait.",
            'e.g. "a round pink brain with big glasses and a worried face"',
        ),
        "intro": "A cute 3D animated frame of talking body organs.",
        "people": "Every character is a cute body organ with big expressive eyes, a mouth and small arms, never a human.",
        "look": (
            "Soft glossy 3D rendered characters inside a stylised glowing pink-and-red body interior, "
            "friendly cartoon proportions, warm light, clean and not gory."
        ),
    },
    "ai-mascot": {
        "name": "AI mascot",
        "note": "A low-poly 3D coral blob mascot with square eyes, in a dark moody room with warm light.",
        **_CHARACTER,
        "figures": (
            "Every character is a small cute low-poly 3D blob mascot with a cloud-like rounded body, two square black eyes and stubby feet, "
            "never a human. A character's look is its colour and one prop or expression (a sweat drop, a pointer stick, tiny glasses). "
            "Only the mascot is ever drawn: a human, such as the developer it talks to, is a voice heard off-screen, so list them "
            "as a character but never name or describe them in a scene.",
            'e.g. "a coral-orange low-poly cloud-shaped blob with two square black eyes and a pointer stick"',
        ),
        "intro": "A cinematic low-poly 3D render of a cute blob mascot.",
        "people": "Every character is a cute low-poly faceted 3D blob with a cloud-like rounded body, two simple square black eyes and stubby rounded feet, never a human.",
        "look": (
            "Low-poly faceted 3D render with visible flat polygon shading, a small mascot sitting on a stack of books in a dark moody room, "
            "warm orange rim light and soft glow against deep dark brown and black shadows, glowing screens and small lights in the background, "
            "shallow depth of field, cinematic and cosy."
        ),
    },
})

NO_TEXT = "No text, no letters, no numbers, no words, no captions, no speech bubbles, no watermark."


LEGACY = {"studio-tech": "classic-light", "cinematic": "classic-dark", "storybook": "claymation", "comic": "whiteboard"}


def auto_styles() -> dict:
    """The styles the director may pick when the user chose Auto."""
    return {k: v for k, v in STYLES.items() if v.get("auto", True)}


def kind(style: str) -> str:
    """"stick" for the stickman styles, "illustrated" for fully drawn characters."""
    return STYLES.get(LEGACY.get(style, style), {}).get("kind", "stick")


FORMATS = {
    "9:16": {"name": "Vertical 9:16", "out": (1080, 1920), "draw": (768, 1344)},
    "16:9": {"name": "Wide 16:9", "out": (1920, 1080), "draw": (1344, 768)},
}

DURATIONS = [30, 60, 90, 120, 180]

LANGUAGES = {
    "en": {"name": "English", "words_per_second": 2.9},
    "hi": {"name": "हिन्दी · Hindi", "words_per_second": 2.4},
    "es": {"name": "Español · Spanish", "words_per_second": 3.0},
    "fr": {"name": "Français · French", "words_per_second": 2.9},
}

VOICES = {
    "af_heart": {"name": "Heart · warm American female", "lang": "en", "gender": "female"},
    "af_bella": {"name": "Bella · bright American female", "lang": "en", "gender": "female"},
    "bf_emma": {"name": "Emma · British female", "lang": "en", "gender": "female"},
    "am_michael": {"name": "Michael · American male", "lang": "en", "gender": "male"},
    "am_fenrir": {"name": "Fenrir · deep American male", "lang": "en", "gender": "male"},
    "bm_george": {"name": "George · British male", "lang": "en", "gender": "male"},
    "af_nicole": {"name": "Nicole · soft American female", "lang": "en", "gender": "female"},
    "af_sky": {"name": "Sky · young American female", "lang": "en", "gender": "female"},
    "bf_isabella": {"name": "Isabella · British female", "lang": "en", "gender": "female"},
    "am_puck": {"name": "Puck · lively American male", "lang": "en", "gender": "male"},
    "bm_fable": {"name": "Fable · British male", "lang": "en", "gender": "male"},
    "bm_lewis": {"name": "Lewis · older British male", "lang": "en", "gender": "male"},
    "hf_alpha": {"name": "Alpha · Hindi female", "lang": "hi", "gender": "female"},
    "hf_beta": {"name": "Beta · Hindi female", "lang": "hi", "gender": "female"},
    "hm_omega": {"name": "Omega · Hindi male", "lang": "hi", "gender": "male"},
    "hm_psi": {"name": "Psi · Hindi male", "lang": "hi", "gender": "male"},
}
_MORE = {
    "es": [("ef_dora", "Dora", "Spanish", "female"), ("em_alex", "Alex", "Spanish", "male")],
    "fr": [("ff_siwis", "Siwis", "French", "female")],
}
for _lang, _voices in _MORE.items():
    for _id, _name, _accent, _gender in _voices:
        VOICES[_id] = {"name": f"{_name} · {_accent} {_gender}", "lang": _lang, "gender": _gender}

EMOTIONS = {
    "neutral": {"name": "Neutral", "speed": 1.0, "pitch": 0.0, "gain": 1.0, "say": "Speak naturally and clearly."},
    "happy": {"name": "Happy", "speed": 1.05, "pitch": 1.0, "gain": 1.0, "say": "Speak warmly and cheerfully, with a smile in the voice."},
    "excited": {"name": "Excited", "speed": 1.12, "pitch": 1.5, "gain": 1.08, "say": "Speak with high energy and excitement, quickly and brightly."},
    "calm": {"name": "Calm", "speed": 0.93, "pitch": -0.5, "gain": 0.95, "say": "Speak slowly, softly and soothingly, relaxed."},
    "serious": {"name": "Serious", "speed": 0.96, "pitch": -1.0, "gain": 1.0, "say": "Speak gravely and firmly, measured and low."},
    "sad": {"name": "Sad", "speed": 0.88, "pitch": -1.5, "gain": 0.9, "say": "Speak sadly and quietly, heavy and slow, as if holding back tears."},
    "angry": {"name": "Angry", "speed": 1.08, "pitch": -0.5, "gain": 1.12, "say": "Speak angrily, sharp and forceful, with clipped words."},
    "scared": {"name": "Scared", "speed": 1.12, "pitch": 1.5, "gain": 0.92, "say": "Speak fearfully, with a shaky, hurried, breathy voice."},
    "whisper": {"name": "Whisper", "speed": 0.95, "pitch": -0.5, "gain": 0.55, "say": "Whisper softly and secretively, barely above a breath."},
    "sarcastic": {"name": "Sarcastic", "speed": 0.94, "pitch": -0.5, "gain": 1.0, "say": "Speak dryly and sarcastically, deadpan with a slight mocking tone."},
}

_OPENAI_VOICES = [("alloy", "Alloy", "female"), ("coral", "Coral", "female"), ("nova", "Nova", "female"), ("shimmer", "Shimmer", "female"),
                  ("echo", "Echo", "male"), ("onyx", "Onyx", "male"), ("fable", "Fable", "male"), ("ash", "Ash", "male")]
CLOUD_VOICES = {
    "openai": _OPENAI_VOICES,
    "compatible": _OPENAI_VOICES,
    "gemini": [("Kore", "Kore", "female"), ("Zephyr", "Zephyr", "female"), ("Aoede", "Aoede", "female"), ("Leda", "Leda", "female"),
               ("Puck", "Puck", "male"), ("Charon", "Charon", "male"), ("Fenrir", "Fenrir", "male"), ("Orus", "Orus", "male")],
}


def is_cloud_voice(voice: str) -> bool:
    provider, _, name = voice.partition(":")
    return any(name == v[0] for v in CLOUD_VOICES.get(provider, []))


def voice_ok(voice: str) -> bool:
    return voice in VOICES or is_cloud_voice(voice)


def voice_language(voice: str) -> str:
    """The language a voice reads: a local voice's own, or "*" for a cloud voice (any)."""
    return VOICES[voice]["lang"] if voice in VOICES else "*"


SAMPLE_TEXT = {
    "en": "Hi! This is how I sound when I tell your story.",
    "hi": "नमस्ते! जब मैं आपकी कहानी सुनाता हूँ, तो मैं ऐसा सुनाई देता हूँ।",
    "es": "¡Hola! Así sueno cuando cuento tu historia.",
    "fr": "Bonjour ! Voici ma voix quand je raconte votre histoire.",
}

TELLING = {
    "narrator": "One narrator",
    "mixed": "Narrator + character voices",
    "characters": "Characters only",
}

TRANSITIONS = {
    "cut": "Cut",
    "crossfade": "Crossfade",
    "dip": "Dip to black",
    "flash": "Flash",
    "push": "Push",
    "wipe": "Wipe",
    "whip": "Whip pan",
    "zoom": "Zoom blur",
    "iris": "Iris",
    "glitch": "Glitch",
}
TRANSITION_SETTINGS = {
    "auto": "Auto · the director picks",
    "smooth": "Smooth",
    "punchy": "Punchy",
    "cuts": "Cuts only",
    **{k: v for k, v in TRANSITIONS.items() if k != "cut"},
}
_POOLS = {"smooth": ("crossfade", "dip", "wipe", "iris", "zoom"), "punchy": ("flash", "whip", "push", "glitch", "zoom")}


def resolve_transition(setting: str, shot: str, index: int) -> str:
    """The transition a shot actually gets, from the video's setting and the shot's own choice."""
    if setting == "cuts":
        return "cut"
    if setting in TRANSITIONS:
        return setting
    if setting in _POOLS:
        pool = _POOLS[setting]
        return shot if shot in pool else pool[index % len(pool)]
    return shot if shot in TRANSITIONS else "auto"


NARRATOR = "Narrator"

MUSIC = {
    "curious": "Curious",
    "calm": "Calm",
    "uplifting": "Uplifting",
    "lofi": "Lo-fi",
    "cinematic": "Cinematic",
    "suspense": "Suspense",
    "upbeat": "Upbeat",
    "playful": "Playful",
    "chiptune": "Chiptune",
    "dreamy": "Dreamy",
    "sad": "Sad",
    "off": "None",
}

CAMERA_MOVES = ["push_in", "pull_out", "pan_left", "pan_right", "rise", "still", "focus_left", "focus_center", "focus_right"]


def options() -> dict:
    from . import cloud
    from .planner import MODES

    return {
        "modes": [{"id": k, "name": m["name"], "note": m["note"], "defaults": m["defaults"]} for k, m in MODES.items()],
        "styles": [{"id": "auto", "name": "Auto", "note": "The director picks the look that fits what you wrote."}]
        + [{"id": k, "name": v["name"], "note": v["note"]} for k, v in STYLES.items()],
        "formats": [{"id": k, "name": v["name"]} for k, v in FORMATS.items()],
        "durations": DURATIONS,
        "voices": [{"id": k, "name": v["name"], "language": v["lang"], "gender": v["gender"]} for k, v in VOICES.items()] + cloud.voices(),
        "languages": [{"id": k, "name": v["name"]} for k, v in LANGUAGES.items()],
        "telling": [{"id": k, "name": v} for k, v in TELLING.items()],
        "music": [{"id": k, "name": v} for k, v in MUSIC.items()],
        "emotions": [{"id": k, "name": v["name"]} for k, v in EMOTIONS.items()],
        "transitions": [{"id": k, "name": v} for k, v in TRANSITION_SETTINGS.items()],
        "shotTransitions": [{"id": "auto", "name": "Auto"}] + [{"id": k, "name": v} for k, v in TRANSITIONS.items()],
    }


def default_voice(language: str) -> str:
    return next(k for k, v in VOICES.items() if v["lang"] == language)


def cast_voices(characters: list[dict], narrator: str, language: str) -> list[dict]:
    """Gives each character a voice of their gender in the video's language, each different from
    the narrator's and from one another while there are enough to go round. A voice the user
    already chose (and that suits the language) is kept."""
    fits = lambda v: voice_ok(v) and voice_language(v) in (language, "*")
    used = {narrator} | {c["voice"] for c in characters if c.get("voice") and fits(c["voice"])}
    out = []
    for c in characters:
        c = dict(c)
        if not c.get("voice") or not fits(c["voice"]):
            gender = c.get("gender") if c.get("gender") in ("female", "male") else "female"
            pool = [k for k, v in VOICES.items() if v["lang"] == language and v["gender"] == gender]
            fresh = [k for k in pool if k not in used]
            c["voice"] = (fresh or [k for k in pool if k != narrator] or pool)[0]
            used.add(c["voice"])
        out.append(c)
    return out


def cast_in(scene: str, characters: list[dict]) -> list[dict]:
    """The plan's characters who appear in this scene (named in it)."""
    return [c for c in characters if re.search(rf"\b{re.escape(c['name'])}\b", scene, re.I)]


_STICK_LEAD = re.compile(r"^(an?|the)?\s*(\w+\s+){0,2}?stick ?(figure|man|woman)s?\s*(,|with|wearing|who has|in)?\s*", re.I)
_A_FIGURE = re.compile(r"\b(stick figures?|figures?|person|people|man|woman|boy|girl|child|he|she)\b", re.I)


def looks_in(scene: str, characters: list[dict], changes: dict | None) -> dict:
    """The changed looks (a haircut, new clothes) of the characters in this scene."""
    names = {c["name"] for c in cast_in(scene, characters)}
    return {k: v for k, v in (changes or {}).items() if k in names and v}


def image_prompt(style: str, scene: str, characters: list[dict] = (), changes: dict | None = None) -> str:
    """The style's fixed look around the scene, plus how each character in it looks, so they
    stay recognisable from shot to shot (the image model sees one shot at a time).

    In the stickman styles the main character (listed first) always gets the style's locked look;
    the others are stick figures set apart by an accessory or colour, never realistic people."""
    style = LEGACY.get(style, style)
    s = STYLES[style]
    characters = list(characters)
    cast = cast_in(scene, characters)
    who = []
    if kind(style) == "stick":
        main = characters[0] if characters else None
        for c in cast:
            mark = _STICK_LEAD.sub("", c["look"].strip()).rstrip(".")
            if c is main:
                who.append(f"{c['name']} is {s['hero']}.")
            else:
                who.append(f"{c['name']} is another stick figure drawn the same way, set apart only by {mark}." if mark
                           else f"{c['name']} is another stick figure drawn the same way.")
        if not cast and _A_FIGURE.search(scene):
            who.append(f"The main figure is {s['hero']}.")
    else:
        who = [f"{c['name']} is {c['look'].rstrip('.')}." for c in cast]
    who += [f"{name} now has a changed look: {look}." for name, look in looks_in(scene, characters, changes).items()]
    scene = scene.strip()
    if scene and scene[-1] not in ".!?":
        scene += "."
    return " ".join(p for p in [s["intro"], scene, *who, s["people"], s["look"], NO_TEXT] if p)


_ESPEAK = {"hi": "hi", "es": "es", "fr": "fr-fr"}


def speech_lang(voice: str) -> str:
    """The language code Kokoro's phonemizer reads the voice's text in."""
    lang = VOICES.get(voice, {}).get("lang")
    if lang in _ESPEAK:
        return _ESPEAK[lang]
    return "en-gb" if voice.startswith("b") else "en-us"
