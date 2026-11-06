import { useState } from 'react';
import { AlertTriangle, Cloud } from 'lucide-react';
import { toast } from 'sonner';
import { api, type CloudProvider, type CloudStatus } from '../lib/api';
import { Badge, Button, Field, Select, Spinner } from '../components/ui';

const PROVIDERS: Record<CloudProvider, { name: string; base: string; story: string; image: string; voice: string; note: string }> = {
    openai: { name: 'OpenAI', base: 'https://api.openai.com/v1', story: 'gpt-5-mini', image: 'gpt-image-1', voice: 'gpt-4o-mini-tts', note: 'Writes the plan, draws the shots and reads the lines.' },
    claude: { name: 'Claude', base: 'https://api.anthropic.com/v1', story: 'claude-sonnet-5-5', image: '', voice: '', note: 'Writes the plan. It can’t draw or speak, so shots and voices stay on this Mac.' },
    gemini: {
        name: 'Gemini',
        base: 'https://generativelanguage.googleapis.com/v1beta',
        story: 'gemini-2.5-flash',
        image: 'gemini-2.5-flash-image',
        voice: 'gemini-2.5-flash-preview-tts',
        note: 'Writes the plan, draws the shots and reads the lines.',
    },
    compatible: { name: 'OpenAI-compatible', base: '', story: '', image: '', voice: '', note: 'Any server with the OpenAI API (OpenRouter, Together, LM Studio…). Leave the image and voice models blank if it can’t do them.' },
};

const input = 'h-9 w-full rounded-md border border-line bg-panel-2 px-3 font-mono text-xs outline-none transition-colors hover:border-line-strong focus:border-accent';
const off = { autoComplete: 'off', autoCapitalize: 'off', spellCheck: false } as const;

export function CloudSection({ cloud, onChange }: { cloud: CloudStatus; onChange: () => void }) {
    const [provider, setProvider] = useState<CloudProvider>(cloud.provider || 'openai');
    const [token, setToken] = useState('');
    const [base, setBase] = useState('');
    const [story, setStory] = useState('');
    const [image, setImage] = useState('');
    const [voice, setVoice] = useState('');
    const [connecting, setConnecting] = useState(false);
    const [error, setError] = useState('');
    const p = PROVIDERS[provider];
    const missing = !token.trim() ? 'Add your API key.' : provider === 'compatible' && (!base.trim() || !story.trim()) ? 'Add the server address and a story model.' : '';

    const connect = async () => {
        setConnecting(true);
        setError('');
        try {
            await api.cloudConnect(provider, token, base, story, image, voice);
            setToken('');
            toast.success(`${p.name} connected. Choose “Cloud AI” under “Make it on” for a video.`);
            onChange();
        } catch (e) {
            setError(`Couldn’t connect: ${String(e)}`);
        } finally {
            setConnecting(false);
        }
    };

    return (
        <div className='space-y-3'>
            <div>
                <div className='flex items-center gap-2 text-xs text-muted'>
                    Status {cloud.connected ? <Badge tone='success'>{cloud.providerName}</Badge> : <Badge>Off</Badge>}
                </div>
                <p className='mt-1 text-xs leading-relaxed text-subtle'>
                    Optional: use your own OpenAI, Claude, Gemini or OpenAI-compatible account to write plans and draw shots. Your story and
                    scene descriptions are sent to that provider and billed to your account. If it can’t do something (quota used up, you’re
                    offline), this Mac takes over and you’ll see a warning.
                </p>
            </div>

            {cloud.connected ? (
                <div className='space-y-2 rounded-lg border border-line p-3'>
                    <p className='text-xs text-muted'>
                        Pick <span className='font-medium text-fg'>Cloud AI</span> under “Make it on” when you start a video, or in a video’s
                        side panel.
                        {!cloud.imageModel && ' This provider has no image model, so shots are still drawn on this Mac.'}
                        {cloud.voiceModel && ' Its voices are listed with the narrators (the cloud ones can act the emotion of each line).'}
                    </p>
                    {cloud.problem && (
                        <div className='flex gap-2 rounded-md bg-warning-soft p-2 text-xs text-warning-fg'>
                            <AlertTriangle className='mt-0.5 h-3.5 w-3.5 shrink-0' />
                            <span>Last time, the cloud couldn’t help: {cloud.problem.reason}. This Mac did the work instead.</span>
                        </div>
                    )}
                    <div className='flex items-center justify-between pt-1 text-[11px] text-subtle'>
                        <span className='font-mono'>
                            {cloud.storyModel}
                            {cloud.imageModel && ` · ${cloud.imageModel}`}
                            {cloud.voiceModel && ` · ${cloud.voiceModel}`}
                        </span>
                        <Button
                            variant='ghost'
                            size='sm'
                            onClick={async () => {
                                try {
                                    await api.cloudDisconnect();
                                } catch (e) {
                                    toast.error(String(e));
                                }
                                onChange();
                            }}
                        >
                            Disconnect
                        </Button>
                    </div>
                </div>
            ) : (
                <form
                    className='space-y-3 rounded-lg border border-line p-3'
                    onSubmit={(e) => {
                        e.preventDefault();
                        if (!missing && !connecting) connect();
                    }}
                >
                    <Field label='Provider' hint={p.note}>
                        <Select value={provider} onChange={(e) => setProvider(e.target.value as CloudProvider)}>
                            {Object.entries(PROVIDERS).map(([id, v]) => (
                                <option key={id} value={id}>
                                    {v.name}
                                </option>
                            ))}
                        </Select>
                    </Field>
                    <Field label='API key' hint='Kept in your Mac’s Keychain.'>
                        <input value={token} onChange={(e) => setToken(e.target.value)} type='password' {...off} className={input} />
                    </Field>
                    <Field label='Server address' hint={p.base ? 'Leave blank for the default.' : 'Required, e.g. https://openrouter.ai/api/v1'}>
                        <input value={base} onChange={(e) => setBase(e.target.value)} placeholder={p.base} {...off} className={input} />
                    </Field>
                    <Field label='Story model' hint={p.story ? 'Leave blank for the default.' : 'Required.'}>
                        <input value={story} onChange={(e) => setStory(e.target.value)} placeholder={p.story} {...off} className={input} />
                    </Field>
                    {provider !== 'claude' && (
                        <Field label='Image model' hint={p.image ? 'Leave blank for the default.' : 'Optional: blank means shots are drawn on this Mac.'}>
                            <input value={image} onChange={(e) => setImage(e.target.value)} placeholder={p.image} {...off} className={input} />
                        </Field>
                    )}
                    {provider !== 'claude' && (
                        <Field label='Voice model' hint={p.voice ? 'Leave blank for the default.' : 'Optional: blank means voices stay on this Mac.'}>
                            <input value={voice} onChange={(e) => setVoice(e.target.value)} placeholder={p.voice} {...off} className={input} />
                        </Field>
                    )}
                    {error && (
                        <p role='alert' className='text-xs text-warning-fg'>
                            {error}
                        </p>
                    )}
                    <div className='flex items-center justify-between gap-3'>
                        <span className='text-[11px] text-subtle'>{missing}</span>
                        <Button type='submit' variant='primary' size='sm' disabled={connecting || !!missing}>
                            {connecting ? <Spinner className='h-3.5 w-3.5' /> : <Cloud className='h-3.5 w-3.5' />} Connect
                        </Button>
                    </div>
                </form>
            )}
        </div>
    );
}
