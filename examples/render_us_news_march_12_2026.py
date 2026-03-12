#!/usr/bin/env python3
"""Render a short broadcast-fever-dream montage about U.S. news on 2026-03-12."""

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
DURATION = 36.0
SAMPLE_RATE = 48_000

ROOT = Path(__file__).resolve().parents[1]
RENDER_DIR = ROOT / "render" / "us_news_2026_03_12"
FRAME_DIR = RENDER_DIR / "frames"
AUDIO_DIR = RENDER_DIR / "audio"
EXPORT_DIR = ROOT / "exports"
OUTPUT_PATH = EXPORT_DIR / "us-news-2026-03-12.mp4"

HEADLINE_FONT_PATH = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
BODY_FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO_FONT_PATH = "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"

PALETTE = {
    "bg": (10, 13, 18),
    "panel": (18, 24, 32),
    "panel_bright": (28, 36, 46),
    "white": (238, 240, 244),
    "muted": (156, 165, 178),
    "red": (255, 78, 74),
    "cyan": (74, 214, 255),
    "amber": (255, 203, 96),
    "storm": (255, 116, 58),
    "green": (145, 255, 165),
}

SCENES = [
    (0.00, 1.78, "opener"),
    (1.78, 5.50, "drone"),
    (5.50, 6.30, "signal"),
    (6.30, 10.18, "cpi"),
    (10.18, 10.80, "burst"),
    (10.80, 14.56, "storm"),
    (14.56, 15.31, "meanwhile"),
    (15.31, 19.99, "shutdown"),
    (19.99, 23.97, "dashboard"),
    (23.97, 26.34, "break"),
    (26.34, 29.68, "stack"),
    (29.68, 34.09, "climax"),
    (34.09, 36.00, "button"),
]

VOICE_LINES = [
    (0.55, "March twelfth. America in four tabs.", "Samantha", 1.0),
    (7.05, "Inflation cooled. The room did not.", "Samantha", 0.96),
    (15.55, "Storms. Shutdowns. Drone alerts. Delays.", "Samantha", 0.93),
    (30.05, "No single headline can hold the temperature.", "Samantha", 0.92),
]

SOURCE_NOTES = """# Sources used in the video

- ABC7 Los Angeles, March 12, 2026: FBI bulletin warned Iran allegedly aspired to target California with drones if the U.S. struck Iran.
  https://abc7.com/post/live-updates-war-iran-president-trump-shares-us-strategy-amid-israeli-airstrikes/17372542/
- U.S. Bureau of Labor Statistics CPI release for February 2026, published March 11, 2026: CPI rose 0.3 percent in February and 2.4 percent over the prior 12 months; core CPI rose 0.2 percent on the month and 2.5 percent over the year.
  https://www.bls.gov/news.release/cpi.nr0.htm
- Associated Press, March 12, 2026: a married Indiana couple in their 80s were killed after a tornado hit their home, with about 65 million people under severe weather threat.
  https://apnews.com/article/tornado-severe-weather-illinois-indiana-midwest-dce09b60816c498aad9c2a79c18285c1
- ABC News, March 12, 2026: partial DHS shutdown doubled TSA employee callouts, more than 300 TSA officers quit, and some airport wait times reached two hours.
  https://abcnews.com/GMA/Travel/tsa-officer-callouts-spike-amid-partial-government-shutdown/story?id=130963401
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
    path = {
        "headline": HEADLINE_FONT_PATH,
        "body": BODY_FONT_PATH,
        "mono": MONO_FONT_PATH,
    }[role]
    return ImageFont.truetype(path, size=size)


def ensure_dirs() -> None:
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def create_scanline_overlay() -> Image.Image:
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(0, HEIGHT, 4):
        draw.rectangle((0, y, WIDTH, y + 1), fill=(255, 255, 255, 11))
    for y in range(2, HEIGHT, 8):
        draw.rectangle((0, y, WIDTH, y + 2), fill=(0, 0, 0, 16))
    return overlay


def create_grid_overlay(color: tuple[int, int, int], alpha: int = 22, x_step: int = 90, y_step: int = 70) -> Image.Image:
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rgba = hex_color(color, alpha)
    for x in range(0, WIDTH, x_step):
        draw.line((x, 0, x, HEIGHT), fill=rgba, width=1)
    for y in range(0, HEIGHT, y_step):
        draw.line((0, y, WIDTH, y), fill=rgba, width=1)
    return overlay


def create_background(accent: tuple[int, int, int], secondary: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), hex_color(PALETTE["bg"]))
    draw = ImageDraw.Draw(img)
    top = np.array(PALETTE["bg"], dtype=np.float32)
    bottom = np.array(PALETTE["panel"], dtype=np.float32)
    for y in range(0, HEIGHT, 8):
        blend = y / (HEIGHT - 1)
        color = tuple(int(v) for v in top * (1 - blend) + bottom * blend)
        draw.rectangle((0, y, WIDTH, y + 8), fill=hex_color(color))
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse((-250, -180, 820, 620), fill=hex_color(accent, 70))
    gdraw.ellipse((WIDTH - 880, 160, WIDTH + 160, HEIGHT + 160), fill=hex_color(secondary, 64))
    gdraw.polygon(
        [(WIDTH * 0.58, -50), (WIDTH + 50, -50), (WIDTH + 50, HEIGHT * 0.42), (WIDTH * 0.76, HEIGHT * 0.26)],
        fill=hex_color(accent, 32),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    img.alpha_composite(glow)
    img.alpha_composite(SCANLINES)
    return img


SCANLINES = create_scanline_overlay()
GRID_RED = create_grid_overlay(PALETTE["red"])
GRID_CYAN = create_grid_overlay(PALETTE["cyan"])
GRID_AMBER = create_grid_overlay(PALETTE["amber"])
BG_NEUTRAL = create_background(PALETTE["cyan"], PALETTE["panel_bright"])
BG_ALERT = create_background(PALETTE["red"], PALETTE["cyan"])
BG_STORM = create_background(PALETTE["storm"], PALETTE["red"])
BG_CYAN = create_background(PALETTE["cyan"], PALETTE["green"])


def base_frame(kind: str) -> Image.Image:
    if kind == "alert":
        return BG_ALERT.copy()
    if kind == "storm":
        return BG_STORM.copy()
    if kind == "cyan":
        return BG_CYAN.copy()
    return BG_NEUTRAL.copy()


def draw_live_bug(draw: ImageDraw.ImageDraw, label: str, source: str, stamp: str, accent: tuple[int, int, int]) -> None:
    draw.rounded_rectangle((60, 44, 210, 92), radius=12, fill=hex_color(accent))
    draw.text((84, 53), label, font=font("headline", 36), fill=hex_color(PALETTE["bg"]))
    draw.rounded_rectangle((228, 44, 606, 92), radius=12, fill=hex_color(PALETTE["panel"], 218))
    draw.text((252, 56), source.upper(), font=font("mono", 28), fill=hex_color(PALETTE["white"]))
    draw.text((WIDTH - 390, 54), stamp, font=font("mono", 27), fill=hex_color(PALETTE["muted"]))


def draw_ticker(draw: ImageDraw.ImageDraw, t: float, text: str, accent: tuple[int, int, int]) -> None:
    band_top = HEIGHT - 104
    draw.rectangle((0, band_top, WIDTH, HEIGHT), fill=hex_color(PALETTE["panel"], 232))
    draw.rectangle((0, band_top, WIDTH, band_top + 10), fill=hex_color(accent))
    ticker_font = font("mono", 34)
    repeated = f"  {text}  //"
    chunk_w = int(draw.textlength(repeated, font=ticker_font))
    offset = -int((t * 285) % chunk_w)
    for i in range(-1, WIDTH // max(chunk_w, 1) + 3):
        draw.text((offset + i * chunk_w, band_top + 34), repeated, font=ticker_font, fill=hex_color(PALETTE["white"]))


def add_glitch_blocks(img: Image.Image, frame_idx: int, intensity: int, accent: tuple[int, int, int]) -> None:
    rng = random.Random(1000 + frame_idx * 17 + intensity)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(intensity):
        x = rng.randint(0, WIDTH - 220)
        y = rng.randint(80, HEIGHT - 180)
        w = rng.randint(80, 420)
        h = rng.randint(8, 36)
        fill = hex_color(accent if rng.random() > 0.5 else PALETTE["white"], rng.randint(38, 110))
        draw.rectangle((x, y, x + w, y + h), fill=fill)


def draw_capsule(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, accent: tuple[int, int, int]) -> None:
    draw.rounded_rectangle(box, radius=18, fill=hex_color(PALETTE["panel"], 225), outline=hex_color(accent, 210), width=3)
    tx = box[0] + 18
    ty = box[1] + 16
    draw.text((tx, ty), text, font=font("headline", 46), fill=hex_color(PALETTE["white"]))


def multiline(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font_role: str, size: int, fill, spacing: int = 10) -> None:
    draw.multiline_text(xy, text, font=font(font_role, size), fill=fill, spacing=spacing)


def render_opener(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    draw_live_bug(draw, "LIVE", "AMERICA RIGHT NOW", "THU 03.12.2026", PALETTE["red"])
    rise = int(120 * (1 - ease_out_cubic(p)))
    title_font = font("headline", 176)
    sub_font = font("mono", 34)
    draw.text((86, 124 + rise), "AMERICA", font=title_font, fill=hex_color(PALETTE["white"]))
    draw.text((86, 286 + rise), "TODAY", font=title_font, fill=hex_color(PALETTE["cyan"]))
    draw.text((92, 458), "FOUR STORIES // ONE TEMPERATURE // MARCH 12, 2026", font=sub_font, fill=hex_color(PALETTE["muted"]))
    capsules = [
        (92, 590, 464, 678, "DRONE ALERT", PALETTE["red"]),
        (494, 590, 806, 678, "CPI 2.4%", PALETTE["cyan"]),
        (836, 590, 1216, 678, "65M STORMS", PALETTE["storm"]),
        (1246, 590, 1810, 678, "DHS SHUTDOWN", PALETTE["amber"]),
    ]
    for x0, y0, x1, y1, label, accent in capsules:
        box = (x0, y0 - int(48 * (1 - ease_out_cubic(p))), x1, y1 - int(48 * (1 - ease_out_cubic(p))))
        draw_capsule(draw, box, label, accent)
    draw_ticker(draw, t, "STAY CALM // STAY TUNED // AMERICA RIGHT NOW", PALETTE["red"])


def render_drone(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    img.alpha_composite(GRID_RED)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_live_bug(draw, "ALERT", "SOURCE: ABC7 LOS ANGELES", "IRAN RETALIATION WATCH", PALETTE["red"])
    radar_center = (410, 540)
    for radius in (120, 200, 280):
        draw.ellipse((radar_center[0] - radius, radar_center[1] - radius, radar_center[0] + radius, radar_center[1] + radius), outline=hex_color(PALETTE["red"], 150), width=3)
    angle = -70 + 160 * p
    x2 = radar_center[0] + int(math.cos(math.radians(angle)) * 320)
    y2 = radar_center[1] + int(math.sin(math.radians(angle)) * 320)
    draw.line((radar_center[0], radar_center[1], x2, y2), fill=hex_color(PALETTE["cyan"], 220), width=6)
    draw.text((166, 190), "WEST", font=font("headline", 94), fill=hex_color(PALETTE["white"]))
    draw.text((160, 264), "COAST", font=font("headline", 124), fill=hex_color(PALETTE["red"]))
    draw.rounded_rectangle((850, 164, 1784, 414), radius=26, fill=hex_color(PALETTE["panel"], 214))
    multiline(
        draw,
        (894, 208),
        "FBI memo warned Iran allegedly aspired\n"
        "to launch surprise drones from offshore\n"
        "against unspecified California targets.",
        "headline",
        66,
        hex_color(PALETTE["white"]),
    )
    draw.rounded_rectangle((850, 454, 1784, 760), radius=26, fill=hex_color(PALETTE["panel"], 220), outline=hex_color(PALETTE["red"], 200), width=3)
    multiline(
        draw,
        (894, 498),
        "Condition: if the U.S.\n"
        "struck Iran.\n\n"
        "Graphic mood: warning\n"
        "without confirmation.",
        "body",
        56,
        hex_color(PALETTE["muted"]),
        spacing=14,
    )
    add_glitch_blocks(img, frame_idx, 8, PALETTE["red"])
    draw_ticker(draw, t, "CALIFORNIA // DRONE WATCH // SOURCE ABC7 // STAY CALM", PALETTE["red"])


def render_signal(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    colors = [PALETTE["white"], PALETTE["cyan"], PALETTE["amber"], PALETTE["red"], PALETTE["storm"], PALETTE["muted"]]
    band_w = WIDTH // len(colors)
    for idx, color in enumerate(colors):
        draw.rectangle((idx * band_w, 160, (idx + 1) * band_w, 760), fill=hex_color(color))
    noise = Image.effect_noise((WIDTH, HEIGHT), 42).convert("L")
    noise = Image.merge("RGBA", (noise, noise, noise, noise.point(lambda v: int(v * 0.18))))
    img.alpha_composite(noise)
    draw.rectangle((0, 0, WIDTH, 140), fill=hex_color(PALETTE["bg"], 235))
    draw.rectangle((0, HEIGHT - 150, WIDTH, HEIGHT), fill=hex_color(PALETTE["bg"], 235))
    draw.text((110, 250), "SIGNAL LOST", font=font("headline", 188), fill=hex_color(PALETTE["bg"]))
    draw.text((118, 452), "PLEASE STAND BY", font=font("headline", 126), fill=hex_color(PALETTE["bg"]))


def render_cpi(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    img.alpha_composite(GRID_CYAN)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_live_bug(draw, "DATA", "SOURCE: BLS CPI RELEASE", "FEBRUARY 2026", PALETTE["cyan"])
    value_x = 100 + int(30 * math.sin(t * 3.4))
    draw.text((value_x, 176), "2.4%", font=font("headline", 296), fill=hex_color(PALETTE["white"]))
    draw.text((118, 454), "YEAR OVER YEAR", font=font("headline", 102), fill=hex_color(PALETTE["cyan"]))
    draw.text((124, 556), "0.3% MONTH", font=font("headline", 114), fill=hex_color(PALETTE["green"]))
    draw.rounded_rectangle((980, 164, 1788, 760), radius=28, fill=hex_color(PALETTE["panel"], 214))
    multiline(
        draw,
        (1026, 214),
        "core CPI: 2.5% year over year\n"
        "core CPI: +0.2% in February\n\n"
        "cooler headline.\n"
        "still expensive room.",
        "headline",
        66,
        hex_color(PALETTE["white"]),
        spacing=16,
    )
    small_font = font("mono", 30)
    tiny_values = [
        "rent", "insurance", "groceries", "energy", "medical", "airfare", "coffee", "childcare",
        "repairs", "shelter", "services", "fuel", "core", "real wages", "receipts", "checkout",
    ]
    for idx, word in enumerate(tiny_values):
        x = 96 + (idx % 4) * 180 + int(18 * math.sin(t * 2.1 + idx))
        y = 746 + (idx // 4) * 52
        draw.text((x, y), word.upper(), font=small_font, fill=hex_color(PALETTE["muted"]))
    add_glitch_blocks(img, frame_idx, 4, PALETTE["cyan"])
    draw_ticker(draw, t, "PRICE PULSE // CPI +0.3 MONTH // CORE +0.2 MONTH // BLS", PALETTE["cyan"])


def render_burst(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    add_glitch_blocks(img, frame_idx, 18, PALETTE["cyan"])
    add_glitch_blocks(img, frame_idx + 1, 14, PALETTE["red"])
    draw.text((104, 310), "PRICE CHECK", font=font("headline", 212), fill=hex_color(PALETTE["white"]))
    draw.text((112, 512), "SIGNAL SPIKE", font=font("headline", 178), fill=hex_color(PALETTE["red"]))


def render_storm(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    img.alpha_composite(GRID_RED)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_live_bug(draw, "WATCH", "SOURCE: AP / ABC", "SEVERE WEATHER", PALETTE["storm"])
    for idx in range(9):
        x = 90 + idx * 188 + int(24 * math.sin(t * 2.1 + idx))
        draw.rectangle((x, 200, x + 90, 820), fill=hex_color(PALETTE["storm"], 24 + idx * 6))
    draw.text((86, 172), "65M", font=font("headline", 290), fill=hex_color(PALETTE["white"]))
    draw.text((90, 424), "IN SEVERE", font=font("headline", 138), fill=hex_color(PALETTE["storm"]))
    draw.text((92, 552), "WEATHER RISK", font=font("headline", 138), fill=hex_color(PALETTE["white"]))
    draw.rounded_rectangle((890, 176, 1780, 780), radius=26, fill=hex_color(PALETTE["panel"], 220), outline=hex_color(PALETTE["storm"], 220), width=3)
    multiline(
        draw,
        (938, 230),
        "Indiana:\n"
        "a married couple in their 80s\n"
        "were killed when a tornado\n"
        "hit their home.\n\n"
        "The map keeps flashing.",
        "headline",
        64,
        hex_color(PALETTE["white"]),
        spacing=16,
    )
    add_glitch_blocks(img, frame_idx, 6, PALETTE["storm"])
    draw_ticker(draw, t, "TORNADOES // 65 MILLION IN RISK ZONE // INDIANA DEADLY STORM", PALETTE["storm"])


def render_meanwhile(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=hex_color(PALETTE["bg"], 210))
    add_glitch_blocks(img, frame_idx, 10, PALETTE["white"])
    draw.text((244, 290), "MEANWHILE", font=font("headline", 246), fill=hex_color(PALETTE["white"]))
    draw.text((250, 548), "THE AIRPORTS START HUMMING", font=font("headline", 104), fill=hex_color(PALETTE["red"]))


def render_shutdown(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    img.alpha_composite(GRID_AMBER)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_live_bug(draw, "LIVE", "SOURCE: ABC NEWS", "DHS PARTIAL SHUTDOWN", PALETTE["amber"])
    draw.rounded_rectangle((86, 182, 928, 812), radius=26, fill=hex_color(PALETTE["panel"], 220))
    draw.text((136, 212), "DHS", font=font("headline", 168), fill=hex_color(PALETTE["amber"]))
    draw.text((138, 366), "SHUTDOWN", font=font("headline", 176), fill=hex_color(PALETTE["white"]))
    draw.text((140, 576), "TSA CALLOUTS x2", font=font("headline", 108), fill=hex_color(PALETTE["amber"]))
    draw.text((142, 684), "300+ OFFICERS LEFT", font=font("headline", 96), fill=hex_color(PALETTE["white"]))
    board_x = 1010
    board_y = 182
    board_w = 770
    board_h = 630
    draw.rounded_rectangle((board_x, board_y, board_x + board_w, board_y + board_h), radius=22, fill=(19, 18, 15, 255))
    board_font = font("mono", 46)
    rows = [
        ("JFK", "DELAYED", "01:58"),
        ("LAX", "SCREENING", "01:42"),
        ("ATL", "QUEUE", "01:11"),
        ("ORD", "HOLD", "00:57"),
        ("SFO", "WAIT", "02:00"),
        ("SEA", "STANDBY", "01:26"),
    ]
    for idx, (airport, status, wait) in enumerate(rows):
        y = board_y + 68 + idx * 88
        draw.text((board_x + 42, y), airport, font=board_font, fill=hex_color(PALETTE["amber"]))
        flicker = status if (idx + frame_idx // 3) % 3 else "LINE"
        draw.text((board_x + 220, y), flicker, font=board_font, fill=hex_color(PALETTE["white"]))
        draw.text((board_x + 590, y), wait, font=board_font, fill=hex_color(PALETTE["amber"]))
    draw.text((1040, 834), "some waits reached two hours", font=font("headline", 72), fill=hex_color(PALETTE["white"]))
    add_glitch_blocks(img, frame_idx, 6, PALETTE["amber"])
    draw_ticker(draw, t, "AIRPORT DRAG // TSA CALLOUTS DOUBLED // WAIT TIMES UP TO TWO HOURS", PALETTE["amber"])


def draw_meter(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, value: float, accent: tuple[int, int, int]) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=18, fill=hex_color(PALETTE["panel"], 222), outline=hex_color(accent, 180), width=3)
    draw.text((x0 + 26, y0 + 22), label, font=font("headline", 70), fill=hex_color(PALETTE["white"]))
    bar_y = y1 - 92
    draw.rounded_rectangle((x0 + 26, bar_y, x1 - 26, bar_y + 28), radius=14, fill=hex_color(PALETTE["bg"]))
    fill_w = int((x1 - x0 - 52) * clamp(value, 0.0, 1.0))
    draw.rounded_rectangle((x0 + 26, bar_y, x0 + 26 + fill_w, bar_y + 28), radius=14, fill=hex_color(accent))
    pct = int(value * 100)
    draw.text((x0 + 26, y0 + 126), f"{pct:02d}", font=font("headline", 124), fill=hex_color(accent))


def render_dashboard(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    draw_live_bug(draw, "LIVE", "NATIONAL TEMPERATURE", "FOUR WINDOWS", PALETTE["red"])
    values = [
        ("WAR ALERT", 0.88 + 0.03 * math.sin(t * 2.8), PALETTE["red"]),
        ("PRICE PULSE", 0.54 + 0.05 * math.sin(t * 2.1), PALETTE["cyan"]),
        ("STORM LOAD", 0.82 + 0.04 * math.sin(t * 3.2), PALETTE["storm"]),
        ("QUEUE HEAT", 0.74 + 0.05 * math.sin(t * 2.6), PALETTE["amber"]),
    ]
    boxes = [
        (84, 176, 906, 474),
        (1014, 176, 1836, 474),
        (84, 534, 906, 832),
        (1014, 534, 1836, 832),
    ]
    for box, (label, value, accent) in zip(boxes, values):
        draw_meter(draw, box, label, value, accent)
    draw.text((96, 892), "AMERICA TODAY: THE ALERT DOES NOT CHOOSE JUST ONE SUBJECT.", font=font("headline", 84), fill=hex_color(PALETTE["muted"]))
    draw_ticker(draw, t, "AMERICA RIGHT NOW // WAR // PRICES // STORMS // LINES", PALETTE["red"])


def render_break(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=hex_color(PALETTE["bg"], 236))
    draw_live_bug(draw, "LIVE", "CLEAN FRAME", "PAUSE", PALETTE["white"])
    draw.text((110, 370), "AMERICA TODAY:", font=font("headline", 160), fill=hex_color(PALETTE["muted"]))
    draw.text((110, 560), "FOUR ALARMS, ONE SCREEN.", font=font("headline", 174), fill=hex_color(PALETTE["white"]))
    draw.line((110, 760, 1730, 760), fill=hex_color(PALETTE["white"], 180), width=4)


def render_stack(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    draw_live_bug(draw, "LIVE", "LOWER-THIRD FEVER", "STACKED HEADLINES", PALETTE["red"])
    cards = [
        ("DRONE ALERT", "FBI memo points to offshore California threat", PALETTE["red"]),
        ("CPI 2.4%", "BLS says February rose 0.3% on the month", PALETTE["cyan"]),
        ("65M AT RISK", "Severe weather after deadly Indiana tornado", PALETTE["storm"]),
        ("DHS SHUTDOWN", "TSA calls out, lines stretch, airports drag", PALETTE["amber"]),
    ]
    for idx, (title, subtitle, accent) in enumerate(cards):
        y = 182 + idx * 162 - int(34 * math.sin(t * 2.1 + idx))
        draw.rounded_rectangle((92, y, 1828, y + 128), radius=22, fill=hex_color(PALETTE["panel"], 228), outline=hex_color(accent, 190), width=3)
        draw.rectangle((92, y, 360, y + 128), fill=hex_color(accent, 220))
        draw.text((124, y + 22), title, font=font("headline", 80), fill=hex_color(PALETTE["bg"]))
        draw.text((402, y + 32), subtitle, font=font("headline", 62), fill=hex_color(PALETTE["white"]))
    draw_ticker(draw, t, "STACK THE LOWER THIRDS // MAKE THE TENSION LEGIBLE", PALETTE["red"])


def render_climax(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    img.alpha_composite(GRID_RED)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_live_bug(draw, "REDLINE", "AMERICA RIGHT NOW", "ACCUMULATION", PALETTE["red"])
    draw.text((88, 162), "NOT ONE STORY.", font=font("headline", 170), fill=hex_color(PALETTE["white"]))
    draw.text((90, 320), "ACCUMULATION.", font=font("headline", 214), fill=hex_color(PALETTE["red"]))
    boxes = [
        ((94, 560, 472, 806), "WAR", PALETTE["red"], "ALERT"),
        ((518, 560, 896, 806), "PRICES", PALETTE["cyan"], "PULSE"),
        ((942, 560, 1320, 806), "STORMS", PALETTE["storm"], "FLASH"),
        ((1366, 560, 1744, 806), "LINES", PALETTE["amber"], "HUM"),
    ]
    for box, label, accent, sub in boxes:
        draw.rounded_rectangle(box, radius=22, fill=hex_color(PALETTE["panel"], 230), outline=hex_color(accent, 210), width=3)
        draw.text((box[0] + 26, box[1] + 20), label, font=font("headline", 84), fill=hex_color(PALETTE["white"]))
        draw.text((box[0] + 30, box[1] + 108), sub, font=font("headline", 120), fill=hex_color(accent))
    add_glitch_blocks(img, frame_idx, 18, PALETTE["red"])
    add_glitch_blocks(img, frame_idx + 2, 10, PALETTE["cyan"])
    draw_ticker(draw, t, "STAY TUNED // STAY INSIDE // STAY IN LINE // STAY CALM?", PALETTE["red"])


def render_button(img: Image.Image, t: float, p: float, frame_idx: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    fade = int(255 * (1 - p * 0.7))
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 230))
    draw.rounded_rectangle((260, 226, 1660, 772), radius=28, fill=hex_color(PALETTE["panel"], 230), outline=hex_color(PALETTE["white"], 100), width=2)
    draw.text((334, 292), "NO SINGLE STORY", font=font("headline", 172), fill=(PALETTE["white"][0], PALETTE["white"][1], PALETTE["white"][2], fade))
    draw.text((336, 470), "ONLY ACCUMULATION", font=font("headline", 166), fill=(PALETTE["red"][0], PALETTE["red"][1], PALETTE["red"][2], fade))
    draw.text((340, 642), "END TRANSMISSION", font=font("mono", 70), fill=(PALETTE["muted"][0], PALETTE["muted"][1], PALETTE["muted"][2], fade))


RENDERERS = {
    "opener": lambda t, p, frame_idx: render_opener(base_frame("neutral"), t, p, frame_idx),
}


def render_scene_frame(global_t: float, frame_idx: int) -> Image.Image:
    for start, end, scene_id in SCENES:
        if global_t < end or math.isclose(global_t, end):
            local_t = global_t - start
            duration = end - start
            p = clamp(local_t / max(duration, 0.001), 0.0, 1.0)
            break
    else:
        scene_id = SCENES[-1][2]
        start, end = SCENES[-1][0], SCENES[-1][1]
        local_t = global_t - start
        p = 1.0

    if scene_id == "opener":
        img = base_frame("neutral")
        render_opener(img, global_t, p, frame_idx)
    elif scene_id == "drone":
        img = base_frame("alert")
        render_drone(img, global_t, p, frame_idx)
    elif scene_id == "signal":
        img = base_frame("neutral")
        render_signal(img, global_t, p, frame_idx)
    elif scene_id == "cpi":
        img = base_frame("cyan")
        render_cpi(img, global_t, p, frame_idx)
    elif scene_id == "burst":
        img = base_frame("neutral")
        render_burst(img, global_t, p, frame_idx)
    elif scene_id == "storm":
        img = base_frame("storm")
        render_storm(img, global_t, p, frame_idx)
    elif scene_id == "meanwhile":
        img = base_frame("neutral")
        render_meanwhile(img, global_t, p, frame_idx)
    elif scene_id == "shutdown":
        img = base_frame("neutral")
        render_shutdown(img, global_t, p, frame_idx)
    elif scene_id == "dashboard":
        img = base_frame("neutral")
        render_dashboard(img, global_t, p, frame_idx)
    elif scene_id == "break":
        img = base_frame("neutral")
        render_break(img, global_t, p, frame_idx)
    elif scene_id == "stack":
        img = base_frame("neutral")
        render_stack(img, global_t, p, frame_idx)
    elif scene_id == "climax":
        img = base_frame("alert")
        render_climax(img, global_t, p, frame_idx)
    else:
        img = base_frame("neutral")
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
    env = np.minimum(1.0, np.minimum(t / 0.04, (duration - t) / 0.12))
    env = np.clip(env, 0.0, 1.0)
    instantaneous = freq + wobble * np.sin(2 * math.pi * 0.7 * t + phase)
    wave_data = np.sin(2 * math.pi * instantaneous * t + phase)
    buffer[start_idx:end_idx] += amp * env * wave_data


def add_noise(buffer: np.ndarray, start: float, duration: float, amp: float, seed: int) -> None:
    start_idx = int(start * SAMPLE_RATE)
    end_idx = min(len(buffer), int((start + duration) * SAMPLE_RATE))
    if end_idx <= start_idx:
        return
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, 1.0, end_idx - start_idx)
    t = np.linspace(0.0, duration, end_idx - start_idx, endpoint=False)
    env = np.minimum(1.0, np.minimum(t / 0.03, (duration - t) / 0.08))
    buffer[start_idx:end_idx] += amp * env * noise


def add_sweep(buffer: np.ndarray, start: float, duration: float, start_freq: float, end_freq: float, amp: float) -> None:
    start_idx = int(start * SAMPLE_RATE)
    end_idx = min(len(buffer), int((start + duration) * SAMPLE_RATE))
    if end_idx <= start_idx:
        return
    idx = np.arange(end_idx - start_idx)
    t = idx / SAMPLE_RATE
    freqs = np.linspace(start_freq, end_freq, end_idx - start_idx)
    phase = 2 * math.pi * np.cumsum(freqs) / SAMPLE_RATE
    env = np.minimum(1.0, np.minimum(t / 0.02, (duration - t) / 0.12))
    buffer[start_idx:end_idx] += amp * env * np.sin(phase)


def generate_audio_bed() -> Path:
    samples = int(DURATION * SAMPLE_RATE)
    audio = np.zeros(samples, dtype=np.float32)
    add_tone(audio, 0.0, DURATION, 57.0, 0.12, wobble=1.6, phase=0.3)
    add_tone(audio, 0.0, DURATION, 114.0, 0.035, wobble=2.5, phase=1.1)
    add_tone(audio, 10.8, 3.2, 43.0, 0.08, wobble=4.2, phase=0.6)
    add_tone(audio, 29.68, 4.2, 69.0, 0.10, wobble=5.0, phase=1.4)

    for mark in [0.0, 1.78, 5.50, 6.30, 10.18, 10.80, 14.56, 15.31, 19.99, 26.34, 29.68, 34.09]:
        add_tone(audio, mark, 0.09, 1220.0, 0.085)
        add_noise(audio, mark, 0.05, 0.02, int(mark * 1000) + 9)

    for mark in [5.50, 10.18, 14.56, 29.68]:
        add_sweep(audio, mark, 0.38, 148.0, 52.0, 0.11)

    add_noise(audio, 15.2, 0.9, 0.012, 77)
    add_noise(audio, 30.0, 1.4, 0.014, 88)
    audio = np.clip(audio, -0.85, 0.85)

    stereo = np.empty((samples, 2), dtype=np.float32)
    stereo[:, 0] = audio * 0.98
    stereo[:, 1] = np.roll(audio, 220) * 0.94
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

    filters = ["[0:a]volume=0.84[a0]"]
    labels = ["[a0]"]
    for idx, (delay, _, _, level) in enumerate(VOICE_LINES, start=1):
        ms = int(delay * 1000)
        voice_filter = (
            f"[{idx}:a]aresample={SAMPLE_RATE},highpass=f=180,lowpass=f=3600,"
            f"volume={level},adelay={ms}|{ms}"
        )
        if idx == len(VOICE_LINES):
            voice_filter += f",asetrate={int(SAMPLE_RATE * 0.96)},aresample={SAMPLE_RATE}"
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
