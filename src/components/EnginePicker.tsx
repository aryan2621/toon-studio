import { Cloud, Laptop } from 'lucide-react';
import type { Engine } from '../lib/api';
import { Segmented } from './ui';

export function EnginePicker({
    value,
    cloudConnected,
    onChange,
    disabled,
}: {
    value: Engine;
    cloudConnected: boolean;
    onChange: (engine: Engine) => void;
    disabled?: boolean;
}) {
    return (
        <div className={disabled ? 'pointer-events-none opacity-50' : undefined}>
            <Segmented
                size='sm'
                value={value}
                onChange={(engine) => {
                    if (engine === 'cloud' && !cloudConnected) return;
                    onChange(engine);
                }}
                options={[
                    { value: 'local', label: 'This Mac', icon: <Laptop className='h-3.5 w-3.5' />, hint: 'Best quality. About a minute a shot.' },
                    {
                        value: 'cloud',
                        label: 'Cloud AI',
                        icon: <Cloud className='h-3.5 w-3.5' />,
                        hint: cloudConnected ? 'Your OpenAI, Claude, Gemini or compatible account.' : 'Connect a cloud AI in Settings first.',
                    },
                ]}
            />
        </div>
    );
}

export function engineNote(engine: Engine, cloudConnected: boolean) {
    if (engine === 'cloud') {
        return cloudConnected
            ? 'Uses your cloud AI account (your story and scene descriptions are sent to it). Falls back to this Mac, with a warning, if it can’t do it.'
            : 'No cloud AI is connected, so this Mac will make it. Connect it in Settings.';
    }
    return 'Best quality. About a minute a shot; nothing leaves this Mac.';
}
