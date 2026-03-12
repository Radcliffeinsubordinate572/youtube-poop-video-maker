# YouTube Poop Video Maker Skill

Single-skill package for `youtube-poop-video-maker`.

Repo URL:
- `https://github.com/DenisSergeevitch/youtube-poop-video-maker`

Skill entrypoint:
- `SKILL.md`

## What It Does

`youtube-poop-video-maker` tells an agent how to turn text, webpages, code, documents, images, audio, video, or thin prompts into a short absurdist remix video.

It is optimized for:
- YouTube poops
- cursed trailers
- glitch-poetry or reflective meme edits
- surreal montage edits
- self-aware AI collages
- chaotic but readable 20-60 second parody videos with many micro-scenes

The skill includes:
- a procedural `SKILL.md` with trigger rules and workflow
- `scripts/plan_video.py` for generating a structured production plan
- `assets/style_blueprints.json` for randomized visual-comedic styles
- `assets/scene_atoms.json` for scene invention and higher edit density
- `references/MOOD-REFERENCE.md` for mood anchoring
- references for rendering guidance and final output checks

## Who It Is For

Use this when an agent is asked to make a weird, hyper-edited, comedic remix rather than a normal edit.

It is not meant for:
- ordinary trimming or captioning
- standard marketing videos
- routine explainers

## Review Notes

Review source material rights, parody risk, and the final render before publishing anything publicly.

Requirements:
- Python 3
- `ffmpeg`

## Install Paths

- Codex (macOS/Linux): `~/.codex/skills/youtube-poop-video-maker`
- Claude Code (macOS/Linux): `~/.claude/skills/youtube-poop-video-maker`

## Install on macOS/Linux

### Codex

```bash
git clone https://github.com/DenisSergeevitch/youtube-poop-video-maker.git /tmp/youtube-poop-video-maker && mkdir -p ~/.codex/skills && rm -rf ~/.codex/skills/youtube-poop-video-maker && cp -R /tmp/youtube-poop-video-maker ~/.codex/skills/youtube-poop-video-maker
```

### Claude Code

```bash
git clone https://github.com/DenisSergeevitch/youtube-poop-video-maker.git /tmp/youtube-poop-video-maker && mkdir -p ~/.claude/skills && rm -rf ~/.claude/skills/youtube-poop-video-maker && cp -R /tmp/youtube-poop-video-maker ~/.claude/skills/youtube-poop-video-maker
```

## Quick Examples

- "Make a YouTube poop from this landing page."
- "Turn this codebase summary into a cursed trailer."
- "Make this script feel like an AI meltdown montage."
- "Show what this product launch feels like as a reflective glitch short."
- "Render a surreal short from this image set and voice memo."

## Script Overview

List available styles:

```bash
python3 scripts/plan_video.py --list-styles
```

Generate a plan from a prompt:

```bash
python3 scripts/plan_video.py --query "turn this pricing page into a cursed short" --material-summary "B2B SaaS pricing page with too many claims" --output plan.json
```

Generate a reproducible code-themed plan:

```bash
python3 scripts/plan_video.py --material-type code --theme "a codebase arguing with itself" --style-id terminal-confessional --duration-sec 40 --seed 7
```

## License

MIT. See `LICENSE.txt`.
