import { useEffect, useRef, useState } from 'react';
import { Pause, Play } from 'lucide-react';
import { toast } from 'sonner';
import { api, fileUrl } from '../lib/api';
import { IconButton, Spinner } from './ui';

// One player for the whole app, so starting a preview stops any other.
let current: { audio: HTMLAudioElement; stop: () => void } | null = null;

function SamplePreview({ label, deps, disabled, limitMs, load }: { label: string; deps: unknown[]; disabled?: boolean; limitMs?: number; load: () => Promise<string | null> }) {
    const [state, setState] = useState<'idle' | 'loading' | 'playing'>('idle');
    const mine = useRef<HTMLAudioElement | null>(null);

    const stop = () => {
        mine.current?.pause();
        if (current?.audio === mine.current) current = null;
        mine.current = null;
        setState('idle');
    };

    // A different choice, or leaving the page, stops the sample.
    useEffect(() => stop, deps);

    const play = async () => {
        current?.stop();
        setState('loading');
        try {
            const path = await load();
            if (!path) return setState('idle');
            const audio = new Audio(fileUrl(path));
            audio.volume = 0.8;
            audio.onended = stop;
            mine.current = audio;
            current = { audio, stop };
            await audio.play();
            if (limitMs) setTimeout(() => mine.current === audio && stop(), limitMs);
            setState('playing');
        } catch (e) {
            stop();
            toast.error(`Couldn’t play the sample: ${String(e)}`);
        }
    };

    return (
        <IconButton label={state === 'playing' ? 'Stop the preview' : label} variant='secondary' disabled={disabled} onClick={state === 'playing' ? stop : play}>
            {state === 'loading' ? <Spinner className='h-3.5 w-3.5' /> : state === 'playing' ? <Pause className='h-4 w-4' /> : <Play className='h-4 w-4' />}
        </IconButton>
    );
}

export function MusicPreview({ mood, file }: { mood?: string; file?: string | null }) {
    return (
        <SamplePreview
            label='Listen to this music'
            deps={[mood, file]}
            disabled={!file && (!mood || mood === 'off')}
            limitMs={file ? 20000 : undefined}
            load={async () => file ?? (mood && mood !== 'off' ? await api.musicSample(mood) : null)}
        />
    );
}

export function VoicePreview({ voice, emotion = 'neutral' }: { voice: string; emotion?: string }) {
    return <SamplePreview label='Listen to this voice' deps={[voice, emotion]} disabled={!voice} load={() => api.voiceSample(voice, emotion)} />;
}
