import { voicesFor, type Captions, type Engine, type Options, type Ratio, type Telling } from './api';

export interface VideoDefaults {
    ratio: Ratio;
    duration: number;
    style: string;
    mode: string;
    language: string;
    voice: string;
    telling: Telling;
    speed: number;
    captions: Captions;
    musicMood: string;
    transitions: string;
    sfx: boolean;
    engine: Engine;
}

const KEY = 'toon-video-defaults';
const PACES = [0.9, 1, 1.1];

export function loadDefaults(options: Options): VideoDefaults {
    let saved: Partial<VideoDefaults> = {};
    try {
        saved = JSON.parse(localStorage.getItem(KEY) || '{}');
    } catch {
    }
    const pick = <T,>(value: T | undefined, allowed: T[], fallback: T) => (value !== undefined && allowed.includes(value) ? value : fallback);
    const language = pick(saved.language, options.languages.map((l) => l.id), 'en');
    const voices = voicesFor(options, language).map((v) => v.id);
    return {
        ratio: pick(saved.ratio, ['9:16', '16:9'], '9:16'),
        duration: pick(saved.duration, options.durations, 60),
        style: pick(saved.style, options.styles.map((s) => s.id), options.styles[0].id),
        mode: pick(saved.mode, options.modes.map((m) => m.id), 'auto'),
        language,
        voice: pick(saved.voice, voices, voices[0]),
        telling: pick(saved.telling, options.telling.map((t) => t.id), 'mixed'),
        speed: pick(saved.speed, PACES, 1),
        captions: pick(saved.captions, ['subtitles', 'keywords', 'off'], 'subtitles'),
        musicMood: pick(saved.musicMood, options.music.map((m) => m.id), 'curious'),
        transitions: pick(saved.transitions, options.transitions.map((t) => t.id), 'auto'),
        sfx: saved.sfx ?? true,
        engine: saved.engine === 'cloud' ? 'cloud' : 'local',
    };
}

export function saveDefaults(defaults: VideoDefaults) {
    try {
        localStorage.setItem(KEY, JSON.stringify(defaults));
    } catch {
    }
}

export function resetDefaults() {
    try {
        localStorage.removeItem(KEY);
    } catch {
    }
}
