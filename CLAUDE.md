# Toon Studio

Tauri 2 desktop app (macOS, Apple silicon). React 19 + Tailwind 4 UI in `src/`, Python core in `core/toon_core/` (packed as the `toon-core` sidecar). Run: `pnpm tauri dev`. Typecheck: `pnpm exec tsc --noEmit`. Dev notes: `docs/dev.md`.

# UI

The global "UI standards" apply (no AI-looking UI). Project specifics:
- Dense desktop utility, system UI font stack, one neutral accent (not the Claude coral), radii 4–8px (`rounded-lg` only on dialogs), borders instead of shadows, no blur.
- Reuse `src/components/ui.tsx` (`Button`, `Field`, `Select`, `Modal`, `Badge`, `IconButton`) and the tokens in `src/index.css`.
- Known tells still here, fix when touching these files: `--font-serif` and the Source Serif/Inter `@fontsource` imports in `src/index.css`; `font-serif` headings in `App.tsx`, `SetupView.tsx`, `ShareDialog.tsx`, `ProjectView.tsx`, `NewVideoView.tsx`; `rounded-2xl` on `Modal` and the New Video section card; `backdrop-blur` on the Modal scrim and the New Video footer; `shadow-sm` on primary buttons and the segmented control.

# Product rules (do not break)
- Everything works on macOS; local models (llama.cpp + stable-diffusion.cpp + Kokoro) are the default; cloud AI (OpenAI, Claude, Gemini, OpenAI-compatible) is optional and keys live in the Keychain.
- Visual styles live in `core/toon_core/styles.py` (`STYLES`); removed ids map through `styles.LEGACY`. Keep the catalog to looks backed by current short-form trends.
- Don't write tests unless asked.
