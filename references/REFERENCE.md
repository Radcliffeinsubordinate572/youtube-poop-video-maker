# Reference Guide

This guide expands the main skill with a stronger mood target, scene design patterns, and anti-cartoon guardrails.

## The target feel

The strongest outputs in this category are not random noise. They feel like **designed instability**:

- the opening image is immediately legible
- the piece has an emotional claim, not just edits
- scenes change often
- the palette is controlled
- the weirdness escalates in waves
- the final beat lands like a thought, not an accident

A good visual rule is **70 / 20 / 10**:

- **70% stable base** — the main frame, text block, UI panel, code card, or image crop
- **20% active motion** — zooms, cursor movement, scrolls, wipes, card builds
- **10% rupture** — the glitch, dropout, stutter, warning, or contradiction

When every layer screams, the result looks cheap. Keep a stable frame to violate.

## Why simpler prompts can outperform over-specified skills

A free-form prompt like “use whatever resources you like” often produces more creative results because it gives the agent permission to invent support scenes. Preserve that freedom here.

This skill should therefore:

- invent bridge scenes even when they were not explicitly requested
- use the random blueprint as a mood lens rather than rigid template matching
- prefer scene abundance over one long overworked sequence
- let the “personal spin” appear in captions, voice, and framing decisions

## Scene architecture

Think in terms of a **scene swarm** rather than a short traditional edit.

Useful scene classes:

### 1) Opener scenes

Purpose: make the premise feel immediate in under ~1.2 seconds.

Good opener types:

- warning card
- terminal boot
- hard title over black
- browser frozen at the funniest region
- whispered subtitle over near-darkness
- lower-third with no context yet

### 2) Anchor scenes

Purpose: clearly show what the video is about.

Good anchor scenes:

- readable source crop
- terminal confession
- token stream
- headline board
- code close-up
- document heading frame
- dashboard counter
- attention-map or diagram view

### 3) Bridge scenes

Purpose: make the edit feel rich and alive without needing new literal information.

Good bridge scenes:

- static burst
- cursor hold
- freeze zoom
- one-line subtitle card
- black-frame whisper
- notification storm
- progress bar
- VHS or recording timestamp

### 4) Break scenes

Purpose: reset the eye and ear.

Good break scenes:

- almost-silent subtitle hold
- empty UI panel
- frozen browser with cursor idle
- single sentence on a dark field

### 5) Climax scenes

Purpose: peak the contradiction without destroying legibility.

Good climax scenes:

- multi-panel stack
- contradiction slam
- chorus subtitle wall
- dense lower-third overload
- final dashboard redline

### 6) Button scenes

Purpose: end decisively.

Good button scenes:

- deadpan freeze-frame
- collapse to cursor
- soft failure dialog
- final aphorism title card
- abrupt audio cut on a single line

## How many scenes is enough?

This skill should bias upward.

For a piece around 30–35 seconds, a good default is:

- 1 opener
- 5–7 anchor scenes
- 2–4 bridge scenes
- 1 break
- 1 climax
- 1 button

That usually lands around **11–15 scenes**.

If the source is thin, do not reduce the count. Invent support scenes instead.

## Material-specific guidance

### Text only

The failure mode is “animated essay paragraph.” Avoid that.

Use:

- short caption cards
- one repeated line with mutation
- a terminal or browser wrapper
- subtitles that contradict the main line
- symbolic UI or diagram scenes

### Webpages and URLs

The failure mode is “screen recording with effects.” Avoid that.

Use:

- hero section as one anchor
- CTA or pricing block as another anchor
- crop-ins rather than constant full-page views
- browser chrome as framing
- reaction subtitles or warning straps
- invented transition cards that borrow the page typography

### Code

The failure mode is “tiny code under heavy glitch.” Avoid that.

Use:

- readable code cards
- terminal panes
- stack traces and logs as chorus material
- cursor motion and line emphasis
- variable names or comments as refrain text
- synthesized system dialogs or compilation counters

### No source material

The failure mode is “abstract motion wallpaper.” Avoid that.

Create a full fake ecosystem:

- system boot
- browser or terminal shell
- diagnostics panel
- lower-third / ticker
- metrics or progress view
- subtitle confession
- final failure dialog

## Non-cartoon aesthetic rules

To keep results aesthetically pleasing and closer to moody internet-cinema than to playful cartoon remix:

Favor:

- graphite, navy, black, steel, off-white, muted red, acid yellow, LED green, icy blue
- clean sans-serif or monospaced typography
- sharp title treatment
- selective glow
- negative space
- hard cuts plus occasional elegant fade

Avoid by default:

- candy pink / baby pastel dominant palettes
- rounded sticker icons everywhere
- comic bubble text
- maximal squash-and-stretch
- all-over rainbow channel splitting
- constant camera shake
- childish sticker-board layouts

## TTS guidance

TTS works best as a flavor, not an essay narrator.

Good uses:

- warning lines
- confession fragments
- deadpan system prompts
- repeated chorus phrases
- one final line for the button

Good processing options:

- light band-limit
- low drone under speech
- subtle pitch drop
- stutter on one emphasized word
- sudden mute or dropout after a line

Avoid:

- long unbroken monologues
- clipping
- piling multiple heavily processed voices on every scene

## Blueprint usage

The planner randomly chooses a mood blueprint. Treat it as guidance for:

- palette
- typography
- motion density
- transition language
- audio tone
- scene biases

Do not force every scene into the blueprint in an obvious cosplay way. The blueprint should shape the video globally while leaving room for source-specific invention.

## The opening and ending matter most

If time is limited, spend the extra effort on:

- the first 1.5 seconds
- the first fully readable anchor scene
- the break scene
- the final 2 seconds

Those moments determine whether the piece feels authored.
