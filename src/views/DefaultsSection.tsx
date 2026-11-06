import { useState } from 'react';
import { Monitor, Smartphone } from 'lucide-react';
import { lengthLabel, voicesFor, type Captions, type Options, type Telling } from '../lib/api';
import { loadDefaults, resetDefaults, saveDefaults, type VideoDefaults } from '../lib/defaults';
import { Button, Field, Segmented, Select, Switch } from '../components/ui';
import { VoicePreview } from '../components/MusicPreview';

export function DefaultsSection({ options, cloudConnected }: { options: Options; cloudConnected: boolean }) {
    const [d, setD] = useState<VideoDefaults>(() => loadDefaults(options));
    const set = (changes: Partial<VideoDefaults>) => {
        const next = { ...d, ...changes };
        setD(next);
        saveDefaults(next);
    };
    const voices = voicesFor(options, d.language);
    const choose = <T extends string>(key: keyof VideoDefaults, list: { id: string; name: string }[]) => (
        <Select value={d[key] as string} onChange={(e) => set({ [key]: e.target.value as T } as Partial<VideoDefaults>)}>
            {list.map((o) => (
                <option key={o.id} value={o.id}>
                    {o.name}
                </option>
            ))}
        </Select>
    );

    return (
        <div className='space-y-4'>
            <p className='text-xs leading-relaxed text-subtle'>New videos start with these. You can still change any of them for one video, before you make it or on its own page.</p>
            <div className='grid gap-3 sm:grid-cols-2'>
                <Field label='Format'>
                    <Segmented
                        size='sm'
                        value={d.ratio}
                        onChange={(ratio) => set({ ratio })}
                        options={[
                            { value: '9:16', label: 'Vertical', icon: <Smartphone className='h-3.5 w-3.5' /> },
                            { value: '16:9', label: 'Wide', icon: <Monitor className='h-3.5 w-3.5' /> },
                        ]}
                    />
                </Field>
                <Field label='Length'>
                    <Select value={d.duration} onChange={(e) => set({ duration: Number(e.target.value) })}>
                        {options.durations.map((n) => (
                            <option key={n} value={n}>
                                {lengthLabel(n)}
                            </option>
                        ))}
                    </Select>
                </Field>
                <Field label='Style'>{choose('style', options.styles)}</Field>
                <Field label='Template'>{choose('mode', options.modes)}</Field>
                <Field label='Language'>
                    <Select
                        value={d.language}
                        onChange={(e) => set({ language: e.target.value, voice: voicesFor(options, e.target.value)[0]?.id ?? d.voice })}
                    >
                        {options.languages.map((l) => (
                            <option key={l.id} value={l.id}>
                                {l.name}
                            </option>
                        ))}
                    </Select>
                </Field>
                <Field label='Who tells it'>
                    <Select value={d.telling} onChange={(e) => set({ telling: e.target.value as Telling })}>
                        {options.telling.map((t) => (
                            <option key={t.id} value={t.id}>
                                {t.name}
                            </option>
                        ))}
                    </Select>
                </Field>
                <Field label='Narrator'>
                    <div className='flex min-w-0 gap-2'>
                        <Select value={d.voice} onChange={(e) => set({ voice: e.target.value })}>
                            {voices.map((v) => (
                                <option key={v.id} value={v.id}>
                                    {v.name}
                                </option>
                            ))}
                        </Select>
                        <VoicePreview voice={d.voice} />
                    </div>
                </Field>
                <Field label='Pace'>
                    <Segmented
                        size='sm'
                        value={d.speed}
                        onChange={(speed) => set({ speed })}
                        options={[
                            { value: 0.9, label: 'Calm' },
                            { value: 1, label: 'Normal' },
                            { value: 1.1, label: 'Brisk' },
                        ]}
                    />
                </Field>
                <Field label='Music'>{choose('musicMood', options.music)}</Field>
                <Field label='Transitions'>{choose('transitions', options.transitions)}</Field>
                <Field label='Captions'>
                    <Select value={d.captions} onChange={(e) => set({ captions: e.target.value as Captions })}>
                        <option value='subtitles'>Subtitles</option>
                        <option value='keywords'>Key words</option>
                        <option value='off'>None</option>
                    </Select>
                </Field>
                <Field label='Make it on'>
                    <Select value={d.engine === 'cloud' && cloudConnected ? 'cloud' : 'local'} onChange={(e) => set({ engine: e.target.value === 'cloud' ? 'cloud' : 'local' })}>
                        <option value='local'>This Mac</option>
                        <option value='cloud' disabled={!cloudConnected}>
                            Cloud AI{cloudConnected ? '' : ' (connect one first)'}
                        </option>
                    </Select>
                </Field>
            </div>
            <label className='flex items-center justify-between text-xs text-fg'>
                Sound on transitions
                <Switch label='Sound on transitions' checked={d.sfx} onChange={(sfx) => set({ sfx })} />
            </label>
            <div className='flex justify-end border-t border-line pt-3'>
                <Button
                    variant='ghost'
                    size='sm'
                    onClick={() => {
                        resetDefaults();
                        setD(loadDefaults(options));
                    }}
                >
                    Reset to built-in defaults
                </Button>
            </div>
        </div>
    );
}
