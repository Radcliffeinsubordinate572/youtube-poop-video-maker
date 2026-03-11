# Reference Guide

This file expands the main skill instructions with material-specific tactics and deeper style direction.

## Core principle

A strong YouTube poop is not random noise. The best results feel like **designed instability**:

- the premise is clear,
- the joke escalates in a controlled way,
- the style is recognizable,
- the frame stays readable,
- and the ending lands cleanly.

A useful visual rule of thumb is **70 / 20 / 10**:

- **70% stable base** — the main image, text block, or layout grid
- **20% active motion** — zooms, cursor moves, reveals, wipes
- **10% disruption** — the actual glitch, interruption, punchline, or rupture

If every layer is screaming at once, the result feels cheap rather than intentional.

## Material tactics by input type

### Text only

Text-only prompts can still produce excellent results when typography becomes the main actor.

Best tactics:

- Break text into short repeatable phrases.
- Use one or two memorable fragments as refrain material.
- Alternate full-frame statement cards with smaller callout captions.
- Add symbolic support imagery rather than trying to literalize every line.
- Let voice and text disagree slightly for comedic tension.

Avoid:

- paragraph-sized caption blocks
- constant full-speed motion
- captions that enter before the viewer can read the previous one

### Webpages and URLs

Treat the page as both source material and set design.

Best tactics:

- Use hero sections, headings, buttons, testimonials, and fine print as recurring visual motifs.
- Crop into the page’s strongest compositional regions.
- Use cursor motion deliberately, almost like choreography.
- Repeat one suspicious or funny phrase three times max, each time framed differently.
- Reveal contradictions through zoomed callouts and scroll snaps.

Avoid:

- static full-page screenshots held for long durations
- showing too many tabs or windows at once
- tiny unreadable body text used as joke setup

### Code and developer material

Code should feel tactile and legible.

Best tactics:

- Show readable snippets, not entire files.
- Use terminals, stack traces, logs, and comments as rhythm material.
- Turn variable names or error phrases into chorus captions.
- Use cursor placement and line highlights to direct attention.
- Pair clean code crops with one strong monospaced type treatment.

Avoid:

- CRT and glitch overlays on every shot
- unreadably small syntax screenshots
- purely decorative code that never connects to the joke

### Audio-led inputs

When audio is the strongest source, make the voice or sound the backbone.

Best tactics:

- build captions tightly around rhythm and key words
- use waveform or frequency graphics only as support
- cut visuals on consonants, pauses, or repeated phrases
- reserve pitch shifts for specific punch moments

Avoid:

- waveform-only visuals for the entire runtime
- overprocessed speech that becomes unintelligible

### No source material

No source does not mean no concept.

Best tactics:

- Create a strong thesis sentence first.
- Use one repeated phrase or symbol as the anchor.
- Build visuals from type, grids, gradients, simple icons, and mock interfaces.
- Use sound design and pacing to imply narrative progression.
- Let the style blueprint do most of the world-building.

Avoid:

- adding effects without a central recurring motif
- trying to imitate a specific copyrighted clip when original motion graphics would work better

## Style library notes

The planner chooses from these at random unless the user specifies a style.

### Cathedral Glitch

Best for introspective AI themes, solemn absurdity, and original-from-scratch pieces.

Use when you want:

- reverence breaking into nonsense
- clean symmetry before rupture
- spiritual or ceremonial framing for silly phrases

Keep it pretty by:

- centering compositions before distortions
- using glow carefully
- letting bright highlights appear only on chosen peaks

### Browser Baroque

Best for webpages, docs, interface-heavy jokes, and commentary about internet behavior.

Use when you want:

- ornate tab/page choreography
- elegant annotation-heavy comedy
- premium-browser aesthetics that slowly curdle

Keep it pretty by:

- limiting simultaneous windows
- protecting whitespace
- using cursor motion like a camera move, not a panic attack

### Terminal Confessional

Best for code, logs, debugging, and machine-self-awareness.

Use when you want:

- terminal intimacy
- monospaced melancholy
- errors framed as dramatic admissions

Keep it pretty by:

- keeping code crops large
- limiting accent colors
- using minimal CRT/scanline treatment

### Kinetic Caption Ballet

Best for text-led material, narration-heavy edits, and clean fast pacing.

Use when you want:

- typography as performance
- emphasis through scale and spacing
- elegant motion design with precise timing

Keep it pretty by:

- letting blank space exist
- limiting how much text appears at once
- breaking lines for rhythm, not just width

### Pastel Panic

Best for personal, emotional, paradoxically cute, or softly uncanny edits.

Use when you want:

- polished sweetness hiding instability
- cute design language carrying harsh or existential lines
- sticker-pop energy with emotional whiplash

Keep it pretty by:

- preserving contrast
- reserving harsh red for accents only
- keeping backgrounds light but not washed out

### VHS Velvet

Best for archive-flavored edits, nostalgia jokes, and warm low-fi luxury.

Use when you want:

- analog softness
- deliberate retro seriousness
- gentle decay rather than ugly static overload

Keep it pretty by:

- keeping the analog treatment subtle
- using blur only on select shots
- protecting readability of text overlays

### Keynote Meltdown

Best for pitch decks, product pages, explainers, and fake-corporate seriousness.

Use when you want:

- polished presentation language
- smooth grids and hierarchy
- escalating sabotage of a clean opening

Keep it pretty by:

- starting genuinely polished
- degrading the order gradually
- preserving alignment until the break point

### Opera of Errors

Best for trailer-like escalation, fake-epic stakes, and dramatic over-interpretation.

Use when you want:

- prestige-trailer seriousness
- title cards and silences
- one tiny detail treated as fate itself

Keep it pretty by:

- not overusing black frames
- saving the biggest audio hits for the endgame
- letting silence work as part of the rhythm

## Editing heuristics

### Hook first

The first 1–1.5 seconds should establish one of the following immediately:

- the central phrase,
- the strongest visual motif,
- the fake-serious tone,
- or the main contradiction.

### Repetition with mutation

Repeat things, but change one dimension each time:

- crop
- pitch
- speed
- typography weight
- context
- caption wording
- emotional framing

### Stillness is a weapon

At least one quiet beat makes the later chaos read as intentional. A good stillness moment can be:

- a frozen browser frame
- a blinking cursor
- a single centered caption
- a near-silent title card

### The final button matters

Good endings are usually one of these:

- a very short callback line
- a freeze-frame with one perfect caption
- a dead-silent title card
- an overblown trailer sting followed by instant cut-to-black

## Audio notes

Priorities:

1. intelligibility
2. timing
3. contrast
4. loudness

Useful moves:

- short mute before impact
- pitch drop on repeated word
- stutter only on one or two key syllables
- bed music that supports tone without burying speech
- final loudnorm pass on the export

## Minimal render strategy

A reliable production pattern is:

1. collect or generate assets
2. build 6–10 short beats
3. pre-render fragile or layered beats separately
4. assemble beats in ffmpeg
5. normalize audio and finalize export settings once

This usually produces cleaner results than trying to invent the whole edit inside one massive filtergraph.
