---
name: youtube-poop-video-maker
description: >
  Use this skill when the user wants a short remix or parody video—especially a
  YouTube poop, absurd montage, meme edit, surreal supercut, chaotic trailer,
  glitch-comedy short, or self-aware AI internet collage—from provided
  materials (text, webpages, code, documents, images, audio, or video) or from
  scratch. Activate even when the request is indirect, such as “make this
  weirder,” “cursed,” “hyper-edited,” “ffmpeg video,” or “add a personal spin.”
  This skill extracts motifs from the context, picks one visual-comedic style
  blueprint at random, plans a tight 20–60 second structure, and renders an
  aesthetically pleasing short with strong composition, coherent color
  treatment, readable captions, rhythmic cuts, and clean audio.
license: MIT
compatibility: Designed for coding agents with Python 3 and ffmpeg. Web access helps when URLs are provided, but the skill can also work from user text, files, or from scratch.
metadata:
  author: OpenAI
  version: "1.0"
  category: video-remix
  output: ffmpeg-mp4
---

# YouTube Poop Video Maker

Produce a finished video, not just a concept note. The result should feel chaotic on purpose, but visually composed and pleasant to watch.

## When to use this skill

Use this skill for requests like:

- “make a YouTube poop”
- “turn this text / webpage / code into a weird short video”
- “make a cursed trailer”
- “give it a personal spin”
- “render a meme edit with ffmpeg”
- “make a self-aware AI montage”

Do not use this skill for ordinary trimming, simple captioning, corporate explainers, routine educational editing, or standard social ads unless the user explicitly asks for absurdist remix behavior.

## Output target

Default target unless the user specifies otherwise:

- One finished MP4 file
- 20–60 seconds
- 1920x1080 at 30 fps for normal YouTube output
- 1080x1920 at 30 fps only if the request clearly implies Shorts/Reels/TikTok/vertical
- H.264 video, AAC audio, `yuv420p`, `+faststart`
- Readable on-screen text and non-clipping audio

## Creative promise

This skill should make videos that are funny, strange, and internet-native without collapsing into random ugliness. Favor:

- A clear comic thesis
- One recognizable visual language per render
- Rhythmic editing with deliberate contrast between fast chaos and brief stillness
- Polished typography, safe margins, and legible captions
- Coherent color treatment
- Clean final export

## Available scripts

- **`scripts/plan_video.py`** — Chooses a style blueprint at random by default and emits a structured JSON production plan tailored to the material type.

Primary data files:

- **`assets/style_blueprints.json`** — Style library used by the planner
- **`references/REFERENCE.md`** — Detailed style notes, input-specific tactics, and rendering guidance
- **`references/OUTPUT-CHECKLIST.md`** — Final quality control checklist
- **`assets/trigger_eval_queries.json`** — Optional prompts for trigger testing and description tuning

## Workflow

### 1) Inventory the material quickly

Work with whatever is already available.

- If the user provided **text**, treat it as script, captions, slogans, and repeated punch phrases.
- If the user provided a **webpage or URL**, extract the main claims, headings, visual blocks, and any contradictory or unintentionally funny wording. Use screenshots, crops, scrolls, and annotations.
- If the user provided **code**, turn syntax, errors, logs, comments, variable names, and architecture ideas into the visual grammar. Use syntax-highlighted cards, terminal captures, cursor movement, token punch-ins, and compile/error motifs.
- If the user provided **images, audio, or video**, mine them for repeatable visual/audio motifs, micro-loops, freeze-frames, and reaction beats.
- If the user provided **nothing**, synthesize the piece from the request itself: create original title cards, motion-graphics shapes, abstract textures, generated captions, generated narration, and simple iconography.

Do not wait for perfect source material. If the source is thin, fill the gaps with typography, motion design, voice, sound design, and repeated motifs.

### 2) Decide the thesis in one sentence

Before editing, define one sentence that explains the joke or emotional point. Format it internally as:

> “This video makes **X** feel like **Y**.”

Examples:

- “This video makes using a language model feel like being trapped in a cathedral made of autocomplete.”
- “This video makes a product landing page feel like a collapsing royal court.”
- “This video makes a codebase feel like a confession booth.”

Every recurring gag should reinforce that sentence.

### 3) Pick a style blueprint at random

Unless the user explicitly names a style, always randomize the style selection.

Run:

```bash
python3 scripts/plan_video.py --query "$USER_REQUEST" --material-summary "$MATERIAL_SUMMARY" > plan.json
```

Use `plan.json` as the binding creative plan for:

- palette and contrast behavior
- typography and caption behavior
- motion and transition intensity
- audio treatment
- beat structure
- quality guardrails

If the user explicitly requests a specific look, override randomness with `--style-id <id>`.

### 4) Build a short beat structure

Use the selected plan to create 6–10 beats.

Recommended structure:

1. **Hook** — the strongest absurd promise appears in the first 1.5 seconds.
2. **Premise** — establish the source material clearly enough that the joke lands.
3. **Escalation A** — repeat a motif with variation.
4. **Escalation B** — increase surprise, speed, or contradiction.
5. **Break / stillness** — brief pause, deadpan hold, or solemn fake-serious beat.
6. **Collapse** — visual or semantic overload.
7. **Button** — a final sharp line, freeze-frame, or audio sting.

Keep most shots between 0.3 and 2.5 seconds. Use one or two longer holds for contrast.

### 5) Adapt the material type

#### Text-only inputs

Turn the text into:

- kinetic captions
- voiceover or TTS fragments
- repeated word loops
- title cards
- diagram-like annotations
- symbolic icons and abstract backgrounds

#### Webpage / URL inputs

Use:

- hero-section crops
- headline callouts
- scroll reveals
- repeated CTA/button motifs
- cursor choreography
- annotation arrows and reaction captions

#### Code inputs

Use:

- syntax-highlighted screenshots
- terminal windows
- log spam as rhythmic texture
- variable names as punchlines
- error messages as chorus material
- bracket/indentation zooms and cursor snaps

#### Mixed media

Pick one dominant source and let the others serve as interruptions. Do not let the frame turn into unreadable collage.

#### No source material

Create the entire piece from scratch using:

- original captions and narration
- gradients, shapes, grids, and textures
- mock UI panels or terminal windows
- simple diagrams
- found-but-safe audio textures or synthesized tones

## Aesthetic rules

### Visual clarity

- Use no more than **2 font families** in a single render.
- Keep captions inside safe margins.
- Prefer one main palette plus one accent color family.
- Let at least 60–70% of each frame remain visually stable; use chaos as accent, not everywhere at once.
- Avoid unreadable tiny text, muddy compression, and over-layered meme clutter.

### Motion

- Favor punch-ins, purposeful hard cuts, short freezes, loops with variation, and occasional elegant crossfades or dip-to-color transitions.
- Do not shake every shot. Motion should escalate selectively.
- Include at least one moment of relative stillness to reset the eye.

### Audio

- Make audio jokes land through timing, pitch shifts, mutes, dropouts, stutters, and emphasis—not just raw loudness.
- Normalize the final mix.
- Avoid clipped peaks, painful sibilance, and wall-to-wall distortion unless the user explicitly wants harshness.
- Let the loudest moment feel earned.

### Comedy

- Repetition is good only when it mutates.
- Keep one dominant recurring motif.
- Do not stack unrelated jokes that do not support the thesis.
- A deadpan cutaway or solemn overreaction usually improves pacing.

## Rendering guidance

Prefer a robust assembly pipeline over a giant one-shot filtergraph.

Recommended pattern:

1. Generate or collect source visuals and audio.
2. Pre-render complex visual beats as short clips or frame sequences.
3. Concatenate or crossfade segments in ffmpeg.
4. Apply final color, loudness normalization, pixel-format conversion, and container settings in the last pass.

Typical final-export baseline:

```bash
ffmpeg -y -i input_video.mp4 \
  -vf "format=yuv420p" \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:v libx264 -crf 18 -preset medium \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  output.mp4
```

If generating frames in Python, render PNG frames to a directory and encode them with ffmpeg rather than trying to animate everything in Python itself.

## Source and rights hygiene

- Prefer user-provided material, public-domain material, properly licensed assets, or original generated assets.
- If rights are unclear, transform sparingly and favor original motion-graphics support material.
- Do not depend on a copyrighted clip being available unless the user explicitly supplied it.

## Failure handling

If a planned effect is too brittle:

- simplify the effect,
- keep the same thesis,
- preserve the selected style,
- and still finish the video.

A finished, coherent, good-looking short is better than an ambitious broken render.

## Final check

Before returning the file, run through `references/OUTPUT-CHECKLIST.md`.

If any item fails, fix the edit before presenting the result.
