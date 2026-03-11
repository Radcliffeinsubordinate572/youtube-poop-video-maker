#!/usr/bin/env python3
"""Choose a random style blueprint and emit a structured production plan.

This script is designed for agentic use inside an Agent Skill:
- non-interactive
- helpful --help output
- structured JSON to stdout
- clear errors to stderr
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

STYLE_ANALOGIES = {
    "cathedral-glitch": "a sacred artifact breaking into ecstatic autocomplete",
    "browser-baroque": "a palace of tabs, notifications, and petty drama",
    "terminal-confessional": "a guilty monologue whispered through a terminal",
    "kinetic-caption-ballet": "a typographic dance that argues with itself",
    "pastel-panic": "a cute panic attack that never quite stops smiling",
    "vhs-velvet": "a luxurious nostalgic tape discovered after a bad decision",
    "keynote-meltdown": "a keynote presentation losing control in public",
    "opera-of-errors": "a prestige trailer about a catastrophic misunderstanding",
}

MATERIAL_STRATEGIES: Dict[str, Dict[str, List[str]]] = {
    "text": {
        "primary_assets": [
            "kinetic captions",
            "voiceover or TTS phrases",
            "title cards",
            "repeated word loops",
            "symbolic icons and abstract backgrounds",
        ],
        "secondary_assets": [
            "highlighted quotes",
            "diagram arrows",
            "single-word impact frames",
        ],
        "fallbacks": [
            "use typography as the main performer",
            "add simple shapes, gradients, and textures instead of forcing literal imagery",
        ],
        "avoid": [
            "do not place long paragraphs on screen",
            "do not use more than one dense sentence at a time",
        ],
    },
    "url": {
        "primary_assets": [
            "hero-section crops",
            "scroll reveals",
            "button and CTA close-ups",
            "annotation arrows",
            "cursor choreography",
        ],
        "secondary_assets": [
            "headline repetition",
            "cropped visual motifs from the page",
            "mock browser chrome for framing",
        ],
        "fallbacks": [
            "if the page is thin, use its wording as captions and build support visuals around it",
            "crop into strong layout regions instead of showing the full page all the time",
        ],
        "avoid": [
            "do not fill the frame with unreadable full-page screenshots",
            "do not keep more than three interface layers visible at once",
        ],
    },
    "webpage": {
        "primary_assets": [
            "hero-section crops",
            "scroll reveals",
            "button and CTA close-ups",
            "annotation arrows",
            "cursor choreography",
        ],
        "secondary_assets": [
            "headline repetition",
            "cropped visual motifs from the page",
            "mock browser chrome for framing",
        ],
        "fallbacks": [
            "if the page is thin, use its wording as captions and build support visuals around it",
            "crop into strong layout regions instead of showing the full page all the time",
        ],
        "avoid": [
            "do not fill the frame with unreadable full-page screenshots",
            "do not keep more than three interface layers visible at once",
        ],
    },
    "code": {
        "primary_assets": [
            "syntax-highlighted code cards",
            "terminal windows",
            "log and stack-trace textures",
            "cursor punches",
            "token zoom-ins",
        ],
        "secondary_assets": [
            "variable names as captions",
            "error messages as chorus material",
            "diagrammed architecture snippets",
        ],
        "fallbacks": [
            "use large readable code crops rather than full-file screenshots",
            "turn logs and comments into repeated punchlines",
        ],
        "avoid": [
            "do not show unreadable tiny code",
            "do not drown all code in heavy glitch effects",
        ],
    },
    "document": {
        "primary_assets": [
            "heading crops",
            "page annotations",
            "callout boxes",
            "section title repetition",
            "diagram re-framing",
        ],
        "secondary_assets": [
            "highlighted phrases",
            "page-turn or slide-build transitions",
            "clean title cards",
        ],
        "fallbacks": [
            "pull short claims out of the document and animate them as captions",
            "use the document layout as a motif rather than showing every page",
        ],
        "avoid": [
            "do not leave whole pages static for too long",
            "do not overload pages with extra text overlays",
        ],
    },
    "image": {
        "primary_assets": [
            "parallax crops",
            "cutout masks",
            "punch zooms",
            "freeze-frame callouts",
            "layered foreground/background motion",
        ],
        "secondary_assets": [
            "captioned reactions",
            "zoom-to-detail reveals",
            "subtle texture overlays",
        ],
        "fallbacks": [
            "if only one image exists, loop it with progressively different crops and captions",
            "use motion and text to create escalation",
        ],
        "avoid": [
            "do not keep every zoom at the same speed",
            "do not blur the source beyond recognition unless it is the joke",
        ],
    },
    "audio": {
        "primary_assets": [
            "waveform cards",
            "captioned transcript fragments",
            "reactive backgrounds",
            "meter motion",
            "speaker-label cards",
        ],
        "secondary_assets": [
            "frequency-bar motion",
            "sound-triggered cuts",
            "frozen title frames with text emphasis",
        ],
        "fallbacks": [
            "if the audio is sparse, use transcript text as the visual backbone",
            "punctuate key words with shape animation and image inserts",
        ],
        "avoid": [
            "do not let waveform-only visuals dominate the entire piece",
            "do not hide important words behind flashy motion",
        ],
    },
    "video": {
        "primary_assets": [
            "micro-loops",
            "freeze-frames",
            "reverse stabs",
            "zoom-ins on reaction moments",
            "framed crop replays",
        ],
        "secondary_assets": [
            "caption overlays",
            "impact titles",
            "brief picture-in-picture interruptions",
        ],
        "fallbacks": [
            "if the footage is limited, reuse the best 2-3 moments with stronger variation",
            "alternate real motion with graphic interruption cards",
        ],
        "avoid": [
            "do not just stack random jump cuts",
            "do not overcompress by repeatedly re-encoding intermediate files",
        ],
    },
    "mixed": {
        "primary_assets": [
            "one dominant source type",
            "supporting interruption cards from the other sources",
            "recurring cross-media motif",
        ],
        "secondary_assets": [
            "one shared phrase or icon carried across media types",
            "clean separators between source families",
        ],
        "fallbacks": [
            "let one source lead about 70% of the runtime",
            "use the other sources for escalation or punchline interruption only",
        ],
        "avoid": [
            "do not let the frame become unreadable collage",
            "do not treat every source as equally important",
        ],
    },
    "none": {
        "primary_assets": [
            "original title cards",
            "generated captions",
            "mock UI or terminal panels",
            "gradients, shapes, grids, and textures",
            "simple icons and diagrams",
        ],
        "secondary_assets": [
            "generated narration or TTS",
            "procedural animation",
            "abstract reaction frames",
        ],
        "fallbacks": [
            "build the whole piece from typography, shape language, and sound design",
            "repeat one phrase or symbol as the anchor motif",
        ],
        "avoid": [
            "do not wait for source material",
            "do not mistake random motion for a concept",
        ],
    },
}

GENERAL_EDITING_RULES = [
    "Front-load the strongest absurd promise within the first 1.5 seconds.",
    "Keep most shots between 0.3 and 2.5 seconds; use one or two longer holds for contrast.",
    "Use no more than two font families in the final video.",
    "Preserve safe margins for all captions and titles.",
    "Maintain one dominant recurring motif and mutate it instead of inventing unrelated jokes.",
    "Include at least one moment of relative stillness to reset the eye.",
    "Normalize the final mix and avoid clipped peaks.",
]

QUALITY_CHECKS = [
    "The opening frame is legible and interesting without pausing.",
    "The video communicates one clear comic thesis.",
    "The chosen style is visible in color, type, motion, and sound—not just in captions.",
    "At least one beat provides visual stillness or deadpan contrast.",
    "Captions remain readable on a laptop screen at 100% size.",
    "The palette feels coherent rather than randomly saturated.",
    "Audio peaks are controlled and speech is understandable.",
    "The final 2-3 seconds land a clean button instead of trailing off.",
]

FFMPEG_HINTS = [
    "Pre-render complex beats as short clips or frame sequences, then assemble with ffmpeg.",
    "Use concat or simple crossfades instead of a single brittle mega-filtergraph.",
    "Apply loudness normalization in the final pass: loudnorm=I=-16:TP=-1.5:LRA=11.",
    "Export H.264/AAC with yuv420p and +faststart for broad playback compatibility.",
    "If generating frames in Python, encode them with ffmpeg rather than animating the final container in Python.",
]


def load_styles() -> List[Dict[str, Any]]:
    root = Path(__file__).resolve().parents[1]
    style_path = root / "assets" / "style_blueprints.json"
    try:
        return json.loads(style_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Error: style library not found at {style_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Error: could not parse style library JSON: {exc}") from exc



def detect_material_type(query: str, material_summary: str) -> str:
    text = f"{query}\n{material_summary}".strip().lower()
    if not text:
        return "none"

    scores = {
        "url": 0,
        "webpage": 0,
        "code": 0,
        "document": 0,
        "image": 0,
        "audio": 0,
        "video": 0,
        "text": 0,
    }

    if re.search(r"https?://|\bwww\.|\.(com|io|dev|app|ai|org|net)\b", text):
        scores["url"] += 4
        scores["webpage"] += 3
    if re.search(r"\b(webpage|website|landing page|site|url|homepage|article)\b", text):
        scores["webpage"] += 3
    if re.search(r"\b(code|repo|repository|codebase|stack trace|terminal|cli|source file|build log|commit diff)\b", text):
        scores["code"] += 4
    if re.search(r"def\s+\w+\(|class\s+\w+|import\s+\w+|from\s+\w+\s+import|console\.log|function\s*\(|=>|<div|SELECT\s+.+FROM|INSERT\s+INTO|UPDATE\s+\w+|ERROR:|Traceback", text):
        scores["code"] += 4
    if re.search(r"\b(pdf|doc|document|spec|readme|slide|deck|proposal|manual|report)\b", text):
        scores["document"] += 3
    if re.search(r"\b(text|copy|writing|quote|quotes|transcript|script|caption|captions|prompt|post)\b", text):
        scores["text"] += 3
    if re.search(r"\b(image|photo|png|jpg|jpeg|gif|screenshot|illustration)\b", text):
        scores["image"] += 3
    if re.search(r"\b(audio|podcast|mp3|wav|voice memo|speech recording)\b", text):
        scores["audio"] += 3
    if re.search(r"\b(clip|footage|mp4|mov|mkv|webm|b-roll|scene)\b", text):
        scores["video"] += 3

    non_text_scores = {k: v for k, v in scores.items() if k != "text"}
    if max(non_text_scores.values()) == 0 and scores["text"] == 0:
        return "none"

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top_type, top_score = ranked[0]
    second_type, second_score = ranked[1]

    if top_score <= 1:
        return "text"
    if top_score == second_score and top_score >= 3:
        return "mixed"
    if top_type == "url":
        return "webpage"
    return top_type



def choose_aspect_ratio(query: str, forced: str) -> Tuple[str, str]:
    if forced == "16:9":
        return "16:9", "1920x1080"
    if forced == "9:16":
        return "9:16", "1080x1920"
    if forced == "1:1":
        return "1:1", "1080x1080"

    q = query.lower()
    if re.search(r"\b(shorts|reels|tiktok|vertical|9:16|story)\b", q):
        return "9:16", "1080x1920"
    if re.search(r"\b(square|1:1|instagram post)\b", q):
        return "1:1", "1080x1080"
    return "16:9", "1920x1080"



def pick_style(styles: List[Dict[str, Any]], style_id: str | None, seed: int | None) -> Tuple[Dict[str, Any], int | None]:
    if style_id:
        matches = [style for style in styles if style["id"] == style_id]
        if not matches:
            valid = ", ".join(sorted(style["id"] for style in styles))
            raise SystemExit(f"Error: unknown --style-id '{style_id}'. Valid ids: {valid}")
        return matches[0], seed

    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    style = rng.choice(styles)
    return style, seed



def derive_subject_label(material_type: str, query: str, material_summary: str) -> str:
    explicit = (query or material_summary).strip()
    if material_type == "code":
        return "the code and its logic"
    if material_type in {"webpage", "url"}:
        return "the webpage and its claims"
    if material_type == "document":
        return "the document and its tone"
    if material_type == "image":
        return "the image and its details"
    if material_type == "audio":
        return "the audio and its repeated phrases"
    if material_type == "video":
        return "the footage and its most replayable moments"
    if material_type == "mixed":
        return "the mixed source material"
    if material_type == "none":
        return "the request itself"
    if explicit:
        return "the text"
    return "the material"



def build_beats(duration_sec: int, material_type: str, style: Dict[str, Any]) -> List[Dict[str, Any]]:
    if duration_sec < 24:
        template = [
            ("hook", 0.16, "Open with the clearest absurd promise and the strongest immediately readable image."),
            ("premise", 0.18, "Show what is being remixed so the viewer understands the joke."),
            ("escalation-a", 0.18, "Repeat one motif with a new caption, pitch shift, or crop."),
            ("break", 0.14, "Insert a deadpan hold, silence, or solemn fake-serious beat."),
            ("collapse", 0.22, "Let the chosen style peak with layered interruption and sharper timing."),
            ("button", 0.12, "End on one final line, freeze-frame, or hard audio sting."),
        ]
    elif duration_sec <= 40:
        template = [
            ("hook", 0.12, "Open with the strongest absurd promise in under 1.5 seconds."),
            ("premise", 0.15, "Establish the source material clearly enough that the joke lands."),
            ("escalation-a", 0.16, "Repeat a central motif with variation and stronger framing."),
            ("escalation-b", 0.16, "Increase contradiction, cut rate, or performative overreaction."),
            ("break", 0.12, "Give the eye and ear a brief reset through stillness or solemnity."),
            ("collapse", 0.19, "Peak the style with the densest, cleanest, most intentional chaos."),
            ("button", 0.10, "Land a clean final payoff and stop decisively."),
        ]
    else:
        template = [
            ("hook", 0.10, "Open with a very strong first image and phrase."),
            ("premise", 0.14, "Make the source unmistakable and introduce the thesis."),
            ("escalation-a", 0.14, "Create the first recurring gag pattern."),
            ("escalation-b", 0.14, "Mutate the gag through timing, pitch, or framing."),
            ("break", 0.10, "Insert a short deadpan breath or reverent fake pause."),
            ("escalation-c", 0.14, "Bring in the second-wave interruption and a stronger contradiction."),
            ("collapse", 0.16, "Peak the chosen style without losing readability."),
            ("button", 0.08, "Deliver a final stinger or title-card punchline."),
        ]

    beats: List[Dict[str, Any]] = []
    cursor = 0.0
    for idx, (label, ratio, direction) in enumerate(template):
        start = cursor
        end = duration_sec if idx == len(template) - 1 else round(duration_sec * sum(r for _, r, _ in template[: idx + 1]), 2)
        cursor = end
        beats.append(
            {
                "label": label,
                "start_sec": round(start, 2),
                "end_sec": round(end, 2),
                "direction": direction,
                "material_note": material_note_for_beat(material_type, label),
                "style_note": style_note_for_beat(style, label),
            }
        )
    return beats



def material_note_for_beat(material_type: str, beat_label: str) -> str:
    if material_type == "code":
        notes = {
            "hook": "Lead with the most readable funny token, log line, or error fragment.",
            "premise": "Show enough code context that the later edits remain legible.",
            "break": "Use a blank terminal or blinking cursor as the deadpan reset.",
            "button": "Finish on an error, prompt, or absurd variable-name callback.",
        }
        return notes.get(beat_label, "Use code crops, logs, and terminal behavior as the primary visual language.")
    if material_type in {"webpage", "url"}:
        notes = {
            "hook": "Start on the strongest headline, CTA, or visually loaded page region.",
            "premise": "Show enough page structure that the audience understands the source.",
            "break": "Use a still full-browser frame or frozen cursor beat.",
            "button": "End on a recontextualized button, headline, or scroll snap.",
        }
        return notes.get(beat_label, "Use crops, cursor motion, scrolls, and annotations instead of static full-page views.")
    if material_type == "text":
        notes = {
            "hook": "Open with the sharpest phrase as large kinetic type.",
            "premise": "Set the tone with a readable caption sequence or short narration pass.",
            "break": "Use a sparse text frame or whispered single-word card.",
            "button": "End on the shortest, hardest-hitting phrase.",
        }
        return notes.get(beat_label, "Let captions, title cards, and shape motion do most of the work.")
    if material_type == "none":
        notes = {
            "hook": "Invent a striking opening card or synthetic visual motif immediately.",
            "premise": "State the premise through narration, title cards, or mock UI.",
            "break": "Use negative space or near-silence to reset the pace.",
            "button": "End with a decisive title card, sting, or deadpan freeze.",
        }
        return notes.get(beat_label, "Build from original text, shapes, mock interfaces, and sound design.")
    return "Use the dominant source type clearly and keep the frame readable."



def style_note_for_beat(style: Dict[str, Any], beat_label: str) -> str:
    style_id = style["id"]
    if beat_label == "hook":
        motion_hint = style['motion'].split(',')[0].lower()
        return f"State the chosen look immediately through {motion_hint}, the planned palette, and clearly branded typography."
    if beat_label == "break":
        return f"During the reset beat, keep the frame clean enough for the {style['name']} identity to remain visible."
    if beat_label == "collapse":
        return f"Peak with {style['transitions'].split(',')[0].lower()} and a stronger pass of {style['audio'].split(',')[0].lower()} without losing legibility."
    if beat_label == "button":
        return f"Let the ending feel like a distilled final gesture of {style['name']}."
    return f"Preserve the {style['name']} palette, typography, and motion logic throughout this beat."



def make_plan(args: argparse.Namespace) -> Dict[str, Any]:
    styles = load_styles()

    if args.list_styles:
        return {
            "styles": [
                {"id": style["id"], "name": style["name"], "one_sentence_direction": style["one_sentence_direction"]}
                for style in styles
            ]
        }

    material_type = args.material_type
    if material_type == "auto":
        material_type = detect_material_type(args.query, args.material_summary)

    style, seed_used = pick_style(styles, args.style_id, args.seed)
    aspect_ratio, resolution = choose_aspect_ratio(args.query, args.aspect_ratio)

    if args.duration_sec < 12 or args.duration_sec > 90:
        raise SystemExit("Error: --duration-sec must be between 12 and 90 for this skill.")

    subject_label = derive_subject_label(material_type, args.query, args.material_summary)
    theme = args.theme.strip() if args.theme.strip() else subject_label
    thesis_starter = f"This video makes {theme} feel like {STYLE_ANALOGIES.get(style['id'], 'a stylized collapse of meaning')}."

    strategy = MATERIAL_STRATEGIES.get(material_type, MATERIAL_STRATEGIES["mixed"])
    beats = build_beats(args.duration_sec, material_type, style)

    plan: Dict[str, Any] = {
        "query": args.query,
        "material_summary": args.material_summary,
        "material_type": material_type,
        "theme": theme,
        "seed_used": seed_used,
        "selected_style": style,
        "project_defaults": {
            "duration_sec": args.duration_sec,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "fps": 30,
            "container": "mp4",
            "video_codec": "libx264",
            "audio_codec": "aac",
            "pixel_format": "yuv420p",
            "movflags": "+faststart",
        },
        "thesis_starter": thesis_starter,
        "material_strategy": strategy,
        "beat_sheet": beats,
        "editing_rules": GENERAL_EDITING_RULES + style.get("guardrails", []) + strategy.get("avoid", []),
        "ffmpeg_hints": FFMPEG_HINTS,
        "quality_checks": QUALITY_CHECKS,
    }
    return plan



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Choose a YouTube-poop style blueprint and generate a structured production plan "
            "tailored to the request and material type."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 scripts/plan_video.py --query \"make a youtube poop about what it's like to be a LLM\"\n"
            "  python3 scripts/plan_video.py --query \"turn this landing page into a cursed short\" --material-summary \"https://example.com pricing page\"\n"
            "  python3 scripts/plan_video.py --material-type code --theme \"a codebase arguing with itself\" --style-id terminal-confessional --duration-sec 40\n"
        ),
    )
    parser.add_argument("--query", default="", help="Original user request or condensed prompt.")
    parser.add_argument(
        "--material-summary",
        default="",
        help="Short description of the available source material. Use this instead of pasting huge inputs.",
    )
    parser.add_argument(
        "--material-type",
        default="auto",
        choices=["auto", "text", "url", "webpage", "code", "document", "image", "audio", "video", "mixed", "none"],
        help="Force a specific material type or let the script infer it.",
    )
    parser.add_argument("--theme", default="", help="Override the theme or subject label used in the thesis starter.")
    parser.add_argument(
        "--duration-sec",
        type=int,
        default=32,
        help="Desired runtime in seconds. This skill is optimized for short 20-60 second pieces.",
    )
    parser.add_argument("--style-id", default="", help="Optional style id to override random selection.")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed for reproducible style selection.")
    parser.add_argument(
        "--aspect-ratio",
        default="auto",
        choices=["auto", "16:9", "9:16", "1:1"],
        help="Force output aspect ratio or infer it from the request.",
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="Print the available style blueprints as JSON and exit.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional path to write the JSON plan. If omitted, the plan is written to stdout.",
    )
    return parser



def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    plan = make_plan(args)
    serialized = json.dumps(plan, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(serialized + "\n", encoding="utf-8")
        print(serialized)
    else:
        print(serialized)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
