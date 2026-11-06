import { useState } from 'react';
import { Check, Cloud, Cpu, Download, FileText, Info, SlidersHorizontal, Trash2, X } from 'lucide-react';
import { toast } from 'sonner';
import { revealItemInDir } from '@tauri-apps/plugin-opener';
import { api, formatGb, type DownloadState, type ModelChoice, type Options, type Status } from '../lib/api';
import { Badge, Button, IconButton, Modal, ProgressBar, Spinner, cx } from '../components/ui';
import { CloudSection } from './CloudSection';
import { DefaultsSection } from './DefaultsSection';

/** Which story and image models to use, and downloading or deleting them. */
export function SettingsDialog({
    status,
    options,
    download,
    onRefresh,
    onClose,
}: {
    status: Status;
    options: Options;
    download: DownloadState;
    onRefresh: () => Promise<Status>;
    onClose: () => void;
}) {
    const [downloading, setDownloading] = useState(false);
    const [tab, setTab] = useState<'defaults' | 'models' | 'cloud' | 'about'>('defaults');

    const choose = async (choice: ModelChoice) => {
        try {
            await api.setSettings({ [choice.kind]: choice.id });
            const next = await onRefresh();
            if (next.missing.length) {
                setDownloading(true);
                await api.download();
                await onRefresh();
            }
        } catch (e) {
            if (String(e) !== 'Cancelled') toast.error(String(e));
            await onRefresh();
        } finally {
            setDownloading(false);
        }
    };

    const remove = async (choice: ModelChoice) => {
        try {
            await api.deleteModel(choice.id);
            await onRefresh();
        } catch (e) {
            toast.error(String(e));
        }
    };

    const section = (kind: 'story' | 'image', title: string, text: string) => (
        <div className='space-y-2'>
            <div>
                <h3 className='text-sm font-medium text-fg'>{title}</h3>
                <p className='text-xs text-subtle'>{text}</p>
            </div>
            {status.choices
                .filter((c) => c.kind === kind)
                .map((c) => {
                    const tooBig = c.minRamGb > status.ramGb;
                    return (
                        <div key={c.id} className={cx('flex items-center gap-3 rounded-lg border p-3', c.active ? 'border-accent bg-accent/5' : 'border-line')}>
                            <div className='min-w-0 flex-1'>
                                <div className='flex items-center gap-2 text-sm text-fg'>
                                    {c.name}
                                    <span className='text-xs text-subtle'>{formatGb(c.sizeMb)}</span>
                                    {tooBig && <Badge tone='warning'>needs {c.minRamGb} GB memory</Badge>}
                                </div>
                                <p className='text-xs text-muted'>{c.note}</p>
                            </div>
                            {c.active ? (
                                <Badge tone='success'>
                                    <Check className='h-3 w-3' /> In use
                                </Badge>
                            ) : (
                                <>
                                    {c.downloaded && (
                                        <IconButton label='Delete download' size='icon-sm' onClick={() => remove(c)}>
                                            <Trash2 className='h-3.5 w-3.5' />
                                        </IconButton>
                                    )}
                                    <Button size='sm' disabled={downloading || !!status.job} onClick={() => choose(c)}>
                                        {c.downloaded ? (
                                            'Use'
                                        ) : (
                                            <>
                                                <Download className='h-3.5 w-3.5' /> Use
                                            </>
                                        )}
                                    </Button>
                                </>
                            )}
                        </div>
                    );
                })}
        </div>
    );

    const fileProgress = download.total ? (download.done ?? 0) / download.total : 0;

    const tabs = [
        { id: 'defaults', label: 'Defaults', icon: SlidersHorizontal },
        { id: 'models', label: 'Models', icon: Cpu },
        { id: 'cloud', label: 'Cloud AI', icon: Cloud },
        { id: 'about', label: 'About', icon: Info },
    ] as const;
    const title = tabs.find((t) => t.id === tab)!.label;

    return (
        <Modal onClose={onClose} dismissable={!downloading} label='Settings' className='max-w-3xl rounded-lg!'>
            <div className='flex h-[32rem] max-h-[80vh]'>
                <nav
                    role='tablist'
                    aria-label='Settings'
                    aria-orientation='vertical'
                    className='flex w-44 shrink-0 flex-col gap-0.5 overflow-y-auto border-r border-line bg-panel-2 p-2'
                    onKeyDown={(e) => {
                        const step = e.key === 'ArrowDown' ? 1 : e.key === 'ArrowUp' ? -1 : 0;
                        if (!step) return;
                        e.preventDefault();
                        const next = tabs[(tabs.findIndex((t) => t.id === tab) + step + tabs.length) % tabs.length];
                        setTab(next.id);
                        document.getElementById(`settings-tab-${next.id}`)?.focus();
                    }}
                >
                    <h2 className='px-2 pb-1.5 pt-0.5 text-sm font-semibold'>Settings</h2>
                    {tabs.map((t) => (
                        <button
                            key={t.id}
                            id={`settings-tab-${t.id}`}
                            role='tab'
                            aria-selected={tab === t.id}
                            aria-controls='settings-panel'
                            tabIndex={tab === t.id ? 0 : -1}
                            onClick={() => setTab(t.id)}
                            className={cx(
                                'flex items-center gap-2 rounded-md px-2.5 py-1.5 text-left text-sm transition-colors',
                                tab === t.id ? 'bg-panel font-medium text-fg ring-1 ring-line-strong' : 'text-muted hover:bg-panel hover:text-fg',
                            )}
                        >
                            <t.icon className='h-4 w-4' /> {t.label}
                        </button>
                    ))}
                </nav>
                <div className='flex min-w-0 flex-1 flex-col'>
                    <div className='flex items-center justify-between px-5 pb-1.5 pt-3'>
                        <h3 className='text-base font-semibold'>{title}</h3>
                        <IconButton label='Close' size='icon-sm' disabled={downloading} onClick={onClose}>
                            <X className='h-4 w-4' />
                        </IconButton>
                    </div>
                    <div key={tab} id='settings-panel' role='tabpanel' aria-labelledby={`settings-tab-${tab}`} className='fade-in flex-1 space-y-5 overflow-y-auto px-5 pb-4 pt-1'>
                        {tab === 'defaults' && <DefaultsSection options={options} cloudConnected={status.cloud.connected} />}
                        {tab === 'models' && (
                            <>
                                {section('story', 'Story AI', 'Writes the director’s plan. Runs only while planning.')}
                                {section('image', 'Image AI', 'Draws the shots. Changing it redraws shots the next time a video is updated.')}
                            </>
                        )}
                        {tab === 'cloud' && <CloudSection cloud={status.cloud} onChange={onRefresh} />}
                        {tab === 'about' && (
                            <div className='space-y-3 text-sm text-muted'>
                                <p>
                                    {status.cloud.connected
                                        ? 'Voice and editing always run on this Mac.'
                                        : `Everything runs on this Mac (${status.ramGb} GB memory). Nothing is uploaded.`}
                                </p>
                                <Button variant='ghost' size='sm' onClick={async () => revealItemInDir(await api.logsDir())}>
                                    <FileText className='h-3.5 w-3.5' /> Open logs folder
                                </Button>
                            </div>
                        )}
                        {downloading && (
                            <div className='space-y-1.5 rounded-lg bg-panel-2 p-3'>
                                <div className='flex items-center gap-2 text-xs text-muted'>
                                    <Spinner className='h-3 w-3' /> Downloading {formatGb(download.done ?? 0)} of {formatGb(download.total ?? 0)}
                                </div>
                                <ProgressBar value={fileProgress} />
                                <Button variant='ghost' size='sm' onClick={() => api.cancelDownload()}>
                                    Cancel
                                </Button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </Modal>
    );
}
