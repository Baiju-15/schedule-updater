#!/usr/bin/env python3
"""
Generate a premium, animated hero banner and static preview for Schedule Updater.

Visual Identity:
- Dark navy dashboard palette (#070b16) with subtle matrix grid.
- Electric cyan (#00f0ff), teal (#2dd4bf), violet (#c084fc), and emerald (#34d399) highlights.
- Glowing calendar icon, clean typography, rounded dashboard cards.
- 6-second seamless loop at 12 fps (72 frames total).
- Optimized palette and dither settings via FFmpeg (< 3 MB target).
"""

import argparse
import math
import os
import shutil
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 380
DEFAULT_FPS = 12
DEFAULT_FRAMES = 72

FONT_CANDIDATES = {
    "regular": [
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/Adwaita/AdwaitaSans-Regular.ttf",
    ],
    "bold": [
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/Adwaita/AdwaitaSans-Bold.ttf",
    ],
    "mono": [
        "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf",
        "/usr/share/fonts/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
    ],
    "mono_bold": [
        "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf",
        "/usr/share/fonts/liberation/LiberationMono-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSansMono-Bold.ttf",
    ],
}


def resolve_font_path(candidates):
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def get_font_dict():
    p_reg = resolve_font_path(FONT_CANDIDATES["regular"])
    p_bold = resolve_font_path(FONT_CANDIDATES["bold"])
    p_mono = resolve_font_path(FONT_CANDIDATES["mono"])
    p_mbold = resolve_font_path(FONT_CANDIDATES["mono_bold"])

    def load(path, size, fallback_bold=False):
        if path and os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    return {
        "title": load(p_bold, 21),
        "badge": load(p_mbold, 10),
        "sub": load(p_reg, 11),
        "sub_mono": load(p_mono, 10),
        "card_stage": load(p_mbold, 10),
        "card_title": load(p_bold, 13),
        "item_bold": load(p_bold, 11),
        "item_desc": load(p_reg, 10),
        "chip": load(p_mbold, 9),
        "pipeline": load(p_mbold, 9),
    }


def periodic_dist(t, center):
    return abs((t - center + 0.5) % 1.0 - 0.5)


def gaussian_pulse(t, center, sigma=0.09):
    d = periodic_dist(t, center)
    return math.exp(-(d**2) / (2 * (sigma**2)))


def render_frame(t, fonts, width=CANVAS_WIDTH, height=CANVAS_HEIGHT):
    img = Image.new("RGBA", (width, height), (7, 11, 22, 255))
    draw = ImageDraw.Draw(img)

    # 1. Background Grid (subtle technical coordinate dots)
    for x in range(24, width, 28):
        for y in range(24, height, 28):
            draw.point((x, y), fill=(24, 38, 70, 90))

    # Stage pulse activation weights
    p1 = gaussian_pulse(t, 0.12, 0.09)
    p2 = gaussian_pulse(t, 0.38, 0.09)
    p3 = gaussian_pulse(t, 0.63, 0.09)
    p4 = gaussian_pulse(t, 0.88, 0.09)

    # 2. Header
    # Calendar Icon Squircle
    draw.rounded_rectangle([32, 18, 76, 62], radius=10, fill=(13, 22, 44, 255), outline=(0, 240, 255, 180), width=1)

    # Binder rings
    draw.rectangle([42, 14, 46, 20], fill=(0, 240, 255, 230))
    draw.rectangle([62, 14, 66, 20], fill=(0, 240, 255, 230))

    # Calendar top bar
    draw.rounded_rectangle([34, 20, 74, 32], radius=3, fill=(0, 240, 255, 240))

    # Calendar grid cells
    pulse_dot = int(180 + 75 * math.sin(2 * math.pi * t))
    for row in range(3):
        for col in range(4):
            cx = 40 + col * 8
            cy = 38 + row * 6
            if row == 1 and col == 2:
                draw.rectangle([cx, cy, cx + 5, cy + 4], fill=(52, 211, 153, pulse_dot))
            else:
                draw.rectangle([cx, cy, cx + 5, cy + 4], fill=(148, 163, 184, 180))

    # Title
    draw.text((88, 20), "SCHEDULE UPDATER", font=fonts["title"], fill=(248, 250, 252))

    # Version badge
    draw.rounded_rectangle([316, 22, 372, 42], radius=5, fill=(14, 38, 68), outline=(0, 240, 255, 180), width=1)
    draw.text((326, 26), "v2.1.0", font=fonts["badge"], fill=(0, 240, 255))

    # Deterministic Engine badge
    draw.rounded_rectangle([378, 22, 575, 42], radius=5, fill=(12, 38, 48), outline=(20, 184, 166, 180), width=1)
    draw.text((388, 26), "DETERMINISTIC AGENT SKILL", font=fonts["badge"], fill=(45, 212, 191))

    # Tagline
    draw.text((89, 46), "Intelligent Multi-Format Timetable Ingestion • Conflict-Free Reconciliation • Safe Google Calendar Dispatch", font=fonts["sub"], fill=(148, 163, 184))

    # Header Right Status Pill
    green_pulse = int(170 + 85 * math.sin(4 * math.pi * t))
    draw.rounded_rectangle([940, 22, 1168, 44], radius=6, fill=(11, 30, 28), outline=(16, 185, 129, 160), width=1)
    draw.ellipse([952, 29, 960, 37], fill=(52, 211, 153, green_pulse))
    draw.text((968, 26), "HOST CONNECTOR PROTOCOL", font=fonts["badge"], fill=(52, 211, 153))

    draw.text((942, 48), "No Google credentials stored • Zero blind writes", font=fonts["sub_mono"], fill=(100, 116, 139))

    # Header Divider Line with smooth fading light sweep
    draw.line([(32, 72), (1168, 72)], fill=(24, 38, 68), width=1)
    sweep_alpha = int(180 * (math.sin(math.pi * t) ** 2))
    if sweep_alpha > 2:
        sweep_x = 32 + t * (1168 - 32)
        sweep_w = 90
        x_start = max(32, sweep_x - sweep_w)
        x_end = min(1168, sweep_x + sweep_w)
        draw.line([(x_start, 72), (x_end, 72)], fill=(0, 240, 255, sweep_alpha), width=1)

    # 3. Four Dashboard Cards
    cards = [
        {"x1": 32, "x2": 260, "stage": "STAGE 01", "title": "INGESTION", "color": (56, 189, 248), "phase": p1},
        {"x1": 298, "x2": 582, "stage": "STAGE 02", "title": "EXTRACT & VALIDATE", "color": (45, 212, 191), "phase": p2},
        {"x1": 620, "x2": 904, "stage": "STAGE 03", "title": "PREVIEW & RECONCILE", "color": (192, 132, 252), "phase": p3},
        {"x1": 942, "x2": 1168, "stage": "STAGE 04", "title": "SAFE HOST DISPATCH", "color": (52, 211, 153), "phase": p4},
    ]

    for c in cards:
        x1, x2 = c["x1"], c["x2"]
        y1, y2 = 86, 334
        glow_alpha = int(50 + 205 * c["phase"])
        border_col = (
            int(c["color"][0] * (c["phase"] * 0.75 + 0.25)),
            int(c["color"][1] * (c["phase"] * 0.75 + 0.25)),
            int(c["color"][2] * (c["phase"] * 0.75 + 0.25)),
            glow_alpha
        )

        if c["phase"] > 0.35:
            draw.rounded_rectangle([x1 - 1, y1 - 1, x2 + 1, y2 + 1], radius=11, outline=(c["color"][0], c["color"][1], c["color"][2], int(100 * c["phase"])), width=1)

        draw.rounded_rectangle([x1, y1, x2, y2], radius=10, fill=(11, 18, 36, 245), outline=border_col, width=1)
        draw.text((x1 + 14, y1 + 12), c["stage"], font=fonts["card_stage"], fill=c["color"])
        draw.text((x1 + 14, y1 + 26), c["title"], font=fonts["card_title"], fill=(241, 245, 249))
        draw.line([(x1 + 14, y1 + 46), (x2 - 14, y1 + 46)], fill=(24, 38, 66), width=1)

    # Card 1 (Ingestion Formats)
    formats = [
        ("PDF / Scanned", "Native text + OCR fallback", (56, 189, 248), 0.05),
        ("PNG / JPG / WEBP", "Tesseract vision pipeline", (45, 212, 191), 0.10),
        ("DOCX / HTML", "Formatted table parsing", (129, 140, 248), 0.15),
        ("Markdown / TXT", "Pasted text & raw schedule", (192, 132, 252), 0.20),
    ]
    for i, (fmt_name, fmt_desc, fmt_col, sub_t) in enumerate(formats):
        fy = 142 + i * 44
        sub_pulse = gaussian_pulse(t, sub_t, 0.06)
        item_border = (
            int(fmt_col[0] * (sub_pulse * 0.7 + 0.2)),
            int(fmt_col[1] * (sub_pulse * 0.7 + 0.2)),
            int(fmt_col[2] * (sub_pulse * 0.7 + 0.2)),
            int(60 + 190 * sub_pulse)
        )
        draw.rounded_rectangle([44, fy, 248, fy + 38], radius=6, fill=(15, 24, 48), outline=item_border, width=1)
        draw.ellipse([54, fy + 14, 60, fy + 20], fill=fmt_col)
        draw.text((68, fy + 6), fmt_name, font=fonts["item_bold"], fill=(226, 232, 240))
        draw.text((68, fy + 21), fmt_desc, font=fonts["item_desc"], fill=(148, 163, 184))

    # Card 2 (Extract & Validate)
    draw.rounded_rectangle([310, 142, 570, 202], radius=6, fill=(14, 25, 48), outline=(24, 48, 80), width=1)
    draw.text((322, 148), "EXTRACT ENGINE", font=fonts["item_bold"], fill=(45, 212, 191))
    draw.text((322, 165), "• Temporal extraction & ISO 8601 normalization", font=fonts["item_desc"], fill=(203, 213, 225))
    draw.text((322, 180), "• Multi-day spans & overnight crossing detection", font=fonts["item_desc"], fill=(148, 163, 184))

    draw.rounded_rectangle([310, 210, 570, 270], radius=6, fill=(14, 25, 48), outline=(24, 48, 80), width=1)
    draw.text((322, 216), "VALIDATE ENGINE", font=fonts["item_bold"], fill=(56, 189, 248))
    draw.text((322, 233), "• Strict AM/PM logic & timezone verification", font=fonts["item_desc"], fill=(203, 213, 225))
    draw.text((322, 248), "• RFC 5545 recurrence (UNTIL vs COUNT checks)", font=fonts["item_desc"], fill=(148, 163, 184))

    chip2_border = (20, 184, 166, int(100 + 155 * p2))
    draw.rounded_rectangle([310, 278, 570, 318], radius=6, fill=(12, 34, 40), outline=chip2_border, width=1)
    draw.text((322, 286), "✓ SAFETY INVARIANT:", font=fonts["chip"], fill=(45, 212, 191))
    draw.text((322, 300), "Never guesses yearless dates or ambiguous times", font=fonts["item_desc"], fill=(241, 245, 249))

    # Card 3 (Preview & Reconcile)
    draw.rounded_rectangle([632, 142, 892, 202], radius=6, fill=(18, 22, 52), outline=(38, 42, 88), width=1)
    draw.text((644, 148), "PREVIEW PLANNER", font=fonts["item_bold"], fill=(192, 132, 252))
    draw.text((644, 165), "• 4 operation modes (PREVIEW_ONLY, CREATE, ...)", font=fonts["item_desc"], fill=(203, 213, 225))
    draw.text((644, 180), "• Zero-write guarantee: preview never touches API", font=fonts["item_desc"], fill=(148, 163, 184))

    draw.rounded_rectangle([632, 210, 892, 270], radius=6, fill=(18, 22, 52), outline=(38, 42, 88), width=1)
    draw.text((644, 216), "RECONCILIATION ENGINE", font=fonts["item_bold"], fill=(168, 85, 247))
    draw.text((644, 233), "• Conflict & duplicate detection via identity_key", font=fonts["item_desc"], fill=(203, 213, 225))
    draw.text((644, 248), "• Surgical patch_fields map; preserves user notes", font=fonts["item_desc"], fill=(148, 163, 184))

    chip3_border = (168, 85, 247, int(100 + 155 * p3))
    draw.rounded_rectangle([632, 278, 892, 318], radius=6, fill=(28, 20, 48), outline=chip3_border, width=1)
    draw.text((644, 286), "✓ NO SILENT DELETION:", font=fonts["chip"], fill=(192, 132, 252))
    draw.text((644, 300), "Absence in timetable never infers event cancellation", font=fonts["item_desc"], fill=(241, 245, 249))

    # Card 4 (Safe Host Execution)
    draw.rounded_rectangle([954, 142, 1156, 270], radius=6, fill=(11, 28, 30), outline=(20, 74, 60), width=1)

    # Shield motif
    sx, sy = 1055, 172
    shield_pts = [
        (sx, sy - 20),
        (sx + 18, sy - 14),
        (sx + 18, sy + 6),
        (sx, sy + 22),
        (sx - 18, sy + 6),
        (sx - 18, sy - 14)
    ]
    shield_fill = (16, int(68 + 40 * p4), int(54 + 30 * p4))
    shield_outline = (52, int(211 + 44 * p4), int(153 + 40 * p4))
    draw.polygon(shield_pts, fill=shield_fill, outline=shield_outline, width=1)
    draw.line([(sx - 8, sy + 1), (sx - 2, sy + 7), (sx + 8, sy - 7)], fill=shield_outline, width=2)

    draw.text((964, 204), "VERIFIED PROTOCOL", font=fonts["card_stage"], fill=(52, 211, 153))
    draw.text((964, 220), "• Atomic state lock file", font=fonts["item_desc"], fill=(203, 213, 225))
    draw.text((964, 235), "• Read-after-write verification", font=fonts["item_desc"], fill=(203, 213, 225))
    draw.text((964, 250), "• Explicit approval on delete", font=fonts["item_desc"], fill=(148, 163, 184))

    chip4_border = (52, 211, 153, int(100 + 155 * p4))
    draw.rounded_rectangle([954, 278, 1156, 318], radius=6, fill=(12, 42, 34), outline=chip4_border, width=1)
    draw.text((964, 286), "✓ VERIFIED DISPATCH:", font=fonts["chip"], fill=(52, 211, 153))
    draw.text((964, 300), "Safe host connector execution", font=fonts["item_desc"], fill=(241, 245, 249))

    # Connectors with smooth cosine fade-in/out
    def get_conn_dot(time_val, t_start, t_dur):
        rel = time_val - t_start
        if 0.0 <= rel <= t_dur:
            prog = rel / t_dur
            alpha = math.sin(math.pi * prog)
            return prog, alpha
        return 0.0, 0.0

    c_defs = [
        (260, 210, 298, 210, (56, 189, 248), 0.18, 0.14),
        (582, 210, 620, 210, (45, 212, 191), 0.43, 0.14),
        (904, 210, 942, 210, (192, 132, 252), 0.68, 0.14),
    ]
    for x1, y1, x2, y2, col, ts, td in c_defs:
        draw.line([(x1, y1), (x2, y2)], fill=(28, 44, 76), width=2)
        prog, alpha = get_conn_dot(t, ts, td)
        if alpha > 0.01:
            px = x1 + prog * (x2 - x1)
            dot_alpha = int(255 * alpha)
            draw.ellipse([px - 4, y1 - 4, px + 4, y1 + 4], fill=(col[0], col[1], col[2], dot_alpha))
            draw.ellipse([px - 2, y1 - 2, px + 2, y1 + 2], fill=(255, 255, 255, dot_alpha))

    # 4. Bottom Pipeline Bar
    draw.line([(32, 354), (1168, 354)], fill=(20, 32, 56), width=1)
    stages_nav = [
        ("01 INGEST", 100),
        ("02 EXTRACT", 350),
        ("03 VALIDATE", 530),
        ("04 PREVIEW", 710),
        ("05 RECONCILE", 890),
        ("06 SAFE DISPATCH", 1080),
    ]
    for label, nx in stages_nav:
        draw.ellipse([nx - 14, 352, nx - 10, 356], fill=(56, 189, 248, 160))
        draw.text((nx - 4, 348), label, font=fonts["pipeline"], fill=(100, 116, 139))

    # Traveling runner with smooth sine squared fading
    runner_alpha = int(255 * (math.sin(math.pi * t) ** 2))
    if runner_alpha > 2:
        runner_x = 32 + t * (1168 - 32)
        draw.ellipse([runner_x - 4, 351, runner_x + 4, 357], fill=(0, 240, 255, int(runner_alpha * 0.6)))
        draw.ellipse([runner_x - 2, 352, runner_x + 2, 356], fill=(255, 255, 255, runner_alpha))

    return img


def generate_assets(output_gif, output_preview, fps=DEFAULT_FPS, total_frames=DEFAULT_FRAMES, keep_frames=False):
    fonts = get_font_dict()
    temp_dir = "/tmp/su_intro_frames"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    print(f"Generating {total_frames} frames ({CANVAS_WIDTH}x{CANVAS_HEIGHT} @ {fps} fps)...")
    for f in range(total_frames):
        t = f / float(total_frames)
        frame = render_frame(t, fonts)
        frame.save(os.path.join(temp_dir, f"frame_{f:03d}.png"), format="PNG")

    # Save static preview at t = 0.25 (balanced active state)
    print(f"Saving preview image to {output_preview}...")
    preview_img = render_frame(0.25, fonts)
    os.makedirs(os.path.dirname(os.path.abspath(output_preview)), exist_ok=True)
    preview_img.save(output_preview, format="PNG")

    # Encode with FFmpeg
    print(f"Encoding animated GIF to {output_gif} using FFmpeg...")
    os.makedirs(os.path.dirname(os.path.abspath(output_gif)), exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(temp_dir, "frame_%03d.png"),
        "-filter_complex",
        "[0:v] split [a][b]; [a] palettegen=max_colors=112:stats_mode=diff [p]; [b][p] paletteuse=dither=none",
        output_gif
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg encoding error:\n", res.stderr, file=sys.stderr)
        sys.exit(res.returncode)

    if not keep_frames and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    gif_size = os.path.getsize(output_gif)
    png_size = os.path.getsize(output_preview)
    print(f"Done! Created:\n  GIF: {output_gif} ({gif_size:,} bytes, {gif_size / (1024*1024):.2f} MB)")
    print(f"  PNG: {output_preview} ({png_size:,} bytes, {png_size / 1024:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description="Generate animated intro banner for Schedule Updater")
    parser.add_argument("--output-gif", default="assets/schedule-updater-intro.gif", help="Destination GIF path")
    parser.add_argument("--output-preview", default="assets/schedule-updater-preview.png", help="Destination PNG path")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help="Frames per second (default: 12)")
    parser.add_argument("--frames", type=int, default=DEFAULT_FRAMES, help="Total frame count (default: 72)")
    parser.add_argument("--keep-frames", action="store_true", help="Keep temporary frame PNG files")
    args = parser.parse_args()

    generate_assets(args.output_gif, args.output_preview, fps=args.fps, total_frames=args.frames, keep_frames=args.keep_frames)


if __name__ == "__main__":
    main()
