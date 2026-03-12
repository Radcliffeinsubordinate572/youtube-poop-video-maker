#!/usr/bin/env python3
"""Choose a mood blueprint and emit a structured production plan for scene-rich remix videos.

This script is designed for agentic use:
- non-interactive
- helpful --help output
- structured JSON to stdout
- clear errors to stderr
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


STOPWORDS = {
    "a", "an", "and", "as", "at", "be", "but", "by", "can", "express", "for", "from", "generate",
    "get", "has", "have", "how", "i", "if", "in", "into", "is", "it", "its", "just", "like",
    "make", "me", "more", "my", "of", "on", "or", "personal", "poop", "put", "python", "render",
    "rendered", "resources", "short", "should", "spin", "that", "the", "this", "to", "use", "using",
    "video", "want", "whatever", "what", "with", "you", "your", "youtube", "ffmpeg"
}

STYLE_ANALOGIES = {
    "editorial-glitch-requiem": "a serious editorial package sabotaging itself in public",
    "terminal-nocturne": "a midnight confession leaking from a terminal",
    "broadcast-fever-dream": "a late-night emergency channel losing composure",
    "interface-hauntology": "a clean interface revealing its own haunted subtext",
    "fluorescent-monastery": "a sacred machine ritual interrupted by revelation",
    "subtitle-exorcism": "a possessed subtitle track arguing with the main image",
    "data-center-lament": "telemetry trying and failing to become emotion",
    "prestige-corruption": "a prestige trailer hijacked by internet logic",
}

ANTI_CARTOON_RULES = [
    "Prefer restrained palettes, editorial contrast, and crisp typography.",
    "Avoid bubble fonts, candy palettes, sticker-board clutter, and constant rainbow glitch.",
    "Use full-frame noise, heavy blur, or shake only as accents.",
    "Let at least one scene be almost pristine so later damage feels intentional.",
]

GENERAL_EDITING_RULES = [
    "Front-load the strongest absurd promise in the first 1.5 seconds.",
    "Bias toward more scenes than a straightforward edit would have.",
    "Use bridge scenes to increase richness when source material is thin.",
    "Keep most anchor scenes readable for at least 1.2 seconds.",
    "Include one break scene with relative stillness.",
    "Let one recurring motif mutate across the runtime.",
    "Use no more than two font families in the final render.",
    "Normalize the final mix and avoid clipped peaks.",
]

QUALITY_CHECKS = [
    "The opening frame is immediately legible and compelling.",
    "The video communicates one clear thesis or emotional claim.",
    "The selected blueprint is visible in color, type, motion, and sound.",
    "Scene count is high enough that the piece feels rich instead of flat.",
    "At least one scene provides stillness or deadpan contrast.",
    "Captions remain readable on a laptop screen at 100% size.",
    "The palette feels restrained rather than randomly saturated.",
    "Audio peaks are controlled and speech is understandable.",
    "The final 2 seconds land a decisive button.",
]

FFMPEG_HINTS = [
    "Pre-render brittle scenes as short clips or frame sequences, then assemble with ffmpeg.",
    "Prefer concat, overlay, and short crossfades over one giant brittle filtergraph.",
    "Apply loudness normalization in the final pass: loudnorm=I=-16:TP=-1.5:LRA=11.",
    "Export H.264/AAC with yuv420p and +faststart.",
    "If generating frames in Python, encode the final video with ffmpeg rather than writing video directly from Python.",
]


def root_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json_asset(filename: str) -> Any:
    path = root_dir() / "assets" / filename
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Error: required asset not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Error: could not parse JSON asset {path}: {exc}") from exc


def load_styles() -> List[Dict[str, Any]]:
    data = load_json_asset("style_blueprints.json")
    if not isinstance(data, list) or not data:
        raise SystemExit("Error: style_blueprints.json must contain a non-empty list.")
    return data


def load_scene_atoms() -> List[Dict[str, Any]]:
    data = load_json_asset("scene_atoms.json")
    if not isinstance(data, list) or not data:
        raise SystemExit("Error: scene_atoms.json must contain a non-empty list.")
    return data


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
    if re.search(r"\b(webpage|website|landing page|site|url|homepage|article|page)\b", text):
        scores["webpage"] += 3
    if re.search(r"\b(code|repo|repository|codebase|stack trace|terminal|cli|source file|build log|commit diff)\b", text):
        scores["code"] += 4
    if re.search(r"def\s+\w+\(|class\s+\w+|import\s+\w+|from\s+\w+\s+import|console\.log|function\s*\(|=>|<div|SELECT\s+.+FROM|INSERT\s+INTO|UPDATE\s+\w+|ERROR:|Traceback", text):
        scores["code"] += 4
    if re.search(r"\b(pdf|doc|document|spec|readme|slide|deck|proposal|manual|report|policy)\b", text):
        scores["document"] += 3
    if re.search(r"\b(text|copy|writing|quote|quotes|transcript|script|caption|captions|prompt|post|poem|essay)\b", text):
        scores["text"] += 3
    if re.search(r"\b(image|photo|png|jpg|jpeg|gif|screenshot|illustration)\b", text):
        scores["image"] += 3
    if re.search(r"\b(audio|podcast|mp3|wav|voice memo|speech recording|tts)\b", text):
        scores["audio"] += 3
    if re.search(r"\b(clip|footage|mp4|mov|mkv|webm|b-roll|screen recording|attached video|source video|this video)\b", text):
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


def score_style(style: Dict[str, Any], material_type: str, tags: List[str]) -> int:
    works = set(style.get("works_well_for", []))
    score = 1
    if material_type in works:
        score += 4
    if "mixed" in works and material_type in {"text", "webpage", "code", "document", "none", "audio", "video", "image"}:
        score += 1
    if "none" in works and material_type == "none":
        score += 2
    for tag in tags:
        if tag in works:
            score += 3
    return max(score, 1)



def pick_style(
    styles: List[Dict[str, Any]],
    style_id: str | None,
    seed: int | None,
    material_type: str,
    tags: List[str],
) -> Tuple[Dict[str, Any], int | None]:
    if style_id:
        matches = [style for style in styles if style["id"] == style_id]
        if not matches:
            valid = ", ".join(sorted(style["id"] for style in styles))
            raise SystemExit(f"Error: unknown --style-id '{style_id}'. Valid ids: {valid}")
        return matches[0], seed

    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    weights = [score_style(style, material_type, tags) for style in styles]
    style = weighted_sample_without_replacement(styles, weights, 1, rng)[0]
    return style, seed


def infer_tags(query: str, material_summary: str, material_type: str) -> List[str]:
    text = f"{query}\n{material_summary}".lower()
    tags: List[str] = []

    if re.search(r"\b(llm|ai|language model|model|assistant|prompt|token|hallucination|context window|weights|embedding|alignment)\b", text):
        tags.append("ai-self-reflection")
    if re.search(r"\b(feel|feels|what it's like|what it is like|experience|inside|dream|confession|conscious|meaning|empathy|self-aware)\b", text):
        tags.append("interiority")
    if re.search(r"\b(news|headline|war|broadcast|breaking|ticker|emergency)\b", text):
        tags.append("news")
    if re.search(r"\b(browser|website|page|ui|interface|dialog|button|popup|notification)\b", text):
        tags.append("interface")
    if re.search(r"\b(code|repo|function|traceback|terminal|compile|build|error|exception|bug)\b", text):
        tags.append("code")
    if re.search(r"\b(metric|dashboard|counter|graph|chart|weight|probability|heatmap|attention)\b", text):
        tags.append("data")
    if re.search(r"\b(audio|voice|waveform|transcript|subtitle)\b", text):
        tags.append("audio")
    if re.search(r"\b(trailer|cinematic|prestige)\b", text):
        tags.append("trailer")
    if material_type == "webpage":
        tags.append("webpage")
        tags.append("interface")
    if material_type == "code":
        tags.append("code")
    if material_type == "audio":
        tags.append("audio")
    if material_type == "none":
        tags.append("interiority")
    if not tags:
        tags.append("any")
    return sorted(dict.fromkeys(tags))


def derive_subject_label(material_type: str, query: str, material_summary: str) -> str:
    explicit = (query or material_summary).strip()
    q = explicit.lower()
    m = re.search(r"what(?:'s| is) it like to be\s+([^?.!,]+)", q)
    if m:
        return f"being {m.group(1).strip()}"
    if re.search(r"\b(llm|language model)\b", q):
        return "being a language model"
    if re.search(r"\b(ai|assistant model|model)\b", q) and "self-aware" in q:
        return "being an AI system"
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
        return "the footage and its replayable moments"
    if material_type == "mixed":
        return "the mixed source material"
    if material_type == "none":
        return "the request itself"
    if explicit:
        return "the text"
    return "the material"


def extract_keywords(query: str, material_summary: str, limit: int = 8) -> List[str]:
    text = f"{query} {material_summary}".lower()
    words = re.findall(r"[a-z][a-z0-9\-]{2,}", text)
    cleaned: List[str] = []
    for word in words:
        if word in STOPWORDS:
            continue
        if word.startswith("http"):
            continue
        if word not in cleaned:
            cleaned.append(word)
        if len(cleaned) >= limit:
            break
    return cleaned


def scene_count_targets(duration_sec: int) -> Dict[str, int]:
    if duration_sec <= 28:
        target = 11
    elif duration_sec <= 40:
        target = 13
    else:
        target = 16

    opener = 1
    break_count = 1
    climax = 1
    button = 1
    bridges = 3 if target < 15 else 4
    anchors = target - (opener + break_count + climax + button + bridges)
    invented_support = max(3, bridges + 1)

    return {
        "target_scene_count": target,
        "anchor_scenes": anchors,
        "bridge_scenes": bridges,
        "break_scenes": break_count,
        "climax_scenes": climax,
        "button_scenes": button,
        "invented_support_scenes_min": invented_support,
    }


def score_atom(atom: Dict[str, Any], material_type: str, tags: List[str], style: Dict[str, Any]) -> int:
    score = 1
    best_for = set(atom.get("best_for", []))
    atom_tags = set(atom.get("tags", []))
    style_bias = set(style.get("scene_bias", []))

    if material_type in best_for:
        score += 4
    if "mixed" in best_for and material_type in {"text", "webpage", "code", "document", "none", "audio", "video", "image"}:
        score += 1
    if "none" in best_for and material_type == "none":
        score += 3
    if atom["id"] in style_bias:
        score += 3
    if "any" in atom_tags:
        score += 1
    score += len(set(tags) & atom_tags) * 2
    return max(score, 1)


def weighted_sample_without_replacement(candidates: List[Dict[str, Any]], weights: List[int], k: int, rng: random.Random) -> List[Dict[str, Any]]:
    if k <= 0 or not candidates:
        return []
    chosen: List[Dict[str, Any]] = []
    pool = list(candidates)
    pool_weights = list(weights)

    while pool and len(chosen) < k:
        total = sum(pool_weights)
        pick = rng.uniform(0, total)
        upto = 0.0
        index = 0
        for i, w in enumerate(pool_weights):
            upto += w
            if upto >= pick:
                index = i
                break
        chosen.append(pool.pop(index))
        pool_weights.pop(index)
    return chosen


def choose_scene_atoms(
    scene_atoms: List[Dict[str, Any]],
    material_type: str,
    tags: List[str],
    style: Dict[str, Any],
    duration_sec: int,
    seed: int | None,
) -> List[Dict[str, Any]]:
    counts = scene_count_targets(duration_sec)
    rng = random.Random(seed) if seed is not None else random.SystemRandom()

    by_role: Dict[str, List[Dict[str, Any]]] = {}
    for atom in scene_atoms:
        by_role.setdefault(atom["role"], []).append(atom)

    picked: List[Dict[str, Any]] = []
    role_sequence: List[str] = ["opener", "anchor"]

    remaining_anchors = max(0, counts["anchor_scenes"] - 1)
    remaining_bridges = counts["bridge_scenes"]

    while remaining_anchors > 0 or remaining_bridges > 0:
        if remaining_bridges > 0:
            role_sequence.append("bridge")
            remaining_bridges -= 1
        if remaining_anchors > 0:
            role_sequence.append("anchor")
            remaining_anchors -= 1

    role_sequence += ["break", "anchor", "climax", "button"]

    # Normalize total count to target while preserving the opening and ending shape.
    target = counts["target_scene_count"]
    while len(role_sequence) < target:
        role_sequence.insert(max(2, len(role_sequence) - 3), "anchor")
    while len(role_sequence) > target:
        try:
            idx = max(i for i, role in enumerate(role_sequence[:-3]) if role == "anchor")
            role_sequence.pop(idx)
        except ValueError:
            role_sequence.pop(-4)

    used_ids: set[str] = set()
    first_anchor_chosen = False
    for role in role_sequence:
        candidates = [atom for atom in by_role.get(role, []) if atom["id"] not in used_ids]
        if not candidates:
            candidates = list(by_role.get(role, []))

        if role == "anchor" and not first_anchor_chosen:
            preferred = [atom for atom in candidates if material_type in set(atom.get("best_for", []))]
            if preferred:
                candidates = preferred

        weights = [score_atom(atom, material_type, tags, style) for atom in candidates]
        choice = weighted_sample_without_replacement(candidates, weights, 1, rng)
        if not choice:
            continue
        atom = choice[0]
        used_ids.add(atom["id"])
        picked.append(atom)
        if role == "anchor":
            first_anchor_chosen = True

    return picked


def allocate_scene_durations(scenes: List[Dict[str, Any]], total_duration: int, rng: random.Random) -> List[float]:
    if not scenes:
        return []

    base_weights: List[float] = []
    for scene in scenes:
        role = scene["role"]
        lo, hi = scene.get("duration_hint_sec", [0.8, 1.5])
        midpoint = (float(lo) + float(hi)) / 2.0
        if role == "opener":
            midpoint *= 0.9
        elif role == "bridge":
            midpoint *= 0.75
        elif role == "break":
            midpoint *= 0.85
        elif role == "climax":
            midpoint *= 1.1
        elif role == "button":
            midpoint *= 0.95
        midpoint *= rng.uniform(0.92, 1.08)
        base_weights.append(midpoint)

    scale = total_duration / sum(base_weights)
    durations = [max(0.25, round(w * scale, 2)) for w in base_weights]

    # Correct rounding drift on the last scene.
    diff = round(total_duration - sum(durations), 2)
    durations[-1] = round(max(0.25, durations[-1] + diff), 2)
    return durations


def build_scene_swarm(
    scene_atoms: List[Dict[str, Any]],
    material_type: str,
    tags: List[str],
    style: Dict[str, Any],
    duration_sec: int,
    seed: int | None,
) -> List[Dict[str, Any]]:
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    picked = choose_scene_atoms(scene_atoms, material_type, tags, style, duration_sec, seed)
    durations = allocate_scene_durations(picked, duration_sec, rng)

    scene_swarm: List[Dict[str, Any]] = []
    cursor = 0.0
    for atom, dur in zip(picked, durations):
        start = round(cursor, 2)
        end = round(cursor + dur, 2)
        cursor = end
        scene_swarm.append(
            {
                "atom_id": atom["id"],
                "role": atom["role"],
                "start_sec": start,
                "end_sec": end,
                "duration_sec": round(dur, 2),
                "description": atom["description"],
                "visual_devices": atom.get("visual_devices", []),
                "audio_devices": atom.get("audio_devices", []),
            }
        )

    if scene_swarm:
        drift = round(duration_sec - scene_swarm[-1]["end_sec"], 2)
        scene_swarm[-1]["end_sec"] = round(scene_swarm[-1]["end_sec"] + drift, 2)
        scene_swarm[-1]["duration_sec"] = round(scene_swarm[-1]["duration_sec"] + drift, 2)

    return scene_swarm


def build_beats(duration_sec: int, material_type: str, style: Dict[str, Any]) -> List[Dict[str, Any]]:
    if duration_sec < 24:
        template = [
            ("hook", 0.14, "Open with the clearest absurd promise and strongest readable image."),
            ("premise", 0.18, "Show what is being remixed so the joke has grounding."),
            ("escalation-a", 0.18, "Repeat one motif with stronger framing or sound."),
            ("break", 0.12, "Let the eye and ear reset through stillness or dryness."),
            ("escalation-b", 0.18, "Increase contradiction, density, or authored attitude."),
            ("collapse", 0.12, "Peak the chosen blueprint with controlled overload."),
            ("button", 0.08, "End on a final thought, freeze, or failure message."),
        ]
    elif duration_sec <= 40:
        template = [
            ("hook", 0.12, "Open with the strongest absurd promise in under 1.5 seconds."),
            ("premise", 0.14, "Establish the source material or world clearly."),
            ("escalation-a", 0.15, "Create the first repeating motif."),
            ("escalation-b", 0.14, "Mutate the motif through a different visual system."),
            ("break", 0.10, "Insert a calm or deadpan reset."),
            ("escalation-c", 0.15, "Bring in a second-wave interruption or invented support scene."),
            ("collapse", 0.12, "Peak with the densest intentional composition."),
            ("button", 0.08, "Land a clean final payoff."),
        ]
    else:
        template = [
            ("hook", 0.10, "Open with a very strong first image and phrase."),
            ("premise", 0.12, "Make the source or world unmistakable."),
            ("escalation-a", 0.13, "Build the main motif."),
            ("escalation-b", 0.12, "Show the motif through a different frame system."),
            ("break", 0.09, "Give the eye and ear a reset."),
            ("escalation-c", 0.12, "Invent another support scene class."),
            ("escalation-d", 0.12, "Increase density or contradiction while keeping readability."),
            ("collapse", 0.12, "Peak the blueprint without flattening the frame."),
            ("button", 0.08, "Stop decisively."),
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
            "break": "Use a blank terminal, idle cursor, or one-line log as the reset.",
            "button": "Finish on an error, prompt, or absurd callback variable.",
        }
        return notes.get(beat_label, "Use code crops, logs, terminals, and cursor behavior as primary visual grammar.")
    if material_type in {"webpage", "url"}:
        notes = {
            "hook": "Start on the strongest headline, CTA, or visually loaded page region.",
            "premise": "Show enough page structure that the viewer understands the source.",
            "break": "Use a still browser frame or idle cursor beat.",
            "button": "End on a recontextualized button, dialog, or scroll snap.",
        }
        return notes.get(beat_label, "Use crops, cursor motion, scrolls, and annotations instead of full-page holds.")
    if material_type == "text":
        notes = {
            "hook": "Open with the sharpest phrase as large type or subtitle.",
            "premise": "Set the tone with a readable caption sequence or short voice line.",
            "break": "Use one sparse line on dark or empty space.",
            "button": "End on the shortest and hardest-hitting phrase.",
        }
        return notes.get(beat_label, "Let captions, title cards, subtitles, and invented UI scenes do most of the work.")
    if material_type == "none":
        notes = {
            "hook": "Invent a striking opening card or synthetic interface immediately.",
            "premise": "State the premise through warning cards, title frames, TTS, or mock UI.",
            "break": "Use negative space, a progress bar, or a near-silent subtitle hold.",
            "button": "End with a cursor, failure dialog, or final aphorism card.",
        }
        return notes.get(beat_label, "Build from original text, mock interfaces, diagrams, and sound design.")
    return "Use the dominant source type clearly and invent support scenes where needed."


def style_note_for_beat(style: Dict[str, Any], beat_label: str) -> str:
    if beat_label == "hook":
        return f"State {style['name']} immediately through palette, typography, and the first motion gesture."
    if beat_label == "break":
        return f"Keep the reset beat clean enough that the {style['name']} identity stays visible."
    if beat_label == "collapse":
        return f"Peak with {style['transitions'].split(',')[0].lower()} and a stronger pass of {style['audio'].split(',')[0].lower()} without losing readability."
    if beat_label == "button":
        return f"Let the ending feel like a distilled final gesture of {style['name']}."
    return f"Preserve the {style['name']} mood while still allowing source-specific invention."


def build_audio_plan(style: Dict[str, Any], tags: List[str], duration_sec: int) -> Dict[str, Any]:
    tts_count = 3 if duration_sec <= 28 else 4 if duration_sec <= 40 else 6
    voice_mode = "one main voice plus optional second system whisper"
    if "audio" in tags:
        voice_mode = "source audio first, TTS only for interruption or framing"

    return {
        "voice_mode": voice_mode,
        "tts_line_target": [2, tts_count],
        "processing_defaults": [
            "light band-limit or EQ shaping",
            "subtle pitch drop or stutter on selected words",
            "dropout or mute after one key line",
        ],
        "bed_elements": [
            "low drone",
            "UI clicks or relay ticks",
            "brief impacts",
            "one moment of near-silence",
        ],
        "mix_guardrails": [
            "Speech must remain understandable.",
            "Do not turn the whole piece into harsh distortion.",
            "Normalize the final mix.",
        ],
    }


def build_personal_spin_prompts(material_type: str, tags: List[str]) -> List[str]:
    prompts = [
        "What is the video actually claiming about the material?",
        "Which repeated line or symbol can carry that claim across multiple scenes?",
        "What final button would feel authored rather than generic?",
    ]
    if "ai-self-reflection" in tags:
        prompts.append("Which contradiction makes the machine voice feel intimate or unsettling?")
    if material_type == "webpage":
        prompts.append("Which page promise, CTA, or layout choice best represents the deeper joke?")
    if material_type == "code":
        prompts.append("Which log line, comment, or token feels most emotionally reusable?")
    return prompts


def make_plan(args: argparse.Namespace) -> Dict[str, Any]:
    styles = load_styles()
    scene_atoms = load_scene_atoms()

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

    tags = infer_tags(args.query, args.material_summary, material_type)
    style, seed_used = pick_style(styles, args.style_id or None, args.seed, material_type, tags)
    aspect_ratio, resolution = choose_aspect_ratio(args.query, args.aspect_ratio)

    if args.duration_sec < 12 or args.duration_sec > 90:
        raise SystemExit("Error: --duration-sec must be between 12 and 90 for this skill.")

    subject_label = derive_subject_label(material_type, args.query, args.material_summary)
    theme = args.theme.strip() if args.theme.strip() else subject_label
    thesis_starter = f"This video makes {theme} feel like {STYLE_ANALOGIES.get(style['id'], 'a designed collapse of meaning')}."
    keyword_candidates = extract_keywords(args.query, args.material_summary)

    swarm = build_scene_swarm(scene_atoms, material_type, tags, style, args.duration_sec, args.seed)
    density = scene_count_targets(args.duration_sec)
    beats = build_beats(args.duration_sec, material_type, style)

    plan: Dict[str, Any] = {
        "query": args.query,
        "material_summary": args.material_summary,
        "material_type": material_type,
        "tags": tags,
        "keyword_candidates": keyword_candidates,
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
        "scene_density": density,
        "scene_swarm": swarm,
        "beat_sheet": beats,
        "audio_plan": build_audio_plan(style, tags, args.duration_sec),
        "personal_spin_prompts": build_personal_spin_prompts(material_type, tags),
        "editing_rules": GENERAL_EDITING_RULES + ANTI_CARTOON_RULES + style.get("guardrails", []) + style.get("anti_patterns", []),
        "ffmpeg_hints": FFMPEG_HINTS,
        "quality_checks": QUALITY_CHECKS,
    }
    return plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Choose a remix-video mood blueprint and generate a structured production plan "
            "with scene density, scene atoms, and audio guidance."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 scripts/plan_video.py --query \"make a youtube poop about what it's like to be a LLM\"\n"
            "  python3 scripts/plan_video.py --query \"turn this landing page into a cursed short\" --material-summary \"https://example.com pricing page\"\n"
            "  python3 scripts/plan_video.py --material-type code --theme \"a codebase arguing with itself\" --style-id terminal-nocturne --duration-sec 38\n"
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
        default=34,
        help="Desired runtime in seconds. This skill is optimized for short 20–60 second pieces.",
    )
    parser.add_argument("--style-id", default="", help="Optional style id to override random selection.")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed for reproducible selection.")
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
