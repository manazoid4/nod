# What people have built with Fable and GPT-6, and what it means for Piblo (11 Nov 2026)

Quick scan: Google-style search, GitHub, Anthropic's own prompting guide. Treat community posts as anecdotes; sources disagree and several are repost farms.

## What people reportedly built
- **A local, private "Whisper Flow" clone**: one builder planned with Opus, then executed with Fable. This is the same idea as Piblo's free offline voice typing, so the approach is proven.
- **A navigable Yosemite from NASA elevation data, soft-body physics, procedural shaders, video analysis** within days of launch.
- **One-prompt games and sites** (a card game with real strategy, an explorable Hogwarts, a cinematic vinyl-label store). Matt Shumer says Hogwarts came together much faster than his earlier forest because Fable read his old session traces and learned what worked.
- **GPT-6 Astra**: one-shot Blender scenes, physics games, a Mac messenger clone, agents talking in Unreal. At least one hands-on review says most results came from iterating, not one shot. One-shot is a demo, not a guarantee.

## Rules that repeat across the best sources
1. Give the goal, not the steps; fence it with a few house rules.
2. Give a hard, checkable bar for "done", not adjectives.
3. The builder never grades its own work: use a fresh-context verifier on the real output.
4. Clear obstacles up front (budgets, key locations, "only stop if blocked"); front-load questions, then run unattended.
5. Simplest thing that works; no extra features or abstractions.
6. Use `high` effort by default, `xhigh` only for the hardest parts; lead with the outcome in the final message.
7. Fable is for hard work: delegate routine drafting and scanning to cheaper models.

Sources: Anthropic "Prompting Claude Fable 5" (platform.claude.com docs), shumer.dev/how-i-prompt-fable, theaileverage.beehiiv.com/p/fable-5-beginner-s-guide, DEV Community prompt library, modemguides first-week demos; GPT-6 Astra roundups (Lenny's Newsletter, The Neuron, MindStudio).

## YouTube transcript feature for Piblo (added to the one-shot as part of "Send it to Piblo")
MIT-licensed references to learn from: `KIRVO-REPORTING/video-to-notes` (captions first, Whisper fallback, timestamps, Obsidian export), `jamesbubenik/VidSift` (local-first, searchable library), `tcsenpai/youlama` (captions, faster-whisper, Ollama), `swaub/YTTranscript` (offline, map-reduce summaries; its default Qwen2.5-3B model is non-commercial, so pick a permissive one).
Fit: share link from phone, captions fetched, local summary, searchable transcript, "read me the 3-line version". Needs a labelled outbound fetch in Private mode; stay within YouTube's terms.
