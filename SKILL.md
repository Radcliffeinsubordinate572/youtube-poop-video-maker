---
name: youtube-poop-video-maker
description: Use this skill when the user wants a short YouTube poop, cursed trailer, glitch-poetry montage, absurd supercut, reflective meme edit, or FFmpeg-rendered remix video from text, webpages, code, documents, media, or from scratch. Activate for prompts like “make this weirder,” “give it a personal spin,” “what it feels like,” “render with ffmpeg,” or self-aware AI / LLM montage requests. The skill plans and renders a dense, aesthetically pleasing 20–60 second video with many micro-scenes, readable typography, restrained neon or analog treatments, controlled audio, optional TTS fragments, and a randomly chosen mood blueprint.
license: MIT
compatibility: Python 3 and ffmpeg are required. Pillow and basic media tooling are helpful. Web access is useful for URLs but not required.
metadata:
  author: OpenAI
  version: "1.1"
  category: video-remix
  output: ffmpeg-mp4
---

# YouTube Poop Video Maker

Produce a finished video, not just a concept or storyboard. The result should feel inventive, dense, and internet-native while still looking composed.

See:
- [the reference guide](references/REFERENCE.md)
- [the mood anchor guide](references/MOOD-REFERENCE.md)
- [the output checklist](references/OUTPUT-CHECKLIST.md)

Useful bundled files:
- `scripts/plan_video.py`
- `assets/style_blueprints.json`
- `assets/scene_atoms.json`
- `assets/trigger_eval_queries.json`

## When to use this skill

Use this skill when the user wants:

- a YouTube poop, cursed trailer, absurd montage, reflective glitch short, or surreal supercut
- a video rendered with ffmpeg from text, a webpage, code, a document, media, or no source material at all
- a video with a personal spin, strong POV, or “what it feels like” framing
- a self-aware AI / LLM / internet-culture short
- something “weirder,” “more edited,” “hypercut,” “meme-y,” “chaotic,” or “poetic,” but still aesthetically pleasing

Do not use this skill for routine trimming, simple caption burns, ordinary explainers, standard motion graphics, or conventional ads unless the user explicitly wants remix behavior.

## Core promise

This skill should not flatten creativity into a single house style. The random blueprint is a **mood lens**, not a cage.

The finished piece should usually have:

- more scenes than a straightforward edit would have
- a clear thesis or emotional claim
- readable frames and controlled palettes
- one dominant recurring motif
- at least one authored gesture that feels personal rather than generic
- a decisive final button

## Default output target

Unless the user specifies otherwise:

- one finished MP4
- 20–60 seconds
- 1920x1080 at 30 fps for normal YouTube
- 1080x1920 at 30 fps only when the request clearly implies Shorts/Reels/TikTok/vertical
- H.264 video, AAC audio, `yuv420p`, `+faststart`

## Workflow

### 1) Inventory the material quickly

Work with whatever is already available.

- If the user provided **text**, mine phrases, contradictions, repeated wording, and emotional temperature.
- If the user provided a **webpage or URL**, extract headlines, CTA text, layout motifs, screenshots, crops, and scroll moments.
- If the user provided **code**, use readable snippets, terminal windows, errors, comments, variable names, logs, and cursor motion.
- If the user provided **documents**, use section titles, callouts, diagrams, and page framing.
- If the user provided **images, audio, or video**, mine loops, reaction beats, freeze-frames, speaker fragments, textures, and captionable details.
- If the user provided **nothing**, synthesize the whole world from the request: title cards, browser chrome, terminal panes, lower-thirds, dashboards, progress bars, token streams, warning cards, diagrams, and simple motion graphics.

Do not stall because the source is thin. Invent support scenes.

### 2) Decide the thesis

Before editing, define one short internal sentence:

> “This video makes **X** feel like **Y**.”

Examples:

- “This video makes talking to a language model feel like a late-night emergency broadcast from inside a datacenter.”
- “This video makes a landing page feel like a ceremonial lie detector.”
- “This video makes a codebase feel like a guilty terminal confession.”

Every recurring gag should support that claim.

### 3) Pick a mood blueprint at random

Unless the user names a style, always randomize the blueprint.

Run:

```bash
python3 scripts/plan_video.py --query "$USER_REQUEST" --material-summary "$MATERIAL_SUMMARY" > plan.json
```

If the user explicitly asks for a particular bundled look, override randomness with:

```bash
python3 scripts/plan_video.py --query "$USER_REQUEST" --material-summary "$MATERIAL_SUMMARY" --style-id STYLE_ID > plan.json
```

Use the plan as creative guidance for palette, motion, audio, scene density, and scene invention.

### 4) Build a scene swarm, not just a beat sheet

Aim for **many micro-scenes**.

Recommended density by runtime:

- **20–28s:** about 9–12 scenes
- **29–40s:** about 11–15 scenes
- **41–60s:** about 13–18 scenes

Within those counts, include:

- **anchor scenes** that clearly present the source or thesis
- **bridge scenes** that act like interruptions, glitches, or breath marks
- **one break scene** with relative stillness
- **one climax scene**
- **one button scene**

Most straightforward edits underperform here because they do too few scenes. This skill should feel like there were more ideas than seconds.

### 5) Use the blueprint as mood, not cosplay

Make the render feel designed and serious enough to be beautiful, even when the content is absurd.

Favor:

- dark or restrained bases with selective accents
- editorial contrast
- luminous highlights used sparingly
- readable type with safe margins
- purposeful glitches instead of random ugliness
- a tension between sincerity and sabotage

Avoid unless the user explicitly asks for it:

- cutesy sticker energy
- bubble fonts
- candy palettes
- childish bounce-easing everywhere
- emoji swarms
- rainbow saturation for its own sake
- full-frame noise on every shot

### 6) Add a personal spin

The video should have an attitude.

Put that attitude into:

- the thesis sentence
- a repeated line or motif
- the choice of invented support scenes
- the TTS or captions
- the final button

For self-reflective AI / LLM pieces, prefer intimacy, contradiction, dread, dry wit, or machine-poetry over generic meme randomness.

### 7) Handle audio with restraint

TTS is allowed and often useful, but do not let it become wall-to-wall exposition.

Use TTS for short fragments, warnings, confessions, or chorus lines. A good default is:

- one main voice
- optional second “system” or whisper voice
- 2–8 short lines total for a 20–60s piece
- processing through light pitch shift, band-limit, stutter, dropout, or reverb only where it improves the scene

Also use:

- drones
- pulses
- UI clicks
- mute cuts
- dropouts
- low-key impact hits
- brief silence

Normalize the final mix. Keep speech understandable.

### 8) Render robustly

Prefer a reliable assembly pipeline:

1. Gather or create assets.
2. Pre-render brittle or complex scenes as clips or frame sequences.
3. Assemble in ffmpeg.
4. Do final loudness normalization and compatibility settings in the last pass.

Baseline export:

```bash
ffmpeg -y -i input_video.mp4 \
  -vf "format=yuv420p" \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:v libx264 -crf 18 -preset medium \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  output.mp4
```

If generating scenes in Python, render PNG frames to a directory and encode them with ffmpeg rather than trying to animate the final container entirely inside Python.

## Material adaptation rules

### Text-only input

Do not merely animate paragraphs. Turn text into a world:

- kinetic captions
- title cards
- subtitles
- warning straps
- token streams
- browser or terminal mockups
- diagrams
- original TTS phrases

### Webpage or URL input

Do not hold a full page statically for long. Use:

- headline crops
- CTA/button repetition
- browser chrome
- cursor movement
- scroll reveals
- annotations
- invented support frames that echo the page’s tone

### Code input

Make code tactile and legible:

- readable syntax cards
- terminal panes
- build logs
- error walls
- variable-name punchlines
- cursor snaps
- architecture diagrams
- prompt loops

### No source material

Create an original montage world immediately. Good default invented scenes include:

- boot or warning cards
- lower-thirds and tickers
- terminal confession frames
- dashboard counters
- attention maps
- frozen subtitles
- soft-failure buttons

## Failure handling

If an effect is brittle, simplify the effect, preserve the thesis, preserve the mood, and still finish the render. A finished coherent short beats an over-ambitious broken one.

## Rights hygiene

Prefer user-provided material, public-domain or properly licensed sources, or original generated assets. If rights are unclear, rely more heavily on original motion graphics and transformed support material.

## Final check

Before returning the video, review `references/OUTPUT-CHECKLIST.md`.
