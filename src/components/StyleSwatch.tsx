/** A tiny drawn preview of each visual style, for the style picker. */
export function StyleSwatch({ style }: { style: string }) {
    const illustrated: Record<string, { sky: string[]; hill: string; far: string; coat: string; line: string }> = {
        whiteboard: { sky: ['#ffffff', '#f1f1f1'], hill: '#ffffff', far: '#f4f4f4', coat: '#e5382d', line: '#222' },
        chalkboard: { sky: ['#264a3c', '#1e3a2f'], hill: '#2c5646', far: '#24493b', coat: '#f1f1e6', line: '#f1f1e6' },
        claymation: { sky: ['#fde3b8', '#f7c98a'], hill: '#8fc27a', far: '#b7d99b', coat: '#e8663d', line: 'none' },
        'fruit-drama': { sky: ['#ffe7c2', '#ffc98a'], hill: '#d9a066', far: '#e9bd86', coat: '#e0302a', line: 'none' },
        organs: { sky: ['#ffd1da', '#f58aa0'], hill: '#c9456a', far: '#e06a8a', coat: '#f7a1b5', line: 'none' },
        'ai-mascot': { sky: ['#1a0d0d', '#3a1a14'], hill: '#c4622d', far: '#2a1410', coat: '#f4956a', line: 'none' },
    };
    const looks: Record<string, { bg: string; line: string; accent: string }> = {
        'classic-light': { bg: '#ffffff', line: '#111111', accent: '#e5382d' },
        'classic-dark': { bg: '#050505', line: '#f5f5f5', accent: '#2ee6f0' },
    };
    if (style in illustrated) {
        const look = illustrated[style];
        return (
            <svg viewBox='0 0 160 90' className='block aspect-video w-full' aria-hidden>
                <defs>
                    <linearGradient id={`sky-${style}`} x1='0' y1='0' x2='0' y2='1'>
                        <stop offset='0' stopColor={look.sky[0]} />
                        <stop offset='1' stopColor={look.sky[1]} />
                    </linearGradient>
                </defs>
                <rect width='160' height='90' fill={`url(#sky-${style})`} />
                <path d='M0 58 Q40 40 85 52 T160 46 V90 H0Z' fill={look.far} stroke={look.line} strokeWidth='1.5' />
                <path d='M0 70 Q50 56 100 66 T160 62 V90 H0Z' fill={look.hill} stroke={look.line} strokeWidth='1.5' />
                {style === 'fruit-drama' ? (
                    <g>
                        <circle cx='70' cy='54' r='11' fill={look.coat} />
                        <path d='M70 43 q2 -6 8 -6 q-1 6 -8 6z' fill='#4c9a3c' />
                        <circle cx='66' cy='53' r='1.3' fill='#111' />
                        <circle cx='74' cy='53' r='1.3' fill='#111' />
                    </g>
                ) : style === 'organs' ? (
                    <g>
                        <path d='M70 66 C54 55 58 43 66 44 C69 44 70 47 70 47 C70 47 71 44 74 44 C82 43 86 55 70 66z' fill={look.coat} />
                        <circle cx='66' cy='53' r='1.3' fill='#111' />
                        <circle cx='74' cy='53' r='1.3' fill='#111' />
                    </g>
                ) : style === 'ai-mascot' ? (
                    <g>
                        <path d='M58 62 Q56 48 64 46 Q68 40 74 45 Q84 46 82 60 Q82 66 70 66 Q58 67 58 62z' fill={look.coat} />
                        <rect x='64' y='52' width='3' height='3' fill='#111' />
                        <rect x='73' y='52' width='3' height='3' fill='#111' />
                    </g>
                ) : (
                    <g>
                        <circle cx='70' cy='47' r='5' fill='#f6d7c3' stroke={look.line} strokeWidth='1' />
                        <path d='M65 46 Q70 39 75 46 Z' fill='#2b2b2b' />
                        <path d='M64 62 L66 52 Q70 50 74 52 L76 62 Z' fill={look.coat} stroke={look.line} strokeWidth='1' />
                    </g>
                )}
            </svg>
        );
    }
    if (style === 'auto') {
        return (
            <svg viewBox='0 0 160 90' className='block aspect-video w-full' aria-hidden>
                <rect width='80' height='45' fill='#ffffff' />
                <rect x='80' width='80' height='45' fill='#050505' />
                <rect y='45' width='80' height='45' fill='#264a3c' />
                <rect x='80' y='45' width='80' height='45' fill='#fde3b8' />
                <circle cx='80' cy='45' r='20' fill='#d97757' />
                <path d='M80 31 l3.6 9.4 l9.4 3.6 l-9.4 3.6 l-3.6 9.4 l-3.6 -9.4 l-9.4 -3.6 l9.4 -3.6 z' fill='#ffffff' />
            </svg>
        );
    }
    const look = looks[style] ?? looks['classic-light'];
    return (
        <svg viewBox='0 0 160 90' className='block aspect-video w-full' aria-hidden>
            <rect width='160' height='90' fill={look.bg} />
            <circle cx='112' cy='34' r='9' fill='none' stroke={look.accent} strokeWidth='2.5' />
            {/* The figure */}
            <g stroke={look.line} strokeWidth='2.4' strokeLinecap='round' fill='none'>
                <circle cx='62' cy='28' r='7' />
                <line x1='62' y1='35' x2='62' y2='56' />
                <line x1='62' y1='41' x2='50' y2='50' />
                <line x1='62' y1='41' x2='76' y2='33' />
                <line x1='62' y1='56' x2='54' y2='72' />
                <line x1='62' y1='56' x2='70' y2='72' />
            </g>
        </svg>
    );
}
