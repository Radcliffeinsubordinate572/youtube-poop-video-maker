#!/usr/bin/env python3
"""Render a terminal-styled montage about EU news on 2026-03-12."""

from __future__ import annotations

import math
import random
import subprocess
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION = 34.0
SAMPLE_RATE = 48_000

ROOT = Path(__file__).resolve().parents[1]
RENDER_DIR = ROOT / "render" / "eu_news_2026_03_12_terminal"
FRAME_DIR = RENDER_DIR / "frames"
AUDIO_DIR = RENDER_DIR / "audio"
EXPORT_DIR = ROOT / "exports"
OUTPUT_PATH = EXPORT_DIR / "eu-news-2026-03-12-terminal.mp4"

LABEL_FONT_PATH = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
MONO_FONT_PATH = "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"

PALETTE = {
    "bg": (4, 8, 10),
    "panel": (9, 16, 18),
    "panel2": (12, 22, 25),
    "line": (26, 48, 52),
    "white": (232, 239, 237),
    "muted": (129, 150, 147),
    "green": (137, 255, 173),
    "blue": (121, 217, 255),
    "amber": (244, 199, 104),
    "red": (255, 103, 103),
}

SCENES = [
    (0.00, 1.83, "boot"),
    (1.83, 6.16, "lords"),
    (6.16, 6.86, "cut"),
    (6.86, 10.48, "ukraine"),
    (10.48, 11.37, "notify"),
    (11.37, 14.93, "hungary"),
    (14.93, 15.72, "reset"),
    (15.72, 19.33, "poland"),
    (19.33, 23.27, "wave"),
    (23.27, 25.14, "break"),
    (25.14, 28.39, "quotes"),
    (28.39, 32.26, "climax"),
    (32.26, 34.00, "button"),
]

VOICE_LINES = [
    (0.70, "Booting Europe feed.", "Daniel", 0.92),
    (11.85, "Legacy, front line, fuel cap, blocked loans.", "Daniel", 0.82),
    (29.10, "The cursor keeps blinking.", "Daniel", 0.86),
]

SOURCE_NOTES = """# Sources used in the video

- Associated Press, March 12, 2026: Britain is ejecting hereditary nobles from Parliament after 700 years, with most hereditary peers already removed in 1999 and the remaining holdouts now targeted.
  https://apnews.com/article/uk-house-of-lords-hereditary-peers-expelled-535df8781dd01e8970acda1dca99d3d4
- Associated Press, March 12, 2026: Russia and Ukraine both claimed front-line progress while talks linked to U.S. mediation were delayed or shifted because of the regional crisis around Iran.
  https://apnews.com/article/russia-ukraine-war-talks-us-iran-f9069ab3f4cde813af0e6221daf6bf71
- Associated Press, March 12, 2026: Hungary said it would set a price cap on gasoline and diesel starting at midnight local time.
  https://apnews.com/article/hungary-orban-urges-eu-lift-russia-sanctions-af6d81352ca6333175afb49c552d11fa
- Associated Press, March 12, 2026: Polish President Karol Nawrocki refused to sign a law that would let Poland tap 44 billion euros in EU defense loans.
  https://apnews.com/article/poland-defense-european-union-loans-president-veto-c68b60654f1c4624009638ad8ecccec8
"""


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def ease_out_cubic(t: float) -> float:
    t = clamp(t, 0.0, 1.0)
    return 1 - (1 - t) ** 3


def hex_color(rgb: tuple[int, int, int], alpha: int = 255) -> tuple[int, int, int, int]:
    return (rgb[0], rgb[1], rgb[2], alpha)


@lru_cache(maxsize=64)
def font(role: str, size: int) -> ImageFont.FreeTypeFont:
    path = MONO_FONT_PATH if role == "mono" else LABEL_FONT_PATH
    return ImageFont.truetype(path, size=size)


def ensure_dirs() -> None:
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def create_background(accent: tuple[int, int, int], accent2: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), hex_color(PALETTE["bg"]))
    draw = ImageDraw.Draw(img)
    top = np.array(PALETTE["bg"], dtype=np.float32)
    bottom = np.array(PALETTE["panel2"], dtype=np.float32)
    for y in range(0, HEIGHT, 6):
        blend = y / max(1, HEIGHT - 1)
        color = tuple(int(v) for v in top * (1 - blend) + bottom * blend)
        draw.rectangle((0, y, WIDTH, y + 6), fill=hex_color(color))
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse((-220, 30, 760, 780), fill=hex_color(accent, 48))
    gdraw.ellipse((WIDTH - 920, -80, WIDTH + 60, 740), fill=hex_color(accent2, 42))
    gdraw.rectangle((0, HEIGHT - 220, WIDTH, HEIGHT), fill=hex_color(accent2, 14))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    img.alpha_composite(glow)
    return img


def create_scanlines(alpha: int) -> Image.Image:
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(0, HEIGHT, 4):
        draw.line((0, y, WIDTH, y), fill=(255, 255, 255, alpha), width=1)
    return overlay


def create_grid(color: tuple[int, int, int], alpha: int = 22) -> Image.Image:
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rgba = hex_color(color, alpha)
    for x in range(0, WIDTH, 96):
        draw.line((x, 0, x, HEIGHT), fill=rgba, width=1)
    for y in range(0, HEIGHT, 68):
        draw.line((0, y, WIDTH, y), fill=rgba, width=1)
    return overlay


def create_vignette() -> Image.Image:
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 84))
    draw.rounded_rectangle((84, 60, WIDTH - 84, HEIGHT - 60), radius=34, fill=(0, 0, 0, 0))
    return overlay.filter(ImageFilter.GaussianBlur(26))


BG_GREEN = create_background(PALETTE["green"], PALETTE["blue"])
BG_BLUE = create_background(PALETTE["blue"], PALETTE["green"])
BG_AMBER = create_background(PALETTE["amber"], PALETTE["green"])
BG_RED = create_background(PALETTE["red"], PALETTE["blue"])
SCAN_SOFT = create_scanlines(10)
SCAN_MED = create_scanlines(16)
GRID_GREEN = create_grid(PALETTE["green"])
GRID_BLUE = create_grid(PALETTE["blue"])
GRID_AMBER = create_grid(PALETTE["amber"])
GRID_RED = create_grid(PALETTE["red"])
VIGNETTE = create_vignette()


def base_frame(kind: str, scans: bool = False) -> Image.Image:
    if kind == "green":
        img = BG_GREEN.copy()
    elif kind == "amber":
        img = BG_AMBER.copy()
    elif kind == "red":
        img = BG_RED.copy()
    else:
        img = BG_BLUE.copy()
    if scans:
        img.alpha_composite(SCAN_SOFT)
    img.alpha_composite(VIGNETTE)
    return img


def draw_shell_header(draw: ImageDraw.ImageDraw, left: str, right: str, accent: tuple[int, int, int]) -> None:
    draw.rounded_rectangle((54, 36, WIDTH - 54, 90), radius=16, fill=hex_color(PALETTE["panel"], 224), outline=hex_color(PALETTE["line"], 220), width=2)
    draw.ellipse((78, 53, 94, 69), fill=hex_color(PALETTE["red"]))
    draw.ellipse((108, 53, 124, 69), fill=hex_color(PALETTE["amber"]))
    draw.ellipse((138, 53, 154, 69), fill=hex_color(PALETTE["green"]))
    draw.text((186, 48), left, font=font("mono", 28), fill=hex_color(PALETTE["white"]))
    draw.text((WIDTH - 420, 48), right, font=font("mono", 28), fill=hex_color(accent))


def draw_window(img: Image.Image, box: tuple[int, int, int, int], title: str, accent: tuple[int, int, int], active: bool = False) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    fill_alpha = 230 if active else 208
    draw.rounded_rectangle(box, radius=22, fill=hex_color(PALETTE["panel"], fill_alpha), outline=hex_color(accent, 210), width=3)
    draw.rectangle((box[0], box[1], box[2], box[1] + 48), fill=hex_color(accent, 36))
    draw.text((box[0] + 24, box[1] + 9), title, font=font("mono", 28), fill=hex_color(PALETTE["white"]))


def draw_prompt(draw: ImageDraw.ImageDraw, x: int, y: int, command: str, accent: tuple[int, int, int]) -> int:
    prompt = "eu@night:~$"
    draw.text((x, y), prompt, font=font("mono", 34), fill=hex_color(accent))
    start_x = x + int(draw.textlength(prompt + " ", font=font("mono", 34)))
    draw.text((start_x, y), command, font=font("mono", 34), fill=hex_color(PALETTE["white"]))
    return start_x


def draw_cursor(draw: ImageDraw.ImageDraw, x: int, y: int, h: int, color: tuple[int, int, int], on: bool) -> None:
    if on:
        draw.rectangle((x, y, x + 14, y + h), fill=hex_color(color))


def draw_lines(draw: ImageDraw.ImageDraw, x: int, y: int, lines: list[tuple[str, tuple[int, int, int]]], size: int, spacing: int = 12) -> None:
    yy = y
    for text, color in lines:
        draw.text((x, yy), text, font=font("mono", size), fill=hex_color(color))
        yy += size + spacing


def draw_progress(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], pct: float, accent: tuple[int, int, int], label: str) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=14, fill=hex_color(PALETTE["panel2"], 220), outline=hex_color(PALETTE["line"], 220), width=2)
    draw.text((x0 + 18, y0 + 10), label, font=font("mono", 24), fill=hex_color(PALETTE["muted"]))
    bar = (x0 + 18, y1 - 28, x1 - 18, y1 - 10)
    draw.rounded_rectangle(bar, radius=8, fill=hex_color(PALETTE["bg"]))
    fill_w = int((bar[2] - bar[0]) * clamp(pct, 0.0, 1.0))
    draw.rounded_rectangle((bar[0], bar[1], bar[0] + fill_w, bar[3]), radius=8, fill=hex_color(accent))


def draw_popup(img: Image.Image, box: tuple[int, int, int, int], title: str, body: str, accent: tuple[int, int, int]) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle(box, radius=20, fill=hex_color(PALETTE["panel"], 236), outline=hex_color(accent, 210), width=2)
    draw.rectangle((box[0], box[1], box[2], box[1] + 42), fill=hex_color(accent, 44))
    draw.text((box[0] + 18, box[1] + 8), title, font=font("mono", 24), fill=hex_color(PALETTE["white"]))
    draw.multiline_text((box[0] + 18, box[1] + 62), body, font=font("mono", 24), fill=hex_color(PALETTE["white"]), spacing=8)


def add_glitch(img: Image.Image, frame_idx: int, accent: tuple[int, int, int], count: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(frame_idx * 19 + count)
    for _ in range(count):
        x = rng.randint(70, WIDTH - 280)
        y = rng.randint(120, HEIGHT - 150)
        w = rng.randint(140, 420)
        h = rng.randint(4, 18)
        fill = hex_color(accent if rng.random() > 0.5 else PALETTE["white"], rng.randint(36, 110))
        draw.rectangle((x, y, x + w, y + h), fill=fill)


def draw_wave(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], t: float, accent: tuple[int, int, int]) -> None:
    x0, y0, x1, y1 = box
    mid = (y0 + y1) // 2
    points = []
    steps = 90
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        wave_a = math.sin(t * 3.6 + i * 0.24) * 34
        wave_b = math.sin(t * 7.4 + i * 0.51) * 10
        y = mid + wave_a + wave_b
        points.append((x, y))
    draw.line(points, fill=hex_color(accent), width=4)
    draw.line((x0, mid, x1, mid), fill=hex_color(PALETTE["line"], 180), width=1)


def render_boot(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    img.alpha_composite(SCAN_MED)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_shell_header(draw, "~/feeds/eu", "SESSION 03.12.2026", PALETTE["green"])
    box = (126, 154, WIDTH - 126, HEIGHT - 188)
    draw_window(img, box, "boot.log", PALETTE["green"], active=True)
    logs = [
        "[ok] init /feeds/eu",
        "[ok] mount parliament.db",
        "[ok] sync frontline.sock",
        "[ok] attach fuel-cap.alerts",
        "[ok] attach defense-loans.pipe",
        "[warn] legacy process still running",
        "[live] tail -f /var/log/europe.feed",
    ]
    visible = max(2, min(len(logs), int(2 + p * len(logs))))
    lines = [(line, PALETTE["green"] if "[ok]" in line or "[live]" in line else PALETTE["amber"]) for line in logs[:visible]]
    draw_lines(draw, 168, 236, lines, 38, spacing=14)
    draw.text((164, 664), "EU.FEED", font=font("label", 188), fill=hex_color(PALETTE["white"]))
    tail = "tail -f /var/log/europe.feed"
    cx = draw_prompt(draw, 170, 844, tail, PALETTE["green"])
    draw_cursor(draw, cx + int(draw.textlength(tail, font=font("mono", 34))) + 6, 846, 34, PALETTE["green"], frame_idx % 18 < 10)


def render_lords(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    img.alpha_composite(GRID_GREEN)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_shell_header(draw, "~/feeds/eu/uk", "HOUSE-OF-LORDS.LOG", PALETTE["green"])
    left = (90, 148, 1108, 924)
    right = (1142, 148, 1830, 924)
    draw_window(img, left, "sudo purge peers --hereditary", PALETTE["green"], active=True)
    draw_window(img, right, "legacy.status", PALETTE["amber"])
    cmd = "sudo purge peers --hereditary --after 700y"
    cx = draw_prompt(draw, 124, 214, cmd, PALETTE["green"])
    draw_cursor(draw, cx + int(draw.textlength(cmd, font=font("mono", 34))) + 8, 216, 34, PALETTE["green"], frame_idx % 20 < 11)
    lines = [
        ("-> most hereditary peers removed in 1999", PALETTE["white"]),
        ("-> remaining holdouts now targeted", PALETTE["white"]),
        ("-> chamber still processing centuries of cache", PALETTE["muted"]),
        ("status: reform live", PALETTE["green"]),
    ]
    draw_lines(draw, 126, 302, lines, 32, spacing=18)
    draw.text((124, 514), "700 YEARS", font=font("label", 156), fill=hex_color(PALETTE["white"]))
    draw.text((124, 670), "OUTDATED PROCESS", font=font("label", 112), fill=hex_color(PALETTE["green"]))
    fact_lines = [
        ("legacy_house=true", PALETTE["amber"]),
        ("peer_cache=partial", PALETTE["white"]),
        ("manual_override=parliament", PALETTE["white"]),
        ("deprecation_notice=active", PALETTE["green"]),
    ]
    draw_lines(draw, 1180, 234, fact_lines, 28, spacing=16)
    draw.text((1180, 452), "1999", font=font("label", 126), fill=hex_color(PALETTE["amber"]))
    draw.text((1180, 582), "MOST PEERS", font=font("label", 74), fill=hex_color(PALETTE["white"]))
    draw.text((1180, 650), "REMOVED", font=font("label", 98), fill=hex_color(PALETTE["white"]))
    draw_progress(draw, (1180, 782, 1768, 860), 0.84 + 0.04 * math.sin(t * 2.6), PALETTE["green"], "reform.apply")


def render_cut(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=hex_color(PALETTE["bg"], 245))
    add_glitch(img, frame_idx, PALETTE["green"], 18)
    draw.text((200, 338), "REC 00:06:16", font=font("mono", 84), fill=hex_color(PALETTE["white"]))
    draw.text((200, 496), "context switch", font=font("label", 118), fill=hex_color(PALETTE["green"]))


def render_ukraine(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    img.alpha_composite(GRID_BLUE)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_shell_header(draw, "~/feeds/eu/frontline", "watch -n1 talks.queue", PALETTE["blue"])
    left = (90, 146, 960, 936)
    right = (996, 146, 1830, 936)
    draw_window(img, left, "frontline.status", PALETTE["blue"], active=True)
    draw_window(img, right, "talks.queue", PALETTE["amber"])
    draw.text((132, 220), "both sides claim progress", font=font("label", 88), fill=hex_color(PALETTE["white"]))
    draw_progress(draw, (136, 360, 892, 440), 0.61 + 0.04 * math.sin(t * 2.2), PALETTE["red"], "moscow.push")
    draw_progress(draw, (136, 476, 892, 556), 0.57 + 0.05 * math.sin(t * 2.7), PALETTE["blue"], "kyiv.push")
    draw_lines(
        draw,
        136,
        630,
        [
            ("front_line=hot", PALETTE["red"]),
            ("claims=conflicting", PALETTE["white"]),
            ("map=still moving", PALETTE["muted"]),
        ],
        30,
        spacing=14,
    )
    cmd = "queue talks --venue turkey --status delayed"
    draw_prompt(draw, 1034, 224, cmd, PALETTE["blue"])
    draw_lines(
        draw,
        1034,
        316,
        [
            ("venue: shifting", PALETTE["amber"]),
            ("cause: regional crisis around Iran", PALETTE["white"]),
            ("state: on hold / re-route pending", PALETTE["muted"]),
            ("operator note: diplomacy interrupted", PALETTE["amber"]),
        ],
        28,
        spacing=18,
    )
    draw.text((1034, 620), "TALKS", font=font("label", 152), fill=hex_color(PALETTE["white"]))
    draw.text((1034, 764), "ON HOLD", font=font("label", 174), fill=hex_color(PALETTE["amber"]))


def render_notify(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    draw_shell_header(draw, "~/feeds/eu", "NOTIFICATION BURST", PALETTE["amber"])
    popups = [
        ((164, 208, 704, 402), "alert.legacy", "peer process\nstill active", PALETTE["green"]),
        ((540, 430, 1090, 642), "alert.route", "talks venue\nchanged", PALETTE["blue"]),
        ((1112, 248, 1716, 474), "alert.fuel", "cap begins\n00:00 local", PALETTE["amber"]),
        ((980, 622, 1764, 864), "alert.loans", "44B request\nsignature missing", PALETTE["red"]),
    ]
    for idx, (box, title, body, accent) in enumerate(popups):
        x_jitter = int(10 * math.sin(t * 8 + idx))
        y_jitter = int(8 * math.cos(t * 6 + idx))
        moved = (box[0] + x_jitter, box[1] + y_jitter, box[2] + x_jitter, box[3] + y_jitter)
        draw_popup(img, moved, title, body, accent)


def render_hungary(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    img.alpha_composite(GRID_AMBER)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_shell_header(draw, "~/feeds/eu/hungary", "grep -n price_cap fuel.log", PALETTE["amber"])
    box = (90, 148, 1830, 930)
    draw_window(img, box, "fuel.log", PALETTE["amber"], active=True)
    cmd = "grep -n \"price cap\" /feeds/eu/hungary/fuel.log"
    draw_prompt(draw, 126, 210, cmd, PALETTE["amber"])
    draw_lines(
        draw,
        126,
        300,
        [
            ("241: government says cap starts at midnight local", PALETTE["white"]),
            ("242: target fuels: gasoline, diesel", PALETTE["white"]),
            ("243: operator: Viktor Orban", PALETTE["muted"]),
            ("244: motive: shield drivers from price shock", PALETTE["muted"]),
        ],
        32,
        spacing=18,
    )
    draw.text((120, 516), "PRICE CAP", font=font("label", 182), fill=hex_color(PALETTE["amber"]))
    draw.text((126, 686), "00:00", font=font("label", 190), fill=hex_color(PALETTE["white"]))
    draw.text((1180, 272), "gasoline", font=font("mono", 56), fill=hex_color(PALETTE["amber"]))
    draw.text((1180, 364), "diesel", font=font("mono", 56), fill=hex_color(PALETTE["amber"]))
    draw.text((1180, 510), "effective_at=midnight_local", font=font("mono", 34), fill=hex_color(PALETTE["white"]))
    draw_progress(draw, (1180, 700, 1760, 782), 0.94, PALETTE["amber"], "policy.apply")
    add_glitch(img, frame_idx, PALETTE["amber"], 5)


def render_reset(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=hex_color(PALETTE["bg"], 240))
    draw.text((140, 366), "connection reset by peer", font=font("mono", 86), fill=hex_color(PALETTE["white"]))
    draw.text((144, 540), "reopening eu.feed...", font=font("label", 96), fill=hex_color(PALETTE["amber"]))
    add_glitch(img, frame_idx, PALETTE["amber"], 12)


def render_poland(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    img.alpha_composite(GRID_RED)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_shell_header(draw, "~/feeds/eu/poland", "tmux attach defense-session", PALETTE["red"])
    boxes = [
        (90, 148, 942, 560),
        (978, 148, 1830, 560),
        (90, 598, 1830, 930),
    ]
    titles = ["loan_request.yaml", "signature.status", "console"]
    accents = [PALETTE["blue"], PALETTE["red"], PALETTE["amber"]]
    for box, title, accent in zip(boxes, titles, accents):
        draw_window(img, box, title, accent, active=True)
    draw_lines(
        draw,
        126,
        216,
        [
            ("defense_loans: 44000000000", PALETTE["white"]),
            ("unit: euros", PALETTE["muted"]),
            ("source: EU defense facility", PALETTE["blue"]),
        ],
        30,
        spacing=16,
    )
    draw.text((1018, 230), "signed=false", font=font("mono", 56), fill=hex_color(PALETTE["red"]))
    draw.text((1018, 332), "status=veto", font=font("mono", 56), fill=hex_color(PALETTE["red"]))
    draw.text((1018, 438), "actor=Nawrocki", font=font("mono", 38), fill=hex_color(PALETTE["white"]))
    cmd = "cat /feeds/eu/poland/defense.log"
    draw_prompt(draw, 124, 658, cmd, PALETTE["amber"])
    draw_lines(
        draw,
        124,
        742,
        [
            ("-> law not signed", PALETTE["white"]),
            ("-> 44 billion euros remain blocked", PALETTE["white"]),
            ("-> security spending waits on politics", PALETTE["muted"]),
        ],
        34,
        spacing=18,
    )


def render_wave(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    draw_shell_header(draw, "~/feeds/eu", "grep -E '700y|hold|00:00|44B' report.log", PALETTE["green"])
    draw_window(img, (82, 138, 1838, 936), "aggregate.signal", PALETTE["green"], active=True)
    draw_wave(draw, (118, 248, 1798, 480), t, PALETTE["green"])
    draw_lines(
        draw,
        128,
        564,
        [
            ("700 years   -> legacy process", PALETTE["white"]),
            ("talks hold   -> venue unstable", PALETTE["blue"]),
            ("00:00 local  -> fuel cap starts", PALETTE["amber"]),
            ("44B euros    -> defense loans blocked", PALETTE["red"]),
        ],
        34,
        spacing=18,
    )
    draw.text((124, 812), "THE FEED DOES NOT CALM DOWN", font=font("label", 120), fill=hex_color(PALETTE["white"]))


def render_break(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    draw_shell_header(draw, "~/feeds/eu", "waiting...", PALETTE["muted"])
    draw_window(img, (286, 302, 1634, 772), "consensus.wait", PALETTE["line"], active=True)
    pct = 0.04 + 0.02 * math.sin(t * 3.0)
    draw.text((378, 402), "waiting for consensus", font=font("label", 136), fill=hex_color(PALETTE["white"]))
    draw_progress(draw, (382, 576, 1522, 666), pct, PALETTE["green"], "progress")
    draw_cursor(draw, 1528, 610, 34, PALETTE["green"], frame_idx % 20 < 10)


def render_quotes(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    img.alpha_composite(SCAN_MED)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_shell_header(draw, "~/feeds/eu", "monitored excerpts", PALETTE["blue"])
    draw_window(img, (122, 156, 1792, 906), "quotes.capture", PALETTE["blue"], active=True)
    quotes = [
        ("\"after 700 years\"", PALETTE["green"]),
        ("\"talks on hold\"", PALETTE["amber"]),
        ("\"midnight local\"", PALETTE["amber"]),
        ("\"44 billion euros\"", PALETTE["red"]),
    ]
    y = 246
    for idx, (text, accent) in enumerate(quotes):
        box = (176, y, 1608, y + 118)
        draw.rounded_rectangle(box, radius=18, fill=hex_color(PALETTE["panel2"], 224), outline=hex_color(accent, 200), width=2)
        draw.text((212, y + 24), text, font=font("label", 94), fill=hex_color(PALETTE["white"]))
        y += 150
    cross_x = 1500 + int(18 * math.sin(t * 5))
    draw.line((cross_x - 44, 240, cross_x + 44, 240), fill=hex_color(PALETTE["blue"], 180), width=2)
    draw.line((cross_x, 196, cross_x, 284), fill=hex_color(PALETTE["blue"], 180), width=2)


def render_climax(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    img.alpha_composite(GRID_GREEN)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_shell_header(draw, "~/feeds/eu", "watch -n1 europe-feed --all", PALETTE["green"])
    quads = [
        ((84, 154, 900, 510), "legacy.peers", PALETTE["green"], ["700y purge", "peer_cache stale"]),
        ((1020, 154, 1836, 510), "frontline.talks", PALETTE["blue"], ["claims up", "venue hold"]),
        ((84, 564, 900, 920), "fuel.cap", PALETTE["amber"], ["00:00 local", "gasoline diesel"]),
        ((1020, 564, 1836, 920), "defense.loans", PALETTE["red"], ["44B pending", "signed=false"]),
    ]
    for box, title, accent, lines in quads:
        draw_window(img, box, title, accent, active=True)
        draw.text((box[0] + 28, box[1] + 96), lines[0], font=font("label", 98), fill=hex_color(PALETTE["white"]))
        draw.text((box[0] + 30, box[1] + 218), lines[1], font=font("mono", 42), fill=hex_color(accent))
    draw.text((154, 52), "", font=font("mono", 24), fill=hex_color(PALETTE["white"]))
    add_glitch(img, frame_idx, PALETTE["green"], 18)
    add_glitch(img, frame_idx + 4, PALETTE["red"], 9)
    draw.text((354, 446), "NO SINGLE HEADLINE", font=font("label", 126), fill=hex_color(PALETTE["white"], 236))


def render_button(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=hex_color(PALETTE["bg"], 244))
    box = (268, 258, 1654, 810)
    draw_window(img, box, "eu.feed", PALETTE["green"], active=True)
    draw.text((346, 366), "exit 0", font=font("label", 148), fill=hex_color(PALETTE["green"]))
    draw.text((346, 516), "warnings remain", font=font("label", 166), fill=hex_color(PALETTE["white"]))
    tail = "tail -f /var/log/europe.feed"
    cx = draw_prompt(draw, 350, 668, tail, PALETTE["green"])
    draw_cursor(draw, cx + int(draw.textlength(tail, font=font("mono", 34))) + 8, 670, 34, PALETTE["green"], True)


def render_scene_frame(global_t: float, frame_idx: int) -> Image.Image:
    for start, end, scene_id in SCENES:
        if global_t < end or math.isclose(global_t, end):
            local_t = global_t - start
            p = clamp(local_t / max(end - start, 0.001), 0.0, 1.0)
            break
    else:
        scene_id = SCENES[-1][2]
        p = 1.0

    if scene_id == "boot":
        img = base_frame("blue", scans=True)
        render_boot(img, global_t, p, frame_idx)
    elif scene_id == "lords":
        img = base_frame("green")
        render_lords(img, global_t, p, frame_idx)
    elif scene_id == "cut":
        img = base_frame("green")
        render_cut(img, global_t, p, frame_idx)
    elif scene_id == "ukraine":
        img = base_frame("blue")
        render_ukraine(img, global_t, p, frame_idx)
    elif scene_id == "notify":
        img = base_frame("blue")
        render_notify(img, global_t, p, frame_idx)
    elif scene_id == "hungary":
        img = base_frame("amber")
        render_hungary(img, global_t, p, frame_idx)
    elif scene_id == "reset":
        img = base_frame("amber")
        render_reset(img, global_t, p, frame_idx)
    elif scene_id == "poland":
        img = base_frame("red")
        render_poland(img, global_t, p, frame_idx)
    elif scene_id == "wave":
        img = base_frame("green")
        render_wave(img, global_t, p, frame_idx)
    elif scene_id == "break":
        img = base_frame("blue")
        render_break(img, global_t, p, frame_idx)
    elif scene_id == "quotes":
        img = base_frame("blue")
        render_quotes(img, global_t, p, frame_idx)
    elif scene_id == "climax":
        img = base_frame("green")
        render_climax(img, global_t, p, frame_idx)
    else:
        img = base_frame("green")
        render_button(img, global_t, p, frame_idx)
    return img.convert("RGB")


def render_frames() -> None:
    total_frames = int(DURATION * FPS)
    for frame_idx in range(total_frames):
        t = frame_idx / FPS
        img = render_scene_frame(t, frame_idx)
        img.save(FRAME_DIR / f"frame_{frame_idx:05d}.png", optimize=True)


def add_tone(buffer: np.ndarray, start: float, duration: float, freq: float, amp: float, wobble: float = 0.0, phase: float = 0.0) -> None:
    start_idx = int(start * SAMPLE_RATE)
    end_idx = min(len(buffer), int((start + duration) * SAMPLE_RATE))
    if end_idx <= start_idx:
        return
    idx = np.arange(end_idx - start_idx)
    t = idx / SAMPLE_RATE
    env = np.minimum(1.0, np.minimum(t / 0.03, (duration - t) / 0.10))
    env = np.clip(env, 0.0, 1.0)
    freq_curve = freq + wobble * np.sin(2 * math.pi * 0.8 * t + phase)
    wave_data = np.sin(2 * math.pi * freq_curve * t + phase)
    buffer[start_idx:end_idx] += amp * env * wave_data


def add_noise(buffer: np.ndarray, start: float, duration: float, amp: float, seed: int) -> None:
    start_idx = int(start * SAMPLE_RATE)
    end_idx = min(len(buffer), int((start + duration) * SAMPLE_RATE))
    if end_idx <= start_idx:
        return
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, 1.0, end_idx - start_idx)
    t = np.linspace(0.0, duration, end_idx - start_idx, endpoint=False)
    env = np.minimum(1.0, np.minimum(t / 0.02, (duration - t) / 0.05))
    buffer[start_idx:end_idx] += amp * env * noise


def add_click(buffer: np.ndarray, start: float, freq: float, amp: float) -> None:
    add_tone(buffer, start, 0.03, freq, amp, wobble=8.0)


def generate_audio_bed() -> Path:
    samples = int(DURATION * SAMPLE_RATE)
    audio = np.zeros(samples, dtype=np.float32)
    add_tone(audio, 0.0, DURATION, 47.0, 0.085, wobble=1.2, phase=0.2)
    add_tone(audio, 0.0, DURATION, 94.0, 0.020, wobble=2.5, phase=0.8)
    add_tone(audio, 19.33, 3.7, 138.0, 0.028, wobble=7.5, phase=1.4)
    add_tone(audio, 28.39, 3.4, 58.0, 0.070, wobble=4.0, phase=0.6)

    for mark in [0.0, 1.83, 6.16, 6.86, 10.48, 11.37, 14.93, 15.72, 19.33, 23.27, 25.14, 28.39, 32.26]:
        add_click(audio, mark, 1080.0, 0.060)
        add_noise(audio, mark, 0.04, 0.010, int(mark * 1000) + 3)

    for mark in np.arange(2.1, 5.6, 0.26):
        add_click(audio, float(mark), 1480.0, 0.012)
    for mark in np.arange(16.0, 18.3, 0.24):
        add_click(audio, float(mark), 1260.0, 0.010)

    add_noise(audio, 10.48, 0.80, 0.010, 44)
    add_noise(audio, 14.93, 0.50, 0.016, 59)
    audio = np.clip(audio, -0.82, 0.82)

    stereo = np.empty((samples, 2), dtype=np.float32)
    stereo[:, 0] = audio
    stereo[:, 1] = np.roll(audio, 160) * 0.95
    path = AUDIO_DIR / "bed.wav"
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = np.clip(stereo * 32767, -32768, 32767).astype(np.int16)
        wav.writeframes(frames.tobytes())
    return path


def generate_tts_assets() -> list[Path]:
    paths: list[Path] = []
    for idx, (_, line, voice, _) in enumerate(VOICE_LINES, start=1):
        out_path = AUDIO_DIR / f"voice_{idx:02d}.aiff"
        subprocess.run(["say", "-v", voice, line, "-o", str(out_path)], check=True)
        paths.append(out_path)
    return paths


def encode_video() -> Path:
    silent_path = RENDER_DIR / "video_silent.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(FRAME_DIR / "frame_%05d.png"),
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "medium",
            "-pix_fmt",
            "yuv420p",
            str(silent_path),
        ],
        check=True,
    )
    return silent_path


def mix_audio(bed_path: Path, voices: list[Path]) -> Path:
    mixed_path = AUDIO_DIR / "mix.wav"
    inputs = ["ffmpeg", "-y", "-i", str(bed_path)]
    for voice in voices:
        inputs += ["-i", str(voice)]

    filters = ["[0:a]volume=0.86[a0]"]
    labels = ["[a0]"]
    for idx, (delay, _, _, level) in enumerate(VOICE_LINES, start=1):
        ms = int(delay * 1000)
        voice_filter = (
            f"[{idx}:a]aresample={SAMPLE_RATE},highpass=f=170,lowpass=f=3300,"
            f"volume={level},adelay={ms}|{ms}"
        )
        if idx == len(VOICE_LINES):
            voice_filter += f",asetrate={int(SAMPLE_RATE * 0.95)},aresample={SAMPLE_RATE}"
        voice_filter += f"[a{idx}]"
        filters.append(voice_filter)
        labels.append(f"[a{idx}]")
    filters.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,alimiter=limit=0.88[aout]")

    subprocess.run(
        inputs
        + [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[aout]",
            "-c:a",
            "pcm_s16le",
            str(mixed_path),
        ],
        check=True,
    )
    return mixed_path


def finalize(video_path: Path, audio_path: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(audio_path),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-vf",
            "format=yuv420p",
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "medium",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            str(SAMPLE_RATE),
            "-movflags",
            "+faststart",
            str(OUTPUT_PATH),
        ],
        check=True,
    )


def write_notes() -> None:
    (RENDER_DIR / "sources.md").write_text(SOURCE_NOTES, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    write_notes()
    render_frames()
    bed = generate_audio_bed()
    voices = generate_tts_assets()
    silent_video = encode_video()
    mixed_audio = mix_audio(bed, voices)
    finalize(silent_video, mixed_audio)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
